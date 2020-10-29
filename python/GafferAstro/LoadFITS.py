import Gaffer
import GafferAstro
import GafferImage
import IECore
import imath

import inspect

class LoadFITS( GafferImage.ImageNode ) :

	def __init__( self, name = "LoadFITS" ) :

		GafferImage.ImageNode.__init__( self, name )

		self["fileName"] = Gaffer.StringPlug( "fileName" )
		self["resize"] = Gaffer.FloatPlug( defaultValue = 1.0, minValue = 0.001 )

		reader = GafferAstro.FITSReader()
		self["__FITSReader"] = reader
		reader["fileName"].setInput( self["fileName"] )

		scale = GafferAstro.Scale()
		self["__Scale"] = scale
		scale["in"].setInput( reader["out"] )
		scale["factor"].setInput( self["resize"] )
		scale["filter"].setValue( "sharp-gaussian" )

		grade = GafferImage.Grade()
		self["__Grades"] = grade
		grade["channels"].setValue( "Y" )
		grade["blackPoint"].gang()
		grade["whitePoint"].gang()
		grade["gamma"].gang()
		grade["in"].setInput( scale["out"] )

		assembleChannels = GafferAstro.AssembleChannels()
		self["__AssembleChannels"] = assembleChannels

		assembleChannels["in"][0]["value"].setInput( grade["out"] )
		assembleChannels["in"][0]["name"].setValue( "input:Y" )
		assembleChannels["in"].removeChild( assembleChannels["in"][1] )

		collect = GafferImage.CollectImages()
		self["__Collect"] = collect
		collect["in"].setInput( assembleChannels["out"] )
		collect["layerVariable"].setValue( "channel" )

		self["out"].setInput( collect["out"] )

		spreadsheet = Gaffer.Spreadsheet()
		self["__Spreadsheet"] = spreadsheet
		Gaffer.Metadata.registerValue( spreadsheet["rows"], "spreadsheet:defaultRowVisible", False )
		Gaffer.PlugAlgo.promote( spreadsheet["rows"] )
		spreadsheet["selector"].setValue( "${channel}" )

		rows = spreadsheet["rows"].source()
		for column in ( "blackPoint", "whitePoint", "gamma" ) :
			index = rows.addColumn( grade[column]["r"], column )
			grade[column]["r"].setInput( spreadsheet["out"][index] )
			Gaffer.Metadata.registerValue( rows.defaultRow()["cells"][index], "spreadsheet:columnWidth", 50 )

		collect["rootLayers"].setInput( spreadsheet["activeRowNames"] )


IECore.registerRunTimeTyped( LoadFITS, typeName = "GafferAstro::LoadFITS" )
