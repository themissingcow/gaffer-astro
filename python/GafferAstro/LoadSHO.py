import Gaffer
import GafferAstro
import GafferImage
import IECore
import imath

import inspect

class LoadSHO( GafferImage.ImageNode ) :

	def __init__( self, name = "LoadSHO" ) :

		GafferImage.ImageNode.__init__( self, name )

		self.addChild( Gaffer.StringPlug( "fileName" ) )
		self.addChild( Gaffer.FloatPlug( "resize", defaultValue = 1.0, minValue = 0.001 ) )

		assembleChannels = GafferAstro.AssembleChannels()
		self["__AssembleChannels"] = assembleChannels
		self["out"].setInput( assembleChannels["out"] )
		assembleChannels["in"].addChild( Gaffer.NameValuePlug( "", GafferImage.ImagePlug( "value", ), True, "in2", Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic ) )

		channels = {
			"Sii" : "Sulphur_II",
			"Ha" : "Hydrogen-alpha",
			"Oiii" : "Oxygen_III"
		}

		for index, channel in enumerate( channels ) :

			self.addChild( Gaffer.BoolPlug( "enabled%s" % channel, defaultValue = True ) )
			self.addChild( Gaffer.FloatPlug( "blackPoint%s" % channel, defaultValue = 0.0 ) )
			self.addChild( Gaffer.FloatPlug( "whitePoint%s" % channel, defaultValue = 1.0 ) )
			self.addChild( Gaffer.FloatPlug( "gamma%s" % channel, defaultValue = 1.0 ) )
			self.addChild( Gaffer.StringPlug( "channelName%s" % channel, defaultValue = channels[channel] ) )

			reader = GafferAstro.FITSReader()
			self["__FITSReader_%s" % channel] = reader

			scale = GafferAstro.Scale()
			self["__Scale_%s" % channel] = scale
			scale["in"].setInput( reader["out"] )
			scale["factor"].setInput( self["resize"] )
			scale["filter"].setValue( "sharp-gaussian" )

			grade = GafferImage.Grade()
			self["__Grade_%s" % channel] = grade
			grade["channels"].setValue( "Y" )
			grade["blackPoint"].gang()
			grade["blackPoint"]["r"].setInput( self["blackPoint%s" % channel] )
			grade["whitePoint"].gang()
			grade["whitePoint"]["r"].setInput( self["whitePoint%s" % channel] )
			grade["gamma"].gang()
			grade["gamma"]["r"].setInput( self["gamma%s" % channel] )
			grade["in"].setInput( scale["out"] )

			assembleChannels["in"][index]["value"].setInput( grade["out"] )
			assembleChannels["in"][index]["name"].setValue( "input.%s:Y" % channel )
			assembleChannels["in"][index]["enabled"].setInput( self["enabled%s" % channel] )

		# Expressions

		self["__Expression_FileName"] = Gaffer.Expression()
		self["__Expression_FileName"].setExpression(
			inspect.cleandoc( """
			# Paths
			parent["__FITSReader_Sii"]["fileName"] = parent["fileName"].format( channel = parent["channelNameSii"] )
			parent["__FITSReader_Ha"]["fileName"] = parent["fileName"].format( channel = parent["channelNameHa"] )
			parent["__FITSReader_Oiii"]["fileName"] = parent["fileName"].format( channel = parent["channelNameOiii"] )
			""" ),
			"python"
		)

IECore.registerRunTimeTyped( LoadSHO, typeName = "GafferAstro::LoadSHO" )
