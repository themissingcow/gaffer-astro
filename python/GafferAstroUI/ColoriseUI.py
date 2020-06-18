##########################################################################
#
#  Copyright (c) 2020, Tom Cowland. All rights reserved.
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
#      * Neither the name of Tom Cowland nor the names of
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
import GafferAstro

Gaffer.Metadata.registerNode(

	GafferAstro.Colorise,

	"description",
	"""
	Colorises a single channel from the input to produce an RGBA output.
	Colorisation can either be constant, or via a color spline to produce
	false color images.
	""",

	"layout:section:Settings.Map:collapsed", False,

	plugs = {

		"channel" : [

			"description",
			"""
			The source luminance channel.
			""",

			"layout:index", 0,

		],

		"constant" : [

			"description",
			"""
			A fixed multiplier, applied either the direct channel value,
			or the re-mapped color via the map.
			""",

			"layout:index", 1,

		],

		"mapEnabled" : [

			"description",
			"""
			Enables color spline remapping.
			""",

			"layout:section", "Settings.Map"

		],

		"map" : [

			"description",
			"""
			The values in the selected channel are used to pick a color
			from the map. The spline is mapped to the range specified
			in the 'range' plug.
			""",

			"layout:section", "Settings.Map"
		],

		"range" : [

			"description",
			"""
			Determines the range over which the map is applied. The min value
			will map to the left of the spline, and the max value to the right.
			""",

			"layout:section", "Settings.Map"
		]

	}

)
