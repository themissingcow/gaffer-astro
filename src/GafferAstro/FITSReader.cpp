//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2020, Tom Cowland. All rights reserved.
//
//	Redistribution and use in source and binary forms, with or without
//	modification, are permitted provided that the following conditions are
//	met:
//
//		* Redistributions of source code must retain the above
//		  copyright notice, this list of conditions and the following
//		  disclaimer.
//
//		* Redistributions in binary form must reproduce the above
//		  copyright notice, this list of conditions and the following
//		  disclaimer in the documentation and/or other materials provided with
//		  the distribution.
//
//		* Neither the name of Tom Cowland or the names of
//		  any other contributors to this software may be used to endorse or
//		  promote products derived from this software without specific prior
//		  written permission.
//
//	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
//	IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
//	THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
//	PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
//	CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
//	EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
//	PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
//	PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
//	LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
//	NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
//	SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
//
//////////////////////////////////////////////////////////////////////////

#include "GafferAstro/FITSReader.h"

#include "GafferImage/FormatPlug.h"

#include "IECore/CompoundData.h"

#include "OpenEXR/ImathBox.h"

#include <CCfits/CCfits>

#include <tbb/mutex.h>

using namespace CCfits;
using namespace IECore;
using namespace Gaffer;
using namespace GafferImage;
using namespace GafferAstro;

//////////////////////////////////////////////////////////////////////////
// File implementation
//////////////////////////////////////////////////////////////////////////

namespace {

static tbb::mutex g_readMutex;


class File
{
	public :

		File( const std::string &fileName )
			: m_fileName( fileName )
		{
			try
			{
				m_fits.reset( new FITS( fileName, CCfits::Read, false ) );
			}
			catch( CCfits::FitsException &e )
			{
				throw IECore::Exception( e.message() );
				m_fits = nullptr;
			}
		}

		CompoundDataPtr metadata()
		{
			CompoundDataPtr result = new CompoundData();
			if( m_fits )
			{
			}

			return result;
		}

		Imath::Box2i dataWindow()
		{
			if( !m_fits )
			{
				return Imath::Box2i( Imath::V2i( 0 ), Imath::V2i( 0 ) );
			}

			tbb::mutex::scoped_lock l( g_readMutex );

			CCfits::PHDU& image = m_fits->pHDU();

			if( image.axes() != 2 )
			{
				throw IECore::Exception( "Invalid number of image axes" );
			}

			return Imath::Box2i(
				Imath::V2i( 0 ),
				Imath::V2i( image.axis( 0 ), image.axis( 1 ) )
			);
		}

		IECore::ConstStringVectorDataPtr channels()
		{
			IECore::StringVectorDataPtr dataPtr = new IECore::StringVectorData();

			if( m_fits )
			{
				dataPtr->writable().push_back( "Y" );
			}

			return dataPtr;
		}

		IECore::ConstFloatVectorDataPtr	tile( const Imath::Box2i &tile )
		{
			assert( m_fits );

			IECore::FloatVectorDataPtr dataPtr = new IECore::FloatVectorData();
			std::vector<float> &data = dataPtr->writable();

			data.resize( tile.size().x * tile.size().y );

			std::valarray<float> imageData;
			static const std::vector<long> stride = { 1, 1 };

			{
				tbb::mutex::scoped_lock l( g_readMutex );

				CCfits::PHDU& image = m_fits->pHDU();
				int maxX = image.axis( 0 );
				int maxY = image.axis( 1 );
				std::vector<long> bl = { tile.min.x + 1, tile.min.y + 1 };
				std::vector<long> tr = { std::min( maxX, tile.max.x ), std::min( maxY, tile.max.y ) };
				image.read( imageData, bl, tr, stride );
			}

			std::copy( begin(imageData), end(imageData), data.begin() );

			return dataPtr;
		}

	private :

		std::unique_ptr<FITS> m_fits;
		std::string m_fileName;
};

typedef std::shared_ptr<File> FilePtr;


static tbb::mutex g_cacheMutex;
static std::map<std::string, FilePtr> g_fileMap;

FilePtr retrieveFile( const std::string &fileName, const Context *context )
{
	if( fileName.empty() )
	{
		return nullptr;
	}


	const std::string resolvedFileName = context->substitute( fileName );

	tbb::mutex::scoped_lock l( g_cacheMutex );
	if( g_fileMap.find( resolvedFileName ) == g_fileMap.end() )
	{
		g_fileMap[ resolvedFileName ].reset( new File( resolvedFileName ) );
	}

	return g_fileMap[ resolvedFileName ];
}

} // namespace

//////////////////////////////////////////////////////////////////////////
// FITSReader Implementation
//////////////////////////////////////////////////////////////////////////

GAFFER_GRAPHCOMPONENT_DEFINE_TYPE( FITSReader );

FITSReader::FITSReader( const std::string& name )
	:	GafferImage::FlatImageSource( name )
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
}

FITSReader::~FITSReader()
{
}


size_t FITSReader::g_firstPlugIndex = 0;

Gaffer::StringPlug *FITSReader::fileNamePlug()
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

const Gaffer::StringPlug *FITSReader::fileNamePlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

Gaffer::IntPlug *FITSReader::refreshCountPlug()
{
	return getChild<IntPlug>( g_firstPlugIndex + 1 );
}

const Gaffer::IntPlug *FITSReader::refreshCountPlug() const
{
	return getChild<IntPlug>( g_firstPlugIndex + 1 );
}


void FITSReader::affects( const Gaffer::Plug *input, AffectedPlugsContainer &outputs ) const
{
	FlatImageSource::affects( input, outputs );

	if( input == fileNamePlug() || input == refreshCountPlug() )
	{
		for( ValuePlugIterator it( outPlug() ); !it.done(); ++it )
		{
			outputs.push_back( it->get() );
		}
	}
}


void FITSReader::hashFormat( const GafferImage::ImagePlug *parent, const Context *context, IECore::MurmurHash &h ) const
{
	FlatImageSource::hashFormat( parent, context, h );
	hashFileName( context, h );
	refreshCountPlug()->hash( h );
	GafferImage::Format format = FormatPlug::getDefaultFormat( context );
	h.append( format.getDisplayWindow() );
	h.append( format.getPixelAspect() );
}

GafferImage::Format FITSReader::computeFormat( const Context *context, const ImagePlug *parent ) const
{
	const std::string fileName = fileNamePlug()->getValue();
	FilePtr file = retrieveFile( fileName, context );
	if( !file )
	{
		return GafferImage::FormatPlug::getDefaultFormat( context );
	}

	return GafferImage::Format( file->dataWindow(), 1.0f );
}


void FITSReader::hashDataWindow( const GafferImage::ImagePlug *parent, const Context *context, IECore::MurmurHash &h ) const
{
	FlatImageSource::hashDataWindow( parent, context, h );
	hashFileName( context, h );
	refreshCountPlug()->hash( h );
}

Imath::Box2i FITSReader::computeDataWindow( const Context *context, const ImagePlug *parent ) const
{
	const std::string fileName = fileNamePlug()->getValue();
	FilePtr file = retrieveFile( fileName, context );
	if( !file )
	{
		return Imath::Box2i( Imath::V2i( 0 ), Imath::V2i( 0 ) );
	}
	return file->dataWindow();
}

void FITSReader::hashMetadata( const GafferImage::ImagePlug *parent, const Context *context, IECore::MurmurHash &h ) const
{
	FlatImageSource::hashMetadata( parent, context, h );
	hashFileName( context, h );
	refreshCountPlug()->hash( h );
}

IECore::ConstCompoundDataPtr FITSReader::computeMetadata( const Context *context, const ImagePlug *parent ) const
{
	const std::string fileName = fileNamePlug()->getValue();
	FilePtr file = retrieveFile( fileName, context );
	if( !file )
	{
		return parent->metadataPlug()->defaultValue();
	}
	return file->metadata();
}


void FITSReader::hashChannelNames( const GafferImage::ImagePlug *parent, const Context *context, IECore::MurmurHash &h ) const
{
	FlatImageSource::hashChannelNames( parent, context, h );
	hashFileName( context, h );
	refreshCountPlug()->hash( h );
}

IECore::ConstStringVectorDataPtr FITSReader::computeChannelNames( const Context *context, const ImagePlug *parent ) const
{
	std::string fileName = fileNamePlug()->getValue();
	FilePtr file = retrieveFile( fileName, context );

	if( !file )
	{
		return new IECore::StringVectorData();
	}

	return file->channels();
}


void FITSReader::hashChannelData( const GafferImage::ImagePlug *parent, const Context *context, IECore::MurmurHash &h ) const
{
	FlatImageSource::hashChannelData( parent, context, h );

	h.append( context->get<Imath::V2i>( ImagePlug::tileOriginContextName ) );
	h.append( context->get<std::string>( ImagePlug::channelNameContextName ) );

	{
		ImagePlug::GlobalScope c( context );
		hashFileName( context, h );
		refreshCountPlug()->hash( h );
	}
}

IECore::ConstFloatVectorDataPtr FITSReader::computeChannelData( const std::string &channelName, const Imath::V2i &tileOrigin, const Context *context, const ImagePlug *parent ) const
{
	ImagePlug::GlobalScope c( context );
	std::string fileName = fileNamePlug()->getValue();
	FilePtr file = retrieveFile( fileName, context );

	if( !file )
	{
		return parent->channelDataPlug()->defaultValue();
	}

	const Imath::Box2i tileBound( tileOrigin, tileOrigin + Imath::V2i( ImagePlug::tileSize() ) );

	Imath::Box2i dataWindow = outPlug()->dataWindowPlug()->getValue();
	if( !BufferAlgo::intersects( dataWindow, tileBound ) )
	{
		throw IECore::Exception( boost::str(
			boost::format( "FITSReader : Invalid tile (%i,%i) -> (%i,%i) not within data window (%i,%i) -> (%i,%i)." ) %
			tileBound.min.x % tileBound.min.y % tileBound.max.x % tileBound.max.y %
			dataWindow.min.x % dataWindow.min.y % dataWindow.max.x % dataWindow.max.y
		) );
	}

	return file->tile( tileBound );
}


void FITSReader::hashFileName( const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	const std::string fileName = fileNamePlug()->getValue();
	h.append( fileName );
	if( IECore::StringAlgo::substitutions( fileName ) & IECore::StringAlgo::FrameSubstitutions )
	{
		h.append( context->getFrame() );
	}
}

