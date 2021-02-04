//////////////////////////////////////////////////////////////////////////
//
//  Copyright (c) 2021, Tom Cowland. All rights reserved.
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

#pragma once

#include "GafferAstro/ColorAlgo.h"

#include <algorithm>
#include <stdlib.h>


namespace GafferAstro
{

template<typename T>
void ColorAlgo::rgb2hsl( T &color )
{
	const typename T::BaseType &r = color[0];
	const typename T::BaseType &g = color[1];
	const typename T::BaseType &b = color[2];

	const typename T::BaseType xMax = std::max( r, std::max( g, b ) );
	const typename T::BaseType xMin = std::min( r, std::min( g, b ) );

	const typename T::BaseType c = xMax - xMin;
	const typename T::BaseType l = ( xMax + xMin ) / 2.0;

	typename T::BaseType h;
	if( c == 0.0 )
	{
		h = 0.0;
	}
	else if( xMax == r )
	{
		h = ( g - b ) / c;
	}
	else if( xMax == g )
	{
		h = 2.0 + ( ( b - r ) / c );
	}
	else
	{
		h = 4.0 + ( ( r - g ) / c );
	}
	h /= 6.0;

	if( h < 0.0 )
	{
		h += 1.0;
	}

	typename T::BaseType s = 0.0;
	if( l > 0.0 && l < 1.0 )
	{
		s = ( xMax - l ) / std::min( l, typename T::BaseType(1.0) - l );
	}

	color[0] = h;
	color[1] = s;
	color[2] = l;
}

template<typename T>
void ColorAlgo::hsl2rgb( T &color )
{
	typename T::BaseType h = color[0];
	const typename T::BaseType &s = color[1];
	const typename T::BaseType &l = color[2];

	if( h == 1.0 )
	{
		h = 0.0;
	}
	h *= 6.0;
	const typename T::BaseType c = ( 1.0 - abs( ( 2.0 * l ) - 1.0 ) ) * s;
	const typename T::BaseType x = c * ( 1.0 - abs( fmodf( h, 2.0 ) - 1.0 ) );

	typename T::BaseType r = 0.0, g = 0.0, b = 0.0;

	switch( int( floor( h ) ) )
	{
		case 0 :
			r = c;
			g = x;
			break;
		case 1 :
			r = x;
			g = c;
			break;
		case 2 :
			g = c;
			b = x;
			break;
		case 3 :
			g = x;
			b = c;
			break;
		case 4:
			r = x;
			b = c;
			break;
		default :
			r = c;
			b = x;
	}

	const typename T::BaseType m = l - ( c / 2.0 );

	color[0] = r + m;
	color[1] = g + m;
	color[2] = b + m;
}

} // namespace GafferAstro

