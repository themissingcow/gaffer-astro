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

import unittest

import GafferTest

import GafferAstro

class FileAlgoTest( GafferTest.TestCase ) :

	def testSplitPathTemplate( self ) :

			self.assertEqual(
				GafferAstro.FileAlgo.splitPathTemplate( "/dir/prefixA-${token}-suffix.${extension}" ),
				( "/dir", "prefixA-${token}-suffix.${extension}" )
			)

			self.assertEqual(
				GafferAstro.FileAlgo.splitPathTemplate( "/dir/${dir}/${token}-suffix.${extension}" ),
				( "/dir", "${dir}/${token}-suffix.${extension}" )
			)

			self.assertEqual(
				GafferAstro.FileAlgo.splitPathTemplate( "/dir/a/${dir}/b/${token}-suffix.${extension}" ),
				( "/dir/a", "${dir}/b/${token}-suffix.${extension}" )
			)

			self.assertEqual(
				GafferAstro.FileAlgo.splitPathTemplate( "${token}-suffix.${extension}" ),
				( "", "${token}-suffix.${extension}" )
			)

			self.assertEqual(
				GafferAstro.FileAlgo.splitPathTemplate( "/dir/a/file.ext" ),
				( "/dir/a/file.ext", "" )
			)

	def testPathsMatchingTemplate( self ) :

		paths = (
			"/dir/prefixA-token1-suffix.a",
			"/dir/prefixA-token2-suffix.b",
			"/dir/prefixB-token1.ext",
			"/dir/prefixB-token2.ext",
			"/dir/d1/token1-suffix.c",
			"/dir/d2/token2-suffix.d",
			"/dir/token1-suffix.a",
		)

		self.assertEqual(
			GafferAstro.FileAlgo.pathsMatchingTemplate( "/dir/prefixA-${token}-suffix.${extension}", paths ),
			[
				( "/dir/prefixA-token1-suffix.a", { "token" : "token1", "extension" : "a" } ),
				( "/dir/prefixA-token2-suffix.b", { "token" : "token2", "extension" : "b" } )
			]
		)

		self.assertEqual(
			GafferAstro.FileAlgo.pathsMatchingTemplate( "/dir/prefixB-${token}.${extension}", paths ),
			[
				( "/dir/prefixB-token1.ext", { "token" : "token1", "extension" : "ext" } ),
				( "/dir/prefixB-token2.ext", { "token" : "token2", "extension" : "ext" } )
			]
		)

		self.assertEqual(
			GafferAstro.FileAlgo.pathsMatchingTemplate( "/dir/${dir}/${token}-suffix.${extension}", paths ),
			[
				( "/dir/d1/token1-suffix.c", { "dir" : "d1", "token" : "token1", "extension" : "c" } ),
				( "/dir/d2/token2-suffix.d", { "dir" : "d2", "token" : "token2", "extension" : "d" } )
			]
		)


if __name__ == "__main__":
	unittest.main()
