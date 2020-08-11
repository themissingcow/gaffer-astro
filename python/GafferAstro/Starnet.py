import Gaffer
import GafferDispatch
import GafferImage
import IECore
import imath

import inspect

class Starnet( GafferDispatch.TaskNode ) :

	def __init__( self, name = "Starnet" ) :

		GafferDispatch.TaskNode.__init__( self, name )

		self.addChild( GafferImage.ImagePlug( "in" ) )

		self.addChild( Gaffer.StringPlug( "fileName", defaultValue = '', ) )
		self.addChild( Gaffer.StringPlug( "channels", defaultValue = 'Y', ) )
		self.addChild( Gaffer.StringPlug( "dataType", defaultValue = 'float', ) )

		imageWriter = GafferImage.ImageWriter()
		self["__ImageWriter"] = imageWriter
		imageWriter["channels"].setInput( self["channels"] )
		imageWriter["tiff"]["dataType"].setInput( self["dataType"] )
		imageWriter["in"].setInput( self["in"] )

		imageReader = GafferImage.ImageReader()
		self["__ImageReader"] = imageReader
		imageReader["missingFrameMode"].setValue( 1 )
		imageReader["fileName"].setInput( self["fileName"] )

		self.addChild( GafferImage.ImagePlug( "out", direction = Gaffer.Plug.Direction.Out ) )
		self["out"].setInput( imageReader["out"] )

		sysStarnet = GafferDispatch.SystemCommand()
		self["__SystemCommand_starnet"] = sysStarnet
		sysStarnet["command"].setValue( 'starnet "{input}" "{output}"' )
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
		self["Expression"] = Gaffer.Expression()
		self["Expression"].setExpression(
			inspect.cleandoc( """
			fileName = parent["fileName"]
			if fileName and not fileName.endswith( ".tif" ) :
				raise ValueError( "fileName must be a .tif file" )
			tmpName = fileName.replace( ".tif", "-input.tif" )
			parent["__ImageWriter"]["fileName"] = tmpName
			""" ),
			"python"
		)


IECore.registerRunTimeTyped( Starnet, typeName = "GafferAstro::Starnet" )
