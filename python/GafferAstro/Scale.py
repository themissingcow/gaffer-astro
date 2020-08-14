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
import GafferImage
import IECore

import inspect


class Scale( GafferImage.ImageProcessor ) :

	def __init__( self, name = "Scale" ) :

		GafferImage.ImageProcessor.__init__( self, name )

		self.addChild( Gaffer.FloatPlug( "factor", defaultValue = 1, minValue = 0 ) )
		self.addChild( Gaffer.StringPlug( "filter", defaultValue = "sharp-gaussian" ) )

		self["__Resize"] = GafferImage.Resize()
		self["__Resize"]["filter"].setInput( self["filter"] )
		self["__Resize"]["in"].setInput( self["in"] )

		self["out"].setInput( self["__Resize"]["out"] )

		self["__Expression"] = Gaffer.Expression()
		self["__Expression"].setExpression(
			inspect.cleandoc( """
			format = parent["__Resize"]["in"]["format"]
			w = format.getDisplayWindow()
			parent["__Resize"]["format"]["displayWindow"]["min"]["x"] = parent["factor"] * w.min().x
			parent["__Resize"]["format"]["displayWindow"]["min"]["y"] = parent["factor"] * w.min().y
			parent["__Resize"]["format"]["displayWindow"]["max"]["x"] = parent["factor"] * w.max().x
			parent["__Resize"]["format"]["displayWindow"]["max"]["y"] = parent["factor"] * w.max().y
			parent["__Resize"]["format"]["pixelAspect"] = format.getPixelAspect()
			""" ),
			"python"
		)


IECore.registerRunTimeTyped( Scale, typeName = "GafferAstro::Scale" )
