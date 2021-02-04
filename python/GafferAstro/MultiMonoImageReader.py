##########################################################################
#
#  Copyright (c) 2021, Tom Cowland. All rights reserved.
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

import inspect


class MultiMonoImageReader( GafferImage.ImageNode ) :

	def __init__( self, name = "MultiMonoImageReader" ) :

		GafferImage.ImageNode.__init__( self, name )

		self["fileName"] = Gaffer.StringPlug( "fileName", defaultValue = "${token}.${extension}" )
		self["resize"] = Gaffer.FloatPlug( defaultValue = 1.0, minValue = 0.001 )

		fitsReader = GafferAstro.FITSReader()
		self["__FITSReader"] = fitsReader
		fitsReader["fileName"].setInput( self["fileName"] )

		xisfReader = GafferAstro.XISFReader()
		self["__XISFReader"] = xisfReader
		xisfReader["fileName"].setInput( self["fileName"] )

		imageReader = GafferImage.ImageReader()
		self["__ImageReader"] = imageReader
		imageReader["fileName"].setInput( self["fileName"] )

		readerSwitch = Gaffer.Switch()
		readerSwitch.setup( fitsReader["out"] )
		self["__ReaderSwitch"] = readerSwitch
		readerSwitch["in"][0].setInput( fitsReader["out"] )
		readerSwitch["in"][1].setInput( xisfReader["out"] )
		readerSwitch["in"][2].setInput( imageReader["out"] )

		switchExpression = Gaffer.Expression()
		self["__SwitchExpression"] = switchExpression
		switchExpression.setExpression(
			inspect.cleandoc( """
				map = { "fits" : 0, "xsif" : 1 }
				parent["__ReaderSwitch"]["index"] = map.get( context[ "extension" ], 2 )
			""" ),
			"python"
		)

		scale = GafferAstro.Scale()
		self["__Scale"] = scale
		scale["in"].setInput( readerSwitch["out"] )
		scale["factor"].setInput( self["resize"] )
		scale["filter"].setValue( "sharp-gaussian" )

		variables = Gaffer.ContextVariables()
		variables.setup( scale["out"] )
		self["__Variables"] = variables
		variables["in"].setInput( scale["out"] )
		variables["variables"].addChild( Gaffer.NameValuePlug( "extension", IECore.StringData( "" ), name="extension" ) )
		variables["variables"].addChild( Gaffer.NameValuePlug( "token", IECore.StringData( "" ), name="token" ) )

		collectChannels = GafferAstro.CollectChannels()
		self["__CollectChannels"] = collectChannels
		collectChannels["in"].setInput( variables["out"] )
		collectChannels["channelVariable"].setValue( "channel" )

		self["out"].setInput( collectChannels["out"] )

		spreadsheet = Gaffer.Spreadsheet()
		self["__Spreadsheet"] = spreadsheet
		spreadsheet["selector"].setValue( "${channel}" )

		tokenColumnIndex = spreadsheet["rows"].addColumn( Gaffer.StringPlug( "filenameToken", defaultValue="${channel}" ) )
		Gaffer.Metadata.registerValue( spreadsheet["rows"].defaultRow()["cells"]["filenameToken"], "spreadsheet:staticColumn", True, persistent = False )

		extensionColumnIndex = spreadsheet["rows"].addColumn( Gaffer.StringPlug( "extension", defaultValue = "xisf" ) )
		Gaffer.Metadata.registerValue( spreadsheet["rows"].defaultRow()["cells"]["extension"], "spreadsheet:staticColumn", True, persistent = False )
		Gaffer.Metadata.registerValue( spreadsheet["rows"].defaultRow()["cells"]["extension"]["value"], 'preset:fits', 'fits', persistent = False )
		Gaffer.Metadata.registerValue( spreadsheet["rows"].defaultRow()["cells"]["extension"]["value"], 'preset:xisf', 'xisf', persistent = False )
		Gaffer.Metadata.registerValue( spreadsheet["rows"].defaultRow()["cells"]["extension"]["value"], 'preset:tif', 'tif', persistent = False )
		Gaffer.Metadata.registerValue( spreadsheet["rows"].defaultRow()["cells"]["extension"]["value"], 'presetsPlugValueWidget:allowCustom', True, persistent = False )
		Gaffer.Metadata.registerValue( spreadsheet["rows"].defaultRow()["cells"]["extension"]["value"], 'plugValueWidget:type', 'GafferUI.PresetsPlugValueWidget', persistent = False )
		self["__Variables"]["variables"]["extension"]["value"].setInput( spreadsheet["out"]["extension"] )

		collectChannels["channels"].setInput( spreadsheet["activeRowNames"] )

		variablesExpression = Gaffer.Expression()
		self["__variablesExpression"] = variablesExpression
		variablesExpression.setExpression(
			inspect.cleandoc(
				"""
					customToken = parent["__Spreadsheet"]["out"]["filenameToken"]
					channel = context["channel"]
					parent["__Variables"]["variables"]["token"]["value"] = customToken or channel
				"""
				.format( tokenIndex = tokenColumnIndex )
			),
			"python"
		)

		Gaffer.PlugAlgo.promote( spreadsheet["rows"] )

IECore.registerRunTimeTyped( MultiMonoImageReader, typeName = "GafferAstro::MultiMonoImageReader" )
