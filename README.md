Sonic-R-Utilities
=================

Utilities for modifying or viewing the files of Sonic R.

Note that any Python programs are designed for Python 3. They should not require any external dependencies.

Files from the Sonic R disk may be required, however. (It's rather difficult to convert something you don't have, generally speaking.)

# Contents

## Track utilities

### blender_import_track.py
Blender addon to import Sonic R tracks with vertex color data. Only supports geometry files.

### srt2obj.py
Commandline utility for converting a Sonic R track to a Wavefront OBJ. Exports all sections, not just the visible geometry.

### srtread.py
Commandline utility that dumps raw track data to the console. Only supports geometry files right now.

## Character utilities

### srm2obj.py
Commandline utility to convert a Sonic R character file to a Wavefront OBJ. Does not support animations, so everything will be clumped together in the middle.

### obj2srm.py
Commandline utility to convert a Wavefront OBJ to a Sonic R model. Only supports one texture page per model. Ensure that your OBJ's parts are in the right order. If you're using Blender, use the alternate OBJ exporter in the MISC directory.

### srmReorder.py
Commandline utility to reorder parts in a Sonic R model.

### modelview.exe
Modified version of a Sonic R character model viewer by xdaniel on the Sonic Retro forums. (I've lost the source code, so I can only provide the binary) Requires x86-64 Windows. Camera is controlled via mouse and WASD & TFGH (slower), F9 resets the camera position, numpad +/- select which model part to render (defaults to all). Use F1 and F2 to animate the character. Command line is: "SonicR.exe <model file> <texture file>"

## Misc

### export_obj.py
Drop-in replacement for Blender's OBJ exporter that exports all parts alphabetically instead of randomly. This means you can control the order of parts by prefixing a 00/01/etc. number.

To install, go to [blender install directory]/scripts/addons/io_scene_obj/. and replace export_obj.py.
