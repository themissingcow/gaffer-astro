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

#include "GafferAstro/ColorAlgo.h"

#include <algorithm>

using namespace GafferAstro;
using namespace Imath;

namespace {

inline float smoothstep( float edge0, float edge1, float x )
{
	if( edge0 == edge1 ) {
		return ( x < edge0 ) ? 0 : 1;
	}

	x = std::clamp( ( x - edge0 ) / ( edge1 - edge0 ), 0.0f, 1.0f );
	return x * x * ( 3.0 - 2.0 * x );
}

inline float smoothpulse( float center, float range, float transition, float x, bool wrap = false )
{
	const float edge1 = center - ( range / 2.0f );
	const float edge2 = center + ( range / 2.0f );

	const float edge0 = edge1 - transition;
	const float edge3 = edge2 + transition;

	if( wrap )
	{
		const float offset = ( x > 0.5f ) ? -1.0 : 1.0;
		return std::max(
			smoothstep( edge0, edge1, x ) - smoothstep( edge2, edge3, x ),
			smoothstep( edge0, edge1, x + offset ) - smoothstep( edge2, edge3, x + offset )
		);
	}
	else
	{
		return smoothstep( edge0, edge1, x ) - smoothstep( edge2, edge3, x );
	}
}

void conformHSL( float &h, float &s, float &vl )
{
	h = fmodf( h, 1.0f );
	s = std::clamp( s, 0.0f, 1.0f );
	vl = std::max( vl, 0.0f );
}

} // namespace

void ColorAlgo::adjustHueSaturationRange(
	const V3f &adjust,
	const Color3f &center, const V3f &range, const V3f &transition,
	Color3f &color,
	bool offsetMode, bool outputMask
)
{
	float &h = color[0];
	float &s = color[1];
	float &vl = color[2];

	const float mH = smoothpulse( center[0], range[0], transition[0], h, true );
	const float mS = smoothpulse( center[1], range[1], transition[1], s );
	const float mVL = smoothpulse( center[2], range[2], transition[2], vl );
	const float mix = std::min( mH, std::min( mS, mVL ) );

	if( outputMask )
	{
		h = 0;
		s = 0;
		vl = mix;
	}
	else
	{
		h =  ( mix * ( h + adjust[0]  ) ) + ( ( 1.0 - mix ) * h  );
		if( offsetMode )
		{
			s =  ( mix * ( s + adjust[1]  ) ) + ( ( 1.0 - mix ) * s  );
			vl = ( mix * ( vl + adjust[2] ) ) + ( ( 1.0 - mix ) * vl );
		}
		else
		{
			s =  ( mix * ( s * adjust[1]  ) ) + ( ( 1.0 - mix ) * s  );
			vl = ( mix * ( vl * adjust[2] ) ) + ( ( 1.0 - mix ) * vl );
		}
	}

	conformHSL( h, s, vl );
}

