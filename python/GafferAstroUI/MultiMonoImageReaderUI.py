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

import Gaffer
import GafferUI
import GafferAstro

import IECore

import imath

import functools
import weakref


Gaffer.Metadata.registerNode(

	GafferAstro.MultiMonoImageReader,

	"description",
	"""
	""",

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


def __addRow( weakNode, name = None, filenameToken = None, extension = None ) :

	if weakNode() is None :
		return

	rowsPlug = weakNode()["rows"]

	with Gaffer.UndoScope( rowsPlug.ancestor( Gaffer.ScriptNode ) ) :

		row = rowsPlug.addRow()

		if name :
			row["name"].setValue( name )

		if filenameToken :
			row["cells"]["filenameToken"]["value"].setValue( filenameToken )
		else :
			row["cells"]["filenameToken"].enabledPlug().setValue( False )

		if extension :
			row["cells"]["extension"]["value"].setValue( extension )
		else :
			row["cells"]["extension"].enabledPlug().setValue( False )


def __existingRows( rowsPlug ) :

	rows = []

	defaultToken = rowsPlug.defaultRow()["cells"]["filenameToken"]["value"].getValue()
	defaultExtension = rowsPlug.defaultRow()["cells"]["extension"]["value"].getValue()

	for r in rowsPlug.children() :

		if r.isSame( rowsPlug.defaultRow() ) :
				continue

		token = r["cells"]["filenameToken"]["value"].getValue() if r["cells"]["filenameToken"].enabledPlug().getValue() else defaultToken
		token = token or r["name"]
		extension = r["cells"]["extension"]["value"].getValue() if r["cells"]["extension"].enabledPlug().getValue() else defaultExtension
		rows.append( ( token, extension ) )

	return rows

def __addRowButtonMenuDefinition( menuDefinition, widget ) :

	node = widget.getPlug().node()

	if not isinstance( node, GafferAstro.MultiMonoImageReader ) :
		return

	weakNode = weakref.ref( node )

	menuDefinition.append( "/Empty", { "command" : functools.partial( __addRow, weakNode ) } )

	with widget.ancestor( GafferUI.NodeEditor ).getContext() :
		template = node["fileName"].getValue()
		defaultExtension = node["rows"].defaultRow()["cells"]["extension"]["value"].getValue()
		existingRows = __existingRows( node["rows"] )

	if not template :
		return

	baseDir, _ = GafferAstro.FileAlgo.splitPathTemplate( template )
	matches = GafferAstro.FileAlgo.filesMatchingTemplate( template )

	if not matches :
		return

	menuDefinition.append( "/EmptyDivider", { "divider" : True, "label" : "File Matches" } )

	for m in matches :
		token = m[1].get( "token", None )
		extension = m[1].get( "extension", None )
		menuDefinition.append( "/%s" % ( m[0][len(baseDir):] ), {
			"command" : functools.partial(
				__addRow, weakNode,
				token,
				token,
				extension if extension != defaultExtension else None
			),
			"active" : ( token, extension ) not in existingRows
		} )

GafferUI.SpreadsheetUI.addRowButtonMenuSignal().connect( __addRowButtonMenuDefinition, scoped = False )
