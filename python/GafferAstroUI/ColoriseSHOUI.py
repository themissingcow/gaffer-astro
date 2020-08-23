import imath
import IECore
import Gaffer
import GafferAstro

Gaffer.Metadata.registerNode(

	GafferAstro.ColoriseSHO,

	'uiEditor:emptySections', IECore.StringVectorData( [  ] ),
	'uiEditor:emptySectionIndices', IECore.IntVectorData( [  ] ),
	'layout:section:Settings.Output:summary', '',
	'noduleLayout:customGadget:addButtonTop:visible', False,
	'noduleLayout:customGadget:addButtonBottom:visible', False,
	'noduleLayout:customGadget:addButtonLeft:visible', False,
	'noduleLayout:customGadget:addButtonRight:visible', False,
	plugs = {

		"show" : [
			'description', 'The index of the input which is passed through. A value\nof 0 chooses the first input, 1 the second and so on. Values\nlarger than the number of available inputs wrap back around to\nthe beginning.',
			'nodule:type', '',
			'plugValueWidget:type', 'GafferUI.PresetsPlugValueWidget',
			'preset:Mix', 0,
			'preset:Sii', 1,
			'preset:Ha', 2,
			'preset:Oiii', 3,
			'layout:section', 'Settings',
			'layout:index', 2,
		],

		"sourceSii" : [
			'label', 'Source',
			'preset:Starnet', 'starnet.Sii',
			'preset:Normal', 'input.Sii',
			'layout:section', 'Settings.Sii',
			'layout:index', 3,
		],

		"mapSii" : [
			'nodule:type', '',
			'description', "The values in the selected channel are used to pick a color\nfrom the map. The spline is mapped to the range specified\nin the 'range' plug.",
			'layout:section', 'Settings.Sii',
			'layout:index', 4,
			'label', 'Map',
		],

		"rangeSii" : [
			'nodule:type', '',
			'description', 'Determines the range over which the map is applied. The min value\nwill map to the left of the spline, and the max value to the right.',
			'layout:section', 'Settings.Sii',
			'layout:index', 5,
			'label', 'Map Range',
		],

		"saturationSii" : [
			'nodule:type', '',
			'description', 'Saturation from the v1.2 release of the ASC CDL color correction formula.',
			'layout:section', 'Settings.Sii',
			'layout:index', 6,
			'label', 'Saturation',
		],

		"multiplySii" : [
			'layout:section', 'Settings.Sii',
			'layout:index', 7,
			'label', 'Multiply',
			'nodule:type', '',
		],

		"gammaSii" : [
			'layout:section', 'Settings.Sii',
			'layout:index', 8,
			'label', 'Gamma',
			'nodule:type', '',
		],


		"sourceHa" : [
			'preset:Starnet', 'starnet.Ha',
			'preset:Normal', 'input.Ha',
			'layout:section', 'Settings.Ha',
			'layout:index', 9,
		],

		"mapHa" : [
			'nodule:type', '',
			'description', "The values in the selected channel are used to pick a color\nfrom the map. The spline is mapped to the range specified\nin the 'range' plug.",
			'layout:section', 'Settings.Ha',
			'layout:index', 10,
			'label', 'Map',
		],

		"rangeHa" : [
			'nodule:type', '',
			'description', 'Determines the range over which the map is applied. The min value\nwill map to the left of the spline, and the max value to the right.',
			'layout:section', 'Settings.Ha',
			'layout:index', 11,
			'label', 'Map Range',
		],

		"saturationHa" : [
			'nodule:type', '',
			'description', 'Saturation from the v1.2 release of the ASC CDL color correction formula.',
			'layout:section', 'Settings.Ha',
			'layout:index', 12,
			'label', 'Saturation',
		],

		"multiplyHa" : [
			'layout:section', 'Settings.Ha',
			'layout:index', 13,
			'label', 'Multiply',
			'nodule:type', '',
		],

		"gammaHa" : [
			'layout:section', 'Settings.Ha',
			'layout:index', 14,
			'label', 'Gamma',
			'nodule:type', '',
		],

		"sourceOiii" : [
			'preset:Starnet', 'starnet.Oii',
			'preset:Normal', 'input.Oii',
			'layout:section', 'Settings.Oiii',
			'layout:index', 15,
		],

		"mapOiii" : [
			'nodule:type', '',
			'description', "The values in the selected channel are used to pick a color\nfrom the map. The spline is mapped to the range specified\nin the 'range' plug.",
			'layout:section', 'Settings.Oiii',
			'layout:index', 16,
			'label', 'Map',
		],

		"rangeOiii" : [
			'nodule:type', '',
			'description', 'Determines the range over which the map is applied. The min value\nwill map to the left of the spline, and the max value to the right.',
			'layout:section', 'Settings.Oiii',
			'layout:index', 17,
			'label', 'Map Range',
		],

		"saturationOiii" : [
			'nodule:type', '',
			'description', 'Saturation from the v1.2 release of the ASC CDL color correction formula.',
			'layout:section', 'Settings.Oiii',
			'layout:index', 18,
			'label', 'Saturation',
		],

		"multiplyOiii" : [
			'layout:section', 'Settings.Oiii',
			'layout:index', 19,
			'label', 'Multiply',
			'nodule:type', '',
		],

		"gammaOiii" : [
			'layout:section', 'Settings.Oiii',
			'layout:index', 20,
			'label', 'Gamma',
			'nodule:type', '',
		],


		"saturation" : [
			'nodule:type', '',
			'description', 'Saturation from the v1.2 release of the ASC CDL color correction formula.',
			'layout:section', 'Settings.Output',
			'layout:index', 21,
		],

		"whitePoint" : [
			'layout:section', 'Settings.Output',
			'layout:index', 23,
			'nodule:type', '',
		],

		"blackPoint" : [
			'layout:section', 'Settings.Output',
			'layout:index', 22,
			'nodule:type', '',
		],

		"multiply" : [
			'nodule:type', '',
			'description', 'An additional multiplier on the output values.',
			'layout:section', 'Settings.Output',
			'layout:index', 24,
		],

		"gamma" : [
			'layout:section', 'Settings.Output',
			'layout:index', 25,
			'nodule:type', '',
		],
	}
)
