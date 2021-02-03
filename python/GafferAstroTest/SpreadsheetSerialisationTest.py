##########################################################################
#
#  Copyright (c) 2020, Tom Cowland. All rights reserved.
#  Copyright (c) 2019, Image Engine Design Inc. All rights reserved.
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
#      * Neither the name of John Haddon nor the names of
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

import unittest

import IECore

import Gaffer
import GafferTest

import GafferAstro

class SpreadsheetSerialisationTest( GafferTest.TestCase ) :

	def testDynamicColumns( self ) :

		s = Gaffer.ScriptNode()

		s["s"] = Gaffer.Spreadsheet()
		s["s"]["rows"].addColumn( Gaffer.IntPlug( "column1" ) )
		s["s"]["rows"].addColumn( Gaffer.IntPlug( "column2" ) )
		s["s"]["rows"].addRow()
		s["s"]["rows"].addRow()

		s["s"]["rows"][0]["cells"]["column1"]["value"].setValue( 10 )
		s["s"]["rows"][1]["cells"]["column1"]["value"].setValue( 20 )
		s["s"]["rows"][1]["cells"]["column1"]["enabled"].setValue( False )
		s["s"]["rows"][1]["name"].setValue( "rrr" )
		s["s"]["rows"][2]["name"].setValue( "zzz" )
		s["s"]["rows"][2]["cells"]["column1"]["value"].setValue( 30 )
		s["s"]["rows"][2]["cells"]["column2"]["value"].setValue( 40 )

		ss = s.serialise()
		self.assertEqual( ss.count( "addChild" ), 1 )
		self.assertEqual( ss.count( "addColumn" ), 2 )
		self.assertEqual( ss.count( "addRows" ), 1 )

		s2 = Gaffer.ScriptNode()
		s2.execute( ss )

		self.assertEqual( s2["s"]["rows"].keys(), s["s"]["rows"].keys() )
		for r in s2["s"]["rows"].keys() :
			self.assertEqual( s2["s"]["rows"][r]["name"].getValue(), s["s"]["rows"][r]["name"].getValue() )
			self.assertEqual( s2["s"]["rows"][r]["enabled"].getValue(), s["s"]["rows"][r]["enabled"].getValue() )
			self.assertEqual( s2["s"]["rows"][r]["cells"].keys(), s["s"]["rows"][r]["cells"].keys() )
			for c in s2["s"]["rows"][r]["cells"].keys() :
				self.assertEqual( s2["s"]["rows"][r]["cells"][c]["enabled"].getValue(), s["s"]["rows"][r]["cells"][c]["enabled"].getValue() )
				self.assertEqual( s2["s"]["rows"][r]["cells"][c]["value"].getValue(), s["s"]["rows"][r]["cells"][c]["value"].getValue() )

	def testStaticColumns( self ) :

		s = Gaffer.ScriptNode()

		s["s"] = Gaffer.Spreadsheet()
		for column in ( "column1", "column2" ) :
			s["s"]["rows"].addColumn( Gaffer.IntPlug( column ) )
			Gaffer.Metadata.registerValue( s["s"]["rows"][0]["cells"][column], "spreadsheet:staticColumn", True, persistent = False )

		s["s"]["rows"].addRow()
		s["s"]["rows"].addRow()

		ss = s.serialise()
		self.assertEqual( ss.count( "addChild" ), 1 )
		self.assertEqual( ss.count( "addColumn" ), 0 )
		self.assertEqual( ss.count( "addRows" ), 1 )

		s["s"]["rows"].addColumn( Gaffer.StringPlug( "column3" ) )

		ss = s.serialise()
		self.assertEqual( ss.count( "addChild" ), 1 )
		self.assertEqual( ss.count( "addColumn" ), 1 )
		self.assertEqual( ss.count( "addRows" ), 1 )

if __name__ == "__main__":
	unittest.main()
