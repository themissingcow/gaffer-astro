##########################################################################
#
#  Copyright (c) 2013, John Haddon. All rights reserved.
#  Copyright (c) 2013, Image Engine Design Inc. All rights reserved.
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
import imath

import Gaffer
import GafferUI
import GafferAstroUI


__all__ = [ 'ColorSliderPlugValueWidget', 'RGBColorSliderPlugValueWidget', 'HSVColorSliderPlugValueWidget' ]


class ColorSliderPlugValueWidget( GafferUI.PlugValueWidget ) :

	def __init__( self, plugs, components="rgbahsv", **kw ) :

		self.__sliders = GafferAstroUI.ColorChooser( components = components, showSwatch = False )
		GafferUI.PlugValueWidget.__init__( self, self.__sliders, plugs, **kw )

		# we use these to decide which actions to merge into a single undo
		self.__lastChangedReason = None
		self.__mergeGroupId = 0

		self._qtWidget().setFixedHeight( 60 )

		self.__colorChangedConnection = self.__sliders.colorChangedSignal().connect( Gaffer.WeakMethod( self.__colorChanged ) )

		self._updateFromPlug()

	def setHighlighted( self, highlighted ) :

		GafferUI.PlugValueWidget.setHighlighted( self, highlighted )

		self.__sliders.setHighlighted( highlighted )

	# We currently only support a single plug, we use the legacy method to make
	# auditing which widgets support multiple plugs easier later on.
	def _updateFromPlug( self ) :

		color = imath.Color4f( 0 )

		plug = self.getPlug()
		if plug is not None :
			with self.getContext() :
				color = plug.getValue()

		with Gaffer.BlockedConnection( self.__colorChangedConnection ) :
			self.__sliders.setColor( color )

	def __colorChanged( self, colorChooser, reason ) :

		if self._editable( canEditAnimation = True ) :

			if not self.__sliders.changesShouldBeMerged( self.__lastChangedReason, reason ) :
				self.__mergeGroupId += 1
			self.__lastChangedReason = reason

			self.__setPlugValues( mergeGroup = "ColorSliderPlugValueWidget%d%d" % ( id( self, ), self.__mergeGroupId ) )

		return False

	def __setPlugValues( self, mergeGroup="" ) :

		with Gaffer.UndoScope( next( iter( self.getPlugs() ) ).ancestor( Gaffer.ScriptNode ), mergeGroup=mergeGroup ) :

			with Gaffer.BlockedConnection( self._plugConnections() ) :

				for plug in self.getPlugs() :

					if Gaffer.Animation.isAnimated( plug ) :
						curve = Gaffer.Animation.acquire( plug )
						if self.__numericWidget.getText() != self.__numericWidget.valueToString( curve.evaluate( self.getContext().getTime() ) ) :
							curve.addKey(
								Gaffer.Animation.Key(
									self.getContext().getTime(),
									self.__numericWidget.getValue(),
									Gaffer.Animation.Type.Linear
								)
							)
					else :
						try :
							plug.setValue( self.__sliders.getColor() )
						except Exception as e:
							print( e )
							pass

		# We always need to update the UI from the plugs after trying to set them,
		# because the plugs might clamp the value to something else. Furthermore
		# they might not even emit `plugDirtiedSignal() if they happens to clamp to the same
		# value as before. We block calls to `_updateFromPlugs()` while setting
		# the value to avoid having to do the work twice if `plugDirtiedSignal()` _is_ emitted.
		self._updateFromPlugs()


class RGBColorSliderPlugValueWidget( ColorSliderPlugValueWidget ) :
	def __init__( self, plugs, **kw ) :
		ColorSliderPlugValueWidget.__init__( self, plugs, components = "rgba", **kw )

class HSVColorSliderPlugValueWidget( ColorSliderPlugValueWidget ) :
	def __init__( self, plugs, **kw ) :
		ColorSliderPlugValueWidget.__init__( self, plugs, components = "hsva", **kw )


for cls in ( ColorSliderPlugValueWidget, RGBColorSliderPlugValueWidget, HSVColorSliderPlugValueWidget ) :
	GafferUI.PlugValueWidget.registerType( Gaffer.Color3fPlug, cls )
	GafferUI.PlugValueWidget.registerType( Gaffer.Color4fPlug, cls )
