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

#ifndef GAFFERASTRO_COLORISE_H
#define GAFFERASTRO_COLORISE_H

#include "GafferAstro/Export.h"
#include "GafferAstro/TypeIds.h"

#include "GafferImage/FlatImageProcessor.h"

#include "Gaffer/CompoundNumericPlug.h"
#include "Gaffer/SplinePlug.h"
#include "Gaffer/StringPlug.h"

using namespace GafferImage;

namespace GafferAstro
{

class GAFFERASTRO_API Colorise : public FlatImageProcessor
{

	public :

		Colorise( const std::string &name=defaultName<Colorise>() );
		~Colorise() override;

		GAFFER_GRAPHCOMPONENT_DECLARE_TYPE( GafferAstro::Colorise, ColoriseTypeId, ImageProcessor );

		Gaffer::StringPlug *channelPlug();
		const Gaffer::StringPlug *channelPlug() const;

		Gaffer::BoolPlug *mapEnabledPlug();
		const Gaffer::BoolPlug *mapEnabledPlug() const;

		Gaffer::SplinefColor4fPlug *mapPlug();
		const Gaffer::SplinefColor4fPlug *mapPlug() const;

		Gaffer::V2fPlug *rangePlug();
		const Gaffer::V2fPlug *rangePlug() const;

		Gaffer::Color4fPlug *constantPlug();
		const Gaffer::Color4fPlug *constantPlug() const;

		void affects( const Gaffer::Plug *input, AffectedPlugsContainer &outputs ) const override;

	protected :

		void hash( const Gaffer::ValuePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const override;
		void compute( Gaffer::ValuePlug *output, const Gaffer::Context *context ) const override;
		Gaffer::ValuePlug::CachePolicy computeCachePolicy( const Gaffer::ValuePlug *output ) const override;

		virtual void hashChannelNames( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const override;
		virtual IECore::ConstStringVectorDataPtr computeChannelNames( const Gaffer::Context *context, const ImagePlug *parent ) const override;

		virtual void hashChannelData( const GafferImage::ImagePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const override;
		virtual IECore::ConstFloatVectorDataPtr computeChannelData( const std::string &channelName, const Imath::V2i &tileOrigin, const Gaffer::Context *context, const ImagePlug *parent ) const override;

		virtual bool affectsColorData( const Gaffer::Plug *input ) const;
		virtual void hashColorData( const Gaffer::Context *context, IECore::MurmurHash &h ) const;
		virtual void computeColorData(
			const Gaffer::Context *context,
			IECore::FloatVectorData *r, IECore::FloatVectorData *g, IECore::FloatVectorData *b,
			IECore::FloatVectorData *a
		) const;

	private :

		Gaffer::ObjectPlug *colorDataPlug();
		const Gaffer::ObjectPlug *colorDataPlug() const;

		static size_t g_firstPlugIndex;
		static IECore::StringVectorDataPtr g_channelNames;

};

IE_CORE_DECLAREPTR( Colorise );

} // namespace GafferAstro

#endif // GAFFERASTRO_COLORISE_H
