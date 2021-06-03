import Gaffer
import GafferDispatch
import GafferImage
import IECore
import imath

import inspect

class Starnet( GafferDispatch.TaskNode ) :

	def __init__( self, name = "Starnet" ) :

		GafferDispatch.TaskNode.__init__( self, name )

		self["in"] = GafferImage.ImagePlug( "in" )

		self["fileName"] = Gaffer.StringPlug( defaultValue = '', )
		self["channels"] = Gaffer.StringPlug( defaultValue = 'Y', )
		self["dataType"] = Gaffer.StringPlug( defaultValue = 'uint16', )

		imageWriter = GafferImage.ImageWriter()
		self["__ImageWriter"] = imageWriter
		imageWriter["channels"].setInput( self["channels"] )
		imageWriter["tiff"]["dataType"].setInput( self["dataType"] )
		imageWriter["in"].setInput( self["in"] )

		constant = GafferImage.Constant()
		self["__Constant"] = constant

		imageReader = GafferImage.ImageReader()
		self["__ImageReader"] = imageReader
		imageReader["missingFrameMode"].setValue( 1 )
		imageReader["fileName"].setInput( self["fileName"] )

		outputSwitch = Gaffer.Switch()
		self["__OutputSwitch"] = outputSwitch
		outputSwitch.setup( imageReader["out"] )
		outputSwitch["in"][0].setInput( constant["out"] )
		outputSwitch["in"][1].setInput( imageReader["out"] )

		self["out"] = GafferImage.ImagePlug( direction = Gaffer.Plug.Direction.Out )
		self["out"].setInput( outputSwitch["out"] )

		sysStarnet = GafferDispatch.SystemCommand()
		self["__SystemCommand_starnet"] = sysStarnet
		sysStarnet["command"].setValue( 'starnet -v "{input}" "{output}"' )
		sysStarnet["shell"].setValue( False )
		sysStarnet["substitutions"].addChild( Gaffer.NameValuePlug( "input", IECore.StringData( "" ) ) )
		sysStarnet["substitutions"].addChild( Gaffer.NameValuePlug( "output", IECore.StringData( "" ) ) )
		sysStarnet["substitutions"]["NameValuePlug"]["value"].setInput( imageWriter["fileName"] )
		sysStarnet["substitutions"]["NameValuePlug1"]["value"].setInput( imageReader["fileName"] )
		sysStarnet["preTasks"][0].setInput( imageWriter["task"] )

		sysCleanup = GafferDispatch.SystemCommand()
		self["__SystemCommand_cleanup"] = sysCleanup
		sysCleanup["command"].setValue( 'rm "{input}"' )
		sysCleanup["shell"].setValue( False )
		sysCleanup["substitutions"].addChild( Gaffer.NameValuePlug( "input", IECore.StringData( "" ) ) )
		sysCleanup["substitutions"]["NameValuePlug"]["value"].setInput( imageWriter["fileName"] )
		sysCleanup["preTasks"][0].setInput( sysStarnet["task"] )

		self["task"].setInput( sysCleanup["task"] )

		# Expressions
		self["__Expression"] = Gaffer.Expression()
		self["__Expression"].setExpression(
			inspect.cleandoc( """
				import os
				fileName = parent["fileName"]
				if fileName and not fileName.endswith( ".tif" ) :
					raise ValueError( "fileName must be a .tif file" )
				tmpName = fileName.replace( ".tif", "-input.tif" )
				parent["__ImageWriter"]["fileName"] = tmpName
				parent["__Constant"]["format"] = parent["__ImageWriter"]["in"]["format"]
				parent["__OutputSwitch"]["index"] = 1 if os.path.exists(parent["__ImageReader"]["fileName"]) else 0
			""" ),
			"python"
		)


IECore.registerRunTimeTyped( Starnet, typeName = "GafferAstro::Starnet" )
