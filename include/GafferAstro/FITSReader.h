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

#pragma once

#include "GafferAstro/Export.h"
#include "GafferAstro/TypeIds.h"

#include "GafferImage/FlatImageSource.h"

#include "Gaffer/StringPlug.h"
#include "Gaffer/NumericPlug.h"


namespace GafferAstro
{

class GAFFERASTRO_API FITSReader : public GafferImage::FlatImageSource
{
	public :

		FITSReader( const std::string& name=defaultName<FITSReader>() );
		~FITSReader() override;

		GAFFER_GRAPHCOMPONENT_DECLARE_TYPE( GafferAstro::FITSReader, FITSReaderTypeId, GafferImage::FlatImageSource )

		Gaffer::StringPlug *fileNamePlug();
		const Gaffer::StringPlug *fileNamePlug() const;

		Gaffer::IntPlug *refreshCountPlug();
		const Gaffer::IntPlug *refreshCountPlug() const;

		void affects( const Gaffer::Plug *input, AffectedPlugsContainer &outputs ) const override;

	protected :

		void hashFormat( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const override;
		void hashDataWindow( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const override;
		void hashMetadata( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const override;
		void hashChannelNames( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const override;
		void hashChannelData( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const override;

		GafferImage::Format computeFormat( const Gaffer::Context *context, const GafferImage::ImagePlug *parent ) const override;
		Imath::Box2i computeDataWindow( const Gaffer::Context *context, const GafferImage::ImagePlug *parent ) const override;
		IECore::ConstCompoundDataPtr computeMetadata( const Gaffer::Context *context, const GafferImage::ImagePlug *parent ) const override;
		IECore::ConstStringVectorDataPtr computeChannelNames( const Gaffer::Context *context, const GafferImage::ImagePlug *parent ) const override;
		IECore::ConstFloatVectorDataPtr computeChannelData( const std::string &channelName, const Imath::V2i &tileOrigin, const Gaffer::Context *context, const GafferImage::ImagePlug *parent ) const override;

	private :

		void hashFileName( const Gaffer::Context *context, IECore::MurmurHash &h ) const;

		static size_t g_firstPlugIndex;
};


IE_CORE_DECLAREPTR( FITSReader )

} // namespace GafferAstro
