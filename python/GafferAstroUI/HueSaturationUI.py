import imath
import IECore
import Gaffer
import GafferAstro

Gaffer.Metadata.registerNode(

	GafferAstro.HueSaturation,

	plugs = {

		"model" : [
			'description', 'The color model in which to process the image.',
			'plugValueWidget:type', 'GafferUI.PresetsPlugValueWidget',
			'preset:HSL', "hsl",
			'preset:HSV', "hsv",
			'layout:section', 'Settings',
		],

		"inModel" : [
			'description', 'Assume incoming colors are in this model.',
			'plugValueWidget:type', 'GafferUI.PresetsPlugValueWidget',
			'preset:RGB', "rgb",
			'preset:HSL', "hsl",
			'preset:HSV', "hsv",
			'layout:section', 'Advanced',
		],

		"outModel" : [
			'description', 'Output colors in this model.',
			'plugValueWidget:type', 'GafferUI.PresetsPlugValueWidget',
			'preset:RGB', "rgb",
			'preset:HSL', "hsl",
			'preset:HSV', "hsv",
			'layout:section', 'Advanced',
		],

		"offsetMode" : [
			'description', 'When enabled, the adjustment will be applied as an offset to saturation and value/lightness rather than as a scale.',
			'layout:section', 'Advanced',
		],

	}
)
