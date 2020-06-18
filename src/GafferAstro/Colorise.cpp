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

#include "GafferAstro/Colorise.h"

#include "GafferImage/ImageAlgo.h"

#include "Gaffer/Context.h"

using namespace IECore;
using namespace Gaffer;
using namespace GafferImage;
using namespace GafferAstro;

namespace
{
	struct ColoriseParametersScope : public Gaffer::Context::EditableScope
	{
		ColoriseParametersScope( const Gaffer::Context *context )
			:   EditableScope( context )
		{
			remove( GafferImage::ImagePlug::tileOriginContextName );
			remove( GafferImage::ImagePlug::channelNameContextName );
		}
	};

}

GAFFER_GRAPHCOMPONENT_DEFINE_TYPE( Colorise );

size_t Colorise::g_firstPlugIndex = 0;
IECore::StringVectorDataPtr Colorise::g_channelNames = new IECore::StringVectorData( { "R", "G", "B", "A" } );

Colorise::Colorise( const std::string &name )
	:	FlatImageProcessor( name, 1, 1 )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	addChild( new StringPlug( "channel", Gaffer::Plug::In, "Y" ) );

	addChild( new BoolPlug( "mapEnabled" ) );

	SplinefColor4fPlug::ValueType mapDefault;
	mapDefault.points.insert( SplinefColor4fPlug::ValueType::Point( 0.0f, Imath::Color4f( 0.0f, 0.0f, 0.0f, 1.0f ) ) );
	mapDefault.points.insert( SplinefColor4fPlug::ValueType::Point( 1.0f, Imath::Color4f( 1.0f ) ) );
	addChild( new SplinefColor4fPlug( "map", Gaffer::Plug::In, mapDefault ) );

	addChild( new V2fPlug( "range", Gaffer::Plug::In, Imath::V2f( 0.0f, 1.0f ) ) );

	addChild( new Color4fPlug( "constant", Gaffer::Plug::In, Imath::Color4f( 1.0f ) ) );

	addChild( new ObjectPlug( "__colorData", Gaffer::Plug::Out, new ObjectVector ) );

	// We don't ever want to change the these, so we make pass-through connections.
	outPlug()->formatPlug()->setInput( inPlug()->formatPlug() );
	outPlug()->dataWindowPlug()->setInput( inPlug()->dataWindowPlug() );
	outPlug()->metadataPlug()->setInput( inPlug()->metadataPlug() );
	outPlug()->deepPlug()->setInput( inPlug()->deepPlug() );
	outPlug()->sampleOffsetsPlug()->setInput( inPlug()->sampleOffsetsPlug() );
}

Colorise::~Colorise()
{
}

Gaffer::StringPlug *Colorise::channelPlug()
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

const Gaffer::StringPlug *Colorise::channelPlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

Gaffer::BoolPlug *Colorise::mapEnabledPlug()
{
	return getChild<BoolPlug>( g_firstPlugIndex + 1 );
}

const Gaffer::BoolPlug *Colorise::mapEnabledPlug() const
{
	return getChild<BoolPlug>( g_firstPlugIndex + 1 );
}

Gaffer::SplinefColor4fPlug *Colorise::mapPlug()
{
	return getChild<SplinefColor4fPlug>( g_firstPlugIndex + 2 );
}

const Gaffer::SplinefColor4fPlug *Colorise::mapPlug() const
{
	return getChild<SplinefColor4fPlug>( g_firstPlugIndex + 2 );
}

Gaffer::V2fPlug *Colorise::rangePlug()
{
	return getChild<V2fPlug>( g_firstPlugIndex + 3 );
}

const Gaffer::V2fPlug *Colorise::rangePlug() const
{
	return getChild<V2fPlug>( g_firstPlugIndex + 3 );
}

Gaffer::Color4fPlug *Colorise::constantPlug()
{
	return getChild<Color4fPlug>( g_firstPlugIndex + 4 );
}

const Gaffer::Color4fPlug *Colorise::constantPlug() const
{
	return getChild<Color4fPlug>( g_firstPlugIndex + 4 );
}

Gaffer::ObjectPlug *Colorise::colorDataPlug()
{
	return getChild<ObjectPlug>( g_firstPlugIndex + 5 );
}

const Gaffer::ObjectPlug *Colorise::colorDataPlug() const
{
	return getChild<ObjectPlug>( g_firstPlugIndex + 5 );
}

void Colorise::affects( const Gaffer::Plug *input, AffectedPlugsContainer &outputs ) const
{
	FlatImageProcessor::affects( input, outputs );

	if( input == colorDataPlug() )
	{
		outputs.push_back( outPlug()->channelDataPlug() );
	}
	else if( affectsColorData( input ) )
	{
		outputs.push_back( colorDataPlug() );
	}
}

void Colorise::hash( const Gaffer::ValuePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	FlatImageProcessor::hash( output, context, h );

	if( output == colorDataPlug() )
	{
		hashColorData( context, h );
	}
}

void Colorise::compute( Gaffer::ValuePlug *output, const Gaffer::Context *context ) const
{
	if( output == colorDataPlug() )
	{
		FloatVectorDataPtr rgba[4];

		for( int i = 0; i < 4; ++i )
		{
			rgba[i] = new FloatVectorData();
		}

		computeColorData( context, rgba[0].get(), rgba[1].get(), rgba[2].get(), rgba[3].get() );

		ObjectVectorPtr result = new ObjectVector();
		result->members().push_back( rgba[0] );
		result->members().push_back( rgba[1] );
		result->members().push_back( rgba[2] );
		result->members().push_back( rgba[3] );

		static_cast<ObjectPlug *>( output )->setValue( result );
		return;
	}

	FlatImageProcessor::compute( output, context );
}


Gaffer::ValuePlug::CachePolicy Colorise::computeCachePolicy( const Gaffer::ValuePlug *output ) const
{
	if( output == outPlug()->channelDataPlug() )
	{
		// Because our implementation of compute for channelData is so simple,
		// just copying data out of our intermediate colorDataPlug(), it is
		// actually quicker not to cache the result.
		return ValuePlug::CachePolicy::Uncached;
	}
	return FlatImageProcessor::computeCachePolicy( output );
}

void Colorise::hashChannelNames( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	FlatImageProcessor::hashChannelNames( parent, context, h );
}

IECore::ConstStringVectorDataPtr Colorise::computeChannelNames( const Gaffer::Context *context, const ImagePlug *parent ) const
{
	return g_channelNames;
}

void Colorise::hashChannelData( const GafferImage::ImagePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	FlatImageProcessor::hashChannelData( output, context, h );
	const std::string &channel = context->get<std::string>( ImagePlug::channelNameContextName );
	h.append( channel );
	colorDataPlug()->hash( h );
}

IECore::ConstFloatVectorDataPtr Colorise::computeChannelData( const std::string &channelName, const Imath::V2i &tileOrigin, const Gaffer::Context *context, const ImagePlug *parent ) const
{
	ConstObjectVectorPtr colorData = boost::static_pointer_cast<const ObjectVector>( colorDataPlug()->getValue() );
	const int dataIndex = ImageAlgo::colorIndex( channelName );
	return dataIndex >= 0 ? boost::static_pointer_cast<const FloatVectorData>( colorData->members()[dataIndex] ) : nullptr;
}

bool Colorise::affectsColorData( const Gaffer::Plug *input ) const
{
	return (
		input == inPlug()->channelDataPlug() ||
		input == inPlug()->channelNamesPlug() ||
		input == channelPlug() ||
		input == mapEnabledPlug() ||
		input == mapPlug() ||
		mapPlug()->isAncestorOf( input ) ||
		input == rangePlug() ||
		rangePlug()->isAncestorOf( input ) ||
		input == constantPlug() ||
		constantPlug()->isAncestorOf( input )
	);
}

void Colorise::hashColorData( const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	ColoriseParametersScope s( context );

	inPlug()->channelNamesPlug()->hash( h );
	channelPlug()->hash( h );
	mapEnabledPlug()->hash( h );
	mapPlug()->hash( h );
	rangePlug()->hash( h );
	constantPlug()->hash( h );

	const std::string &channelName = channelPlug()->getValue();
	if( channelName != "" )
	{
		ConstStringVectorDataPtr channelNamesData;
		{
			ImagePlug::GlobalScope globalScope( context );
			channelNamesData = inPlug()->channelNamesPlug()->getValue();
		}
		const std::vector<std::string> &channelNames = channelNamesData->readable();

		ImagePlug::ChannelDataScope channelDataScope( context );

		if( ImageAlgo::channelExists( channelNames, channelName ) )
		{
			channelDataScope.setChannelName( channelName );
			inPlug()->channelDataPlug()->hash( h );
		}
	}
}

void Colorise::computeColorData( const Gaffer::Context *context, IECore::FloatVectorData *rData, IECore::FloatVectorData *gData, IECore::FloatVectorData *bData, IECore::FloatVectorData *aData  ) const
{
	ColoriseParametersScope parameterScipe( context );

	ConstFloatVectorDataPtr sourceChannelData = nullptr;

	ConstStringVectorDataPtr channelNamesData;
	{
		ImagePlug::GlobalScope globalScope( context );
		channelNamesData = inPlug()->channelNamesPlug()->getValue();
	}
	const std::vector<std::string> &channelNames = channelNamesData->readable();

	const std::string &channelName = channelPlug()->getValue();
	if( channelName == "" )
	{
		throw IECore::Exception( "No source channel set" );
	}

	{
		ImagePlug::ChannelDataScope channelDataScope( context );
		if( ImageAlgo::channelExists( channelNames, channelName ) )
		{
			channelDataScope.setChannelName( channelName );
			sourceChannelData = inPlug()->channelDataPlug()->getValue();
		}
	}

	if( !sourceChannelData )
	{
		throw IECore::Exception( "Source channel '" + channelName + "' does not exist" );
	}

	auto &s = sourceChannelData->readable();
	const size_t numPixels = s.size();

	auto &r = rData->writable();
	auto &g = gData->writable();
	auto &b = bData->writable();
	auto &a = aData->writable();

	r.resize( numPixels );
	g.resize( numPixels );
	b.resize( numPixels );
	a.resize( numPixels );

	const Imath::Color4f constant = constantPlug()->getValue();

	const SplinefColor4f map = mapPlug()->getValue().spline();
	const bool mapEnabled = mapEnabledPlug()->getValue();
	const Imath::V2f range = rangePlug()->getValue();

	for( size_t i = 0; i<numPixels; ++i )
	{
		Imath::Color4f color = constant;

		if( mapEnabled )
		{
			const float position =  ( s[i] - range[0] ) / std::max( 0.0001f, range[1] - range[0] );
			color *= map( std::min( 1.0f, std::max( 0.0f, position ) ) );
		}
		else
		{
			color.r *= s[i];
			color.g *= s[i];
			color.b *= s[i];
		}

		r[i] = color.r;
		g[i] = color.g;
		b[i] = color.b;
		a[i] = color.a;
	}
}
