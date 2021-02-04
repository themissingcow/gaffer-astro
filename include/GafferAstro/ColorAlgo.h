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

#include "GafferAstro/Export.h"

#include "OpenEXR/ImathColor.h"

namespace GafferAstro
{

namespace ColorAlgo
{

enum ColorModel
{
	RGB,
	HSV,
	HSL
};

// Conversions

template<typename T>
GAFFERASTRO_API void rgb2hsl( T &color );

template<typename T>
GAFFERASTRO_API void hsl2rgb( T &color );

template<typename T>
GAFFERASTRO_API void rgb2hsv( T &color );

template<typename T>
GAFFERASTRO_API void hsv2rgb( T &color );

// HSL Adjustments

// Offsets the supplied color where it lies within range of the center color.
// Colors outside of the range will be left unchanged.
// The hue component is wrapped, saturation is clamped between 0-1 and v/l is positive.
GAFFERASTRO_API void adjustHueSaturationRange(
	const Imath::V3f &adjust,
	const Imath::Color3f &center, const Imath::V3f &range, const Imath::V3f &transition,
	Imath::Color3f &color,
	bool offsetMode = false, bool outputMask = false
);

} // namespace ColorAlgo

} // namespace GafferAstro

#include "GafferAstro/ColorAlgo.inl"
