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
#include "GafferAstro/TypeIds.h"

#include "GafferImage/ColorProcessor.h"

#include "Gaffer/CompoundNumericPlug.h"
#include "Gaffer/StringPlug.h"

using namespace GafferImage;

namespace GafferAstro
{

class GAFFERASTRO_API HueSaturation : public ColorProcessor
{

	public :

		HueSaturation( const std::string &name=defaultName<HueSaturation>() );
		~HueSaturation() override;

		GAFFER_GRAPHCOMPONENT_DECLARE_TYPE( GafferAstro::HueSaturation, HueSaturationTypeId, GafferImage::ColorProcessor );

		Gaffer::StringPlug *inModelPlug();
		const Gaffer::StringPlug *inModelPlug() const;

		Gaffer::StringPlug *modelPlug();
		const Gaffer::StringPlug *modelPlug() const;

		Gaffer::StringPlug *outModelPlug();
		const Gaffer::StringPlug *outModelPlug() const;

		Gaffer::V3fPlug *adjustPlug();
		const Gaffer::V3fPlug *adjustPlug() const;

		Gaffer::Color3fPlug *centerPlug();
		const Gaffer::Color3fPlug *centerPlug() const;

		Gaffer::V3fPlug *rangePlug();
		const Gaffer::V3fPlug *rangePlug() const;

		Gaffer::V3fPlug *transitionPlug();
		const Gaffer::V3fPlug *transitionPlug() const;

		Gaffer::BoolPlug *offsetModePlug();
		const Gaffer::BoolPlug *offsetModePlug() const;

		Gaffer::BoolPlug *outputMaskPlug();
		const Gaffer::BoolPlug *outputMaskPlug() const;

	protected :

		virtual bool affectsColorData( const Gaffer::Plug *input ) const override;
		virtual void hashColorData( const Gaffer::Context *context, IECore::MurmurHash &h ) const override;
		virtual void processColorData( const Gaffer::Context *context, IECore::FloatVectorData *r, IECore::FloatVectorData *g, IECore::FloatVectorData *b ) const override;

	private :

		static size_t g_firstPlugIndex;

};

IE_CORE_DECLAREPTR( HueSaturation );

} // namespace GafferAstro
