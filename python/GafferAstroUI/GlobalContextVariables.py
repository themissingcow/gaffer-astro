import Gaffer
import GafferUI

import functools


class GlobalContextVariables( GafferUI.Editor ) :

	ShowInEditorMetadataKey = "globalContextVariablesEditor:show"

	def __init__( self, scriptNode, **kw ) :

		scrolledContainer = GafferUI.ScrolledContainer(
			horizontalMode=GafferUI.ScrollMode.Never,
			verticalMode=GafferUI.ScrollMode.Automatic,
			borderWidth = 5
		)
		GafferUI.Editor.__init__( self, scrolledContainer, scriptNode, **kw )

		with scrolledContainer :
			self.__plugList = GafferUI.ListContainer( borderWidth = 6, spacing = 4 )

		variables = scriptNode["variables"]

		variables.childAddedSignal().connect( Gaffer.WeakMethod( self.__updateLayout ), scoped = False )
		variables.childRemovedSignal().connect( Gaffer.WeakMethod( self.__updateLayout ), scoped = False )
		Gaffer.Metadata.plugValueChangedSignal( scriptNode ).connect( Gaffer.WeakMethod( self.__plugMetadataChanged ), scoped = False )

		self.__updateLayout()

	def __repr__( self ) :

		return "GafferAstroUI.GlobalContextVariables( scriptNode )"

	def __updateLayout( self, *unused ) :

		exposedPlugs = filter(
			lambda plug : Gaffer.Metadata.value( plug, self.ShowInEditorMetadataKey, False ),
			self.scriptNode()["variables"]
		)

		exposedPlugs.sort( key = lambda plug : Gaffer.Metadata.value( plug, 'layout:index', 999 ) )

		del self.__plugList[:]
		with self.__plugList :

			if not exposedPlugs :
				GafferUI.Label( text="No exposed Global Context Variables" )
				GafferUI.Label( text="Right-click a variable in Project Settings to show here." )
				return

			for plug in exposedPlugs :
				GafferUI.PlugValueWidget.create( plug )

	def __plugMetadataChanged( self, plug, key, reason ) :

		if not self.scriptNode()["variables"].isAncestorOf( plug ) :
			return

		if not key.startswith( 'globalContextVariablesEditor:' ) and not key.startswith( 'plugValueWidget:' ) :
			return

		self.__updateLayout()

	@classmethod
	def setPlugsShownInMenu( cls, plugs, shownInMenu ) :

		with Gaffer.UndoScope( next(iter(plugs)).ancestor( Gaffer.ScriptNode ) ) :
			for plug in plugs :
				nameValuePlug = plug if isinstance( plug, Gaffer.NameValuePlug ) else plug.ancestor( Gaffer.NameValuePlug )
				Gaffer.Metadata.registerValue( nameValuePlug, cls.ShowInEditorMetadataKey, shownInMenu )

	@classmethod
	def appendPlugValueWidgetMenuDefinitions( cls, menuDefinition, plugValueWidget ) :

		plugs = plugValueWidget.getPlugs()
		if not plugs :
			return

		scriptNode = next(iter(plugs)).ancestor( Gaffer.ScriptNode )
		if not scriptNode :
			return

		findNameValuePlug = lambda p : p if isinstance( p, Gaffer.NameValuePlug ) else p.ancestor( Gaffer.NameValuePlug )

		supportedPlugs = filter( scriptNode["variables"].isAncestorOf, plugs )
		nameValuePlugs = map( findNameValuePlug, supportedPlugs )

		checked = all( [ Gaffer.Metadata.value( p, cls.ShowInEditorMetadataKey, False ) for p in nameValuePlugs ] )

		menuDefinition.append( "/GlobalsPanelDivider", { "divider" : True } )
		menuDefinition.append(
			"/Show in Globals Panel", {
				"active" : len(nameValuePlugs) > 0,
				"checkBox" : nameValuePlugs and checked,
				"command" : functools.partial( cls.setPlugsShownInMenu, nameValuePlugs )
			}
		)

GafferUI.Editor.registerType( "GlobalContextVariables", GlobalContextVariables )
