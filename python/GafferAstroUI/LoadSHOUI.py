import imath
import IECore
import Gaffer
import GafferAstro

Gaffer.Metadata.registerNode(

	GafferAstro.LoadSHO,

	plugs = {

		"fileName" : [

			'layout:section', 'Settings',
			'layout:index', 1,

			"plugValueWidget:type", "GafferUI.FileSystemPathPlugValueWidget",
			"path:leaf", True,
			"path:bookmarks", "fits",
			"fileSystemPath:extensions", "fits",
			"fileSystemPath:extensionsLabel", "Show only image files",
			"fileSystemPath:includeSequences", False,

		],

		"resize" : [
			'nodule:type', '',
			'layout:section', 'Settings',
			'layout:index', 2,
		],

		"enabledSii" : [
			'layout:section', 'Settings.Sii',
			'layout:index', 3,
			'label', 'Enabled',
		],

		"blackPointSii" : [
			'layout:section', 'Settings.Sii',
			'layout:index', 4,
			'label', 'Black Point',
		],

		"whitePointSii" : [
			'layout:section', 'Settings.Sii',
			'layout:index', 5,
			'label', 'White Point',
		],

		"gammaSii" : [
			'layout:section', 'Settings.Sii',
			'layout:index', 6,
			'label', 'Gamma',
		],

		"enabledHa" : [
			'layout:section', 'Settings.Ha',
			'layout:index', 7,
			'label', 'Enabled',
		],

		"blackPointHa" : [
			'layout:section', 'Settings.Ha',
			'layout:index', 8,
			'label', 'Black Point',
		],

		"whitePointHa" : [
			'layout:section', 'Settings.Ha',
			'layout:index', 9,
			'label', 'White Point',
		],

		"gammaHa" : [
			'layout:section', 'Settings.Ha',
			'layout:index', 10,
			'label', 'Gamma',
		],

		"enabledOiii" : [
			'layout:section', 'Settings.Oiii',
			'layout:index', 11,
			'label', 'Enabled',
		],

		"blackPointOiii" : [
			'layout:section', 'Settings.Oiii',
			'layout:index', 12,
			'label', 'Black Point',
		],

		"whitePointOiii" : [
			'layout:section', 'Settings.Oiii',
			'layout:index', 13,
			'label', 'White Point',
		],

		"gammaOiii" : [
			'layout:section', 'Settings.Oiii',
			'layout:index', 14,
			'label', 'Gamma',
		],

		"channelNameSii" : [
			'layout:section', 'Settings.Channel Names',
			'layout:index', 15,
			'label', 'Sii',
		],

		"channelNameHa" : [
			'layout:section', 'Settings.Channel Names',
			'layout:index', 16,
			'label', 'Ha',
		],

		"channelNameOiii" : [
			'layout:section', 'Settings.Channel Names',
			'layout:index', 17,
			'label', 'Oiii',
		],

	}


)
