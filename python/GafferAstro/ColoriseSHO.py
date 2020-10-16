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
import imath


class ColoriseSHO( GafferImage.ImageProcessor ) :

	__mapDefaults = {

		"Sii" : Gaffer.SplineDefinitionfColor4f(
			(
				( 0, imath.Color4f( 0, 0, 0, 1 ) ),
				( 0.13, imath.Color4f( 0.0741839781, 0.0327994451, 0.0327994451, 1 ) ),
				( 0.23, imath.Color4f( 0.195373669, 0.0846425965, 0.0906697512, 1 ) ),
				( 0.47, imath.Color4f( 0.467200011, 0.0537280068, 0.0537280068, 1 ) ),
				( 0.8, imath.Color4f( 0.467200011, 0.0537280068, 0.0537280068, 1 ) ),
				( 1, imath.Color4f( 0.579999983, 0.579999983, 0.579999983, 1 ) )
			),
			Gaffer.SplineDefinitionInterpolation( 1 )
		),

		"Ha" : Gaffer.SplineDefinitionfColor4f(
			(
				( 0, imath.Color4f( 0, 0, 0, 1 ) ),
				( 0.56, imath.Color4f( 0.563531935, 0.361336678, 0.123977043, 1 ) ),
				( 0.8, imath.Color4f( 0.800000012, 0.795640051, 0.363999993, 1 ) ),
				( 1, imath.Color4f( 1, 1, 1, 1 ) )
			),
			Gaffer.SplineDefinitionInterpolation( 1 )
		),

		"Oiii" : Gaffer.SplineDefinitionfColor4f(
			(
				( 0, imath.Color4f( 0, 0, 0, 1 ) ),
				( 0.21, imath.Color4f( 0.0576000027, 0.119232699, 0.159999996, 1 ) ),
				( 0.8, imath.Color4f( 0, 0.445500046, 0.810000002, 1 ) ),
				( 1, imath.Color4f( 0.289999992, 0.621249974, 0.699999988, 1 ) )
			),
			Gaffer.SplineDefinitionInterpolation( 1 )
		)
	}

	def __init__( self, name = "ColoriseSHO" ) :

		GafferImage.ImageProcessor.__init__( self, name )

		self["show"] = Gaffer.IntPlug( defaultValue = 0, minValue = 0, maxValue = 3 )

		# Channel colorising

		merge = GafferImage.Merge()
		self["__Merge"] = merge
		merge["operation"].setValue( 0 )

		outputSwitch = Gaffer.Switch()
		self["__Switch_output"] = outputSwitch
		outputSwitch.setup( self["out"] )
		outputSwitch["index"].setInput( self["show"] )
		outputSwitch["in"][ 0 ].setInput( merge["out"] )

		for channel in GafferAstro.NarrowbandChannels :

			self["source%s" % channel] = Gaffer.StringPlug( defaultValue = '%s.input' % channel )
			self["range%s" % channel] = Gaffer.V2fPlug( defaultValue = imath.V2f( 0, 1 ) )
			self["map%s" % channel] = Gaffer.SplinefColor4fPlug( defaultValue = self.__mapDefaults[ channel ] )
			self["saturation%s" % channel] = Gaffer.FloatPlug( defaultValue = 1.0, minValue = 0.0 )
			self["multiply%s" % channel] = Gaffer.FloatPlug( defaultValue = 1.0 )
			self["gamma%s" % channel] = Gaffer.FloatPlug( defaultValue = 1.0 )

			colorise =  GafferAstro.Colorise()
			self["__Colorise_%s" % channel ] = colorise

			colorise["in"].setInput( self["in"] )
			colorise["channel"].setInput( self["source%s" % channel] )
			colorise["mapEnabled"].setValue( True )
			colorise["range"].setInput( self["range%s" % channel ] )
			# Work around issue where setInput doesn't sync the number of knots
			colorise["map"].setValue( self["map%s" % channel ].getValue() )
			colorise["map"].setInput( self["map%s" % channel ] )

			cdl = GafferImage.CDL()
			self["__CDL_%s" % channel ] = cdl
			cdl["in"].setInput( colorise["out"] )
			cdl["saturation"].setInput( self["saturation%s" % channel ] )

			grade = GafferImage.Grade()
			self["__Grade_%s" % channel ] = grade
			grade["in"].setInput( cdl["out"] )
			grade["multiply"].gang()
			grade["multiply"]["r"].setInput( self["multiply%s" % channel ] )
			grade["gamma"].gang()
			grade["gamma"]["r"].setInput( self ["gamma%s" % channel ] )

			merge["in"][ len(merge["in"]) - 1 ].setInput( grade["out"] )
			outputSwitch["in"][ len(outputSwitch["in"]) - 1 ].setInput( grade["out"] )

		self["saturation"] = Gaffer.FloatPlug( defaultValue = 1.0, minValue = 0.0 )
		self["blackPoint"] = Gaffer.FloatPlug( defaultValue = 0.0 )
		self["whitePoint"] = Gaffer.FloatPlug( defaultValue = 1.0 )
		self["multiply"] = Gaffer.Color4fPlug( defaultValue = imath.Color4f( 1, 1, 1, 1 ) )
		self["gamma"] = Gaffer.FloatPlug( defaultValue = 1.0, minValue = 0.0 )

		outputCdl = GafferImage.CDL()
		self["__CDL_output"] = outputCdl
		outputCdl["in"].setInput( outputSwitch["out"] )
		outputCdl["saturation"].setInput( self["saturation"] )

		outputGrade = GafferImage.Grade()
		self["__Grade_output"] = outputGrade
		outputGrade["in"].setInput( outputCdl["out"] )
		outputGrade["blackPoint"].gang()
		outputGrade["blackPoint"]["r"].setInput( self["blackPoint"] )
		outputGrade["whitePoint"].gang()
		outputGrade["whitePoint"]["r"].setInput( self["whitePoint"] )
		outputGrade["multiply"].setInput( self["multiply"] )
		outputGrade["gamma"].gang()
		outputGrade["gamma"]["r"].setInput( self["gamma"] )

		copyChannels = GafferImage.CopyChannels()
		self["__CopyChannels"] = copyChannels
		copyChannels["in"][ 0 ].setInput( self["in"] )
		copyChannels["in"][ 1 ].setInput( outputGrade["out"] )
		copyChannels["channels"].setValue( "*" )

		self["out"].setInput( copyChannels["out"] )

IECore.registerRunTimeTyped( ColoriseSHO, typeName = "GafferAstro::ColoriseSHO" )
