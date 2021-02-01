//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2017, Image Engine Design Inc. All rights reserved.
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

#include "GafferAstro/CollectChannels.h"

#include "GafferImage/BufferAlgo.h"
#include "GafferImage/ImageAlgo.h"
#include "GafferImage/ImageProcessor.h"

#include "Gaffer/ArrayPlug.h"
#include "Gaffer/Context.h"

using namespace std;
using namespace Imath;
using namespace IECore;
using namespace Gaffer;
using namespace GafferImage;
using namespace GafferAstro;

//////////////////////////////////////////////////////////////////////////
// Internal utilities
//////////////////////////////////////////////////////////////////////////

namespace
{

/// \todo Maybe move this to BufferAlgo.h? It could probably be reused
/// in Offset::computeChannelData() at least.
void copyRegion( const float *fromBuffer, const Box2i &fromWindow, const Box2i &fromRegion, float *toBuffer, const Box2i &toWindow, const V2i &toOrigin )
{
	const int width = fromRegion.max.x - fromRegion.min.x;

	V2i fromP = fromRegion.min;
	V2i toP = toOrigin;
	for( int maxY = fromRegion.max.y; fromP.y < maxY; ++fromP.y, ++toP.y )
	{
		memcpy(
			toBuffer + BufferAlgo::index( toP, toWindow ),
			fromBuffer + BufferAlgo::index( fromP, fromWindow ),
			sizeof( float ) * width
		);
	}
}

string sourceChannel( const string &requestedChannel, const vector<string> &channels )
{
	if( requestedChannel.empty() )
	{
		return channels.size() > 0 ? channels[0] : "";
	}

	if( std::find( channels.cbegin(), channels.cend(), requestedChannel ) != channels.cend() )
	{
		return requestedChannel;
	}

	return "";
}

} // namespace

//////////////////////////////////////////////////////////////////////////
// CollectChannels
//////////////////////////////////////////////////////////////////////////

GAFFER_NODE_DEFINE_TYPE( CollectChannels );

size_t CollectChannels::g_firstPlugIndex = 0;

CollectChannels::CollectChannels( const std::string &name )
	:	ImageProcessor( name )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	addChild( new StringVectorDataPlug( "channels", Plug::In, new StringVectorData ) );
	addChild( new StringPlug( "channelVariable", Plug::In, "collect:channelName" ) );
	addChild( new StringPlug( "sourceChannel", Plug::In, "" ) );
}

CollectChannels::~CollectChannels()
{
}

Gaffer::StringVectorDataPlug *CollectChannels::channelsPlug()
{
	return getChild<Gaffer::StringVectorDataPlug>( g_firstPlugIndex + 0 );
}

const Gaffer::StringVectorDataPlug *CollectChannels::channelsPlug() const
{
	return getChild<Gaffer::StringVectorDataPlug>( g_firstPlugIndex + 0 );
}

Gaffer::StringPlug *CollectChannels::channelVariablePlug()
{
	return getChild<Gaffer::StringPlug>( g_firstPlugIndex + 1 );
}

const Gaffer::StringPlug *CollectChannels::channelVariablePlug() const
{
	return getChild<Gaffer::StringPlug>( g_firstPlugIndex + 1 );
}

Gaffer::StringPlug *CollectChannels::sourceChannelPlug()
{
	return getChild<Gaffer::StringPlug>( g_firstPlugIndex + 2 );
}

const Gaffer::StringPlug *CollectChannels::sourceChannelPlug() const
{
	return getChild<Gaffer::StringPlug>( g_firstPlugIndex + 2 );
}


void CollectChannels::affects( const Gaffer::Plug *input, AffectedPlugsContainer &outputs ) const
{
	ImageProcessor::affects( input, outputs );

	const ImagePlug *imagePlug = input->parent<ImagePlug>();
	if( imagePlug && imagePlug == inPlug() )
	{
		if( input == imagePlug->dataWindowPlug() )
		{
			outputs.push_back( outPlug()->dataWindowPlug() );
		}

		if( input == imagePlug->channelNamesPlug() )
		{
			outputs.push_back( outPlug()->channelNamesPlug() );
		}

		if( input == imagePlug->channelDataPlug() )
		{
			outputs.push_back( outPlug()->channelDataPlug() );
		}

		if( input == imagePlug->formatPlug() )
		{
			outputs.push_back( outPlug()->formatPlug() );
		}

		if( input == imagePlug->metadataPlug() )
		{
			outputs.push_back( outPlug()->metadataPlug() );
		}

		if( input == imagePlug->sampleOffsetsPlug() )
		{
			outputs.push_back( outPlug()->sampleOffsetsPlug() );
		}

		if( input == imagePlug->deepPlug() )
		{
			outputs.push_back( outPlug()->deepPlug() );
			outputs.push_back( outPlug()->dataWindowPlug() );
			outputs.push_back( outPlug()->channelDataPlug() );
		}
	}
	else if( input == channelsPlug() || input == channelVariablePlug() || input == sourceChannelPlug() )
	{
		outputs.push_back( outPlug()->channelNamesPlug() );
		outputs.push_back( outPlug()->channelDataPlug() );
		outputs.push_back( outPlug()->dataWindowPlug() );
		outputs.push_back( outPlug()->formatPlug() );
		outputs.push_back( outPlug()->metadataPlug() );
		outputs.push_back( outPlug()->sampleOffsetsPlug() );
		outputs.push_back( outPlug()->deepPlug() );
	}

}

void CollectChannels::hashFormat( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	ConstStringVectorDataPtr channelsData = channelsPlug()->getValue();

	if( channelsData->readable().size() )
	{
		Context::EditableScope editScope( context );
		editScope.set( channelVariablePlug()->getValue(), channelsData->readable()[0] );
		h = inPlug()->formatPlug()->hash();
	}
	else
	{
		ImageProcessor::hashFormat( parent, context, h );
	}
}

GafferImage::Format CollectChannels::computeFormat( const Gaffer::Context *context, const ImagePlug *parent ) const
{
	ConstStringVectorDataPtr channelsData = channelsPlug()->getValue();

	if( channelsData->readable().size() )
	{
		Context::EditableScope editScope( context );
		editScope.set( channelVariablePlug()->getValue(), channelsData->readable()[0] );
		return inPlug()->formatPlug()->getValue();
	}
	else
	{
		return outPlug()->formatPlug()->defaultValue();
	}
}

void CollectChannels::hashDeep( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	ImageProcessor::hashDeep( parent, context, h );

	const std::string channelVariable = channelVariablePlug()->getValue();

	ConstStringVectorDataPtr channelsData = channelsPlug()->getValue();

	Context::EditableScope editScope( context );
	for( const auto &i : channelsData->readable() )
	{
		editScope.set( channelVariable, i );
		sourceChannelPlug()->hash( h );
		inPlug()->deepPlug()->hash( h );
	}
}

bool CollectChannels::computeDeep( const Gaffer::Context *context, const ImagePlug *parent ) const
{
	int outDeep = -1;
	const std::string channelVariable = channelVariablePlug()->getValue();

	ConstStringVectorDataPtr channelsData = channelsPlug()->getValue();

	Context::EditableScope editScope( context );
	for( const auto &i : channelsData->readable() )
	{
		editScope.set( channelVariable, i );
		bool curDeep = inPlug()->deepPlug()->getValue();
		if( outDeep == -1 )
		{
			outDeep = curDeep;
		}
		else
		{
			if( outDeep != curDeep )
			{
				throw IECore::Exception( "Input to CollectChannels must be consistent, but it is sometimes deep." );
			}
		}
	}

	return outDeep == 1;
}

void CollectChannels::hashSampleOffsets( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	ImageProcessor::hashSampleOffsets( parent, context, h );
	ConstStringVectorDataPtr channelsData;
	string channelVariable;
	{
		ImagePlug::GlobalScope c( context );
		channelsData = channelsPlug()->getValue();
		channelVariable = channelVariablePlug()->getValue();
	}

	Context::EditableScope editScope( context );
	for( const auto &i : channelsData->readable() )
	{
		editScope.set( channelVariable, i );
		sourceChannelPlug()->hash( h );
		inPlug()->sampleOffsetsPlug()->hash( h );
	}
}

IECore::ConstIntVectorDataPtr CollectChannels::computeSampleOffsets( const Imath::V2i &tileOrigin, const Gaffer::Context *context, const ImagePlug *parent ) const
{
	ConstStringVectorDataPtr channelsData;
	string channelVariable;
	{
		ImagePlug::GlobalScope c( context );
		channelsData = channelsPlug()->getValue();
		channelVariable = channelVariablePlug()->getValue();
	}

	IECore::ConstIntVectorDataPtr outSampleOffsetsData;
	Context::EditableScope editScope( context );
	for( const auto &i : channelsData->readable() )
	{
		editScope.set( channelVariable, i );
		IECore::ConstIntVectorDataPtr curSampleOffsetsData = inPlug()->sampleOffsetsPlug()->getValue();
		if( !outSampleOffsetsData )
		{
			outSampleOffsetsData = curSampleOffsetsData;
		}
		else
		{
			ImageAlgo::throwIfSampleOffsetsMismatch( outSampleOffsetsData.get(), curSampleOffsetsData.get(), tileOrigin,
				"SampleOffsets on input to CollectChannels must match."
			);
		}
	}
	return outSampleOffsetsData;
}

void CollectChannels::hashMetadata( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	ConstStringVectorDataPtr channelsData = channelsPlug()->getValue();

	if( channelsData->readable().size() )
	{
		Context::EditableScope editScope( context );
		editScope.set( channelVariablePlug()->getValue(), channelsData->readable()[0] );
		h = inPlug()->metadataPlug()->hash();
	}
	else
	{
		ImageProcessor::hashMetadata( parent, context, h );
	}
}

IECore::ConstCompoundDataPtr CollectChannels::computeMetadata( const Gaffer::Context *context, const ImagePlug *parent ) const
{
	ConstStringVectorDataPtr channelsData = channelsPlug()->getValue();

	if( channelsData->readable().size() )
	{
		Context::EditableScope editScope( context );
		editScope.set( channelVariablePlug()->getValue(), channelsData->readable()[0] );
		return inPlug()->metadataPlug()->getValue();
	}
	else
	{
		return outPlug()->metadataPlug()->defaultValue();
	}
}



void CollectChannels::hashDataWindow( const GafferImage::ImagePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	ImageProcessor::hashDataWindow( output, context, h );

	const std::string channelVariable = channelVariablePlug()->getValue();

	ConstStringVectorDataPtr channelsData = channelsPlug()->getValue();
	const vector<string> &channels = channelsData->readable();

	if( channels.size() == 0 )
	{
		return;
	}

	Context::EditableScope editScope( context );
	editScope.set( channelVariable, channels[0] );
	inPlug()->deepPlug()->hash( h );
	for( unsigned int i = 0; i < channels.size(); i++ )
	{
		editScope.set( channelVariable, channels[i] );
		sourceChannelPlug()->hash( h );
		inPlug()->dataWindowPlug()->hash( h );
	}
}

Imath::Box2i CollectChannels::computeDataWindow( const Gaffer::Context *context, const ImagePlug *parent ) const
{
	Imath::Box2i dataWindow;

	const std::string channelVariable = channelVariablePlug()->getValue();

	ConstStringVectorDataPtr channelsData = channelsPlug()->getValue();
	const vector<string> &channels = channelsData->readable();

	if( channels.size() == 0 )
	{
		return dataWindow;
	}

	Context::EditableScope editScope( context );
	editScope.set( channelVariable, channels[0] );
	bool deep = inPlug()->deepPlug()->getValue();
	for( unsigned int i = 0; i < channels.size(); i++ )
	{
		editScope.set( channelVariable, channels[i] );
		Box2i curDataWindow = inPlug()->dataWindowPlug()->getValue();
		if( i == 0 || !deep )
		{
			dataWindow.extendBy( curDataWindow );
		}
		else
		{
			if( curDataWindow != dataWindow )
			{
				throw IECore::Exception( boost::str( boost::format(
						"DataWindows on deep input to CollectChannels must match. "
						"Received both %i,%i -> %i,%i and %i,%i -> %i,%i"
					) % dataWindow.min.x % dataWindow.min.y % dataWindow.max.x % dataWindow.max.y %
						curDataWindow.min.x % curDataWindow.min.y % curDataWindow.max.x % curDataWindow.max.y
				) );
			}
		}
	}

	return dataWindow;
}

void CollectChannels::hashChannelNames( const GafferImage::ImagePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	ImageProcessor::hashChannelNames( output, context, h );

	const std::string channelVariable = channelVariablePlug()->getValue();

	ConstStringVectorDataPtr channelsData = channelsPlug()->getValue();
	const vector<string> &channels = channelsData->readable();

	h.append( &(channels[0]), channels.size() );

	Context::EditableScope editScope( context );
	for( unsigned int i = 0; i < channels.size(); i++ )
	{
		editScope.set( channelVariable, channels[i] );
		sourceChannelPlug()->hash( h );
		inPlug()->channelNamesPlug()->hash( h );
	}
}

IECore::ConstStringVectorDataPtr CollectChannels::computeChannelNames( const Gaffer::Context *context, const ImagePlug *parent ) const
{
	StringVectorDataPtr channelNamesData = new StringVectorData();
	std::vector<string> &outChannelNames = channelNamesData->writable();

	const std::string channelVariable = channelVariablePlug()->getValue();

	ConstStringVectorDataPtr channelsData = channelsPlug()->getValue();
	const vector<string> &channels = channelsData->readable();

	Context::EditableScope editScope( context );
	for( unsigned int i = 0; i < channels.size(); i++ )
	{
		editScope.set( channelVariable, channels[i] );

		ConstStringVectorDataPtr srcChannelsData = inPlug()->channelNamesPlug()->getValue();
		const std::vector<string> &srcChannels = srcChannelsData->readable();

		if( srcChannels.size() == 0 )
		{
			throw IECore::Exception( boost::str(
				boost::format( "No source channels for output channel '%s'.") % channels[i]
			) );
		}

		const string srcChannel = sourceChannel( sourceChannelPlug()->getValue(), srcChannels );
		if( srcChannel.empty() )
		{
			throw IECore::Exception( boost::str(
				boost::format( "No channel '%s' in input for output channel '%s'.") % sourceChannelPlug()->getValue() % channels[i]
			) );
		}
		outChannelNames.push_back( channels[i] );
	}

	return channelNamesData;
}

void CollectChannels::hashChannelData( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	const std::string &channelName = context->get<string>( ImagePlug::channelNameContextName );

	string channelVariable, srcChannel;
	{
		ImagePlug::GlobalScope c( context );

		ConstStringVectorDataPtr srcChannelsData = inPlug()->channelNamesPlug()->getValue();

		channelVariable = channelVariablePlug()->getValue();
		c.set( channelVariable, channelName );

		sourceChannelPlug()->hash( h );
		srcChannel = sourceChannel( sourceChannelPlug()->getValue(), srcChannelsData->readable() );
	}

	Context::EditableScope editScope( context );
	editScope.set( channelVariable, channelName );
	editScope.set( ImagePlug::channelNameContextName, srcChannel );

	const V2i tileOrigin = context->get<V2i>( ImagePlug::tileOriginContextName );
	const Box2i tileBound( tileOrigin, tileOrigin + V2i( ImagePlug::tileSize() ) );

	IECore::MurmurHash inputChannelDataHash = inPlug()->channelDataPlug()->hash();

	// We've now gathered all data that depends on the tile/channel, so we can use the same editScope
	// for a global context
	editScope.remove( ImagePlug::channelNameContextName );
	editScope.remove( ImagePlug::tileOriginContextName );

	bool deep = inPlug()->deepPlug()->getValue();
	Box2i inputDataWindow = inPlug()->dataWindowPlug()->getValue();

	const Box2i validBound = BufferAlgo::intersection( tileBound, inputDataWindow );
	if( validBound == tileBound || deep )
	{
		h = inputChannelDataHash;
	}
	else
	{
		ImageProcessor::hashChannelData( parent, context, h );
		if( !BufferAlgo::empty( validBound ) )
		{
			h.append( inputChannelDataHash );
			h.append( BufferAlgo::intersection( inputDataWindow, tileBound ) );
		}
	}
}

IECore::ConstFloatVectorDataPtr CollectChannels::computeChannelData( const std::string &channelName, const Imath::V2i &tileOrigin, const Gaffer::Context *context, const ImagePlug *parent ) const
{
	ConstStringVectorDataPtr channelsData;
	string channelVariable, srcChannel;
	{
		ImagePlug::GlobalScope c( context );

		ConstStringVectorDataPtr srcChannelsData = inPlug()->channelNamesPlug()->getValue();

		channelVariable = channelVariablePlug()->getValue();
		c.set( channelVariable, channelName );

		srcChannel = sourceChannel( sourceChannelPlug()->getValue(), srcChannelsData->readable() );
	}

	Context::EditableScope editScope( context );
	editScope.set( channelVariable, channelName );

	// First use this EditableScope as a global scope
	editScope.remove( ImagePlug::channelNameContextName );
	editScope.remove( ImagePlug::tileOriginContextName );

	bool deep = inPlug()->deepPlug()->getValue();
	Box2i inputDataWindow = inPlug()->dataWindowPlug()->getValue();

	const Box2i tileBound( tileOrigin, tileOrigin + V2i( ImagePlug::tileSize() ) );
	const Box2i validBound = BufferAlgo::intersection( tileBound, inputDataWindow );
	if( BufferAlgo::empty( validBound ) )
	{
		return ImagePlug::blackTile();
	}

	// Then set up the scope to evaluate the input channel data
	editScope.set( ImagePlug::channelNameContextName, srcChannel );
	editScope.set( ImagePlug::tileOriginContextName, tileOrigin );

	ConstFloatVectorDataPtr inputData = inPlug()->channelDataPlug()->getValue();

	if( validBound == tileBound || deep )
	{
		// If we're taking the whole tile, then just return the input tile
		// If we're a deep image, then we're just passing through the sampleOffsets,
		// so we also need to pass through the whole data ( and in the deep case we
		// require all inputs to have matching data windows, so this is fine )
		return inputData;
	}
	else
	{
		FloatVectorDataPtr resultData = new FloatVectorData;
		vector<float> &result = resultData->writable();
		result.resize( ImagePlug::tileSize() * ImagePlug::tileSize(), 0.0f );
		copyRegion(
			&inputData->readable().front(),
			tileBound,
			validBound,
			&result.front(),
			tileBound,
			validBound.min
		);
		return resultData;
	}
}

