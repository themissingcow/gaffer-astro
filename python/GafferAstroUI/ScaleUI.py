import itertools

import Gaffer
import GafferAstro
import GafferImage

Gaffer.Metadata.registerNode(

	GafferAstro.Scale,

	plugs = {

		"scale" : [
			'description', 'The scale factor to apply to the input image',
		],

		"filter" : [

			"description",
			"""
			The pixel used when transforming the image. Each
			filter provides different tradeoffs between sharpness and
			the danger of aliasing or ringing.
			""",

			"plugValueWidget:type", "GafferUI.PresetsPlugValueWidget",

			"preset:Default", "",

		] + list( itertools.chain(

			# Disk doesn't make much sense as a resizing filter, and also causes artifacts because
			# its default width is small enough to fall into the gaps between pixels.
			*[ ( "preset:" + x.title(), x ) for x in GafferImage.FilterAlgo.filterNames() if x != "disk" ]

		) ),

	}
)

