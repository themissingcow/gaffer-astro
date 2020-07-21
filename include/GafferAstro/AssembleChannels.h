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

#include "GafferImage/FlatImageProcessor.h"

#include "Gaffer/CompoundNumericPlug.h"
#include "Gaffer/SplinePlug.h"
#include "Gaffer/StringPlug.h"

using namespace GafferImage;

namespace GafferAstro
{

class GAFFERASTRO_API AssembleChannels : public ImageNode
{

	public :

		AssembleChannels( const std::string &name=defaultName<AssembleChannels>() );
		~AssembleChannels() override;

		GAFFER_GRAPHCOMPONENT_DECLARE_TYPE( AssembleChannels, AssembleChannelsTypeId, ImageNode );

		Gaffer::ArrayPlug *inPlugs();
		const Gaffer::ArrayPlug *inPlugs() const;

		void affects( const Gaffer::Plug *input, AffectedPlugsContainer &outputs ) const override;

	protected :

		void hash( const Gaffer::ValuePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const override;
		void compute( Gaffer::ValuePlug *output, const Gaffer::Context *context ) const override;

		virtual void hashChannelNames( const GafferImage::ImagePlug *parent, const Gaffer::Context *context, IECore::MurmurHash &h ) const override;
		virtual IECore::ConstStringVectorDataPtr computeChannelNames( const Gaffer::Context *context, const ImagePlug *parent ) const override;

		virtual void hashChannelData( const GafferImage::ImagePlug *output, const Gaffer::Context *context, IECore::MurmurHash &h ) const override;
		virtual IECore::ConstFloatVectorDataPtr computeChannelData( const std::string &channelName, const Imath::V2i &tileOrigin, const Gaffer::Context *context, const ImagePlug *parent ) const override;

	private :

		bool affectsChannelMap( const Gaffer::Plug *input ) const;
		void hashChannelMap( const Gaffer::Context *context, IECore::MurmurHash &h ) const;
		IECore::ObjectPtr computeChannelMap( const Gaffer::Context *context ) const;

		Gaffer::ObjectPlug *channelMapPlug();
		const Gaffer::ObjectPlug *channelMapPlug() const;

		static size_t g_firstPlugIndex;

};

IE_CORE_DECLAREPTR( AssembleChannels );

} // namespace GafferAstro
