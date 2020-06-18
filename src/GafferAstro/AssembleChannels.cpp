//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2020,  Tom Cowland. All rights reserved.
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
//      * Neither the name of Tom Cowland nor the names of
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

#include "GafferAstro/AssembleChannels.h"

#include "GafferImage/ImageAlgo.h"

#include "Gaffer/ArrayPlug.h"
#include "Gaffer/NameValuePlug.h"

#include "Gaffer/Context.h"

using namespace IECore;
using namespace Gaffer;
using namespace GafferImage;
using namespace GafferAstro;

namespace
{
	struct AssembleChannelsParametersScope : public Gaffer::Context::EditableScope
	{
		AssembleChannelsParametersScope( const Gaffer::Context *context )
			:   EditableScope( context )
		{
			remove( GafferImage::ImagePlug::tileOriginContextName );
			remove( GafferImage::ImagePlug::channelNameContextName );
		}
	};

}

GAFFER_GRAPHCOMPONENT_DEFINE_TYPE( AssembleChannels );

size_t AssembleChannels::g_firstPlugIndex = 0;

AssembleChannels::AssembleChannels( const std::string &name )
	:	ImageNode( name )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	NameValuePlugPtr firstInput = new NameValuePlug( "", new ImagePlug( "in0"), /* defaultEnabled = */ true, "in0" );
	ArrayPlugPtr in = new ArrayPlug(
		"in",
		Plug::In,
		firstInput,
		2,
		Imath::limits<size_t>::max(),
		Plug::Default,
		/* resizeWhenInputsChange = */ false
	);
	addChild( in );

	addChild( new ObjectPlug( "__channelMap", Gaffer::Plug::Out, new CompoundObject ) );

	// We derive all these from the first input
	auto firstInputImagePlug = firstInput->valuePlug<ImagePlug>();
	outPlug()->formatPlug()->setInput( firstInputImagePlug->formatPlug() );
	outPlug()->dataWindowPlug()->setInput( firstInputImagePlug->dataWindowPlug() );
	outPlug()->metadataPlug()->setInput( firstInputImagePlug->metadataPlug() );
	outPlug()->deepPlug()->setInput( firstInputImagePlug->deepPlug() );
	outPlug()->sampleOffsetsPlug()->setInput( firstInputImagePlug->sampleOffsetsPlug() );
}

AssembleChannels::~AssembleChannels()
{
}

Gaffer::ArrayPlug *AssembleChannels::inPlugs()
{
	return getChild<Gaffer::ArrayPlug>( g_firstPlugIndex );
}

const Gaffer::ArrayPlug *AssembleChannels::inPlugs() const
{
	return getChild<Gaffer::ArrayPlug>( g_firstPlugIndex );
}

Gaffer::ObjectPlug *AssembleChannels::channelMapPlug()
{
	return getChild<Gaffer::ObjectPlug>( g_firstPlugIndex + 1 );
}

const Gaffer::ObjectPlug *AssembleChannels::channelMapPlug() const
{
	return getChild<Gaffer::ObjectPlug>( g_firstPlugIndex + 1 );
}

void AssembleChannels::affects( const Gaffer::Plug *input, AffectedPlugsContainer &outputs ) const
{
	ImageNode::affects( input, outputs );

	if( input == channelMapPlug() )
	{
		outputs.push_back( outPlug()->channelNamesPlug() );
		outputs.push_back( outPlug()->channelDataPlug() );
	}
	else if( affectsChannelMap( input ) )
	{
		outputs.push_back( channelMapPlug() );
	}
}

void AssembleChannels::hash( const Gaffer::ValuePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	ImageNode::hash( output, context, h );

	if( output == channelMapPlug() )
	{
		hashChannelMap( context, h );
	}
}

void AssembleChannels::compute( Gaffer::ValuePlug *output, const Gaffer::Context *context ) const
{
	if( output == channelMapPlug() )
	{
		static_cast<ObjectPlug *>( output )->setValue( computeChannelMap( context ) );
		return;
	}

	ImageNode::compute( output, context );
}

void AssembleChannels::hashChannelNames( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	ImageNode::hashChannelNames( parent, context, h );
	channelMapPlug()->hash( h );
}

IECore::ConstStringVectorDataPtr AssembleChannels::computeChannelNames( const Gaffer::Context *context, const ImagePlug *parent ) const
{
	ImagePlug::GlobalScope s( context );
	return runTimeCast<const CompoundObject>(channelMapPlug()->getValue())->member<const StringVectorData>( "channelNames" );
}

void AssembleChannels::hashChannelData( const GafferImage::ImagePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	ImageNode::hashChannelData( output, context, h );

	IECore::ConstCompoundObjectPtr channelMap;
	{
		ImagePlug::GlobalScope s( context );
		channelMapPlug()->hash( h );
		channelMap = runTimeCast<const CompoundObject>( channelMapPlug()->getValue() );
	}

	const std::string &channel = context->get<std::string>( ImagePlug::channelNameContextName );
	h.append( channel );

	const auto& allNames = channelMap->member<const StringVectorData>( "channelNames" )->readable();
	const auto indexIt = std::find( allNames.begin(), allNames.end(), channel );
	if( indexIt != allNames.end() )
	{
		const size_t index = indexIt - allNames.begin();
		int sourceInputIndex = channelMap->member<const IntVectorData>( "sourceInputs" )->readable()[ index ];
		const std::string &sourceChannel  = channelMap->member<const StringVectorData>( "sourceChannels" )->readable()[ index ];

		const ImagePlug *sourceInput = runTimeCast<const ImagePlug>( inPlugs()->getChild<NameValuePlug>( sourceInputIndex )->valuePlug() );

		ConstStringVectorDataPtr inputChannelNamesData;
		{
			ImagePlug::GlobalScope globalScope( context );
			inputChannelNamesData = sourceInput->channelNamesPlug()->getValue();
			h.append( sourceInput->channelNamesHash() );
		}
		const std::vector<std::string> &channelNames = inputChannelNamesData->readable();

		if( ImageAlgo::channelExists( channelNames, sourceChannel ) )
		{
			ImagePlug::ChannelDataScope channelDataScope( context );
			const Imath::V2i tileOrigin = context->get<Imath::V2i>( ImagePlug::tileOriginContextName );
			channelDataScope.setChannelName( sourceChannel );
			h.append( sourceInput->channelDataHash( sourceChannel, tileOrigin ) );
		}
	}
}

IECore::ConstFloatVectorDataPtr AssembleChannels::computeChannelData( const std::string &channelName, const Imath::V2i &tileOrigin, const Gaffer::Context *context, const ImagePlug *parent ) const
{
	IECore::ConstCompoundObjectPtr channelMap;
	{
		ImagePlug::GlobalScope s( context );
		channelMap = runTimeCast<const CompoundObject>( channelMapPlug()->getValue() );
	}

	const std::string &channel = context->get<std::string>( ImagePlug::channelNameContextName );

	const auto& allNames = channelMap->member<const StringVectorData>( "channelNames" )->readable();
	const auto indexIt = std::find( allNames.begin(), allNames.end(), channel );
	if( indexIt != allNames.end() )
	{
		const size_t index = indexIt - allNames.begin();
		int sourceInputIndex = channelMap->member<const IntVectorData>( "sourceInputs" )->readable()[ index ];
		const std::string &sourceChannel  = channelMap->member<const StringVectorData>( "sourceChannels" )->readable()[ index ];

		const ImagePlug *sourceInput = runTimeCast<const ImagePlug>( inPlugs()->getChild<NameValuePlug>( sourceInputIndex )->valuePlug() );

		ConstStringVectorDataPtr inputChannelNamesData;
		{
			ImagePlug::GlobalScope globalScope( context );
			inputChannelNamesData = sourceInput->channelNamesPlug()->getValue();
		}
		const std::vector<std::string> &channelNames = inputChannelNamesData->readable();

		if( ImageAlgo::channelExists( channelNames, sourceChannel ) )
		{
			ImagePlug::ChannelDataScope channelDataScope( context );
			channelDataScope.setChannelName( sourceChannel );
			return sourceInput->channelDataPlug()->getValue();
		}
	}

	return ImagePlug::blackTile();
}

bool AssembleChannels::affectsChannelMap( const Gaffer::Plug *input ) const
{
	return (
		input == inPlugs() ||
		inPlugs()->isAncestorOf( input )
	);
}

void AssembleChannels::hashChannelMap( const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	AssembleChannelsParametersScope s( context );

	const ArrayPlug *in = inPlugs();
	for( int i = 0, e = in->children().size(); i < e; ++i )
	{
		auto p = in->getChild<NameValuePlug>( i );
		p->enabledPlug()->hash( h );
		p->namePlug()->hash( h );
	}
}

IECore::ObjectPtr AssembleChannels::computeChannelMap( const Gaffer::Context *context ) const
{
	AssembleChannelsParametersScope s( context );

	CompoundObjectPtr map = new IECore::CompoundObject();

	StringVectorDataPtr channelNamesData = new IECore::StringVectorData();
	auto &channelNames = channelNamesData->writable();
	map->members()["channelNames"] = channelNamesData;

	StringVectorDataPtr sourceChannelsData = new IECore::StringVectorData();
	auto &sourceChannels = sourceChannelsData->writable();
	map->members()["sourceChannels"] = sourceChannelsData;

	IntVectorDataPtr sourceInputsData = new IECore::IntVectorData();
	auto &sourceInputs = sourceInputsData->writable();
	map->members()["sourceInputs"] = sourceInputsData;

	const ArrayPlug *in = inPlugs();
	for( int i = 0, e = in->children().size(); i < e; ++i )
	{
		auto p = in->getChild<NameValuePlug>( i );
		if( !p->enabledPlug()->getValue() )
		{
			continue;
		}

		// The row name is <srcChannelName>:<destChannelName>

		const std::string &nameStr = p->namePlug()->getValue();
		const auto splitPos = nameStr.find( ":" );
		if( splitPos == std::string::npos )
		{
			continue;
		}

		const std::string src = nameStr.substr( splitPos + 1 );
		const std::string dest = nameStr.substr( 0, splitPos );

		channelNames.push_back( dest );
		sourceChannels.push_back( src );
		sourceInputs.push_back( i );
	}

	return map;
}
