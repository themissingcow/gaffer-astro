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
import GafferDispatch
import GafferImage
import IECore
import imath

import inspect

class PixInsight( GafferDispatch.TaskNode ) :

	jsTemplate = inspect.cleandoc( """
		Console.show();

		let inputPath = "%s";
		let outputPath = "%s";

		// User Script

		%s

		// Process input

		let windows = ImageWindow.open( inputPath );

		if ( windows.length < 1 ) {
			throw new Error( "Unable to open " + inputPath );
		}
		if ( windows.length > 1 ) {
			throw new Error( "Multi-image files not supported " + inputPath );
		}

		let window = windows[0];
		let view = window.mainView;
		view.id = "INPUT"

		P.executeOn( view );

		window.saveAs( outputPath, false, false, true, false );
		window.forceClose();

		CoreApplication.terminateInstance( CoreApplication.instance );
	""" )


	def __init__( self, name = "PixInsight" ) :

		GafferDispatch.TaskNode.__init__( self, name )

		self["in"] = GafferImage.ImagePlug( "in" )

		self["fileName"] = Gaffer.StringPlug( defaultValue = '', )
		self["channels"] = Gaffer.StringPlug( defaultValue = 'Y', )
		self["dataType"] = Gaffer.StringPlug( defaultValue = 'uint16', )
		self["pixScript"] = Gaffer.StringPlug( defaultValue = '', )
		self["slot"] = Gaffer.IntPlug( defaultValue = 2, minValue = 1, maxValue = 256 )

		imageWriter = GafferImage.ImageWriter()
		self["__ImageWriter"] = imageWriter
		imageWriter["channels"].setInput( self["channels"] )
		imageWriter["tiff"]["dataType"].setInput( self["dataType"] )
		imageWriter["in"].setInput( self["in"] )

		imageWriterExpr = Gaffer.Expression()
		self["__ImageWriterExpression"] = imageWriterExpr
		imageWriterExpr.setExpression(
			inspect.cleandoc( """
				fileName = parent["fileName"]
				if fileName and not fileName.endswith( ".xisf" ) :
						raise ValueError( "fileName must be an .xisf file" )
				tmpName = fileName.replace( ".xisf", "-input.tif" )
				parent["__ImageWriter"]["fileName"] = tmpName
			""" ),
			"python"
		)

		xisfReader = GafferAstro.XISFReader()
		self["__XISGReader"] = xisfReader
		xisfReader["missingFrameMode"].setValue( 1 )
		xisfReader["fileName"].setInput( self["fileName"] )

		self["out"] = GafferImage.ImagePlug( direction = Gaffer.Plug.Direction.Out )
		self["out"].setInput( xisfReader["out"] )

		jsCommand = GafferDispatch.PythonCommand()
		self["__GenerateScript"] = jsCommand
		jsCommand["command"].setValue( inspect.cleandoc( """
			js = {trippleQuote}

			{js}

			{trippleQuote} % ( variables["input"], variables["output"], variables["pixScript"] )

			with open( variables["scriptPath"], "w" ) as script :
				script.write( js )
		""" ).format( js = self.jsTemplate, trippleQuote = '"""' ) )
		jsCommand["variables"].addChild( Gaffer.NameValuePlug( "pixScript", "", "pixScript" ) )
		jsCommand["variables"]["pixScript"]["value"].setInput( self["pixScript"] )
		for p in ( "scriptPath", "input", "output" ) :
			nvPlug = Gaffer.NameValuePlug( p, "", p )
			jsCommand["variables"].addChild( nvPlug )
		jsCommand["variables"]["input"]["value"].setInput( imageWriter["fileName"] )
		jsCommand["variables"]["output"]["value"].setInput( xisfReader["fileName"] )
		jsCommand["preTasks"][0].setInput( imageWriter["task"] )

		jsExp = Gaffer.Expression()
		self["__GenerateScriptExr"] = jsExp
		jsExp.setExpression(
			inspect.cleandoc( """
				parent["__GenerateScript"]["variables"]["scriptPath"]["value"] = parent["fileName"].replace( ".xisf", ".js" )
			""" ),
			"python"
		)

		sysPixInsight = GafferDispatch.SystemCommand()
		self["__PixInsight"] = sysPixInsight
		sysPixInsight["command"].setValue( 'PixInsight --automation-mode -r="{script}" -n={slot}' )
		sysPixInsight["substitutions"].addChild( Gaffer.NameValuePlug( "script", "", "script" ) )
		sysPixInsight["substitutions"].addChild( Gaffer.NameValuePlug( "slot", 2, "slot" ) )
		sysPixInsight["substitutions"]["script"]["value"].setInput( jsCommand["variables"]["scriptPath"]["value"] )
		sysPixInsight["substitutions"]["slot"]["value"].setInput( self["slot"] )
		sysPixInsight["shell"].setValue( True )
		sysPixInsight["preTasks"][0].setInput( jsCommand["task"] )

		sysCleanup = GafferDispatch.SystemCommand()
		self["__SystemCommand_cleanup"] = sysCleanup
		sysCleanup["command"].setValue( 'rm "{input}" "{script}"' )
		sysCleanup["substitutions"].addChild( Gaffer.NameValuePlug( "input", IECore.StringData( "" ), "input" ) )
		sysCleanup["substitutions"]["input"]["value"].setInput( imageWriter["fileName"] )
		sysCleanup["substitutions"].addChild( Gaffer.NameValuePlug( "script", IECore.StringData( "" ), "script" ) )
		sysCleanup["substitutions"]["script"]["value"].setInput( jsCommand["variables"]["scriptPath"]["value"] )
		sysCleanup["preTasks"][0].setInput( sysPixInsight["task"] )

		self["task"].setInput( sysCleanup["task"] )

IECore.registerRunTimeTyped( PixInsight, typeName = "GafferAstro::PixInsight" )
