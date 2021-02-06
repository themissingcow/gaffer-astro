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

import GafferImage
import GafferAstro
import GafferAstroUI

import GafferUI

# Nodes

nodeMenu = GafferUI.NodeMenu.acquire( application )

nodeMenu.append( "/Image/Color/Colorise", GafferAstro.Colorise )
nodeMenu.append( "/Image/Color/HueSaturation", GafferAstro.HueSaturation )
nodeMenu.append( "/Image/Color/MultiGrade", GafferAstro.MultiGrade )
nodeMenu.append( "/Image/Channels/AssembleChannels", GafferAstro.AssembleChannels )
nodeMenu.append( "/Image/Channels/CollectChannels", GafferAstro.CollectChannels )
nodeMenu.append( "/Image/File/MultiMonoImageReader", GafferAstro.MultiMonoImageReader )
nodeMenu.append( "/Image/File/FITSReader", GafferAstro.FITSReader )
nodeMenu.append( "/Image/File/XISFReader", GafferAstro.XISFReader )
nodeMenu.append( "/Image/Transform/Scale", GafferAstro.Scale )
nodeMenu.append( "/Image/Transform/Trim", GafferAstro.Trim )

nodeMenu.append( "/Astro/ColoriseSHO", GafferAstro.ColoriseSHO )
nodeMenu.append( "/Astro/LoadSHO", GafferAstro.LoadSHO )
nodeMenu.append( "/Astro/MultiStarnet", GafferAstro.MultiStarnet )
nodeMenu.append( "/Astro/Starnet", GafferAstro.Starnet )

# Menu Bar

scriptWindowMenu = GafferUI.ScriptWindow.menuDefinition( application )

def clearImageCaches( menu ) :
	scope = GafferUI.EditMenu.scope( menu )
	for cls in ( GafferImage.ImageReader, GafferAstro.FITSReader ) :
		for node in cls.RecursiveRange( scope.script ) :
			node['refreshCount'].setValue( node['refreshCount'].getValue() + 1 )

scriptWindowMenu.append( "/Tools/Astro/FlushImageCache", { "command" : clearImageCaches } )
