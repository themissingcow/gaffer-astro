##########################################################################
#
#  Copyright (c) 2011-2014, John Haddon. All rights reserved.
#  Copyright (c) 2011-2014, Image Engine Design Inc. All rights reserved.
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

import os
import re
import sys
import glob
import shutil
import fnmatch
import functools
import platform
import py_compile
import subprocess

###############################################################################################
# Version
###############################################################################################

majorVersion = 1 # backwards-incompatible changes
minorVersion = 0 # new backwards-compatible features
patchVersion = 0 # bug fixes

###############################################################################################
# Command line options
###############################################################################################

optionsFile = None

if "OPTIONS" in ARGUMENTS :
	optionsFile = ARGUMENTS["OPTIONS"]

options = Variables( optionsFile, ARGUMENTS )

options.Add(
	"CXX",
	"The C++ compiler.",
	"clang++" if sys.platform == "darwin" else "g++",
)

options.Add(
	"CXXFLAGS",
	"The extra flags to pass to the C++ compiler during compilation.",
	[ "-pipe", "-Wall" ]
)

options.Add(
	EnumVariable(
		"BUILD_TYPE",
		"Optimisation and debug symbol configuration",
		"RELEASE",
		allowed_values = ('RELEASE', 'DEBUG', 'RELWITHDEBINFO')
	)
)

options.Add(
	"CXXSTD",
	"The C++ standard to build against. A minimum of C++11 is required.",
	"c++11",
)

options.Add(
	BoolVariable( "WARNINGS_AS_ERRORS", "Treat compiler and linker warnings as errors.", False )
)

options.Add(
	"LINKFLAGS",
	"The extra flags to pass to the C++ linker during compilation.",
	""
)

options.Add(
	BoolVariable( "ASAN", "Enable ASan when compiling with clang++", False)
)

options.Add(
	"BUILD_DIR",
	"The destination directory in which the build will be made.",
	"./build/${PLATFORM}/GafferAstro/${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}",
)

options.Add(
	"BUILD_CACHEDIR",
	"Specify a directory for SCons to cache build results in. This allows the sharing of build results"
	"among multiple developers and can significantly reduce build times, particularly when switching"
	"between multiple compilers and build options.",
	""
)

options.Add(
	"PACKAGE_FILE",
	"The file in which the final module will be created by the package target.",
	"./GafferAstro-${MAJOR_VERSION}.${MINOR_VERSION}.${PATCH_VERSION}-${PLATFORM}.tar.gz",
)

options.Add(
	"GAFFER_ROOT",
	"The directory in which Gaffer is installed"
	".../gaffer-build",
)

options.Add(
	"LOCATE_DEPENDENCY_CPPPATH",
	"Locations on which to search for include files "
	"for the dependencies. These are included with -I.",
	[],
)

options.Add(
	"LOCATE_DEPENDENCY_SYSTEMPATH",
	"Locations on which to search for include files "
	"for the dependencies. These are included with -isystem.",
	[],
)

options.Add(
	"LOCATE_DEPENDENCY_LIBPATH",
	"The locations on which to search for libraries for "
	"the dependencies.",
	"",
)

options.Add(
	"LOCATE_DEPENDENCY_PYTHONPATH",
	"The locations on which to search for python modules for "
	"the dependencies.",
	"",
)

options.Add(
	"LOCATE_DEPENDENCY_RESOURCESPATH",
	"The path to the resources provided by the gafferResources project. "
	"If you follow the build instructions using the precompiled "
	"dependencies then you will not need this option.",
	"",
)

options.Add(
	"LOCATE_DEPENDENCY_APPLESEED_SEARCHPATH",
	"The paths in which Appleseed resources are installed.",
	"",
)

options.Add(
	"OPENEXR_LIB_SUFFIX",
	"The suffix used when locating the OpenEXR libraries.",
	"",
)

options.Add(
	"BOOST_LIB_SUFFIX",
	"The suffix used when locating the boost libraries.",
	"",
)

options.Add(
	"GLEW_LIB_SUFFIX",
	"The suffix used when locating the glew libraries.",
	"",
)

options.Add(
	"CORTEX_LIB_SUFFIX",
	"The suffix used when locating the cortex libraries.",
	"",
)

options.Add(
	"CORTEX_PYTHON_LIB_SUFFIX",
	"The suffix used when locating the IECorePython library.",
	"",
)

options.Add(
	"OIIO_LIB_SUFFIX",
	"The suffix used when locating the OpenImageIO libraries.",
	"",
)

options.Add(
	"OCIO_LIB_SUFFIX",
	"The suffix used when locating the OpenColorIO libraries.",
	"",
)

options.Add(
	"OSL_LIB_SUFFIX",
	"The suffix used when locating the OpenShadingLanguage libraries.",
	"",
)

options.Add(
	"ENV_VARS_TO_IMPORT",
	"By default SCons ignores the environment it is run in, to avoid it contaminating the "
	"build process. This can be problematic if some of the environment is critical for "
	"running the applications used during the build. This space separated list of environment "
	"variables is imported to help overcome these problems.",
	"",
)

options.Add(
	"INKSCAPE",
	"Where to find the inkscape binary",
	"inkscape",
)

###############################################################################################
# Basic environment object. All the other environments will be based on this.
###############################################################################################

env = Environment(

	options = options,

	MAJOR_VERSION = str( majorVersion ),
	MINOR_VERSION = str( minorVersion ),
	PATCH_VERSION = str( patchVersion ),

	CPPDEFINES = [
		( "GAFFERASTRO_MAJOR_VERSION", "$MAJOR_VERSION" ),
		( "GAFFERASTRO_MINOR_VERSION", "$MINOR_VERSION" ),
		( "GAFFERASTRO_PATCH_VERSION", "$PATCH_VERSION" ),
	],

	CPPPATH = [
		"include",
		"$LOCATE_DEPENDENCY_CPPPATH",
	],

	CPPFLAGS = [
		"-DBOOST_FILESYSTEM_VERSION=3",
		"-DBOOST_FILESYSTEM_NO_DEPRECATED",
		"-DBOOST_SIGNALS_NO_DEPRECATION_WARNING",
	],

	LIBPATH = [
		"./lib",
		"$GAFFER_ROOT/lib",
		"$LOCATE_DEPENDENCY_LIBPATH",
	],

	FRAMEWORKPATH = "$GAFFER_ROOT/lib",
)

# include 3rd party headers with -isystem rather than -I.
# this should turn off warnings from those headers, allowing us to
# build with -Werror. there are so many warnings from boost
# in particular that this would be otherwise impossible.
for path in [
		"$GAFFER_ROOT/include",
		"$GAFFER_ROOT/include/python$PYTHON_VERSION",
		"$GAFFER_ROOT/include/OpenEXR",
		"$GAFFER_ROOT/include/GL",
	] + env["LOCATE_DEPENDENCY_SYSTEMPATH"] :

	env.Append(
		CXXFLAGS = [ "-isystem", path ]
	)

if "clang++" in os.path.basename( env["CXX"] ):
	env.Append(
		CXXFLAGS = [ "-Wno-unused-local-typedef" ]
	)

env["BUILD_DIR"] = os.path.abspath( env["BUILD_DIR"] )

# DISPLAY and HOME are essential for running gaffer when generating
# the documentation. TERM is needed to get coloured output from the
# compiler.
for e in env["ENV_VARS_TO_IMPORT"].split() + [ "DISPLAY", "HOME", "TERM" ] :
	if e in os.environ :
		env["ENV"][e] = os.environ[e]

if env["PLATFORM"] == "darwin" :

	env.Append( CXXFLAGS = [ "-D__USE_ISOC99" ] )
	env["GAFFER_PLATFORM"] = "macos"

	macosVersion = [ int( v ) for v in platform.mac_ver()[0].split( "." ) ]
	if macosVersion[0] == 10 and macosVersion[1] > 7 :
		# Fix problems with Boost 1.55 and recent versions of Clang.
		env.Append( CXXFLAGS = [ "-DBOOST_HAS_INT128", "-Wno-unused-local-typedef" ] )

elif env["PLATFORM"] == "posix" :

	if "g++" in os.path.basename( env["CXX"] ) :

		gccVersion = subprocess.check_output( [ env["CXX"], "-dumpversion" ], env=env["ENV"] ).decode().strip()
		gccVersion = [ int( v ) for v in gccVersion.split( "." ) ]

		# GCC 4.1.2 in conjunction with boost::flat_map produces crashes when
		# using the -fstrict-aliasing optimisation (which defaults to on with -O2),
		# so we turn the optimisation off here, only for that specific GCC version.
		if gccVersion == [ 4, 1, 2 ] :
			env.Append( CXXFLAGS = [ "-fno-strict-aliasing" ] )

		# GCC emits spurious "assuming signed overflow does not occur"
		# warnings, typically triggered by the comparisons in Box3f::isEmpty().
		# Downgrade these back to warning status.
		if gccVersion >= [ 4, 2 ] :
			env.Append( CXXFLAGS = [ "-Wno-error=strict-overflow" ] )

		if gccVersion >= [ 5, 1 ] :
			env.Append( CXXFLAGS = [ "-D_GLIBCXX_USE_CXX11_ABI=0" ] )

	env["GAFFER_PLATFORM"] = "linux"

env.Append( CXXFLAGS = [ "-std=$CXXSTD", "-fvisibility=hidden" ] )

if env["BUILD_TYPE"] == "DEBUG" :
	env.Append( CXXFLAGS = ["-g", "-O0", "-DTBB_USE_DEBUG=1"] )
elif env["BUILD_TYPE"] == "RELEASE" :
	env.Append( CXXFLAGS = ["-DNDEBUG", "-DBOOST_DISABLE_ASSERTS", "-O3"] )
elif env["BUILD_TYPE"] == "RELWITHDEBINFO" :
	env.Append( CXXFLAGS = ["-DNDEBUG", "-DBOOST_DISABLE_ASSERTS", "-O3", "-g", "-fno-omit-frame-pointer"] )

if env["WARNINGS_AS_ERRORS"] :
	env.Append(
		CXXFLAGS = [ "-Werror" ],
		SHLINKFLAGS = [ "-Wl,-fatal_warnings" ],
	)

if env["BUILD_CACHEDIR"] != "" :
	CacheDir( env["BUILD_CACHEDIR"] )

###############################################################################################
# Check for inkscape and sphinx
###############################################################################################

def findOnPath( file, path ) :

	if os.path.isabs( file ) :
		return file if os.path.exists( file ) else None
	else :
		if isinstance( path, str ) :
			path = path.split( os.pathsep )
		for p in path :
			f = os.path.join( p, file )
			if os.path.exists( f ) :
				return f

	return None

def checkInkscape(context):
	context.Message('Checking for Inkscape... ')
	result = bool( findOnPath( context.sconf.env['INKSCAPE'], os.environ["PATH"] ) )
	context.Result(result)
	return result

def checkQtVersion( context ) :

	context.Message( "Checking for Qt..." )

	program = """
	#include <iostream>
	#include "QtCore/qconfig.h"

	int main()
	{
#ifdef QT_VERSION_MAJOR
		std::cout << QT_VERSION_MAJOR;
#else
		std::cout << 4;
#endif
		return 0;
	}
	"""

	result = context.TryRun( program, ".cpp" )
	if result[0] :
		context.sconf.env["QT_VERSION"] = result[1]

	context.Result( result[0] )
	return result[0]

conf = Configure(
	env,
	custom_tests = {
		"checkInkscape" : checkInkscape,
		"checkQtVersion" : checkQtVersion,
	}
)

haveInkscape = conf.checkInkscape()
if not haveInkscape and env["INKSCAPE"] != "disableGraphics" :
	sys.stderr.write( "ERROR : Inkscape not found. Check INKSCAPE build variable.\n" )
	Exit( 1 )

if not conf.checkQtVersion() :
	sys.stderr.write( "Qt not found\n" )
	Exit( 1 )

if env["ASAN"] :
	env.Append(
		CXXFLAGS = [ "-fsanitize=address" ],
		LINKFLAGS = [ "-fsanitize=address" ],
	)
	if "clang++" in os.path.basename( env["CXX"] ) :
		env.Append(
			CXXFLAGS = [ "-shared-libasan" ],
			LINKFLAGS = [ "-shared-libasan" ],
		)

###############################################################################################
# An environment for running commands with access to the applications we've built
###############################################################################################

def split( stringOrList, separator = ":" ) :

	if isinstance( stringOrList, list ) :
		return stringOrList
	else :
		return stringOrList.split( separator )

commandEnv = env.Clone()
commandEnv["ENV"]["PATH"] = commandEnv.subst( "$BUILD_DIR/bin:" ) + commandEnv["ENV"]["PATH"]

if commandEnv["PLATFORM"]=="darwin" :
	commandEnv["ENV"]["DYLD_LIBRARY_PATH"] = commandEnv.subst( ":".join( [ "$BUILD_DIR/lib" ] + split( commandEnv["LOCATE_DEPENDENCY_LIBPATH"] ) ) )
else :
	commandEnv["ENV"]["LD_LIBRARY_PATH"] = commandEnv.subst( ":".join( [ "$BUILD_DIR/lib" ] + split( commandEnv["LOCATE_DEPENDENCY_LIBPATH"] ) ) )

commandEnv["ENV"]["PYTHONPATH"] = commandEnv.subst( ":".join( split( commandEnv["LOCATE_DEPENDENCY_PYTHONPATH"] ) ) )

# SIP on MacOS prevents DYLD_LIBRARY_PATH being passed down so we make sure
# we also pass through to gaffer the other base vars it uses to populate paths
# for third-party support.
for v in ( 'GAFFER_ROOT', ) :
	commandEnv["ENV"][ v ] = commandEnv[ v ]

def runCommand( command ) :

	command = commandEnv.subst( command )
	sys.stderr.write( command + "\n" )
	subprocess.check_call( command, shell=True, env=commandEnv["ENV"] )

###############################################################################################
# Determine python version
###############################################################################################

pythonVersion = subprocess.Popen( [ "python", "--version" ], env=commandEnv["ENV"], stderr=subprocess.PIPE ).stderr.read().decode().strip()
pythonVersion = pythonVersion.split()[1].rpartition( "." )[0]

env["PYTHON_VERSION"] = pythonVersion

###############################################################################################
# The basic environment for building libraries
###############################################################################################

baseLibEnv = env.Clone()

baseLibEnv.Append(

	LIBS = [
		"boost_signals$BOOST_LIB_SUFFIX",
		"boost_iostreams$BOOST_LIB_SUFFIX",
		"boost_filesystem$BOOST_LIB_SUFFIX",
		"boost_date_time$BOOST_LIB_SUFFIX",
		"boost_thread$BOOST_LIB_SUFFIX",
		"boost_wave$BOOST_LIB_SUFFIX",
		"boost_regex$BOOST_LIB_SUFFIX",
		"boost_system$BOOST_LIB_SUFFIX",
		"boost_chrono$BOOST_LIB_SUFFIX",
		"tbb",
		"Imath$OPENEXR_LIB_SUFFIX",
		"IlmImf$OPENEXR_LIB_SUFFIX",
		"IECore$CORTEX_LIB_SUFFIX",
	],

)

###############################################################################################
# The basic environment for building python modules
###############################################################################################

basePythonEnv = baseLibEnv.Clone()

basePythonEnv.Append(

	CPPFLAGS = [
		"-DBOOST_PYTHON_MAX_ARITY=20",
	],

	LIBS = [
		"boost_python$BOOST_LIB_SUFFIX",
		"IECorePython$CORTEX_PYTHON_LIB_SUFFIX",
		"Gaffer",
	],

)

if basePythonEnv["PLATFORM"]=="darwin" :

	basePythonEnv.Append(
		CPPPATH = [ "$GAFFER_ROOT/lib/Python.framework/Versions/$PYTHON_VERSION/include/python$PYTHON_VERSION" ],
		LIBPATH = [ "$GAFFER_ROOT/lib/Python.framework/Versions/$PYTHON_VERSION/lib/python$PYTHON_VERSION/config" ],
		LIBS = [ "python$PYTHON_VERSION" ],
	)

else :

	basePythonEnv.Append(
		CPPPATH = [ "$BUILD_DIR/include/python$PYTHON_VERSION" ]
	)

###############################################################################################
# Definitions for the libraries we wish to build
###############################################################################################

libraries = {

	"GafferAstro" : {
		"envAppends" : {
			"LIBS" : [ "Gaffer", "GafferImage", "tbb", "libCCFits", "cfitsio" ],
		},
		"pythonEnvAppends" : {
			"LIBS" : [ "GafferAstro", "GafferImage" ],
		}
	},

	"GafferAstroTest" : {
		"envAppends" : {
			"LIBS" : [ "Gaffer", "GafferImage" ],
		},
		"pythonEnvAppends" : {
			"LIBS" : [ "GafferAstroTest", "GafferBindings" ],
		},
		"additionalFiles" : glob.glob( "python/GafferAstroTest/*/*" ) + glob.glob( "python/GafferAstroTest/*/*/*" )
	},

	"GafferAstroUI" : {
		"envAppends" : {
			"LIBS" : [ "Gaffer", "GafferAstro", "Iex$OPENEXR_LIB_SUFFIX", "IECoreGL$CORTEX_LIB_SUFFIX", "IECoreImage$CORTEX_LIB_SUFFIX", "IECoreScene$CORTEX_LIB_SUFFIX", "GafferUI" ],
		},
		"pythonEnvAppends" : {
			"LIBS" : [ "IECoreImage$CORTEX_LIB_SUFFIX", "IECoreGL$CORTEX_LIB_SUFFIX", "GafferUI", "GafferBindings", "GafferAstroUI" ],
			 # Prevent Qt clashing with boost::signals - we can remove
			 # this if we move to boost::signals2.
			 "CXXFLAGS" : [ "-DQT_NO_KEYWORDS" ],
		}
	},

	"misc" : {
		"additionalFiles" : [ "LICENSE" ],
	},

}

# Add on OpenGL libraries to definitions - these vary from platform to platform
for library in ( "GafferAstro", "GafferAstroUI" ) :
	if env["PLATFORM"] == "darwin" :
		libraries[library]["envAppends"].setdefault( "FRAMEWORKS", [] ).append( "OpenGL" )
	else :
		libraries[library]["envAppends"]["LIBS"].append( "GL" )
	libraries[library]["envAppends"]["LIBS"].append( "GLEW$GLEW_LIB_SUFFIX" )

# Add on Qt libraries to definitions - these vary from platform to platform

def addQtLibrary( library, qtLibrary ) :

	if env["PLATFORM"] == "darwin" :
		libraries[library]["pythonEnvAppends"].setdefault( "FRAMEWORKS", [] ).append( "Qt" + qtLibrary )
	else :
		prefix = "Qt" if int( env["QT_VERSION"] ) < 5 else "Qt${QT_VERSION}"
		libraries[library]["pythonEnvAppends"]["LIBS"].append( prefix + qtLibrary )

for library in ( "GafferAstroUI", ) :
	addQtLibrary( library, "Core" )
	addQtLibrary( library, "Gui" )
	addQtLibrary( library, "OpenGL" )
	if int( env["QT_VERSION"] ) > 4 :
		addQtLibrary( library, "Widgets" )

###############################################################################################
# The stuff that actually builds the libraries and python modules
###############################################################################################

for libraryName, libraryDef in libraries.items() :

	# skip this library if we don't have the config we need

	haveRequiredOptions = True
	for requiredOption in libraryDef.get( "requiredOptions", [] ) :
		if not env[requiredOption] :
			haveRequiredOptions = False
			break
	if not haveRequiredOptions :
		continue

	# environment

	libEnv = baseLibEnv.Clone()
	libEnv.Append( CXXFLAGS = "-D{0}_EXPORTS".format( libraryName ) )
	libEnv.Append( **(libraryDef.get( "envAppends", {} )) )

	# library

	librarySource = sorted( glob.glob( "src/" + libraryName + "/*.cpp" ) + glob.glob( "src/" + libraryName + "/*/*.cpp" ) )
	if librarySource :

		library = libEnv.SharedLibrary( "lib/" + libraryName, librarySource )
		libEnv.Default( library )

		libraryInstall = libEnv.Install( "$BUILD_DIR/lib", library )
		libEnv.Alias( "build", libraryInstall )

	# header install

	sedSubstitutions = "; s/!GAFFERASTRO_MAJOR_VERSION!/$MAJOR_VERSION/g"
	sedSubstitutions += "; s/!GAFFERASTRO_MINOR_VERSION!/$MINOR_VERSION/g"
	sedSubstitutions += "; s/!GAFFERASTRO_PATCH_VERSION!/$PATCH_VERSION/g"

	headers = (
		glob.glob( "include/" + libraryName + "/*.h" ) +
		glob.glob( "include/" + libraryName + "/*.inl" ) +
		glob.glob( "include/" + libraryName + "/*/*.h" ) +
		glob.glob( "include/" + libraryName + "/*/*.inl" )
	)

	for header in headers :
		headerInstall = env.Command( "$BUILD_DIR/" + header, header, "sed \"" + sedSubstitutions + "\" $SOURCE > $TARGET" )
		libEnv.Alias( "build", headerInstall )

	# bindings library

	pythonEnv = basePythonEnv.Clone()
	pythonEnv.Append( **(libraryDef.get( "pythonEnvAppends", {} ))  )

	bindingsEnv = pythonEnv.Clone()
	bindingsEnv.Append( CXXFLAGS = "-D{0}BINDINGS_EXPORTS".format( libraryName ) )

	bindingsSource = sorted( glob.glob( "src/" + libraryName + "Bindings/*.cpp" ) )
	if bindingsSource :

		bindingsLibrary = bindingsEnv.SharedLibrary( "lib/" + libraryName + "Bindings", bindingsSource )
		bindingsEnv.Default( bindingsLibrary )

		bindingsLibraryInstall = bindingsEnv.Install( "$BUILD_DIR/lib", bindingsLibrary )
		env.Alias( "build", bindingsLibraryInstall )

	# bindings header install

	bindingsHeaders = (
		glob.glob( "include/" + libraryName + "Bindings/*.h" ) +
		glob.glob( "include/" + libraryName + "Bindings/*.inl" )
	)

	for header in bindingsHeaders :
		headerInstall = env.Command( "$BUILD_DIR/" + header, header, "sed \"" + sedSubstitutions + "\" $SOURCE > $TARGET" )
		bindingsEnv.Alias( "build", headerInstall )

	# python module binary component

	pythonModuleSource = sorted( glob.glob( "src/" + libraryName + "Module/*.cpp" ) )
	if pythonModuleSource :

		pythonModuleEnv = pythonEnv.Clone()
		if bindingsSource :
			pythonModuleEnv.Append( LIBS = [ libraryName + "Bindings" ] )

		pythonModuleEnv["SHLIBPREFIX"] = ""
		if pythonModuleEnv["PLATFORM"] == "darwin" :
			# On OSX, we must build Python modules with the ".so"
			# prefix rather than the ".dylib" you might expect.
			# This is done by changing the SHLIBSUFFIX variable.
			# But this causes a problem with SCons' automatic
			# scanning for the library dependencies of those modules,
			# because by default it expects the libraries to end in
			# "$SHLIBSUFFIX". So we must also explicitly add
			# the original value of SHLIBSUFFIX (.dylib) to the
			# LIBSUFFIXES variable used by the library scanner.
			pythonModuleEnv["LIBSUFFIXES"].append( pythonModuleEnv.subst( "$SHLIBSUFFIX" ) )
			pythonModuleEnv["SHLIBSUFFIX"] = ".so"

		pythonModule = pythonModuleEnv.SharedLibrary( "python/" + libraryName + "/_" + libraryName, pythonModuleSource )
		pythonModuleEnv.Default( pythonModule )

		moduleInstall = pythonModuleEnv.Install( "$BUILD_DIR/python/" + libraryName, pythonModule )
		pythonModuleEnv.Alias( "build", moduleInstall )

	# python component of python module

	pythonFiles = glob.glob( "python/" + libraryName + "/*.py" ) + glob.glob( "python/" + libraryName + "/*/*.py" )
	for pythonFile in pythonFiles :
		pythonFileInstall = env.Command( "$BUILD_DIR/" + pythonFile, pythonFile, "sed \"" + sedSubstitutions + "\" $SOURCE > $TARGET" )
		env.Alias( "build", pythonFileInstall )

	# apps

	for app in libraryDef.get( "apps", [] ) :
		appInstall = env.InstallAs("$BUILD_DIR/apps/{app}/{app}-1.py".format( app=app ), "apps/{app}/{app}-1.py".format( app=app ) )
		env.Alias( "build", appInstall )

	# startup files

	for startupDir in ( 'gui', libraryName ) :
		for startupFile in glob.glob( "startup/{startupDir}/*.py".format( startupDir=startupDir ) ) :
			startupFileInstall = env.InstallAs( "$BUILD_DIR/" + startupFile, startupFile )
			env.Alias( "build", startupFileInstall )

	# additional files

	for additionalFile in libraryDef.get( "additionalFiles", [] ) :
		if additionalFile in pythonFiles :
			continue
		additionalFileInstall = env.InstallAs( "$BUILD_DIR/" + additionalFile, additionalFile )
		env.Alias( "build", additionalFileInstall )

	# osl headers

	for oslHeader in libraryDef.get( "oslHeaders", [] ) :
		oslHeaderInstall = env.InstallAs( "$BUILD_DIR/" + oslHeader, oslHeader )
		env.Alias( "oslHeaders", oslHeaderInstall )
		env.Alias( "build", oslHeaderInstall )

	# osl shaders

	def buildOSL( target, source, env ) :

		subprocess.check_call( [ "oslc", "-I./shaders", "-o", str( target[0] ), str( source[0] ) ], env = env["ENV"] )

	for oslShader in libraryDef.get( "oslShaders", [] ) :
		env.Alias( "build", oslShader )
		compiledFile = commandEnv.Command( "$BUILD_DIR/" + os.path.splitext( oslShader )[0] + ".oso", oslShader, buildOSL )
		env.Depends( compiledFile, "oslHeaders" )
		env.Alias( "build", compiledFile )

	# class stubs

	def buildClassStub( target, source, env ) :

		dir = os.path.dirname( str( target[0] ) )
		if not os.path.isdir( dir ) :
			os.makedirs( dir )

		classLoadableName = dir.rpartition( "/" )[2]

		f = open( str( target[0] ), "w" )
		f.write( "import IECore\n\n" )
		f.write( env.subst( "from $GAFFER_STUB_MODULE import $GAFFER_STUB_CLASS as %s" % classLoadableName ) )

	for classStub in libraryDef.get( "classStubs", [] ) :
		stubFileName = "$BUILD_DIR/" + classStub[1] + "/" + classStub[1].rpartition( "/" )[2] + "-1.py"
		stubEnv = env.Clone(
			GAFFER_STUB_MODULE = libraryName,
			GAFFER_STUB_CLASS = classStub[0],
		)
		stub = stubEnv.Command( stubFileName, "", buildClassStub )
		stubEnv.Alias( "build", stub )

#########################################################################################################
# Graphics
#########################################################################################################

def buildImageCommand( source, target, env ) :

	# Requires env to have buildImageOptions set, containing, at minimum:
	#	- id : The svg object id to export.

	svgFilename = str( source[0] )
	filename = str( target[0] )

	substitutions = inkscapeArgs( env["buildImageOptions"], svgFilename )

	outputDirectory = os.path.dirname( filename )
	if not os.path.isdir( outputDirectory ) :
		os.makedirs( outputDirectory )

	args = " ".join( [
		"--export-png={filePath}",
		"--export-id={id}",
		"--export-width={width:d}",
		"--export-height={height:d}",
		"--export-background-opacity=0",
		"{svgPath}"
	] ).format(
		filePath = os.path.abspath( filename ),
		svgPath = os.path.abspath( svgFilename ),
		**substitutions
	)
	subprocess.check_call( env["INKSCAPE"] + " " + args, shell = True )

def inkscapeArgs( imageOptions, svg ) :

	id_ = imageOptions["id"]

	svgObjectInfo = svgQuery( svg, id_ )
	if svgObjectInfo is None :
		raise RuntimeError( "Object with id '%s' not found" % id_ )

	width = int( round( svgObjectInfo["width"] ) )
	height = int( round( svgObjectInfo["height"] ) )

	return {
		"id" : id_,
		"width" : width,
		"height" : height
	}

# svgQuery is relatively slow as it requires running inkscape, which can be ~1s on macOS.
# As we know any given svg is constant during a build and we can retrieve all object info
# in one go, we cache per file.
__svgQueryCache = {}

def svgQuery( svgFile, id_ ) :

	filepath = os.path.abspath( svgFile )

	objects = __svgQueryCache.get( svgFile, None )
	if objects is None :

		objects = {}

		queryCommand = env["INKSCAPE"] + " --query-all \"" + filepath + "\""
		output = subprocess.check_output( queryCommand, shell=True ).decode()
		for line in output.split( "\n" ) :
			tokens = line.split( "," )
			# <id>,<x>,<y>,<width>,<height>
			if len(tokens) != 5 :
				continue
			objects[ tokens[0] ] = {
				"width" : float( tokens[3] ),
				"height" : float( tokens[4] )
			}

		__svgQueryCache[ svgFile ] = objects

	return objects.get( id_, None )

def imagesToBuild( definitionFile ) :

	with open( definitionFile ) as f :
		exports = eval( f.read() )

	toBuild = []

	for i in exports["ids"] :
		imageOptions = {
			"id" : i,
			"filename" : i + ".png"
		}
		toBuild.append( imageOptions )

	return toBuild

# Bitmaps can be generated from inkscape compatible svg files, using the
# `graphicsCommands` helper.  In order to build images, you need two things:
#
#   - An svg file with one or more well-known object IDs
#   - A sidecar python definitions file that lists the IDs to build. This must
#     live next to the svg, with the same name.
#
# You can then add in a graphics builds as follows (output directories will be
# made for you):
#
#	cmds = graphicsCommands( env, <svgPath>, <outputDirectory> )
#	env.Alias( "build", cmds )
#
# The definition file must be `eval`able to define a single `exports`
# dictionary, structured as follows:
#
#	{ "ids" : [ <id str>, ... ], }
#
def graphicsCommands( env, svg, outputDirectory ) :

	commands = []

	definitionFile = svg.replace( ".svg", ".py" )

	try :

		# Manually construct the Action so we can hash in the build options
		buildAction = Action( buildImageCommand, "Exporting '$TARGET' from '$SOURCE'", varlist=[ "buildImageOptions" ] )

		for options in imagesToBuild( definitionFile ) :
			targetPath = os.path.join( outputDirectory, options["filename"] )
			buildEnv = env.Clone( buildImageOptions = options )
			commands.append( buildEnv.Command( targetPath, svg, buildAction ) )

	except Exception as e :
		raise RuntimeError( "%s: %s" % ( svg, e ) )

	return commands

# GafferAstro UI Images

#if haveInkscape :
#
#	for source in ( "resources/graphics.svg", "resources/GafferLogo.svg", "resources/GafferLogoMini.svg" ) :
#		env.Alias( "build", graphicsCommands( env, source, "$BUILD_DIR/graphics" ) )
#
#else :
#
#	sys.stderr.write( "WARNING : Inkscape not found - not building graphics. Check INKSCAPE build variable.\n" )

#########################################################################################################
# Resources
#########################################################################################################

#resources = None
#if commandEnv.subst( "$LOCATE_DEPENDENCY_RESOURCESPATH" ) :
#
#	resources = []
#	resourceRoot = commandEnv.subst( "$LOCATE_DEPENDENCY_RESOURCESPATH" )
#	for root, dirs, files in os.walk( resourceRoot ) :
#		for f in files :
#			fullPath = os.path.join( root, f )
#			resources.append( commandEnv.Command( fullPath.replace( resourceRoot, "$BUILD_DIR/resources/", 1 ), fullPath, Copy( "$TARGET", "$SOURCE" ) ) )
#
#	commandEnv.NoCache( resources )
#	commandEnv.Alias( "build", resources )

#########################################################################################################
# Installation
#########################################################################################################

def installer( target, source, env ) :

	shutil.copytree( str( source[0] ), str( target[0] ), symlinks=True )

install = env.Command( "$INSTALL_DIR", "$BUILD_DIR", installer )
env.AlwaysBuild( install )
env.NoCache( install )

env.Alias( "install", install )

#########################################################################################################
# Packaging
#########################################################################################################

def packager( target, source, env ) :

	target = str( target[0] )
	source = str( source[0] )
	b = os.path.basename( source )
	d = os.path.dirname( source )
	runCommand( "tar -czf %s -C %s %s" % ( target, d, b ) )

package = env.Command( "$PACKAGE_FILE", "$INSTALL_DIR", packager )
env.NoCache( package )
env.Alias( "package", package )
