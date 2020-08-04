import Gaffer
import GafferImage
import IECore
import imath

import inspect

class Stars( Gaffer.SubGraph ) :

	def __init__( self, name = "Stars" ) :

		Gaffer.SubGraph.__init__( self, name )

		self["enabled"] = Gaffer.BoolPlug( "enabled", defaultValue = True, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, )

		self["source"] = Gaffer.StringPlug( "source", defaultValue = 'Oiii', flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, )
		self["switchIndex"] = Gaffer.IntPlug( "switchIndex", defaultValue = 0, minValue = 0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, )
		self["blackPoint"] = Gaffer.FloatPlug( "blackPoint", defaultValue = 0.0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, )
		self["whitePoint"] = Gaffer.FloatPlug( "whitePoint", defaultValue = 1.0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, )
		self["multiply"] = Gaffer.FloatPlug( "multiply", defaultValue = 1.0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, )
		self["gamma"] = Gaffer.FloatPlug( "gamma", defaultValue = 1.0, minValue = 0.0, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, )
		self["whiteClamp"] = Gaffer.BoolPlug( "whiteClamp", defaultValue = False, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, )

		self["Shuffle_Stars"] = GafferImage.Shuffle( "Shuffle_Stars" )
		self["Shuffle_Stars"]["channels"].addChild( GafferImage.Shuffle.ChannelPlug( "channel", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		self["Shuffle_Stars"]["channels"].addChild( GafferImage.Shuffle.ChannelPlug( "channel1", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		self["Shuffle_Stars"]["channels"].addChild( GafferImage.Shuffle.ChannelPlug( "channel2", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		self["Shuffle_Stars"]["channels"].addChild( GafferImage.Shuffle.ChannelPlug( "channel3", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		self["Shuffle_Stars"].addChild( Gaffer.V2fPlug( "__uiPosition", defaultValue = imath.V2f( 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )

		self["in"] = GafferImage.ImagePlug( "in", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, )
		self["out"] = GafferImage.ImagePlug( "out", direction = Gaffer.Plug.Direction.Out, flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, )

		self["BoxIn"] = Gaffer.BoxIn( "BoxIn" )
		self["BoxIn"].setup( GafferImage.ImagePlug( "out", ) )
		self["BoxIn"].addChild( Gaffer.V2fPlug( "__uiPosition", defaultValue = imath.V2f( 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )

		self["BoxOut"] = Gaffer.BoxOut( "BoxOut" )
		self["BoxOut"].setup( GafferImage.ImagePlug( "in", ) )
		self["BoxOut"].addChild( Gaffer.V2fPlug( "__uiPosition", defaultValue = imath.V2f( 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )

		self["Grade"] = GafferImage.Grade( "Grade" )
		self["Grade"].addChild( Gaffer.V2fPlug( "__uiPosition", defaultValue = imath.V2f( 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )

		self["Merge"] = GafferImage.Merge( "Merge" )
		self["Merge"]["in"].addChild( GafferImage.ImagePlug( "in2", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		self["Merge"].addChild( Gaffer.V2fPlug( "__uiPosition", defaultValue = imath.V2f( 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )

		self["Switch"] = Gaffer.Switch( "Switch" )
		self["Switch"].setup( GafferImage.ImagePlug( "in", ) )
		self["Switch"]["in"].addChild( GafferImage.ImagePlug( "in1", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		self["Switch"]["in"].addChild( GafferImage.ImagePlug( "in2", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		self["Switch"].addChild( Gaffer.V2fPlug( "__uiPosition", defaultValue = imath.V2f( 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )

		self["DeleteChannels"] = GafferImage.DeleteChannels( "DeleteChannels" )
		self["DeleteChannels"].addChild( Gaffer.V2fPlug( "__uiPosition", defaultValue = imath.V2f( 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )

		self["CopyChannels"] = GafferImage.CopyChannels( "CopyChannels" )
		self["CopyChannels"]["in"].addChild( GafferImage.ImagePlug( "in2", flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		self["CopyChannels"].addChild( Gaffer.V2fPlug( "__uiPosition", defaultValue = imath.V2f( 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )

		self["Dot"] = Gaffer.Dot( "Dot" )
		self["Dot"].setup( GafferImage.ImagePlug( "in", ) )
		self["Dot"].addChild( Gaffer.V2fPlug( "__uiPosition", defaultValue = imath.V2f( 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )
		self["Dot1"] = Gaffer.Dot( "Dot1" )
		self["Dot1"].setup( GafferImage.ImagePlug( "in", ) )
		self["Dot1"].addChild( Gaffer.V2fPlug( "__uiPosition", defaultValue = imath.V2f( 0, 0 ), flags = Gaffer.Plug.Flags.Default | Gaffer.Plug.Flags.Dynamic, ) )

		self["Shuffle_Stars"]["in"].setInput( self["BoxIn"]["out"] )
		self["Shuffle_Stars"]["channels"]["channel"]["out"].setValue( 'R' )
		self["Shuffle_Stars"]["channels"]["channel1"]["out"].setValue( 'G' )
		self["Shuffle_Stars"]["channels"]["channel2"]["out"].setValue( 'B' )
		self["Shuffle_Stars"]["channels"]["channel3"]["out"].setValue( 'A' )
		self["Shuffle_Stars"]["channels"]["channel3"]["in"].setValue( 'A' )
		self["Shuffle_Stars"]["__uiPosition"].setValue( imath.V2f( -35.1197166, -65.9784317 ) )

		self["Grade"]["in"].setInput( self["Shuffle_Stars"]["out"] )
		self["Grade"]["blackPoint"]["r"].setInput( self["blackPoint"] )
		self["Grade"]["blackPoint"]["g"].setInput( self["Grade"]["blackPoint"]["r"] )
		self["Grade"]["blackPoint"]["b"].setInput( self["Grade"]["blackPoint"]["r"] )
		self["Grade"]["whitePoint"]["r"].setInput( self["whitePoint"] )
		self["Grade"]["whitePoint"]["g"].setInput( self["Grade"]["whitePoint"]["r"] )
		self["Grade"]["whitePoint"]["b"].setInput( self["Grade"]["whitePoint"]["r"] )
		self["Grade"]["multiply"]["r"].setInput( self["multiply"] )
		self["Grade"]["multiply"]["g"].setInput( self["Grade"]["multiply"]["r"] )
		self["Grade"]["multiply"]["b"].setInput( self["Grade"]["multiply"]["r"] )
		self["Grade"]["gamma"]["r"].setInput( self["gamma"] )
		self["Grade"]["gamma"]["g"].setInput( self["Grade"]["gamma"]["r"] )
		self["Grade"]["gamma"]["b"].setInput( self["Grade"]["gamma"]["r"] )
		self["Grade"]["whiteClamp"].setInput( self["whiteClamp"] )
		self["Grade"]["__uiPosition"].setValue( imath.V2f( -35.1197166, -71.6424942 ) )

		self["Merge"]["in"][0].setInput( self["DeleteChannels"]["out"] )
		self["Merge"]["in"][1].setInput( self["Grade"]["out"] )
		self["Merge"]["__uiPosition"].setValue( imath.V2f( -49.8698616, -79.8065567 ) )

		self["out"].setInput( self["BoxOut"]["__out"] )
		self["BoxIn"]["__in"].setInput( self["in"] )

		Gaffer.Metadata.registerValue( self["BoxIn"]["__in"], 'deletable', True )
		Gaffer.Metadata.registerValue( self["BoxIn"]["__in"], 'renameable', True )
		Gaffer.Metadata.registerValue( self["BoxIn"]["__in"], 'nodule:type', 'GafferUI::StandardNodule' )
		Gaffer.Metadata.registerValue( self["BoxIn"]["__in"], 'description', 'The input image' )
		Gaffer.Metadata.registerValue( self["BoxIn"]["__in"], 'plugValueWidget:type', '' )
		Gaffer.Metadata.registerValue( self["BoxIn"]["__in"], 'noduleLayout:spacing', 2.0 )
		self["BoxIn"]["__uiPosition"].setValue( imath.V2f( -61.9514999, -57.6464005 ) )
		self["BoxOut"]["in"].setInput( self["CopyChannels"]["out"] )
		Gaffer.Metadata.registerValue( self["BoxOut"]["__out"], 'deletable', True )
		Gaffer.Metadata.registerValue( self["BoxOut"]["__out"], 'renameable', True )
		Gaffer.Metadata.registerValue( self["BoxOut"]["__out"], 'nodule:type', 'GafferUI::StandardNodule' )
		Gaffer.Metadata.registerValue( self["BoxOut"]["__out"], 'description', 'The output image generated by this node.' )
		self["BoxOut"]["passThrough"].setInput( self["Dot"]["out"] )
		self["BoxOut"]["enabled"].setInput( self["enabled"] )
		self["BoxOut"]["__uiPosition"].setValue( imath.V2f( -57.4514999, -106.645584 ) )
		self["Switch"]["index"].setInput( self["switchIndex"] )
		Gaffer.Metadata.registerValue( self["Switch"]["in"], 'noduleLayout:section', 'top' )
		self["Switch"]["in"][0].setInput( self["Merge"]["out"] )
		self["Switch"]["in"][1].setInput( self["Grade"]["out"] )
		Gaffer.Metadata.registerValue( self["Switch"]["out"], 'noduleLayout:section', 'bottom' )
		self["Switch"]["__uiPosition"].setValue( imath.V2f( -46.8698616, -90.1494904 ) )
		self["DeleteChannels"]["in"].setInput( self["BoxIn"]["out"] )
		self["DeleteChannels"]["mode"].setValue( 1 )
		self["DeleteChannels"]["channels"].setValue( '[RGB]' )
		self["DeleteChannels"]["__uiPosition"].setValue( imath.V2f( -52.8698616, -65.9784317 ) )
		self["CopyChannels"]["in"][0].setInput( self["BoxIn"]["out"] )
		self["CopyChannels"]["in"][1].setInput( self["Switch"]["out"] )
		self["CopyChannels"]["channels"].setValue( '[RGB]' )
		self["CopyChannels"]["__uiPosition"].setValue( imath.V2f( -58.9514999, -98.3135529 ) )

		self["Dot"]["in"].setInput( self["Dot1"]["out"] )
		self["Dot"]["__uiPosition"].setValue( imath.V2f( -20.063736, -99.1455841 ) )
		self["Dot1"]["in"].setInput( self["BoxIn"]["out"] )
		self["Dot1"]["__uiPosition"].setValue( imath.V2f( -20.063736, -65.1464005 ) )

		# Expressions
		self["Expression"] = Gaffer.Expression()
		self["Expression"].setExpression(
			inspect.cleandoc( """
			parent["Shuffle_Stars"]["channels"]["channel"]["in"] = "input.%s" % parent["source"]
			parent["Shuffle_Stars"]["channels"]["channel1"]["in"] = "input.%s" % parent["source"]
			parent["Shuffle_Stars"]["channels"]["channel2"]["in"] = "input.%s" % parent["source"]
			""" ),
			"python"
		)


IECore.registerRunTimeTyped( Stars, typeName = "GafferAstro::Stars" )
