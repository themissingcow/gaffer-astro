##########################################################################
#
#  Copyright (c) 2020, Tom Cowland. All rights reserved.
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

import os
import unittest
import inspect
import six
import imath

import IECore

import Gaffer
import GafferTest
import GafferImage
import GafferImageTest
import GafferAstro

class CollectChannelsTest( GafferImageTest.ImageTestCase ) :

	def testChannels( self ) :

		constant = GafferImage.Constant()
		constant["color"].setValue( imath.Color4f( 0.5, 1.5, 2.5, 1.0 ) )
		constant["format"].setValue( GafferImage.Format( 10, 10, 1.000 ) )

		collect = GafferAstro.CollectChannels()
		collect["in"].setInput( constant["out"] )

		collect["channels"].setValue( IECore.StringVectorData( [ "R", "G", "B", "A" ] ) )

		self.assertEqual( collect["out"]["format"].getValue(), GafferImage.Format( 10, 10, 1) )

		sampler = GafferImage.ImageSampler()
		sampler["pixel"].setValue( imath.V2f( 1, 1 ) )
		sampler["channels"].setValue( IECore.StringVectorData( [ "R", "G", "B", "A" ] ) )
		sampler["image"].setInput( collect["out"] )

		self.assertEqual( sampler["color"].getValue(), imath.Color4f( 0.5 ) )

		collect["sourceChannel"].setValue( "R" )
		self.assertEqual( sampler["color"].getValue(), imath.Color4f( 0.5 ) )

		collect["sourceChannel"].setValue( "G" )
		self.assertEqual( sampler["color"].getValue(), imath.Color4f( 1.5 ) )

		collect["sourceChannel"].setValue( "B" )
		self.assertEqual( sampler["color"].getValue(), imath.Color4f( 2.5 ) )

		collect["sourceChannel"].setValue( "A" )
		self.assertEqual( sampler["color"].getValue(), imath.Color4f( 1.0 ) )

		self.assertEqual( collect["out"]["channelNames"].getValue(), IECore.StringVectorData( [ "R", "G", "B", "A" ] ) )

		collect["channels"].setValue( IECore.StringVectorData( [ "Cat", "Dog" ] ) )
		self.assertEqual( collect["out"]["channelNames"].getValue(), IECore.StringVectorData( [ "Cat", "Dog" ] ) )

		collect["sourceChannel"].setValue( "doesn't exist" )
		with six.assertRaisesRegex( self, Gaffer.ProcessException, "No channel 'doesn't exist' in input for output channel 'Cat'" ) :
			collect["out"]["channelNames"].getValue()

		collect["channels"].setValue( IECore.StringVectorData( [ "X", "Y", "Z" ] ) )

		e = Gaffer.Expression()
		collect.addChild( e )
		e.setExpression(
			inspect.cleandoc(
				"""
				map = { "X" : "B", "Y" : "G", "Z" : "R" }
				dst = context["collect:channelName"]
				src = map[ dst ]
				parent["sourceChannel"] = src
				"""
			),
			"python"
		)
		sampler["channels"].setValue( IECore.StringVectorData( [ "X", "Y", "Z" ] ) )

		self.assertEqual( collect["out"]["channelNames"].getValue(), IECore.StringVectorData( [ "X", "Y", "Z" ] ) )
		self.assertEqual( sampler["color"].getValue(), imath.Color4f( 2.5, 1.5, 0.5, 0 ) )

	def testMetadata( self ) :

		constant = GafferImage.Constant()
		constant["color"].setValue( imath.Color4f( 0.5, 1.5, 2.5, 1.0 ) )

		metadata = GafferImage.ImageMetadata()
		metadata["in"].setInput( constant["out"] )
		metadata["metadata"].addChild( Gaffer.NameValuePlug( "test", "" ) )

		e = Gaffer.Expression()
		metadata.addChild( e )
		e.setExpression( 'parent["metadata"]["NameValuePlug"]["value"] = context["collect:channelName"]', "python" )

		collect = GafferAstro.CollectChannels()
		collect["in"].setInput( metadata["out"] )

		collect["channels"].setValue( IECore.StringVectorData( [ 'R', 'G', 'B', 'A' ] ) )
		self.assertEqual( collect["out"]["metadata"].getValue(), IECore.CompoundData( { "test" : "R" } ) )

		collect["channels"].setValue( IECore.StringVectorData( [ 'B', 'G', 'R', 'A' ] ) )
		self.assertEqual( collect["out"]["metadata"].getValue(), IECore.CompoundData( { "test" : "B" } ) )

if __name__ == "__main__":
	unittest.main()
