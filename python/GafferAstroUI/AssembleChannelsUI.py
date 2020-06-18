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

Gaffer.Metadata.registerNode(

	GafferAstro.AssembleChannels,

	"description",
	"""
	""",

	plugs = {

		"in" : [
			"nodule:type", "GafferUI::CompoundNodule",
			"noduleLayout:spacing", 2.0,

			"noduleLayout:customGadget:addButton:gadgetType", "GafferAstroUI.AssembleChannelsUI.PlugAdder",

			"plugValueWidget:type", "GafferAstroUI.AssembleChannelsUI._InPlugValueWidget",
		],

		"in.in0" : [

			"deletable", False,

		],

		"in.*" : [

			"nodule:type", "GafferUI::CompoundNodule",
			"plugValueWidget:type", "GafferAstroUI.AssembleChannelsUI._RowPlugValueWidget",
			"deletable", True,

		],

		"in.*.name" : [

			"nodule:type", "",

		],

		"in.*.enabled" : [

			"nodule:type", "",

		],

		"in.*.value" : [

			"plugValueWidget:type", "GafferUI.ConnectionPlugValueWidget",
			"noduleLayout:label", lambda plug : plug.parent()["name"].getValue(),

		],
	}

)


# Equivalent to LayoutPlugValueWidget, but with a little footer with a button
# for adding new inputs.
class _InPlugValueWidget( GafferUI.PlugValueWidget ) :

	def __init__( self, plug, **kw ) :

		column = GafferUI.ListContainer( spacing = 4 )
		GafferUI.PlugValueWidget.__init__( self, column, plug )

		with column :
			self.__plugLayout = GafferUI.PlugLayout( plug )
			self.__addButton = GafferUI.Button( image = "plus.png", hasFrame = False )

		self.__addButton.clickedSignal().connect( Gaffer.WeakMethod( self.__addButtonClicked ), scoped = False )

	def hasLabel( self ) :

		return True

	def setReadOnly( self, readOnly ) :

		GafferUI.PlugValueWidget.setReadOnly( self, readOnly )
		self.__plugLayout.setReadOnly( readOnly )

	def childPlugValueWidget( self, childPlug ) :

		return self.__plugLayout.plugValueWidget( childPlug )

	def _updateFromPlug( self ) :

		self.__addButton.setEnabled( self._editable() )

	def __addButtonClicked( self, button ) :

		with Gaffer.UndoScope( self.getPlug().ancestor( Gaffer.ScriptNode ) ) :
			self.getPlug().resize( len( self.getPlug() ) + 1 )
			parent = self.getPlug().parent()
			if not isinstance( parent, GafferAstro.AssembleChannels ) or self.getPlug() != parent["in"] :
				## See comments in `AssembleChannelsPlugAdder::createConnection()`
				Gaffer.MetadataAlgo.copy( self.getPlug()[-2], self.getPlug()[-1] )

# Widget for an individual input.
class _RowPlugValueWidget( GafferUI.PlugValueWidget ) :

	__labelWidth = 200

	def __init__( self, plug ) :

		column = GafferUI.ListContainer( GafferUI.ListContainer.Orientation.Vertical, spacing = 4 )

		GafferUI.PlugValueWidget.__init__( self, column, plug )

		with column :

			with GafferUI.ListContainer( GafferUI.ListContainer.Orientation.Horizontal, spacing = 4 ) :

				self.__plugValueWidgets = []
				self.__plugValueWidgets.append( GafferUI.StringPlugValueWidget( plug["name"] ) )
				self.__plugValueWidgets.append( GafferUI.BoolPlugValueWidget( plug["enabled"], displayMode = GafferUI.BoolWidget.DisplayMode.Switch ) )
				self.__plugValueWidgets.append( GafferUI.PlugValueWidget.create( plug["value"] ) )

				self.__plugValueWidgets[0].textWidget()._qtWidget().setFixedWidth( self.__labelWidth )

			self.__dragDivider = GafferUI.Divider()

		self._updateFromPlug()

	def setPlug( self, plug ) :

		GafferUI.PlugValueWidget.setPlug( self, plug )

		self.__plugValueWidgets[0].setPlug( plug["name"] )
		self.__plugValueWidgets[1].setPlug( plug["enabled"] )
		self.__plugValueWidgets[2].setPlug( plug["value"] )

	def hasLabel( self ) :

		return True

	def childPlugValueWidget( self, childPlug ) :

		for w in self.__plugValueWidgets :
			if w.getPlug().isSame( childPlug ) :
				return w

		return None

	def setReadOnly( self, readOnly ) :

		if readOnly == self.getReadOnly() :
			return

		GafferUI.PlugValueWidget.setReadOnly( self, readOnly )

		for w in self.__plugValueWidgets :
			w.setReadOnly( readOnly )

	def _updateFromPlug( self ) :

		enabled = False
		with self.getContext() :
			with IECore.IgnoredExceptions( Gaffer.ProcessException ) :
				enabled = self.getPlug()["enabled"].getValue()

		self.__plugValueWidgets[0].setEnabled( enabled )
		self.__plugValueWidgets[2].setEnabled( enabled )
