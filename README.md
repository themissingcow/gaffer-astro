# gaffer-astro
Gaffer Astrophotography tools

## Overview

`GafferAstro` is an early-stages project that brings Astrophotography processing tools to [Gaffer](https://www.gafferhq.org). It is very much a work in progress. It aims to take advantage of Gaffer's node-based processing pipeline to automate post-processing of monochrome astrophotography images.

It currently includes:

 - Basic `FITS` and `XISF` read support.
 - `Starnet` and `PixInsight` processing tasks (requires these to be already installed and working on your system).
 - `CollectChannels` and `AssembleChannels` nodes to aid loading of monochrome astro cam images.
 - `Colorise` and `HueSaturation` image nodes.
 - `MultiMonoImageReader`, `MultiGrade` and `MultiStarnet` tools to ease working with narrowband image channels.
 
 It is only currently being developed/tested on Linux, MacOS should also work.
 
 Any questions, or for more information, [drop me a line](mailto:info@tomcowland.com).
