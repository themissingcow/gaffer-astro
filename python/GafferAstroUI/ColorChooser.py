##########################################################################
#
#  Copyright (c) 2011-2012, John Haddon. All rights reserved.
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

import imath
import math
import sys

import IECore

import Gaffer
import GafferUI

from Qt import QtGui

def rgb2hsl( color ) :

	r = color[0]
	g = color[1]
	b = color[2]

	Xmax = max( r, max( g, b ) )
	Xmin = min( r, min( g, b ) )

	C = Xmax - Xmin

	L = ( Xmax + Xmin ) / 2.0

	if C == 0 :
		H = 0
	elif Xmax == r :
		H = ( g - b ) / C
	elif Xmax == g :
		H = 2.0 + ( ( b - r ) / C )
	else :
		H = 4.0 + ( ( r - g ) / C )
	H /= 6.0

	if L <= 0.0 or L >= 1.0 :
		S = 0
	else :
		S = ( Xmax - L ) / min( L, 1 - L )

	out = type( color )( color )
	out[0] = H
	out[1] = S
	out[2] = L
	return out

def hsl2rgb( color ) :

	H = color[0]
	S = color[1]
	L = color[2]

	H *= 6.0
	C = ( 1.0 - abs( 2.0 * L - 1.0 ) ) * S
	X = C * ( 1 - abs( ( H % 2.0 ) - 1.0 ) )

	i = math.floor( H )
	if i == 0 :
		R, G, B = C, X, 0
	elif i == 1 :
		R, G, B = X, C, 0
	elif i == 2 :
		R, G, B = 0, C, X
	elif i == 3 :
		R, G, B = 0, X, C
	elif i == 4 :
		R, G, B = X, 0, C
	else :
		R, G, B = C, 0, X

	m = L - ( C / 2.0 )

	out = type( color )( color )
	out[0] = R + m
	out[1] = G + m
	out[2] = B + m
	return out

# A custom slider for drawing the backgrounds.
class _ComponentSlider( GafferUI.NumericSlider ) :

	def __init__( self, color, component, useDisplayTransform = True, **kw ) :

		min = hardMin = 0
		max = hardMax = 1

		if component in ( "r", "g", "b", "v" ) :
			hardMax = sys.float_info.max

		GafferUI.NumericSlider.__init__( self, 0.0, min, max, hardMin, hardMax, **kw )

		self._qtWidget().setFixedHeight( 20 )

		self.color = color
		self.component = component
		self.__useDisplayTransform = useDisplayTransform

		if self.__useDisplayTransform :
			GafferUI.DisplayTransform.changedSignal().connect( Gaffer.WeakMethod( self.__displayTransformChanged ), scoped = False )

	def setColor( self, color ) :

		self.color = color
		self._qtWidget().update()

	def getColor( self ) :

		return self.color

	def _drawBackground( self, painter ) :

		size = self.size()
		grad = QtGui.QLinearGradient( 0, 0, size.x, 0 )

		displayTransform = GafferUI.DisplayTransform.get() if self.__useDisplayTransform else lambda x : x

		if self.component == "a" :
			c1 = imath.Color3f( 0 )
			c2 = imath.Color3f( 1 )
		else :
			c1 = imath.Color3f( self.color[0], self.color[1], self.color[2] )
			c2 = imath.Color3f( self.color[0], self.color[1], self.color[2] )
			if self.component in "hsv" :
				c1 = c1.rgb2hsv()
				c2 = c2.rgb2hsv()
			elif self.component in "HSL" :
				c1 = rgb2hsl( c1 )
				c2 = rgb2hsl( c2 )
			a = { "r" : 0, "g" : 1, "b" : 2, "h" : 0, "s" : 1, "v": 2, "H" : 0, "S" : 1, "L" : 2 }[self.component]
			c1[a] = 0
			c2[a] = 1

		numStops = max( 2, size.x // 2 )
		for i in range( 0, numStops ) :

			t = float( i ) / (numStops-1)
			c = c1 + (c2-c1) * t
			if self.component in "hsv" :
				c = c.hsv2rgb()
			elif self.component in "HSL" :
				c = hsl2rgb( c )

			grad.setColorAt( t, self._qtColor( displayTransform( c ) ) )

		brush = QtGui.QBrush( grad )
		painter.fillRect( 0, 0, size.x, size.y, brush )

	def __displayTransformChanged( self ) :

		self._qtWidget().update()

class ColorChooser( GafferUI.Widget ) :

	ColorChangedReason = IECore.Enum.create( "Invalid", "SetColor", "Reset" )

	def __init__( self, color=imath.Color3f( 1 ), useDisplayTransform = True, components="rgb-HSL-a", showSwatch=True, **kw ) :

		self.__column = GafferUI.ListContainer( GafferUI.ListContainer.Orientation.Vertical, spacing = 4 )

		GafferUI.Widget.__init__( self, self.__column, **kw )

		self.__color = color
		self.__defaultColor = color

		self.__sliders = {}
		self.__numericWidgets = {}
		self.__componentValueChangedConnections = []

		with self.__column :

			# sliders and numeric widgets
			for component in components :

				if component == "-" :
					GafferUI.Divider()
					continue

				with GafferUI.ListContainer( GafferUI.ListContainer.Orientation.Horizontal, spacing = 4 ) :

					numericWidget = GafferUI.NumericWidget( 0.0 )
					numericWidget.setFixedCharacterWidth( 6 )
					numericWidget.component = component
					self.__numericWidgets[component] = numericWidget

					slider = _ComponentSlider( color, component, useDisplayTransform = useDisplayTransform )
					self.__sliders[component] = slider

					self.__componentValueChangedConnections.append(
						numericWidget.valueChangedSignal().connect( Gaffer.WeakMethod( self.__componentValueChanged ), scoped = False )
					)

					self.__componentValueChangedConnections.append(
						slider.valueChangedSignal().connect( Gaffer.WeakMethod( self.__componentValueChanged ), scoped = False )
					)

			if showSwatch :

				# initial and current colour swatches
				with GafferUI.ListContainer( GafferUI.ListContainer.Orientation.Horizontal, parenting = { "expand" : True } ) :

					self.__initialColorSwatch = GafferUI.ColorSwatch( color, useDisplayTransform = useDisplayTransform, parenting = { "expand" : True } )
					self.__initialColorSwatch.buttonPressSignal().connect( Gaffer.WeakMethod( self.__initialColorPress ), scoped = False )

					GafferUI.Spacer( imath.V2i( 4, 40 ) )

					self.__colorSwatch = GafferUI.ColorSwatch( color, useDisplayTransform = useDisplayTransform, parenting = { "expand" : True } )

			else :

				self.__initialColorSwatch = None
				self.__colorSwatch = None


		self.__colorChangedSignal = Gaffer.Signal2()

		self.__updateUIFromColor()

	## The default color starts as the value passed when creating the dialogue.
	# It is represented with a swatch which when clicked will revert the current
	# selection back to the original.
	def setInitialColor( self, color ) :

		if self.__initialColorSwatch is not None :
			self.__initialColorSwatch.setColor( color )

	def getInitialColor( self ) :

		if self.__initialColorSwatch is not None :
			return self.__initialColorSwatch.getColor()

	def setColor( self, color ) :

		self.__setColorInternal( color, self.ColorChangedReason.SetColor )

	def getColor( self ) :

		return self.__color

	## A signal emitted whenever the color is changed. Slots should
	# have the signature slot( ColorChooser, reason ). The reason
	# argument may be passed either a ColorChooser.ColorChangedReason,
	# a Slider.PositionChangedReason or a NumericWidget.ValueChangedReason
	# to describe the reason for the change.
	def colorChangedSignal( self ) :

		return self.__colorChangedSignal

	## Returns True if a user would expect the specified sequence
	# of changes to be merged into a single undoable event.
	@classmethod
	def changesShouldBeMerged( cls, firstReason, secondReason ) :

		if isinstance( firstReason, GafferUI.Slider.PositionChangedReason ) :
			return GafferUI.Slider.changesShouldBeMerged( firstReason, secondReason )
		elif isinstance( firstReason, GafferUI.NumericWidget.ValueChangedReason ) :
			return GafferUI.NumericWidget.changesShouldBeMerged( firstReason, secondReason )

		return False

	def __initialColorPress( self, button, event ) :

		self.__setColorInternal( self.getInitialColor(), self.ColorChangedReason.Reset )

	def __componentValueChanged( self, componentWidget, reason ) :

		## \todo We're doing the clamping here because NumericWidget
		# doesn't provide the capability itself. Add the functionality
		# into the NumericWidget and remove this code.
		componentValue = componentWidget.getValue()
		componentValue = max( componentValue, 0 )
		if componentWidget.component in "ahsHS" :
			componentValue = min( componentValue, 1 )

		newColor = self.__color.__class__( self.__color )
		if componentWidget.component in ( "r", "g", "b", "a" ) :
			a = { "r" : 0, "g" : 1, "b" : 2, "a" : 3 }[componentWidget.component]
			newColor[a] = componentValue
		else :
			newColor = newColor.rgb2hsv() if componentWidget.component in "hsv" else rgb2hsl( newColor )
			a = { "h" : 0, "s" : 1, "v" : 2, "H" : 0, "S" : 1, "L" : 2 }[componentWidget.component]
			newColor[a] = componentValue
			newColor = newColor.hsv2rgb() if componentWidget.component in "hsv" else hsl2rgb( newColor )

		self.__setColorInternal( newColor, reason )

	def __setColorInternal( self, color, reason ) :

		dragBeginOrEnd = reason in (
			GafferUI.NumericSlider.PositionChangedReason.DragBegin,
			GafferUI.NumericSlider.PositionChangedReason.DragEnd,
			GafferUI.NumericWidget.ValueChangedReason.DragBegin,
			GafferUI.NumericWidget.ValueChangedReason.DragEnd,
		)
		if color != self.__color or dragBeginOrEnd :
			# we never optimise away drag begin or end, because it's important
			# that they emit in pairs.
			self.__color = color
			if self.__colorSwatch is not None :
				self.__colorSwatch.setColor( color )
			self.__colorChangedSignal( self, reason )

		## \todo This is outside the conditional because the clamping we do
		# in __componentValueChanged means the color value may not correspond
		# to the value in the ui, even if it hasn't actually changed. Move this
		# back inside the conditional when we get the clamping performed internally
		# in NumericWidget.
		self.__updateUIFromColor()

	def __updateUIFromColor( self ) :

		with Gaffer.BlockedConnection( self.__componentValueChangedConnections ) :

			numSliders = len( self.__sliders )

			c = self.getColor()

			for slider in self.__sliders.values() :
				slider.setColor( c )

			for component, index in ( ( "r", 0 ), ( "g", 1 ), ( "b", 2 ) ) :
				if component in self.__sliders :
					self.__sliders[component].setValue( c[index] )
					self.__numericWidgets[component].setValue( c[index] )

			if "a" in self.__sliders :
				if c.dimensions() == 4 :
					self.__sliders["a"].setValue( c[3] )
					self.__numericWidgets["a"].setValue( c[3] )
					self.__sliders["a"].parent().setVisible( True )
				else :
					self.__sliders["a"].parent().setVisible( False )
					numSliders -= 1

			cv = c.rgb2hsv()
			for component, index in ( ( "h", 0 ), ( "s", 1 ), ( "v", 2 ) ) :
				if component in self.__sliders :
					self.__sliders[component].setValue( cv[index] )
					self.__numericWidgets[component].setValue( cv[index] )
			cl = rgb2hsl( c )
			for component, index in ( ( "H", 0 ), ( "S", 1 ), ( "L", 2 ) ) :
				if component in self.__sliders :
					self.__sliders[component].setValue( cl[index] )
					self.__numericWidgets[component].setValue( cl[index] )

