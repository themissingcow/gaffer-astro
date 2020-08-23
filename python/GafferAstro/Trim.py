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
import GafferScene
import IECore

import imath

import inspect

class Trim( GafferImage.ImageProcessor ) :

	def __init__( self, name = "Trim" ) :

		GafferImage.ImageProcessor.__init__( self, name )

		self["flipHorizontal"] =  Gaffer.BoolPlug()
		self["flipVertical"] = Gaffer.BoolPlug()
		self["rotate"] = Gaffer.FloatPlug()
		self["applyCrop"] = Gaffer.BoolPlug( defaultValue = False )
		self["crop"] = Gaffer.Box2fPlug( defaultValue = imath.Box2f( imath.V2f(0), imath.V2f(1) ) )

		mirror = GafferImage.Mirror()
		self["__Mirror"] = mirror
		mirror["horizontal"].setInput( self["flipHorizontal"] )
		mirror["vertical"].setInput( self["flipVertical"] )
		mirror["in"].setInput( self["in"] )

		transform = GafferImage.ImageTransform()
		self["__Transform"] = transform
		transform["transform"]["rotate"].setInput( self["rotate"] )
		transform["filter"].setValue( "sharp-gaussian" )
		transform["in"].setInput( mirror["out"] )

		transformCenterExpr = Gaffer.Expression()
		self["__Expression_Transform"] = transformCenterExpr
		transformCenterExpr.setExpression(
			inspect.cleandoc("""
				import imath
				f = parent["__Transform"]["in"]["format"]
				parent["__Transform"]["transform"]["pivot"] = imath.V2f( f.width() / 2.0, f.height() / 2.0 )
			"""),
			"python"
		)

		crop = GafferImage.Crop()
		self["__Crop"] = crop
		crop["in"].setInput( transform["out"] )

		options = GafferScene.StandardOptions()
		self["__CropWindow"] = options
		options["options"]["renderCropWindow"]["value"].setInput( self["crop"] )

		cropExpr = Gaffer.Expression()
		self["__Expression_Crop"] = cropExpr
		cropExpr.setExpression(
			inspect.cleandoc("""
			import imath

			f = parent["__Crop"]["in"]["format"]
			w = parent["__CropWindow"]["options"]["renderCropWindow"]["value"]

			parent["__Crop"]["area"] = imath.Box2i(
				imath.V2i( f.width() * w.min().x, f.height() * ( 1 - w.max().y ) ),
				imath.V2i( f.width() * w.max().x, f.height() * ( 1 - w.min().y ) )
			)
			"""),
			"python"
		)

		parentPath = GafferAstro.ParentPath()
		self["__ParentPath"] = parentPath

		imageMeta = GafferImage.ImageMetadata()
		self["__ImageMetadata"] = imageMeta
		imageMeta["metadata"].addChild( Gaffer.NameValuePlug( "gaffer:sourceScene", Gaffer.StringPlug( "value" ), True, "member1" ) )
		imageMeta["user"].addChild( Gaffer.StringPlug( "parentPath" ) )
		imageMeta["user"]["parentPath"].setInput( parentPath["parentPath"] )
		imageMeta["in"].setInput( transform["out"] )

		self["__Expression_Meta"] = Gaffer.Expression()
		expr = 'parent["__ImageMetadata"]["metadata"]["member1"]["value"] = parent["__ImageMetadata"]["user"]["parentPath"] + ".__CropWindow.out"'
		self["__Expression_Meta"].setExpression( expr, "python" )

		switch = Gaffer.Switch()
		self["__Switch"] = switch
		switch.setup( crop["out"] )
		switch["in"][0].setInput( imageMeta["out"] )
		switch["in"][1].setInput( crop["out"] )
		switch["index"].setInput( self["applyCrop"] )

		self["out"].setInput( switch["out"] )

IECore.registerRunTimeTyped( Trim, typeName = "GafferAstro::Trim" )
