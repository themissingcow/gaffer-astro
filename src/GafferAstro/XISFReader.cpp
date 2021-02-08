//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2012, John Haddon. All rights reserved.
//  Copyright (c) 2012-2019, Image Engine Design Inc. All rights reserved.
//  Copyright (c) 2020, Tom Cowland. All rights reserved.
//
//  Redistribution and use in source and binary forms, with or without
//  modification, are permitted provided that the following conditions are
//  met:
//
//      * Redistributions of source code must retain the above
//        copyright notice, this list of conditions and the following
//        disclaimer.
//
//      * Redistributions in binary form must reproduce the above
//        copyright notice, this list of conditions and the following
//        disclaimer in the documentation and/or other materials provided with
//        the distribution.
//
//      * Neither the name of John Haddon nor the names of
//        any other contributors to this software may be used to endorse or
//        promote products derived from this software without specific prior
//        written permission.
//
//  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
//  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
//  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
//  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
//  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
//  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
//  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
//  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
//  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
//  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
//////////////////////////////////////////////////////////////////////////

#include "GafferAstro/XISFReader.h"

// The nested TaskMutex needs to be the first to include tbb
#include "GafferAstro/Private/LRUCache.h"

#include "GafferImage/FormatPlug.h"
#include "GafferImage/ImageAlgo.h"

#include "Gaffer/Context.h"
#include "Gaffer/StringPlug.h"

#include "IECoreImage/OpenImageIOAlgo.h"

#include "IECore/Export.h"
#include "IECore/FileSequence.h"
#include "IECore/FileSequenceFunctions.h"
#include "IECore/MessageHandler.h"

#include "boost/bind.hpp"
#include "boost/filesystem/path.hpp"
#include "boost/regex.hpp"

#include "tbb/mutex.h"

#include <memory>

#include "pcl/XISF.h"

using namespace std;
using namespace tbb;
using namespace Imath;
using namespace IECore;
using namespace GafferImage;
using namespace Gaffer;
using namespace GafferAstro;

namespace
{

class LogHandler : public pcl::XISFLogHandler
{
	public:

		LogHandler() = default;

		virtual void Init( const pcl::String& filePath, bool writing )
		{
		}

		virtual void Log( const pcl::String& text, message_type type )
		{
			bool handle;
			IECore::Msg::Level level;

			switch ( type )
			{
				case pcl::XISFMessageType::Warning:
					level = IECore::Msg::Warning;
					handle = true;
					break;
				case pcl::XISFMessageType::RecoverableError:
					level = IECore::Msg::Error;
					handle = true;
					break;
				default :
					handle = false;
			}

			if( handle )
			{
				std::stringstream m;
				m << text;
				IECore::msg( level, "XISFReader", m.str() );
			}
		}

		virtual void Close()
		{
		}
};


const IECore::InternedString g_tileBatchIndexContextName( "__tileBatchIndex" );

struct ChannelMapEntry
{
	ChannelMapEntry( int subImage, int channelIndex )
		: subImage( subImage ), channelIndex( channelIndex )
	{}

	ChannelMapEntry( const ChannelMapEntry & ) = default;

	ChannelMapEntry()
		: subImage( 0 ), channelIndex( 0 )
	{}

	int subImage;
	int channelIndex;
};

// A divide that always rounds down, instead of towards zero
//  ( note that b is assumed positive )
int coordinateDivide( int a, int b )
{
	int result = a / b;
	int remainder = a - result * b;
	return result - ( remainder < 0 );
}

V2i coordinateDivide( V2i a, V2i b )
{
	return V2i( coordinateDivide( a.x, b.x ), coordinateDivide( a.y, b.y ) );
}

// This class handles storing a file handle, and reading data from it in a way compatible with how we want
// to store it on plugs.
//
// The primary complexity is that Gaffer will request channel data a single tile at a time for a single channel,
// but XISF only supports scanline reads.
//
// To avoid repeatedly loading large chunks of data, and then discarding most of it, we group data into
// "tile batches".  A tile batch is an ObjectVector containing an array of separate channelData tiles.  It is
// a large enough chunk of data that it can be read from the file with minimal waste.  We cache tile batches
// on XISFReader::tileBatchPlug, and then XISFReader::computeChannelData just needs to select the
// correct tile batch index, access tileBatchPlug, and then return the tile at the correct tileBatchSubIndex.
// A tile batch is one tile high, and the full width of the image.
//
// Tile batches are selected using V3i "tileBatchIndex".  The Z component is the subimage to load channels from.
// The X and Y component select a region of the image.
//
class File
{

	public:

		File( std::unique_ptr<pcl::XISFReader> reader )
			: m_reader( std::move( reader ) )
		{
			std::vector<std::string> channelNames;

			if( m_reader->NumberOfImages() > 0 )
			{
				m_reader->SelectImage( 0 );
				m_info = m_reader->ImageInfo();

				if( m_info.numberOfChannels == 1 )
				{
					channelNames.push_back( "Y" );
					m_channelMap[ "Y" ] = ChannelMapEntry( 0, 0 );
				}
				else if( m_info.numberOfChannels == 3 )
				{
					channelNames.push_back( "R" );
					channelNames.push_back( "G" );
					channelNames.push_back( "B" );
					m_channelMap[ "R" ] = ChannelMapEntry( 0, 0 );
					m_channelMap[ "G" ] = ChannelMapEntry( 0, 1 );
					m_channelMap[ "B" ] = ChannelMapEntry( 0, 2 );
				}
			}

			m_channelNamesData = new StringVectorData( channelNames );

			// Set up a tile batch that is one tile high, and wide enough to hold everything from the beginning
			// of a scanline to the end
			m_tileBatchSize = V2i( 0, 1 ) +
				ImagePlug::tileIndex( V2i( m_info.width + ImagePlug::tileSize() - 1, 0 ) ) -
				ImagePlug::tileIndex( V2i( 0 ) );
		}


		// Read a chunk of data from the file, formatted as a tile batch that will be stored on the tile batch plug
		ConstObjectVectorPtr readTileBatch( V3i tileBatchIndex )
		{
			V2i batchFirstTile = V2i( tileBatchIndex.x, tileBatchIndex.y ) * m_tileBatchSize;
			Box2i targetRegion = Box2i( batchFirstTile * ImagePlug::tileSize(),
				( batchFirstTile + m_tileBatchSize ) * ImagePlug::tileSize()
			);

			// For scanline images, we always treat the tile batch as starting from the left of the data window
			batchFirstTile.x = ImagePlug::tileIndex( V2i( 0 ) ).x;

			targetRegion.min.x = 0;
			targetRegion.max.x = m_info.width;

			ObjectVectorPtr result = new ObjectVector();

			// Do the actual read of data

			std::vector<float> fileData;
			Box2i fileDataRegion;
			const int nchannels = readRegion( tileBatchIndex.z, targetRegion, fileData, fileDataRegion );
			const V2i fileDataRegionSize = fileDataRegion.size();
			size_t channelPixelOffset = fileDataRegionSize.x * fileDataRegionSize.y;

			// Unpack the channels back into their own tiles. readRegion stores all scanlines for each channel
			// together, rather than in any interleaved fashion.
			int tileBatchNumElements = nchannels * m_tileBatchSize.y * m_tileBatchSize.x;
			result->members().resize( tileBatchNumElements );

			ObjectVectorPtr resultChannels = result;

			for( int c = 0; c < nchannels; c++ )
			{
				const size_t subIndexPixelOffset = channelPixelOffset * c;

				for( int ty = batchFirstTile.y; ty < batchFirstTile.y + m_tileBatchSize.y; ty++ )
				{
					for( int tx = batchFirstTile.x; tx < batchFirstTile.x + m_tileBatchSize.x; tx++ )
					{
						V2i tileOffset = ImagePlug::tileSize() * V2i( tx, ty );
						const int subIndex = tileBatchSubIndex( c, tileOffset );

						const Box2i tileRelativeFileRegion( fileDataRegion.min - tileOffset, fileDataRegion.max - tileOffset );
						const Box2i tileRegion = BufferAlgo::intersection(
							Box2i( V2i( 0 ), V2i( ImagePlug::tileSize() ) ), tileRelativeFileRegion
						);

						if( BufferAlgo::empty( tileRegion ) )
						{
							const FloatVectorData* emptyResult = ImagePlug::blackTile();
							// Result will be treated as const as soon as we set it on the plug, and we're not
							// going to modify any elements after setting them, so it's safe to store a const
							// value in one of the elements
							resultChannels->members()[ subIndex ] = const_cast<FloatVectorData*>( emptyResult );
							continue;
						}

						FloatVectorDataPtr tileData = new IECore::FloatVectorData( std::vector<float>( ImagePlug::tilePixels() ) );
						vector<float> &tile = tileData->writable();

						for( int y = tileRegion.min.y; y < tileRegion.max.y; ++y )
						{
							// Flip scanlines in y as we use bottom origin not top
							const int scanline = fileDataRegion.size().y - 1 - (y - tileRelativeFileRegion.min.y);
							float *tileIndex = &tile[ y * ImagePlug::tileSize() + tileRegion.min.x ];
							float *dataIndex = &fileData[
								subIndexPixelOffset + ( scanline * fileDataRegionSize.x + tileRegion.min.x - tileRelativeFileRegion.min.x )
							];
							memcpy( tileIndex, dataIndex, ( tileRegion.max.x - tileRegion.min.x ) * sizeof(*dataIndex) );
						}
						resultChannels->members()[ subIndex ] = tileData;
					}
				}
			}

			return result;
		}

		// Given a channelName and tileOrigin, return the information necessary to look up the data for this tile.
		// The tileBatchIndex is used to find a tileBatch, and then the tileBatchSubIndex tells you the index
		// within that tile to use
		void findTile( const std::string &channelName, const Imath::V2i &tileOrigin, V3i &batchIndex, int &batchSubIndex ) const
		{
			if( !channelName.size() )
			{
				// For computing sample offset;
				// This is a bit of a weird interface, I should probably fix it
				batchIndex = tileBatchIndex( 0, tileOrigin );
				batchSubIndex = tileBatchSubIndex( 0, tileOrigin );
			}
			else
			{
				ChannelMapEntry channelMapEntry = m_channelMap.at( channelName );
				batchIndex = tileBatchIndex( channelMapEntry.subImage, tileOrigin );
				batchSubIndex = tileBatchSubIndex( channelMapEntry.channelIndex, tileOrigin );
			}
		}

		const pcl::ImageInfo &info() const
		{
			return m_info;
		}

		ConstStringVectorDataPtr channelNamesData()
		{
			return m_channelNamesData;
		}

	private:

		int readRegion( int subImage, const Box2i &targetRegion, std::vector<float> &data, Box2i &dataRegion )
		{
			tbb::mutex::scoped_lock lock( m_mutex );

			m_reader->SelectImage( subImage );

			const Box2i fileDataWindow( V2i( 0 ), V2i( m_info.width, m_info.height ) );
			dataRegion = BufferAlgo::intersection( targetRegion, fileDataWindow );

			const int numRows = dataRegion.size().y;
			const size_t numPixels = numRows * dataRegion.size().x;
			data.resize( m_info.numberOfChannels * numPixels );
			for( int i = 0; i < m_info.numberOfChannels; ++i )
			{
				m_reader->ReadSamples( &data[ i * numPixels ], dataRegion.min.y, numRows, i );
			}

			return m_info.numberOfChannels;
		}

		// Given a subImage index, and a tile origin, return an index to identify the tile batch which
		// where this channel data will be found
		V3i tileBatchIndex( int subImage, V2i tileOrigin ) const
		{
			V2i tileBatchOrigin = coordinateDivide( ImagePlug::tileIndex( tileOrigin ), m_tileBatchSize );
			tileBatchOrigin.x = 0;
			return V3i( tileBatchOrigin.x, tileBatchOrigin.y, subImage );
		}

		// Given a channel index, and a tile origin, return the index within a tile batch where the correct
		// tile will be found.
		int tileBatchSubIndex( int channelIndex, V2i tileOrigin ) const
		{
			int tilePlaneSize = m_tileBatchSize.x * m_tileBatchSize.y;

			V2i tileIndex = ImagePlug::tileIndex( tileOrigin );
			V2i subIndex = tileIndex - coordinateDivide( tileIndex, m_tileBatchSize ) * m_tileBatchSize;
			// For scanline images, horizontal index relative to data window
			subIndex.x = tileIndex.x - ImagePlug::tileIndex( V2i( 0 ) ).x;

			return channelIndex * tilePlaneSize + subIndex.y * m_tileBatchSize.x + subIndex.x;
		}

		std::unique_ptr<pcl::XISFReader> m_reader;
		pcl::ImageInfo m_info;
		ConstStringVectorDataPtr m_channelNamesData;
		std::map<std::string, ChannelMapEntry> m_channelMap;
		Imath::V2i m_tileBatchSize;
		tbb::mutex m_mutex;
};



typedef std::shared_ptr<File> FilePtr;

// For success, file should be set, and error left null
// For failure, file should be left null, and error should be set
struct CacheEntry
{
	FilePtr file;
	std::shared_ptr<std::string> error;
};


CacheEntry fileCacheGetter( const std::string &fileName, size_t &cost )
{
	cost = 1;

	CacheEntry result;

	std::unique_ptr<pcl::XISFReader> reader( new pcl::XISFReader );
	reader->SetLogHandler( new LogHandler );
	reader->Open( pcl::String( fileName.c_str() ) );
	if( !reader->IsOpen() )
	{
		result.error.reset( new std::string( "XISFReader : Could not open " + fileName ) );
		return result;
	}

	result.file.reset( new File( std::move( reader ) ) );

	return result;
}

typedef IECorePreview::LRUCache<std::string, CacheEntry> FileHandleCache;

FileHandleCache *fileCache()
{
	static FileHandleCache *c = new FileHandleCache( fileCacheGetter, 200 );
	return c;
}

// Returns the file handle container for the given filename in the current
// context. Throws if the file is invalid, and returns null if
// the filename is empty.
FilePtr retrieveFile( std::string &fileName, XISFReader::MissingFrameMode mode, const XISFReader *node, const Context *context )
{
	if( fileName.empty() )
	{
		return nullptr;
	}

	const std::string resolvedFileName = context->substitute( fileName );

	FileHandleCache *cache = fileCache();
	CacheEntry cacheEntry = cache->get( resolvedFileName );
	if( !cacheEntry.file )
	{
		if( mode == XISFReader::Black )
		{
			// we can simply return nullptr and rely on the
			// compute methods to return default plug values.
			return nullptr;
		}
		else if( mode == XISFReader::Hold )
		{
			ConstIntVectorDataPtr frameData = node->availableFramesPlug()->getValue();
			const std::vector<int> &frames = frameData->readable();
			if( frames.size() )
			{
				std::vector<int>::const_iterator fIt = std::lower_bound( frames.begin(), frames.end(), (int)context->getFrame() );

				// decrement to get the previous frame, unless
				// this is the first frame, in which case we
				// hold to the beginning of the sequence
				if( fIt != frames.begin() )
				{
					fIt--;
				}

				// setup a context with the new frame
				ContextPtr holdContext = new Context( *context, Context::Shared );
				holdContext->setFrame( *fIt );

				return retrieveFile( fileName, XISFReader::Error, node, holdContext.get() );
			}

			// if we got here, there was no suitable file sequence
			throw IECore::Exception( *(cacheEntry.error) );
		}
		else
		{
			throw IECore::Exception( *(cacheEntry.error) );
		}
	}

	return cacheEntry.file;
}

} // namespace

//////////////////////////////////////////////////////////////////////////
// XISFReader implementation
//////////////////////////////////////////////////////////////////////////

GAFFER_NODE_DEFINE_TYPE( XISFReader );

size_t XISFReader::g_firstPlugIndex = 0;

XISFReader::XISFReader( const std::string &name )
	:	FlatImageSource( name )
{
	storeIndexOfNextChild( g_firstPlugIndex );
	addChild(
		new StringPlug(
			"fileName", Plug::In, "",
			/* flags */ Plug::Default,
			/* substitutions */ IECore::StringAlgo::AllSubstitutions & ~IECore::StringAlgo::FrameSubstitutions
		)
	);
	addChild( new IntPlug( "refreshCount" ) );
	addChild( new IntPlug( "missingFrameMode", Plug::In, Error, /* min */ Error, /* max */ Hold ) );
	addChild( new IntVectorDataPlug( "availableFrames", Plug::Out, new IntVectorData ) );
	addChild( new ObjectVectorPlug( "__tileBatch", Plug::Out, new ObjectVector ) );

	plugSetSignal().connect( boost::bind( &XISFReader::plugSet, this, ::_1 ) );
}

XISFReader::~XISFReader()
{
}

Gaffer::StringPlug *XISFReader::fileNamePlug()
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

const Gaffer::StringPlug *XISFReader::fileNamePlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

Gaffer::IntPlug *XISFReader::refreshCountPlug()
{
	return getChild<IntPlug>( g_firstPlugIndex + 1 );
}

const Gaffer::IntPlug *XISFReader::refreshCountPlug() const
{
	return getChild<IntPlug>( g_firstPlugIndex + 1 );
}

Gaffer::IntPlug *XISFReader::missingFrameModePlug()
{
	return getChild<IntPlug>( g_firstPlugIndex + 2 );
}

const Gaffer::IntPlug *XISFReader::missingFrameModePlug() const
{
	return getChild<IntPlug>( g_firstPlugIndex + 2 );
}

Gaffer::IntVectorDataPlug *XISFReader::availableFramesPlug()
{
	return getChild<IntVectorDataPlug>( g_firstPlugIndex + 3 );
}

const Gaffer::IntVectorDataPlug *XISFReader::availableFramesPlug() const
{
	return getChild<IntVectorDataPlug>( g_firstPlugIndex + 3 );
}

Gaffer::ObjectVectorPlug *XISFReader::tileBatchPlug()
{
	return getChild<ObjectVectorPlug>( g_firstPlugIndex + 4 );
}

const Gaffer::ObjectVectorPlug *XISFReader::tileBatchPlug() const
{
	return getChild<ObjectVectorPlug>( g_firstPlugIndex + 4 );
}

void XISFReader::setOpenFilesLimit( size_t maxOpenFiles )
{
	fileCache()->setMaxCost( maxOpenFiles );
}

size_t XISFReader::getOpenFilesLimit()
{
	return fileCache()->getMaxCost();
}

void XISFReader::affects( const Gaffer::Plug *input, AffectedPlugsContainer &outputs ) const
{
	FlatImageSource::affects( input, outputs );

	if( input == fileNamePlug() || input == refreshCountPlug() )
	{
		outputs.push_back( availableFramesPlug() );
	}

	if( input == fileNamePlug() || input == refreshCountPlug() || input == missingFrameModePlug() )
	{
		outputs.push_back( tileBatchPlug() );
	}

	if( input == fileNamePlug() || input == refreshCountPlug() || input == missingFrameModePlug() )
	{
		for( ValuePlugIterator it( outPlug() ); !it.done(); ++it )
		{
			outputs.push_back( it->get() );
		}
	}
}

void XISFReader::hash( const ValuePlug *output, const Context *context, IECore::MurmurHash &h ) const
{
	FlatImageSource::hash( output, context, h );

	if( output == availableFramesPlug() )
	{
		fileNamePlug()->hash( h );
		refreshCountPlug()->hash( h );
	}
	else if( output == tileBatchPlug() )
	{
		h.append( context->get<V3i>( g_tileBatchIndexContextName ) );

		Gaffer::Context::EditableScope c( context );
		c.remove( g_tileBatchIndexContextName );

		hashFileName( c.context(), h );
		refreshCountPlug()->hash( h );
		missingFrameModePlug()->hash( h );
	}
}

void XISFReader::compute( ValuePlug *output, const Context *context ) const
{
	if( output == availableFramesPlug() )
	{
		FileSequencePtr fileSequence = nullptr;
		IECore::ls( fileNamePlug()->getValue(), fileSequence, /* minSequenceSize */ 1 );

		if( fileSequence )
		{
			IntVectorDataPtr resultData = new IntVectorData;
			std::vector<FrameList::Frame> frames;
			fileSequence->getFrameList()->asList( frames );
			std::vector<int> &result = resultData->writable();
			result.resize( frames.size() );
			std::copy( frames.begin(), frames.end(), result.begin() );
			static_cast<IntVectorDataPlug *>( output )->setValue( resultData );
		}
		else
		{
			static_cast<IntVectorDataPlug *>( output )->setToDefault();
		}
	}
	else if( output == tileBatchPlug() )
	{
		V3i tileBatchIndex = context->get<V3i>( g_tileBatchIndexContextName );

		Gaffer::Context::EditableScope c( context );
		c.remove( g_tileBatchIndexContextName );

		std::string fileName = fileNamePlug()->getValue();
		FilePtr file = retrieveFile( fileName, (MissingFrameMode)missingFrameModePlug()->getValue(), this, c.context() );

		if( !file )
		{
			throw IECore::Exception( "XISFReader - trying to evaluate tileBatchPlug() with invalid file, this should never happen." );
		}

		static_cast<ObjectVectorPlug *>( output )->setValue(
			file->readTileBatch( tileBatchIndex )
		);
	}
	else
	{
		FlatImageSource::compute( output, context );
	}
}

Gaffer::ValuePlug::CachePolicy XISFReader::computeCachePolicy( const Gaffer::ValuePlug *output ) const
{
	if( output == tileBatchPlug() )
	{
		// Request blocking compute for tile batches, to avoid concurrent threads loading
		// the same batch redundantly.
		return ValuePlug::CachePolicy::Standard;
	}
	else if( output == outPlug()->channelDataPlug() )
	{
		// Disable caching on channelDataPlug, since it is just a redirect to the correct tile of
		// the private tileBatchPlug, which is already being cached.
		return ValuePlug::CachePolicy::Uncached;
	}
	return FlatImageSource::computeCachePolicy( output );
}

void XISFReader::hashFileName( const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	// since fileName excludes frame substitutions
	// but we internally vary the result output by
	// frame, we need to explicitly hash the frame
	// when the value contains FrameSubstitutions.
	const std::string fileName = fileNamePlug()->getValue();
	h.append( fileName );
	if( IECore::StringAlgo::substitutions( fileName ) & IECore::StringAlgo::FrameSubstitutions )
	{
		h.append( context->getFrame() );
	}
}

void XISFReader::hashFormat( const GafferImage::ImagePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	FlatImageSource::hashFormat( output, context, h );
	hashFileName( context, h );
	refreshCountPlug()->hash( h );
	missingFrameModePlug()->hash( h );
	GafferImage::Format format = FormatPlug::getDefaultFormat( context );
	h.append( format.getDisplayWindow() );
	h.append( format.getPixelAspect() );
}

GafferImage::Format XISFReader::computeFormat( const Gaffer::Context *context, const ImagePlug *parent ) const
{
	std::string fileName = fileNamePlug()->getValue();
	// when we're in MissingFrameMode::Black we still want to
	// match the format of the Hold frame.
	MissingFrameMode mode = (MissingFrameMode)missingFrameModePlug()->getValue();
	mode = ( mode == Black ) ? Hold : mode;
	FilePtr file = retrieveFile( fileName, mode, this, context );
	if( !file )
	{
		return FormatPlug::getDefaultFormat( context );
	}

	const pcl::ImageInfo &spec = file->info();
	return GafferImage::Format(
		Imath::Box2i(
			Imath::V2i( 0 ),
			Imath::V2i( spec.width, spec.height )
		),
		1.0f
	);
}

void XISFReader::hashDataWindow( const GafferImage::ImagePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	FlatImageSource::hashDataWindow( output, context, h );
	hashFileName( context, h );
	refreshCountPlug()->hash( h );
	missingFrameModePlug()->hash( h );
}

Imath::Box2i XISFReader::computeDataWindow( const Gaffer::Context *context, const ImagePlug *parent ) const
{
	std::string fileName = fileNamePlug()->getValue();
	FilePtr file = retrieveFile( fileName, (MissingFrameMode)missingFrameModePlug()->getValue(), this, context );
	if( !file )
	{
		return parent->dataWindowPlug()->defaultValue();
	}

	const pcl::ImageInfo &spec = file->info();
	Imath::Box2i dataWindow( Imath::V2i( 0 ), Imath::V2i( spec.width, spec.height ) );
	return dataWindow;
}

void XISFReader::hashMetadata( const GafferImage::ImagePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	FlatImageSource::hashMetadata( output, context, h );
	hashFileName( context, h );
	refreshCountPlug()->hash( h );
	missingFrameModePlug()->hash( h );
}

IECore::ConstCompoundDataPtr XISFReader::computeMetadata( const Gaffer::Context *context, const ImagePlug *parent ) const
{
	CompoundDataPtr result = new CompoundData;
	return result;
}

void XISFReader::hashChannelNames( const GafferImage::ImagePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	FlatImageSource::hashChannelNames( output, context, h );
	hashFileName( context, h );
	refreshCountPlug()->hash( h );
	missingFrameModePlug()->hash( h );
}

IECore::ConstStringVectorDataPtr XISFReader::computeChannelNames( const Gaffer::Context *context, const ImagePlug *parent ) const
{
	std::string fileName = fileNamePlug()->getValue();
	FilePtr file = retrieveFile( fileName, (MissingFrameMode)missingFrameModePlug()->getValue(), this, context );
	if( !file )
	{
		return parent->channelNamesPlug()->defaultValue();
	}
	return file->channelNamesData();
}

void XISFReader::hashChannelData( const GafferImage::ImagePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	FlatImageSource::hashChannelData( output, context, h );
	h.append( context->get<V2i>( ImagePlug::tileOriginContextName ) );
	h.append( context->get<std::string>( ImagePlug::channelNameContextName ) );

	{
		ImagePlug::GlobalScope c( context );
		hashFileName( context, h );
		refreshCountPlug()->hash( h );
		missingFrameModePlug()->hash( h );
	}
}

IECore::ConstFloatVectorDataPtr XISFReader::computeChannelData( const std::string &channelName, const Imath::V2i &tileOrigin, const Gaffer::Context *context, const ImagePlug *parent ) const
{
	ImagePlug::GlobalScope c( context );
	std::string fileName = fileNamePlug()->getValue();
	FilePtr file = retrieveFile( fileName, (MissingFrameMode)missingFrameModePlug()->getValue(), this, context );

	if( !file )
	{
		return parent->channelDataPlug()->defaultValue();
	}

	Imath::V2i flippedTileOrigin( tileOrigin );
	flippedTileOrigin.y = file->info().height - tileOrigin.y - ImagePlug::tileSize();

	Box2i dataWindow = outPlug()->dataWindowPlug()->getValue();
	const Box2i tileBound( flippedTileOrigin, flippedTileOrigin + V2i( ImagePlug::tileSize() ) );
	if( !BufferAlgo::intersects( dataWindow, tileBound ) )
	{
		throw IECore::Exception( boost::str(
			boost::format( "XISFReader : Invalid tile (%i,%i) -> (%i,%i) not within data window (%i,%i) -> (%i,%i)." ) %
			tileBound.min.x % tileBound.min.y % tileBound.max.x % tileBound.max.y %
			dataWindow.min.x % dataWindow.min.y % dataWindow.max.x % dataWindow.max.y
		) );
	}

	V3i tileBatchIndex;
	int subIndex;
	file->findTile( channelName, flippedTileOrigin, tileBatchIndex, subIndex );

	c.set( g_tileBatchIndexContextName, tileBatchIndex );

	ConstObjectVectorPtr tileBatch = tileBatchPlug()->getValue();
	ConstObjectPtr curTileChannel = tileBatch->members()[ subIndex ];
	return IECore::runTimeCast< const FloatVectorData >( curTileChannel );
}

void XISFReader::plugSet( Gaffer::Plug *plug )
{
	// this clears the cache every time the refresh count is updated, so you don't get entries
	// from old files hanging around.
	if( plug == refreshCountPlug() )
	{
		fileCache()->clear();
	}
}
