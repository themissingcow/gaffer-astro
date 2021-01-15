##########################################################################
#
#  Copyright (c) 2011-2013, John Haddon. All rights reserved.
#  Copyright (c) 2011-2013, Image Engine Design Inc. All rights reserved.
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

import weakref

import Gaffer
import GafferUI
import GafferAstroUI

from Qt import QtCore, QtWidgets

import imath

_originalColorWidget = GafferUI.ColorPlugValueWidget

class ExtendedColorPlugValueWidget( GafferUI.PlugValueWidget ) :

	def __init__( self, plugs, **kw ) :

		column = GafferUI.ListContainer( orientation = GafferUI.ListContainer.Orientation.Vertical, spacing = 4 )
		GafferUI.PlugValueWidget.__init__( self, column, plugs, **kw )

		self.__widgets = []

		with column :

			with GafferUI.ListContainer( orientation = GafferUI.ListContainer.Orientation.Horizontal, spacing = 4 ) :

				self.__widgets.append( _originalColorWidget( plugs ) )

				toggle = GafferUI.Button( image="pathListingList.png", hasFrame = False )
				toggle.clickedSignal().connect( Gaffer.WeakMethod( self.__toggleSliders ), scoped = False )

			self.__tabs = GafferUI.TabbedContainer()

		self.__tabs._qtWidget().setSizePolicy( QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Maximum )

		rgb = GafferAstroUI.RGBColorSliderPlugValueWidget( plugs )
		self.__widgets.append( rgb )
		self.__tabs.append( rgb, "RGB" )

		HSL = GafferAstroUI.HSLColorSliderPlugValueWidget( plugs )
		self.__widgets.append( HSL )
		self.__tabs.append( HSL, "HSL" )

		hsv = GafferAstroUI.HSVColorSliderPlugValueWidget( plugs )
		self.__widgets.append( hsv )
		self.__tabs.append( hsv, "HSV" )

		self.__tabs.setVisible( False )

	def setPlugs( self, plugs ) :

		for w in self.__widgets :
			w.setPlugs( plugs )

	def _updateFromPlugs( self ) :
		pass

	def __toggleSliders( self, *unused ) :

		self.__tabs.setVisible( not self.__tabs.getVisible() )


GafferUI.PlugValueWidget.registerType( Gaffer.Color3fPlug, ExtendedColorPlugValueWidget )
GafferUI.PlugValueWidget.registerType( Gaffer.Color4fPlug, ExtendedColorPlugValueWidget )
