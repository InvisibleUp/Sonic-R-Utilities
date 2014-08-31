##############################################################################
##                                                                          ##
## SRM2OBJ - Sonic R Model to Wavefront OBJ converter                       ##
## (c) InvisibleUp 2014                                                     ##
## Special thanks to xdaniel on the Sonic Retro forums.                     ##
##                                                                          ##
##############################################################################
import os.path
import argparse
import cmath
import array
from struct import *
from decimal import *

def comboRead(byte1, byte2): # Totally not stolen from my GB emulator. Totally.
	length1 = len(hex(byte1))-2
	length2 = len(hex(byte1))-2
	if length1 != length2:
		raise SystemExit	# Might be a bit harsh
		return -1
	else:
		return (byte1 * (0x10 ** length1))+byte2

		

## Defines
#######################
VertexCounts = []
TriCounts = []
QuadCounts = []

VertexTotal = 0 # All of these are kinda pointless.
TriTotal = 0 # But they are neat, so there's that.
QuadTotal = 0

ModelFileSize = 0
AnimFileSize = 0

getcontext().prec = 50

## Init
#######################
parser = argparse.ArgumentParser(
	description='Converts Sonic R character models to Wavefront .OBJ models.')
parser.add_argument('model',
	help='.BIN file containing model (usually XXX_h.bin)')
#parser.add_argument('animation',
#	help='.BIN file containing animation (usually XanX.bin)')
#parser.add_argument('-f', metavar="FRAME", default=0, nargs='?', type=int,
#	help='Frame # to render. Default 0')
parser.add_argument('output', nargs='?',
	help='.OBJ file to output to. (or "screen")')
parser.add_argument('--silent', action='store_true',
	help="Don't print model info. Always on if output is 'screen'")
args = parser.parse_args()
if args.output == None:
	args.output = os.path.splitext(args.model)[0] + ".obj"
if args.output == "screen":
	args.silent == True
	
# Load model
if args.silent == False:
	print ("Loading model ", args.model, "...", sep="")
try:
	SRMfile = open(args.model, mode='rb')
except OSError:
	print ("Error loading model", args.model)
	# Dump back to command line
	raise SystemExit

ModelFileSize = os.stat(args.model).st_size
if (ModelFileSize % 4 != 0):
	print ("Bad model! (Size should be divisible by 4.)")
	raise SystemExit
	
SRM = array.array('B')
SRMfile.seek(0x00,0)
SRM.fromfile(SRMfile, ModelFileSize) 
SRMfile.close()
	
	
'''# Load animations
if args.silent == False:
	print ("Loading animations ", args.animation, "...", sep="")
try:
	SRAfile = open(args.animation, mode='rb')
except OSError:
	print ("Error loading model", args.amimation)
	# Dump back to command line
	raise SystemExit
	
AnimFileSize = os.stat(args.animation).st_size
#if args.silent == False:
#	print ("Checking validity...")
if (AnimFileSize % 4 != 0):
	print ("Bad model! (Size should be divisible by 4.)")
	raise SystemExit
	
SRA = array.array('B')
SRAfile.seek(0x00,0)
SRA.fromfile(SRAfile, AnimFileSize) 
SRAfile.close()'''


## Counting
#######################
if args.silent == False:
	print ("Counting model parts...")
i = 0
while (1):
	VertexCounts.append(comboRead(SRM[i+1],SRM[i]))
	i += (VertexCounts[-1] * 0x10) + 4
	if(i > ModelFileSize): 
		VertexCounts.pop()
		break
		
	TriCounts.append(comboRead(SRM[i+1],SRM[i]))
	i += (TriCounts[-1] * 0x10) + 4
	if(i > ModelFileSize): 
		TriCounts.pop()
		break
		
	QuadCounts.append(comboRead(SRM[i+1],SRM[i]))
	i += (QuadCounts[-1] * 0x14) + 4
	if(i > ModelFileSize):
		QuadCounts.pop()
		break
	
if len(VertexCounts) == 0:
	print ("Bad model! (There should be more than 0 groups.)")
	raise SystemExit

for i in range(0, len(VertexCounts)):
	VertexTotal += VertexCounts[i]


for i in range(0, len(TriCounts)):
	TriTotal += TriCounts[i]


for i in range(0, len(QuadCounts)):
	QuadTotal += QuadCounts[i]

if args.silent == False:
	print("\t", len(VertexCounts), " groups.", sep="")
	print("\t", VertexTotal, " vertices.", sep="")
	print("\t", TriTotal, " triangles.", sep="")
	print("\t", QuadTotal, " quads.", sep="")
	print("Probably valid at this point.")
	print()
	
## Parsing
#######################
	print ("Parsing model data...")
Vertices = []
Tris = []
Quads = []
TriTex = []
QuadTex = []
filecounter = 0;

# This is an incredibly complicated 3-dimensional array.
for i in range(0, len(VertexCounts)): 	# Dimension 1: Groups
	filecounter += 4 	# Vertices count
	Vertices.append([])
	for j in range(0, VertexCounts[i]): 	# Dimension 2: Vertices
		Vertices[-1].append([])
		temp = []
		for k in range(0, 6):
			temp.append(SRM[filecounter+(j*0x10)+k])
		temp = bytes(temp)
		temp = unpack('hhh', temp)
		for h in range(0, len(temp)):
			Vertices[-1][-1].append(temp[h])

	filecounter += 16*VertexCounts[i]
	
	filecounter += 4 	# Triangle count
	Tris.append([])
	TriTex.append([])
	for j in range(0, TriCounts[i]):
		Tris[-1].append([])
		TriTex[-1].append([])
		temp = []
		for k in range(0, 12):
			temp.append(SRM[filecounter+(j*0x10)+k])
		temp = bytes(temp)
		temp = unpack('HHHBBBBBB', temp)
		for h in range(0, 6):
			Tris[-1][-1].append(temp[h])
		for h in range(0, 6):
			TriTex[-1][-1].append(temp[h+3])
	filecounter += 16*TriCounts[i]
	
	filecounter += 4 	# Quad count
	Quads.append([])
	QuadTex.append([])
	for j in range(0, QuadCounts[i]):
		Quads[-1].append([])
		QuadTex[-1].append([])
		temp = []
		for k in range(0, 16):
			temp.append(SRM[filecounter+(j*0x14)+k])
		temp = bytes(temp)
		temp = unpack('hhhhBBBBBBBB', temp)
		for h in range(0, 8):
			Quads[-1][-1].append(temp[h])
			for h in range(0, 8):
				QuadTex[-1][-1].append(temp[h+4])
	filecounter += 20*QuadCounts[i]

if args.silent == False:
	print ("All points loaded.")
	print ()

'''## Parsing Animation
#######################
	print ("Parsing animation data...")

# Get into position
AnimIndex = 0
LimbCount = []
for i in range(0, 4):
	LimbCount.append(SRA[AnimIndex+i])
LimbCount = bytes(LimbCount)
LimbCount = unpack('l', LimbCount)[0]
if LimbCount != len(VertexCounts):
	print ("Invalid Animations (Limb count does not match with model.)")
	raise SystemExit

for i in range(0, args.f):
	AnimIndex += LimbCount*24
	if (AnimIndex > AnimFileSize): 	# Check to see if we're not overshooting
		AnimIndex -= LimbCount*48
		if args.silent == False:
			print ("Your frame number was too high. It's now", i-1)
			break		

# Move the things
for a in range(0, LimbCount):
	for b in range(0, len(Vertices[a])):
		for c in range(0, 3):
			temp = []
			for i in range(0, 2):
				temp.append(SRA[AnimIndex+i])
			temp = unpack('h', bytes(temp))[0]
			AnimIndex += 2
			#print(4-c)
			Vertices[a][b][c] += temp
			#print (Vertices[a][b][c], a, b, c)
			#print(hex(AnimIndex))
		AnimIndex -= 6
		#print("\t", b)
	AnimIndex += 24
	#print(a)

AnimIndex -= 24*LimbCount + 6
# Rotate the things
# As it turns out, rotating things is complicated.
# TODO: Figure out how to implement this.	
'''
	
## Converting
#######################
Out = "" 	# The string where we dump everything.
VertIndex = 1
TexIndex = 1
Out += "# srm2obj v0.1\nmtllib sonic_h.mtl\n"
for a in range(0, len(VertexCounts)):
	Out += "\no Grp" + str(a) + "\n" 	# Start the group
	for b in range(0, VertexCounts[a]):
		Out += "v "
		Out += str(Vertices[a][b][0] / 100) + " "
		Out += str(Vertices[a][b][1] / 100) + " " 
		Out += str(Vertices[a][b][2] / 100) + ""
		Out += "\n"
		
	for b in range(0, len(TriTex[a])):
		Out += "vt "
		Out += str(TriTex[a][b][0] / 256) + " " +\
			str(TriTex[a][b][1] / 256) + "\nvt " +\
			str(TriTex[a][b][2] / 256) + " " + \
			str(TriTex[a][b][3] / 256) + "\nvt " +\
			str(TriTex[a][b][4] / 256) + " " +\
			str(TriTex[a][b][5] / 256) + "\n"
		
	for b in range(0, len(QuadTex[a])):
		Out += "vt "
		Out += str(QuadTex[a][b][0] / 256) + " " +\
			str(QuadTex[a][b][1] / 256) + "\nvt " +\
			str(QuadTex[a][b][2] / 256) + " " + \
			str(QuadTex[a][b][3] / 256) + "\nvt " +\
			str(QuadTex[a][b][4] / 256) + " " +\
			str(QuadTex[a][b][5] / 256) + "\nvt " +\
			str(QuadTex[a][b][6] / 256) + " " + \
			str(QuadTex[a][b][7] / 256) + "\n"
		
	Out += "usemtl Texture\n"
	Out += "s off\n"
	
	
	for b in range(0, TriCounts[a]):
		Out += "f "
		Out += str(Tris[a][b][0] + VertIndex) + "/" +\
			str(TexIndex) + " "
		Out += str(Tris[a][b][1] + VertIndex) + "/" +\
			str(TexIndex+1) + " "
		Out += str(Tris[a][b][2] + VertIndex) + "/" +\
			str(TexIndex+2)
		TexIndex += 3
		Out += "\n"
	
	for b in range(0, QuadCounts[a]):
		Out += "f "
		Out += str(Quads[a][b][0] + VertIndex) + "/" +\
			str(TexIndex) + " "
		Out += str(Quads[a][b][1] + VertIndex) + "/" +\
			str(TexIndex+1) + " "
		Out += str(Quads[a][b][2] + VertIndex) + "/" +\
			str(TexIndex+2) + " "
		Out += str(Quads[a][b][3] + VertIndex) + "/" +\
			str(TexIndex+3)
		TexIndex += 4
		Out += "\n"
	VertIndex += VertexCounts[a]

if args.output == "screen":
	print (Out)
else:
	objFile = open(args.output, mode='w')
	objFile.write(Out)
	objFile.close()
	if args.silent == False:
		print ("Done!")