#!/usr/bin/python3

##############################################################################
##                                                                          ##
## OBJ2SRM - Wavefront OBJ to Sonic R model converter                       ##
## (c) InvisibleUp 2014-2017                                                ##
## Special thanks to xdaniel on the Sonic Retro forums.                     ##
##                                                                          ##
##############################################################################
import argparse
import os.path
from struct import *
import array

## Init
#######################
parser = argparse.ArgumentParser(
	description='Converts Wavefront .OBJ models to Sonic R character models.')
parser.add_argument('model',
	help='.OBJ file containing model')
parser.add_argument('output', nargs='?',
	help='.BIN file to output to.')
parser.add_argument('--no-tex', action='store_true',
	help="Don't parse texture coordinates.")
args = parser.parse_args()
if args.output == None:
	args.output = os.path.splitext(args.model)[0] + ".bin"
	
	
#do the loading of the obj file
Vertices = [] #vertex
Tris = []
Quads = []
TexCoords = []
TriTex = []
QuadTex = []

try:
	objModel = open(args.model)
except OSError:
	print ("ERROR: Model", args.model, "not found or corrupt. Please check\n",
	"that the filename is correct and try again.")
	# Dump back to command line
	raise SystemExit

VertIndex = 1
for line in objModel:
	line = line.strip().split(' ')
	if line[0] == 'v' : #vertex
		Vertices[-1].append(line[1:])	
		for j in range(0, 3):
			Vertices[-1][-1][j] = float(Vertices[-1][-1][j])
			Vertices[-1][-1][j] *= 100
			Vertices[-1][-1][j] = int(Vertices[-1][-1][j])
	if line[0] == 'vt' : #textures
		TexCoords.append([])
		line[1] = int(float(line[1]) * 255)
		TexCoords[-1].append(line[1])
		line[2] = int(float(line[2]) * 255)
		TexCoords[-1].append(abs(line[2] - 255))
		
	if line[0] == 'o' :
		Vertices.append([])
		Tris.append([])
		Quads.append([])
		TriTex.append([])
		QuadTex.append([])

		try:
			VertIndex += len(Vertices[-2])
		except:
			pass
		
	if line[0] == 'f' :
		# I swear this made sense at one point.
		if len(line) == 4:
			Tris[-1].append([])
			TriTex[-1].append([]) # New 
			for i in range(1,4):
				if i == 0: i = 1
				Tris[-1][-1].append([])
				TriTex[-1][-1].append([])
				Tris[-1][-1][-1] = int(line[i].split('/')[0]) - VertIndex
				TriTex[-1][-1][-1] = int(line[i].split('/')[1]) - 1
		if len(line) == 5:
			Quads[-1].append([])
			QuadTex[-1].append([])
			for i in range(1,5):
				if i == 0: i = 1
				Quads[-1][-1].append([])
				QuadTex[-1][-1].append([])
				Quads[-1][-1][-1] = int(line[i].split('/')[0]) - VertIndex	
				QuadTex[-1][-1][-1] = int(line[i].split('/')[1]) - 1

try:
	SRMfile = open(args.output, mode='wb')
except OSError:
	print ("ERROR: Output is on read-only disk. Please copy this program\n",
	"and any related files to a disk with write access and try again.")
	# Dump back to command line
	raise SystemExit

	
for i in range(0, len(Vertices)): # Part No.
	SRMfile.write(pack('i', len(Vertices[i]))) # Vertex length
	for j in range(0, len(Vertices[i])):	# Write vertices
		SRMfile.write(pack('h', int(Vertices[i][j][0])))
		SRMfile.write(pack('h', int(Vertices[i][j][1])))
		SRMfile.write(pack('h', int(Vertices[i][j][2])))
		for k in range(0, 9):
			SRMfile.write(pack('B', 0))
		SRMfile.write(pack('B', 0x80))
	
	SRMfile.write(pack('i', len(Tris[i]))) # Triangle length
	for j in range(0, len(Tris[i])):	# Write triangles
		SRMfile.write(pack('h', int(Tris[i][j][0])))
		SRMfile.write(pack('h', int(Tris[i][j][1])))
		SRMfile.write(pack('h', int(Tris[i][j][2])))
		if args.no_tex == True:
			SRMfile.write(pack('hhh', 0xFF, 0xFF, 0xFF))
		else:
		# Yes, I know this looks scary. Couldn't help it.
			# TriTex[PART][TRI NO.][POINT NO.]
			SRMfile.write(pack('B', TexCoords[TriTex[i][j][0]][0]))
			SRMfile.write(pack('B', TexCoords[TriTex[i][j][0]][1]))
			SRMfile.write(pack('B', TexCoords[TriTex[i][j][1]][0]))
			SRMfile.write(pack('B', TexCoords[TriTex[i][j][1]][1]))
			SRMfile.write(pack('B', TexCoords[TriTex[i][j][2]][0]))
			SRMfile.write(pack('B', TexCoords[TriTex[i][j][2]][1]))
		SRMfile.write(pack('i', 0))
		
	SRMfile.write(pack('i', len(Quads[i]))) # Quad length
	for j in range(0, len(Quads[i])):	# Write quads
		SRMfile.write(pack('h', int(Quads[i][j][0])))
		SRMfile.write(pack('h', int(Quads[i][j][1])))
		SRMfile.write(pack('h', int(Quads[i][j][2])))
		SRMfile.write(pack('h', int(Quads[i][j][3])))
		if args.no_tex == True:
			SRMfile.write(pack('hhhh', 0xFF, 0xFF, 0xFF, 0xFF))
		else:
			SRMfile.write(pack('B', int(TexCoords[QuadTex[i][j][0]][0])))
			SRMfile.write(pack('B', int(TexCoords[QuadTex[i][j][0]][1])))
			SRMfile.write(pack('B', int(TexCoords[QuadTex[i][j][1]][0])))
			SRMfile.write(pack('B', int(TexCoords[QuadTex[i][j][1]][1])))
			SRMfile.write(pack('B', int(TexCoords[QuadTex[i][j][2]][0])))
			SRMfile.write(pack('B', int(TexCoords[QuadTex[i][j][2]][1])))
			SRMfile.write(pack('B', int(TexCoords[QuadTex[i][j][3]][0])))
			SRMfile.write(pack('B', int(TexCoords[QuadTex[i][j][3]][1])))
		SRMfile.write(pack('i', 0))
SRMfile.write(pack('l', -1))		
