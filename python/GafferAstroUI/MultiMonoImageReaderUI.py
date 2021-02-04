##########################################################################
#
#  Copyright (c) 2020 Tom Cowland. All rights reserved.
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

import IECore

import Gaffer
import GafferUI
import GafferAstro

import imath

Gaffer.Metadata.registerNode(

	GafferAstro.MultiMonoImageReader,

	"description",
	"""
	""",

	"layout:customWidget:addChannelButton:widgetType", "GafferAstroUI.MultiMonoImageReaderUI._AddFooter",
	"layout:customWidget:addChannelButton:section", "Settings",
	"layout:customWidget:addChannelButton:index", 99,

	plugs = {

		"fileName" : [

			"description",
			"""
			""",

			"plugValueWidget:type", "GafferUI.FileSystemPathPlugValueWidget",
			"path:leaf", True,
			"path:bookmarks", "xisf fits",
			"fileSystemPath:extensions", "xisf fits",
			"fileSystemPath:extensionsLabel", "Show only image files",
			"fileSystemPath:includeSequences", False,
			"layout:index", 0

		],

		"resize" : [
			"layout:index", 1,
			"layout:divider", True
		]

	}

)

class _AddFooter( GafferUI.Widget ) :

	def __init__( self, node, **kw ) :

		row = GafferUI.ListContainer( GafferUI.ListContainer.Orientation.Horizontal )
		GafferUI.Widget.__init__( self, row )

		with row :

			self.__addButton = GafferUI.Button( text = "Add Channel" )
			self.__addButton.clickedSignal().connect( Gaffer.WeakMethod( self.__add ), scoped = False )

			GafferUI.Spacer( imath.V2i( 1 ), imath.V2i( 999999, 1 ), parenting = { "expand" : True } )

		self.__node = node

		Gaffer.Metadata.plugValueChangedSignal( node ).connect(
			Gaffer.WeakMethod( self.__plugMetadataChanged ), scoped = False
		)

	def __plugMetadataChanged( self, plug, key, reason ) :

		if plug.isSame( self.__node["rows"] ) and Gaffer.MetadataAlgo.readOnlyAffectedByChange( plug, plug, key ) :
			self.__addButton.setEnabled( not Gaffer.MetadataAlgo.readOnly( plug ) )

	def __add( self, _ ) :

		with Gaffer.UndoScope( self.__node.ancestor( Gaffer.ScriptNode ) ) :
			row = self.__node["rows"].addRow()
			row["cells"]["filenameToken"].enabledPlug().setValue( False )
			row["cells"]["type"].enabledPlug().setValue( False )
