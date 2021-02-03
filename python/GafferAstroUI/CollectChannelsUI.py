##########################################################################
#
#  Copyright (c) 2017, Image Engine Design Inc. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#      * Redistributions of source code must retain the above
#        copyright notice, this list of conditions and the following
#        disclaimer.
#
#      * Redistributions in binary form must reproduce the above
#        copyright notice, this list of conditions and the following
#        disclaimer in the documentation and/or other materials provided with
#        the distribution.
#
#      * Neither the name of John Haddon nor the names of
#        any other contributors to this software may be used to endorse or
#        promote products derived from this software without specific prior
#        written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
#  IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
#  PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
#  LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#  NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#  SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##########################################################################

import Gaffer
import GafferUI
import GafferAstro

Gaffer.Metadata.registerNode(

	GafferAstro.CollectChannels,

	"description",
	"""
	Forms a series of image channels by repeatedly evaluating the input with different Contexts.
	Useful for networks that need to dynamically build an unknown number of image channels.
	""",

	"ui:spreadsheet:activeRowNamesConnection", "channels",
	"ui:spreadsheet:selectorContextVariablePlug", "channelVariable",

	plugs = {

		"in" : [

			"description",
			"""
			The image which will be evaluated for each layer.
			""",

		],

		"channels" : [

			"description",
			"""
			A list of the new channels to create.
			""",

		],

		"channelVariable" : [

			"description",
			"""
			This Context Variable will be set with the current channel name when evaluating the in plug.
			This allows you to vary the upstream processing for each new channel.
			""",

		],

		"sourceChannel" : [

			"description",
			"""
			The name of the channel from the in plug to use to populate each output channel. This is
			evaluated in the same context as the in plug, allowing it to vary per output channel. If
			empty, the first channel will be used.
			""",

		],

	}

)
