//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2021,  Tom Cowland. All rights reserved.
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

#include "GafferAstro/HueSaturation.h"

#include "GafferAstro/ColorAlgo.h"

#include "Gaffer/Context.h"

using namespace IECore;
using namespace Gaffer;
using namespace GafferImage;
using namespace GafferAstro;

namespace
{
	ColorAlgo::ColorModel colorModel( const std::string& str )
	{
		if( str == "hsl" )
		{
			return ColorAlgo::HSL;
		}
		else if( str == "hsv" )
		{
			return ColorAlgo::HSV;
		}
		else if( str == "rgb" )
		{
			return ColorAlgo::RGB;
		}

		throw IECore::Exception( "Invalid color model '" + str + "'" );
	}

	struct HueSaturationParametersScope : public Gaffer::Context::EditableScope
	{
		HueSaturationParametersScope( const Gaffer::Context *context )
			:   EditableScope( context )
		{
			remove( GafferImage::ImagePlug::tileOriginContextName );
			remove( GafferImage::ImagePlug::channelNameContextName );
		}
	};

}

GAFFER_NODE_DEFINE_TYPE( HueSaturation );

size_t HueSaturation::g_firstPlugIndex = 0;

HueSaturation::HueSaturation( const std::string &name )
	:	ColorProcessor( name )
{
	storeIndexOfNextChild( g_firstPlugIndex );

	addChild( new StringPlug( "inModel", Gaffer::Plug::In, "rgb" ) );
	addChild( new StringPlug( "model", Gaffer::Plug::In, "hsl" ) );
	addChild( new StringPlug( "outModel", Gaffer::Plug::In, "rgb" ) );

	addChild( new V3fPlug( "adjust", Gaffer::Plug::In, Imath::V3f( 0.0f, 1.0f, 1.0f ) ) );

	addChild( new Color3fPlug( "center", Gaffer::Plug::In, Imath::Color3f( 0.25f, 0.75f, 0.75f ) ) );
	addChild( new V3fPlug( "range", Gaffer::Plug::In, Imath::V3f( 1.0f ) ) );
	addChild( new V3fPlug( "transition", Gaffer::Plug::In, Imath::V3f( 0.1f ) ) );

	addChild( new BoolPlug( "offsetMode", Gaffer::Plug::In, false ) );
	addChild( new BoolPlug( "outputMask", Gaffer::Plug::In, false ) );
}

HueSaturation::~HueSaturation()
{
}

Gaffer::StringPlug *HueSaturation::inModelPlug()
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

const Gaffer::StringPlug *HueSaturation::inModelPlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex );
}

Gaffer::StringPlug *HueSaturation::modelPlug()
{
	return getChild<StringPlug>( g_firstPlugIndex + 1 );
}

const Gaffer::StringPlug *HueSaturation::modelPlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex + 1 );
}

Gaffer::StringPlug *HueSaturation::outModelPlug()
{
	return getChild<StringPlug>( g_firstPlugIndex + 2 );
}

const Gaffer::StringPlug *HueSaturation::outModelPlug() const
{
	return getChild<StringPlug>( g_firstPlugIndex + 2 );
}

Gaffer::V3fPlug *HueSaturation::adjustPlug()
{
	return getChild<V3fPlug>( g_firstPlugIndex + 3 );
}

const Gaffer::V3fPlug *HueSaturation::adjustPlug() const
{
	return getChild<V3fPlug>( g_firstPlugIndex + 3 );
}

Gaffer::Color3fPlug *HueSaturation::centerPlug()
{
	return getChild<Color3fPlug>( g_firstPlugIndex + 4 );
}

const Gaffer::Color3fPlug *HueSaturation::centerPlug() const
{
	return getChild<Color3fPlug>( g_firstPlugIndex + 4 );
}

Gaffer::V3fPlug *HueSaturation::rangePlug()
{
	return getChild<V3fPlug>( g_firstPlugIndex + 5 );
}

const Gaffer::V3fPlug *HueSaturation::rangePlug() const
{
	return getChild<V3fPlug>( g_firstPlugIndex + 5 );
}

Gaffer::V3fPlug *HueSaturation::transitionPlug()
{
	return getChild<V3fPlug>( g_firstPlugIndex + 6 );
}

const Gaffer::V3fPlug *HueSaturation::transitionPlug() const
{
	return getChild<V3fPlug>( g_firstPlugIndex + 6 );
}

Gaffer::BoolPlug *HueSaturation::offsetModePlug()
{
	return getChild<BoolPlug>( g_firstPlugIndex + 7 );
}

const Gaffer::BoolPlug *HueSaturation::offsetModePlug() const
{
	return getChild<BoolPlug>( g_firstPlugIndex + 7 );
}

Gaffer::BoolPlug *HueSaturation::outputMaskPlug()
{
	return getChild<BoolPlug>( g_firstPlugIndex + 8 );
}

const Gaffer::BoolPlug *HueSaturation::outputMaskPlug() const
{
	return getChild<BoolPlug>( g_firstPlugIndex + 8 );
}

bool HueSaturation::affectsColorData( const Gaffer::Plug *input ) const
{
	if( ColorProcessor::affectsColorData( input ) )
	{
		return true;
	}

	return (
		input == inModelPlug() ||
		input == modelPlug() ||
		input == outModelPlug() ||
		input == adjustPlug() ||
		adjustPlug()->isAncestorOf( input ) ||
		input == centerPlug() ||
		centerPlug()->isAncestorOf( input ) ||
		input == rangePlug() ||
		rangePlug()->isAncestorOf( input ) ||
		input == transitionPlug() ||
		transitionPlug()->isAncestorOf( input ) ||
		input == offsetModePlug() ||
		input == outputMaskPlug()
	);
}

void HueSaturation::hashColorData( const Gaffer::Context *context, IECore::MurmurHash &h ) const
{
	ColorProcessor::hashColorData( context, h );

	HueSaturationParametersScope s( context );

	inModelPlug()->hash( h );
	modelPlug()->hash( h );
	outModelPlug()->hash( h );
	adjustPlug()->hash( h );
	centerPlug()->hash( h );
	rangePlug()->hash( h );
	transitionPlug()->hash( h );
	offsetModePlug()->hash( h );
	outputMaskPlug()->hash( h );
}

void HueSaturation::processColorData( const Gaffer::Context *context, IECore::FloatVectorData *rData, IECore::FloatVectorData *gData, IECore::FloatVectorData *bData  ) const
{
	HueSaturationParametersScope parameterScipe( context );

	const ColorAlgo::ColorModel inModel = colorModel( inModelPlug()->getValue() );
	const ColorAlgo::ColorModel model = colorModel( modelPlug()->getValue() );
	const ColorAlgo::ColorModel outModel = colorModel( outModelPlug()->getValue() );

	const Imath::V3f adjustment = adjustPlug()->getValue();

	Imath::Color3f center = centerPlug()->getValue();
	if( model == ColorAlgo::HSV )
	{
		ColorAlgo::rgb2hsv( center );
	}
	else
	{
		ColorAlgo::rgb2hsl( center );
	};

	const Imath::V3f range = rangePlug()->getValue();
	const Imath::V3f transition = transitionPlug()->getValue();

	const bool offsetMode = offsetModePlug()->getValue();
	const bool outputMask = outputMaskPlug()->getValue();

	const bool haveAdjustments = adjustment != ( offsetMode ? Imath::V3f( 0.0f ) : Imath::V3f( 0.0f, 1.0f, 1.0f ) );

	auto &r = rData->writable();
	auto &g = gData->writable();
	auto &b = bData->writable();

	Imath::Color3f c;

	const size_t numPixels = r.size();
	for( size_t i = 0; i<numPixels; ++i )
	{
		c[0] = r[i];
		c[1] = g[i];
		c[2] = b[i];

		if( inModel != model )
		{
			switch( inModel )
			{
				case ColorAlgo::HSV:
					ColorAlgo::hsv2rgb( c );
					break;
				case ColorAlgo::HSL:
					ColorAlgo::hsl2rgb( c );
					break;
				default: {}
			}

			if( model == ColorAlgo::HSV )
			{
				ColorAlgo::rgb2hsv( c );
			}
			else
			{
				ColorAlgo::rgb2hsl( c );
			};
		}

		if( haveAdjustments )
		{
			ColorAlgo::adjustHueSaturationRange( adjustment, center, range, transition, c, offsetMode, outputMask );
		}

		if( model != outModel )
		{
			if( model == ColorAlgo::HSV )
			{
				ColorAlgo::hsv2rgb( c );
			}
			else
			{
				ColorAlgo::hsl2rgb( c );
			};

			switch( outModel )
			{
				case ColorAlgo::HSV:
					ColorAlgo::rgb2hsv( c );
					break;
				case ColorAlgo::HSL:
					ColorAlgo::rgb2hsl( c );
					break;
				default: {}
			}

		}

		r[i] = c[0];
		g[i] = c[1];
		b[i] = c[2];
	}
}
