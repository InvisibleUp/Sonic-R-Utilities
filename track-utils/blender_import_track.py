# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import bpy
import os.path
import argparse
import array
import random #TEMP
from copy import deepcopy
from struct import *
from mathutils import Vector
from itertools import chain, islice, accumulate
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from bpy.props import (
        BoolProperty,
        FloatProperty,
        StringProperty,
        EnumProperty,
        )
from bpy_extras.io_utils import (
        ImportHelper,
        ExportHelper,
        orientation_helper_factory,
        path_reference_mode,
        axis_conversion,
        )

def makeMaterial(name):
    tex = bpy.data.textures.new('ColorTex', type = 'IMAGE')
    # do not load image
    tex.use_alpha = True
    
    mat = bpy.data.materials.new(name)
    mat.use_shadeless = True # Like Sonic R!
    mtex = mat.texture_slots.add()
    mtex.texture = tex
    mtex.texture_coords = 'UV'
    mtex.use_map_color_diffuse = True 
    mtex.blend_type = "MULTIPLY"
    mat.use_shadeless = True
    mat.use_vertex_color_paint = True
    return mat

def parse(path):
    
    def readDword(filecounter):
        temp = []
        for k in range(0, 4):
            temp.append(SRT[filecounter])
            filecounter += 1
        #temp = bytes(temp).unpack('i', temp)[0]
        temp = unpack("<i", bytes(temp))[0]
        return [filecounter, temp]
            
    def readWord(filecounter):
        temp = []
        for k in range(0, 2):
            temp.append(SRT[filecounter])
            filecounter += 1
        #temp = bytes(temp).unpack('h', temp)[0]
        temp = unpack("<h", bytes(temp))[0]
        return [filecounter, temp]
            
    def readByte(filecounter):
        temp = []
        temp.append(SRT[filecounter])
        filecounter += 1
        #temp = bytes(temp).unpack('B', temp)[0]
        temp = unpack("<B", bytes(temp))[0]
        return [filecounter, temp]

    ## Defines
    #######################
    ModelFileSize = 0
    filecounter = 0
    noParts = 0

    # Storage for coordinates
    TrackTemplate = {
        'X': 0,
        'Y': 0,
        'Z': 0,
        'FaceVtxs': [],
        'TexVtxs': [],
        'ColorVtxs': [],
        'FaceTexPages': []
    }
    TrackParts = []
    #TrackPartTex = []
    #TrackTexPage = []

    DecoTemplate = {
        'X': 0,
        'Y': 0,
        'Z': 0,
        'FaceVtxs': [],
        'TriTexVtxs': [],
        'QuadTexVtxs': [],
        'ColorVtxs': [],
        'TriTexPages': [],
        'QuadTexPages': [],
        'QuadTexVtxs': [],
        'QuadIdxs': [],
        'TriIdxs': [],
    }
    DecoParts = []
    
    #RingVtx = []

    filecounter = 0;
    highestmat = 0;
        
    # Load model
    print ("Loading track ", path, "...", sep="")
    try:
        SRTfile = open(path, mode='rb')
    except OSError:
        raise Exception("Error loading track {}!\n{}".format(path))
        # Dump back to command line

    FileSize = os.stat(path).st_size
    if (FileSize % 2 != 0):
        raise Exception("Bad model! (Size should be divisible by 2.)")

    # Load file into memory. (Seriously doubt this'll be a problem.)	
    SRT = array.array('B')
    SRTfile.seek(0x00,0)
    SRT.fromfile(SRTfile, FileSize) 
    SRTfile.close()


    ## Parse
    #######################

    # Skip header/whatever this is
    temp = readDword(filecounter)
    filecounter = temp[0]
    filecounter += (temp[-1] * 0x80)

    print ("No. of Track Parts:", end = " ")
    temp = readDword(filecounter)
    filecounter = temp[0]
    noParts = temp[1]
    print (noParts, hex(filecounter-4))

    for i in range(0, noParts):
        TrackParts.append(deepcopy(TrackTemplate))
    #	print("\nPart no.", i+1)
        
    #	print ("X pos:  ", end = "\t")
        temp = readDword(filecounter)
        filecounter = temp[0]
        TrackParts[-1]['X'] = temp[1]
    #	print ("Y pos:  ", end = "\t")
        temp = readDword(filecounter)
        filecounter = temp[0]
        TrackParts[-1]['Y'] = temp[1]
    #	print ("Z pos:  ", end = "\t")
        temp = readDword(filecounter)
        filecounter = temp[0]
        TrackParts[-1]['Z'] = temp[1]
    #	print ("Angle?: ", end = "\t")
        filecounter = readDword(filecounter)[0]
    #	print ("No. Points:", end = "\t")
        temp = readDword(filecounter)
        filecounter = temp[0]
        noPoints = temp[1]
        #print ("Unknown: ", end = "\t")
        
        for j in range(0, noPoints):
    #		print ("Point no.", j+1, hex(filecounter))
            
    #		print ("X pos: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['FaceVtxs'].append((temp[1] + TrackParts[-1]['X']) / 100)
    #		print ("Y pos: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['FaceVtxs'].append((temp[1] + TrackParts[-1]['Y']) / 100)
    #		print ("Z pos: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['FaceVtxs'].append((temp[1] + TrackParts[-1]['Z']) / 100)
            
    #		print ("R Tint: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['ColorVtxs'].append((temp[1] / 384) + 0.25)
    #		print ("G Tint: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['ColorVtxs'].append((temp[1] / 384) + 0.25)
    #		print ("B Tint: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['ColorVtxs'].append((temp[1] / 384) + 0.25)
        
    #	print ("No. Faces:", end = "\t")
        temp = readDword(filecounter)
        filecounter = temp[0]
        noPoints = temp[1]
        
        for j in range(0, noPoints):
    #		print ("Face no.", j+1, hex(filecounter))
            
    #		print ("Tex Page: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            #TrackTexPage[-1].append(temp[1])
            temp[1] = temp[1] & 255
            TrackParts[-1]['FaceTexPages'].append(temp[1])
            if temp[1] > highestmat:
                print("New highestmat " + str(temp[1]))
                highestmat = temp[1]

            
    #		print ("TL: ", end = "\t")
            temp = readByte(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['TexVtxs'].append(temp[1] / 256)
            
            temp = readByte(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['TexVtxs'].append(abs(temp[1] - 255) / 256)
            
            
    #		print ("BL: ", end = "\t")
            temp = readByte(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['TexVtxs'].append(temp[1] / 256)
            
            temp = readByte(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['TexVtxs'].append(abs(temp[1] - 255) / 256)
            
    #		print ("TR: ", end = "\t")
            temp = readByte(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['TexVtxs'].append(temp[1] / 256)
            
            temp = readByte(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['TexVtxs'].append(abs(temp[1] - 255) / 256)
            
    #		print ("BR: ", end = "\t")
            temp = readByte(filecounter)
            filecounter = temp[0]
            #TrackPartTex[-1].append(temp[1])
            TrackParts[-1]['TexVtxs'].append(temp[1] / 256)
            
            temp = readByte(filecounter)
            filecounter = temp[0]
            TrackParts[-1]['TexVtxs'].append(abs(temp[1] - 255) / 256)
            
    #		print ("???", end = "\t")
            filecounter = readWord(filecounter)[0]
            
        temp = readDword(filecounter)
        filecounter = temp[0]
#        RingVtx.append([])
        
        if (temp[1] != -1):
            if (temp[1] != 0):
                raise Exception("Error in file. (Track Part ring end != -1.) File may be invalid or corrupt.")
            while(temp[1] != -1):
                """RingVtx[-1].append([]);
                
                temp = readDword(filecounter)
                filecounter = temp[0]
                RingVtx[-1][-1].append(temp[1]) # X
                
                temp = readDword(filecounter)
                filecounter = temp[0]
                RingVtx[-1][-1].append(temp[1]) # Y
                
                temp = readDword(filecounter)
                filecounter = temp[0]
                RingVtx[-1][-1].append(temp[1]) # Z"""
                
                temp = readDword(filecounter)
                filecounter = temp[0]
            
    print ("No. of Decoration Parts:", end = " ")
    temp = readDword(filecounter)
    filecounter = temp[0]
    noParts = temp[1]
    print (noParts, hex(filecounter-4))

    for i in range(0, noParts):
        DecoParts.append(deepcopy(DecoTemplate))
    #	print("\nPart no.", i+1, hex(filecounter))
        
    #	print ("Angle?: ")
        filecounter = readDword(filecounter)[0]
        filecounter = readDword(filecounter)[0]
        filecounter = readDword(filecounter)[0]
        filecounter = readDword(filecounter)[0]
        
    #	print ("X pos:  ", end = "\t")
        temp = readDword(filecounter)
        filecounter = temp[0]
        DecoParts[-1]['X'] = temp[1]
    #	print ("Y pos:  ", end = "\t")
        temp = readDword(filecounter)
        filecounter = temp[0]
        DecoParts[-1]['Y'] = temp[1]
    #	print ("Z pos:  ", end = "\t")
        temp = readDword(filecounter)
        filecounter = temp[0]
        DecoParts[-1]['Z'] = temp[1]
        
    #	print ("Unk: ")
        filecounter = readDword(filecounter)[0]
        filecounter = readWord(filecounter)[0]
        
    #	print ("No. Triangles:")
        temp = readDword(filecounter)
        filecounter = temp[0]
        noPoints = temp[1]
    #	print (noPoints)

        # Fair sanity checking
        if (noPoints < 0):
            raise Exception("Invalid number of tris, file possibly bad")
        if (noPoints > 5000):
            raise Exception("Absurd number of tris, file possibly bad")

        for j in range(0, noPoints):
    #		print ("\nTri no.", j+1)

            #print ("A: ", end = "")  
            temp = readWord(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['TriIdxs'].append(temp[1])
            #print (temp[1])

    #		print ("B: ", end = "")
            temp = readWord(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['TriIdxs'].append(temp[1])

    #		print ("C: ", end = "")
            temp = readWord(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['TriIdxs'].append(temp[1])

    #		print ("TA: ", end = "") 		
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['TriTexVtxs'].append(temp[1] / 256)

            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['TriTexVtxs'].append(abs(temp[1] - 255) / 256)

    #		print ("TB: ", end = "") 
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['TriTexVtxs'].append(temp[1] / 256)

            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['TriTexVtxs'].append(abs(temp[1] - 255) / 256)

    #		print ("TC: ", end = "") 
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['TriTexVtxs'].append(temp[1] / 256)

            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['TriTexVtxs'].append(abs(temp[1] - 255) / 256)

            #print ("Tex. Page: ", end = "")
            temp = readDword(filecounter)
            filecounter = temp[0]
            temp[1] = temp[1] & 255
            DecoParts[-1]['TriTexPages'].append(temp[1])
            if temp[1] > highestmat:
                print("New highestmat " + str(temp[1]))
                highestmat = temp[1]

    #	print ("No. Quads:", end = "\t")
        temp = readDword(filecounter)
        filecounter = temp[0]
        noPoints = temp[1] #They're not points, but eh
    #	print (noPoints)
        
        #Fair sanity checking
        if (noPoints < 0):
            raise Exception("Invalid number of points, file possibly bad")
        if (noPoints > 5000):
            raise Exception("Invalid number of points, file possibly bad")
            
        for j in range(0, noPoints):
    #		print ("Face no.", j+1, hex(filecounter))
            
    #		print ("A: ", end = "\t") ## Vtx no.
            temp = readWord(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['QuadIdxs'].append(temp[1])
    #		print ("B: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['QuadIdxs'].append(temp[1])
    #		print ("C: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['QuadIdxs'].append(temp[1])
    #		print ("D: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['QuadIdxs'].append(temp[1])
            
    #		print ("TA: ", end = "\t")
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['QuadTexVtxs'].append(temp[1] / 256)
            
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['QuadTexVtxs'].append(abs(temp[1] - 255) / 256)
            
    #		print ("TB: ", end = "\t")
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['QuadTexVtxs'].append(temp[1] / 256)
            
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['QuadTexVtxs'].append(abs(temp[1] - 255) / 256)
            
    #		print ("TC: ", end = "\t")
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['QuadTexVtxs'].append(temp[1] / 256)
            
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['QuadTexVtxs'].append(abs(temp[1] - 255) / 256)
            
    #		print ("TD: ", end = "\t")
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['QuadTexVtxs'].append(temp[1] / 256)
            
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['QuadTexVtxs'].append(abs(temp[1] - 255) / 256)
            
    #		print ("Tex Page: ", end = "\t")
            temp = readDword(filecounter)
            filecounter = temp[0]
            temp[1] = temp[1] & 255
            DecoParts[-1]['QuadTexPages'].append(temp[1])
            if temp[1] > highestmat:
                print("New highestmat " + str(temp[1]))
                highestmat = temp[1]
            
    #	print ("No. Vertices:", end = "\t")
        temp = readDword(filecounter)
        filecounter = temp[0]
        noPoints = temp[1]
    #	print (noPoints)
        
        if (noPoints < 0):
            raise Exception("Invalid number of points, file possibly bad")
        if (noPoints > 5000):
            raise Exception("Absurd number of points, file possibly bad")
        
        for j in range(0, noPoints):
    #		print ("Point no.", j+1, hex(filecounter))
            
    #		print ("Unk: ", end = "\t")
            #filecounter = readWord(filecounter)[0]
            
    #		print ("X: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['FaceVtxs'].append((temp[1] + DecoParts[-1]['X']) / 100)
    #		print ("Y: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['FaceVtxs'].append((temp[1] + DecoParts[-1]['Y']) / 100)
    #		print ("Z: ", end = "\t")
            temp = readWord(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['FaceVtxs'].append((temp[1] + DecoParts[-1]['Z']) / 100)
            
            # R
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['ColorVtxs'].append((temp[1] / 384) + 0.25)
            # G
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['ColorVtxs'].append((temp[1] / 384) + 0.25)
            # B
            temp = readByte(filecounter)
            filecounter = temp[0]
            DecoParts[-1]['ColorVtxs'].append((temp[1] / 384) + 0.25)
            
            filecounter = readByte(filecounter)[0] # 0
            
    #		print ("Unk: ", end = "\t")
    #        filecounter = readWord(filecounter)[0]
    #	print ("Unk: ", end = "\t")
    #    filecounter = readWord(filecounter)[0]
        
    return (TrackParts, DecoParts, highestmat)
        

# Export to Blender
def convert(context, TrackParts, DecoParts, highestmat):
    
    #materials = [None] * len(highestmat)
    scene = context.scene
    new_objects = []  # put new objects here
    materials = []
    
    # Create required materials
    print("Adding " + str(highestmat) + " materials...")
    for m in range(0, highestmat):
        materials.append(makeMaterial(str(m)))
        materials[-1].diffuse_color = [random.random() for j in range(3)]
    
    for a in range(0, len(TrackParts)):
        # create a new mesh
        me = bpy.data.meshes.new("Trk") 
        ob = bpy.data.objects.new("Trk", me)
        
        # add all materials to mesh
        for material in materials:
            me.materials.append(material)

        verts = []
        tints = []
        faces = []
        texs = []
        x = TrackParts[a]
        
        # parse verts (list of tuples of 3D world coordinates)
        verts = list(zip(*[iter(x['FaceVtxs'])] * 3))
            
        # parse vtx colors
        tints = list(zip(*[iter(x['ColorVtxs'])] * 3))
            
        # parse tex coords (NOT ->) [ ((Ax, Ay), (Bx, By), (Cx, Cy) (Dx, Dy)), ((Ax, Ay), ... )]
        texs = list(zip(*[iter(x['TexVtxs'])] * 2))
        #texs = list(zip(*[iter(temp)] * 4))
        
        # parse faces (list of tuples of vertex indices)
        for i, f in enumerate(
            zip(
                range(0, len(verts)),
                range(2, len(verts)),
                range(3, len(verts)),
                range(1, len(verts)),
            )
        ):
            if i % 2 == 1:
                continue
            faces.append(list(f))

        # to mesh
        face_lengths = tuple(map(len, faces))

        me.vertices.add(len(verts))
        me.loops.add(sum(face_lengths))
        me.polygons.add(len(faces))
        uvtex = me.uv_textures.new()
        colormap = me.vertex_colors.new()

        me.vertices.foreach_set("co", tuple(chain.from_iterable(verts)))

        vertex_indices = tuple(chain.from_iterable(faces))
        loop_starts = tuple(islice(chain([0], accumulate(face_lengths)), len(faces)))

        me.polygons.foreach_set("loop_total", face_lengths)
        me.polygons.foreach_set("loop_start", loop_starts)
        me.polygons.foreach_set("vertices", vertex_indices)
        
        
        # no edges - calculate them
        me.update(calc_edges=True, calc_tessface=True)
        me.validate()
        
        #print(dir(uvtex))
        #print(dir(uvtex.data[0]))

        j = 0
        pc = 0
        for p in me.polygons:
            
            for i in range(0, len(p.loop_indices)):
                
                # set colors
                #if i >= len(faces[pc]):
                #    break
                tint = tints[faces[pc][i]]
                colormap.data[j].color = tint
                
                # set textures
                me.uv_layers[0].data[j].uv = texs[j]
                
                j += 1
            p.material_index = x['FaceTexPages'][pc]
            pc += 1
        
        ob = bpy.data.objects.new("Trk", me)
        new_objects.append(ob)
        
    # Decoration parts
    for a in range(0, len(DecoParts)):
        # create a new mesh
        me = bpy.data.meshes.new("Deco") 
        ob = bpy.data.objects.new("Deco", me)
        
        # add all materials to mesh
        for material in materials:
            me.materials.append(material)
        
        verts = []
        tints = []
        faces = []
        x = DecoParts[a]

        # parse verts (list of tuples of coordinates)
        verts = list(zip(*[iter(x['FaceVtxs'])] * 3))

        # parse vtx colors
        tints = list(zip(*[iter(x['ColorVtxs'])] * 3))
            
        # parse textures
        texs = list(zip(*[iter(x['TriTexVtxs']+x['QuadTexVtxs'])] * 2))

        # parse faces (list of tuples of vertex indices)
        faces = list(zip(*[iter(x['TriIdxs'])] * 3)) + \
            list(zip(*[iter(x['QuadIdxs'])] * 4))

        #print("Verts and faces parsed!")
        #print("V: ", verts, len(verts))
        #print("F: ", faces, len(faces))
        #print("T: ", tints, len(tints))

        # to mesh
        face_lengths = tuple(map(len, faces))

        me.vertices.add(len(verts))
        me.loops.add(sum(face_lengths))
        me.polygons.add(len(faces))
        uvtex = me.uv_textures.new()
        colormap = me.vertex_colors.new()

        me.vertices.foreach_set("co", tuple(chain.from_iterable(verts)))
        #me.vertex_colors.foreach_set("co", tuple(chain.from_iterable(tints)))

        vertex_indices = tuple(chain.from_iterable(faces))
        loop_starts = tuple(islice(chain([0], accumulate(face_lengths)), len(faces)))
        
        #print("Indices set!")
        #print(vertex_indices)
        #print(loop_starts)

        me.polygons.foreach_set("loop_total", face_lengths)
        me.polygons.foreach_set("loop_start", loop_starts)
        me.polygons.foreach_set("vertices", vertex_indices)
        
        # no edges - calculate them
        me.update(calc_edges=True, calc_tessface=True)
        me.validate()

        # set colors
        j = 0
        pc = 0
        
        for p in me.polygons:
            for i in p.loop_indices:
                
                # Set colors
                vIdx = me.loops[i].vertex_index
                #print(vIdx)
                tint = tints[vIdx]
                colormap.data[j].color = tint
                
                # Set textures
                me.uv_layers[0].data[j].uv = texs[j]
                
                j += 1
            p.material_index = (x['TriTexPages']+x['QuadTexPages'])[pc]
            pc += 1 
            
        #print(len(colormap.data), j, sum(face_lengths))

        # no edges - calculate them
        #me.update(calc_edges=True)
        #me.validate()
        
        ob = bpy.data.objects.new("Deco", me)
        new_objects.append(ob)
        
    return new_objects

def load(context, filepath):
    (TrackParts, DecoParts, highestmat) = parse(filepath)
    
    objlist = convert(context, TrackParts, DecoParts, highestmat)
    
    scn = bpy.context.scene
    
    for o in scn.objects:
        o.select = False
    
    for o in objlist:
        scn.objects.link(o)
        o.select = True

    return {'FINISHED'}

bl_info = {
    "name": "Sonic R Track Importer",
    "author": "InvisibleUp",
    "version": (1, 0),
    "blender": (2, 77, 0),
    "location": "File > Import-Export",
    "description": "Imports a generic Sonic R track. (You will need to manually specify texture locations.)",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",}

if "bpy" in locals():
    import importlib
    if "import_track" in locals():
        importlib.reload(import_track)
#    if "export_obj" in locals():
#        importlib.reload(export_obj)


IOOBJOrientationHelper = orientation_helper_factory("IOOBJOrientationHelper", axis_forward='-Z', axis_up='Y')


class ImportSRT(bpy.types.Operator, ImportHelper, IOOBJOrientationHelper):
    bl_idname = "import_scene.srt"
    bl_label = "Import SRT"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".bin"
    filter_glob = StringProperty(
            default="*.bin;*.srt",
            options={'HIDDEN'},
            )

    def execute(self, context):

        keywords = self.as_keywords(ignore=("axis_forward",
                                            "axis_up",
                                            "filter_glob",
                                            "split_mode",
                                            ))

        return load(context, **keywords)


#class ExportOBJ(bpy.types.Operator, ExportHelper, IOOBJOrientationHelper):
    #"""Save a Wavefront OBJ File"""

    #bl_idname = "export_scene.obj"
    #bl_label = 'Export OBJ'
    #bl_options = {'PRESET'}

    #filename_ext = ".obj"
    #filter_glob = StringProperty(
            #default="*.obj;*.mtl",
            #options={'HIDDEN'},
            #)

    ## context group
    #use_selection = BoolProperty(
            #name="Selection Only",
            #description="Export selected objects only",
            #default=False,
            #)
    #use_animation = BoolProperty(
            #name="Animation",
            #description="Write out an OBJ for each frame",
            #default=False,
            #)

    ## object group
    #use_mesh_modifiers = BoolProperty(
            #name="Apply Modifiers",
            #description="Apply modifiers (preview resolution)",
            #default=True,
            #)

    ## extra data group
    #use_edges = BoolProperty(
            #name="Include Edges",
            #description="",
            #default=True,
            #)
    #use_smooth_groups = BoolProperty(
            #name="Smooth Groups",
            #description="Write sharp edges as smooth groups",
            #default=False,
            #)
    #use_smooth_groups_bitflags = BoolProperty(
            #name="Bitflag Smooth Groups",
            #description="Same as 'Smooth Groups', but generate smooth groups IDs as bitflags "
                        #"(produces at most 32 different smooth groups, usually much less)",
            #default=False,
            #)
    #use_normals = BoolProperty(
            #name="Write Normals",
            #description="Export one normal per vertex and per face, to represent flat faces and sharp edges",
            #default=True,
            #)
    #use_uvs = BoolProperty(
            #name="Include UVs",
            #description="Write out the active UV coordinates",
            #default=True,
            #)
    #use_materials = BoolProperty(
            #name="Write Materials",
            #description="Write out the MTL file",
            #default=True,
            #)
    #use_triangles = BoolProperty(
            #name="Triangulate Faces",
            #description="Convert all faces to triangles",
            #default=False,
            #)
    #use_nurbs = BoolProperty(
            #name="Write Nurbs",
            #description="Write nurbs curves as OBJ nurbs rather than "
                        #"converting to geometry",
            #default=False,
            #)
    #use_vertex_groups = BoolProperty(
            #name="Polygroups",
            #description="",
            #default=False,
            #)

    ## grouping group
    #use_blen_objects = BoolProperty(
            #name="Objects as OBJ Objects",
            #description="",
            #default=True,
            #)
    #group_by_object = BoolProperty(
            #name="Objects as OBJ Groups ",
            #description="",
            #default=False,
            #)
    #group_by_material = BoolProperty(
            #name="Material Groups",
            #description="",
            #default=False,
            #)
    #keep_vertex_order = BoolProperty(
            #name="Keep Vertex Order",
            #description="",
            #default=False,
            #)

    #global_scale = FloatProperty(
            #name="Scale",
            #min=0.01, max=1000.0,
            #default=1.0,
            #)

    #path_mode = path_reference_mode

    #check_extension = True

    #def execute(self, context):
        #from . import export_obj

        #from mathutils import Matrix
        #keywords = self.as_keywords(ignore=("axis_forward",
                                            #"axis_up",
                                            #"global_scale",
                                            #"check_existing",
                                            #"filter_glob",
                                            #))

        #global_matrix = (Matrix.Scale(self.global_scale, 4) *
                         #axis_conversion(to_forward=self.axis_forward,
                                         #to_up=self.axis_up,
                                         #).to_4x4())

        #keywords["global_matrix"] = global_matrix
        #return export_obj.save(context, **keywords)


def menu_func_import(self, context):
    self.layout.operator(ImportSRT.bl_idname, text="Sonic R Track (.bin)")


#def menu_func_export(self, context):
#    self.layout.operator(ExportOBJ.bl_idname, text="Wavefront (.obj)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func_import)
    #bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func_import)
    #bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":
    register()
