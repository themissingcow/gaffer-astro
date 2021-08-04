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
import GafferImage
import IECore

import inspect

class MultiGrade( GafferImage.ImageProcessor ) :

	def __init__( self, name = "MultiGrade" ) :

		GafferImage.ImageProcessor.__init__( self, name )

		grade = GafferImage.Grade()
		self["__Grade"] = grade
		grade["in"].setInput( self["in"] )
		self["out"].setInput( grade["out"] )

		spreadsheet = Gaffer.Spreadsheet()
		self["__Spreadsheet"] = spreadsheet
		spreadsheet["selector"].setValue( "${image:channelName}" )

		Gaffer.Metadata.registerValue( spreadsheet["rows"], "spreadsheet:columnsNeedSerialisation", False, persistent = False )

		for p in ( "blackPoint", "whitePoint", "gamma" ) :
			grade[ p ].gang()
			spreadsheet["rows"].addColumn( grade[ p ]["r"], p )
			grade[ p ]["r"].setInput( spreadsheet["out"][ p ] )

		channelsExpression = Gaffer.Expression()
		self["__ChannelsExpression"] = channelsExpression
		channelsExpression.setExpression(
			inspect.cleandoc(
				"""
				rowNames = parent["__Spreadsheet"]["activeRowNames"]
				parent["__Grade"]["channels"] = " ".join( rowNames )
				"""
			),
			"python"
		)

		promotedRowsPlug = Gaffer.PlugAlgo.promote( spreadsheet["rows"] )
		Gaffer.Metadata.registerValue( promotedRowsPlug, "spreadsheet:columnsNeedSerialisation", False, persistent = False )

IECore.registerRunTimeTyped( MultiGrade, typeName = "GafferAstro::MultiGrade" )
