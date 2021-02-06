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
import GafferDispatch
import IECore

import inspect

class MultiStarnet( GafferDispatch.TaskNode ) :

	def __init__( self, name = "MultiStarnet" ) :

		GafferDispatch.TaskNode.__init__( self, name )

		self["fileName"] = Gaffer.StringPlug( defaultValue = '${channel}.tif', )

		self["in"] = GafferImage.ImagePlug( "in" )

		scale = GafferAstro.Scale()
		self["__Scale"] = scale
		scale["in"].setInput( self["in"] )

		starnet = GafferAstro.Starnet()
		self["__Starnet"] = starnet
		starnet["in"].setInput( scale["out"] )
		starnet["fileName"].setInput( self["fileName" ] )
		Gaffer.PlugAlgo.promote( starnet["dataType"] )

		resize = GafferImage.Resize()
		self["__Resize"] = resize
		resize["in"].setInput( starnet["out"] )

		scaleExpression = Gaffer.Expression()
		self["__ScaleExpression"] = scaleExpression
		scaleExpression.setExpression(
			inspect.cleandoc("""
				import GafferImage
				enabled = parent["__Scale"]["factor"] != 1
				parent["__Scale"]["enabled"] = enabled
				inFormat = parent["__Scale"]["in"]["format"]
				parent["__Resize"]["format"] = GafferImage.Format( inFormat.width(), inFormat.height(), 1.000 )
				parent["__Resize"]["enabled"] = enabled
			"""),
			"python"
		)

		spreadsheet = Gaffer.Spreadsheet()
		self["__Spreadsheet"] = spreadsheet
		spreadsheet["selector"].setValue( "${channel}" )
		Gaffer.Metadata.registerValue( spreadsheet["rows"], "spreadsheet:defaultRowVisible", False, persistent = False )

		spreadsheet["rows"].addColumn( Gaffer.StringPlug( "source" ), "source" )
		Gaffer.Metadata.registerValue( spreadsheet["rows"].defaultRow()["cells"]["source"], "spreadsheet:staticColumn", True, persistent = False )
		starnet["channels"].setInput( spreadsheet["out"]["source"] )

		spreadsheet["rows"].addColumn( Gaffer.FloatPlug( "scale", minValue = 0, defaultValue = 1 ), "scale" )
		Gaffer.Metadata.registerValue( spreadsheet["rows"].defaultRow()["cells"]["scale"], "spreadsheet:staticColumn", True, persistent = False )
		scale["factor"].setInput( spreadsheet["out"]["scale"] )

		Gaffer.PlugAlgo.promote( spreadsheet["rows"] )

		wedge = GafferDispatch.Wedge()
		self["__Wedge"] = wedge
		wedge["variable"].setValue( "channel" )
		wedge["mode"].setValue( 5 )
		wedge["strings"].setInput( spreadsheet["activeRowNames"] )
		wedge["preTasks"]["preTask0"].setInput( starnet["task"] )

		collect = GafferAstro.CollectChannels()
		self["__Collect"] = collect
		collect["in"].setInput( resize["out"] )
		collect["channelVariable"].setValue( "channel" )
		collect["channels"].setInput( spreadsheet["activeRowNames"] )

		copy = GafferImage.CopyChannels()
		self["__Copy"] = copy
		copy["channels"].setValue( "*" )
		copy["in"][0].setInput( self["in"] )
		copy["in"][1].setInput( collect["out"] )

		self["out"] = GafferImage.ImagePlug( direction = Gaffer.Plug.Direction.Out )
		self["out"].setInput( copy["out"] )

		self["task"].setInput( wedge["task"] )

IECore.registerRunTimeTyped( MultiStarnet, typeName = "GafferAstro::MultiStarnet" )
