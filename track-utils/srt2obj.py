##############################################################################
##                                                                          ##
## SRT2OBJ - Sonic R Track Converter (vanilla)                              ##
## (c) InvisibleUp 2014-2016                                                ##
##                                                                          ##
##############################################################################
## NOTE: Does not support track tinting. That's... kinda vital. Eh.
import os.path
import argparse
import array
from struct import *
		

## Defines
#######################
ModelFileSize = 0
filecounter = 0
noParts = 0

def readDword(filecounter):
	temp = []
	for k in range(0, 4):
		temp.append(SRT[filecounter])
		#print(temp, hex(filecounter))
		filecounter += 1
	temp = bytes(temp)
	temp = unpack('i', temp)
	temp = temp[0]
#	print(hex(filecounter - 4), hex(temp))
	return [filecounter, temp]
	
def readWord(filecounter):
	temp = []
	for k in range(0, 2):
		temp.append(SRT[filecounter])
		filecounter += 1
	#print(temp)
	temp = bytes(temp)
	temp = unpack('h', temp)
	temp = temp[0]
#	print(hex(filecounter - 2), hex(temp))
	return [filecounter, temp]
	
def readByte(filecounter):
	temp = []
	temp.append(SRT[filecounter])
	filecounter += 1
	temp = bytes(temp)
	temp = unpack('B', temp)
	temp = temp[0]
#	print(hex(filecounter - 1), hex(temp))
	return [filecounter, temp]

# Storage for coordinates	
TrackPart = []
TrackPartTex = []
TrackTexPage = []

DecoPartVtx = []
DecoPartFace = []
DecoPartTri = []
DecoQuadTex = []
DecoTriTex = []
DecoTexPage = []

Sec3Vtx = []
Sec4Vtx = []
Sec5Vtx = []
Sec6Vtx = []
Sec7Vtx = []
Sec8Vtx = []
Sec9Vtx = []

filecounter = 0;

## Init
#######################
parser = argparse.ArgumentParser(
	description='Reads Sonic R tracks and saves it to an OBJ.')
parser.add_argument('model',
	help='.BIN file containing track (usually ends in .bin)')
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
print ("Loading track ", args.model, "...", sep="")
try:
	SRTfile = open(args.model, mode='rb')
except OSError:
	print ("Error loading track", args.model , "\n", OSError)
	# Dump back to command line
	raise SystemExit

FileSize = os.stat(args.model).st_size
if (FileSize % 2 != 0):
	print ("Bad model! (Size should be divisible by 2.)")
	raise SystemExit

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
#print(hex(temp[0]), "\t", hex(temp[1]))

for i in range(0, noParts):
	TrackPart.append([])
	TrackPartTex.append([])
	TrackTexPage.append([])
#	print("\nPart no.", i+1)
	
#	print ("X pos:  ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	AddX = temp[1]
#	print ("Y pos:  ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	AddY = temp[1]
#	print ("Z pos:  ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	AddZ = temp[1]
#	print ("Angle?: ", end = "\t")
	filecounter = readDword(filecounter)[0]
#	print ("No. Points:", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	noPoints = temp[1]
	#print ("Unknown: ", end = "\t")
	#filecounter = readDword(filecounter)[0]
	
	for j in range(0, noPoints):
#		print ("Point no.", j+1, hex(filecounter))
		
#		print ("X pos: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		TrackPart[-1].append(temp[1]+AddX)
#		print ("Y pos: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		TrackPart[-1].append(temp[1]+AddY)
#		print ("Z pos: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		TrackPart[-1].append(temp[1]+AddZ)
		
#		print ("R Tint: ", end = "\t")
		filecounter = readWord(filecounter)[0]
#		print ("G Tint: ", end = "\t")
		filecounter = readWord(filecounter)[0]
#		print ("B Tint: ", end = "\t")
		filecounter = readWord(filecounter)[0]
	
#	print ("No. Faces:", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	noPoints = temp[1]
#	print (noPoints, hex(filecounter-4))
	
	for j in range(0, noPoints):
#		print ("Face no.", j+1, hex(filecounter))
		
#		print ("Tex Page: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		TrackTexPage[-1].append(temp[1])

		
#		print ("TL: ", end = "\t")
		temp = readByte(filecounter)
		filecounter = temp[0]
		TrackPartTex[-1].append(temp[1])
		
		temp = readByte(filecounter)
		filecounter = temp[0]
		TrackPartTex[-1].append(abs(temp[1] - 255))
		
		
#		print ("BL: ", end = "\t")
		temp = readByte(filecounter)
		filecounter = temp[0]
		TrackPartTex[-1].append(temp[1])
		
		temp = readByte(filecounter)
		filecounter = temp[0]
		TrackPartTex[-1].append(abs(temp[1] - 255))
		
#		print ("TR: ", end = "\t")
		temp = readByte(filecounter)
		filecounter = temp[0]
		TrackPartTex[-1].append(temp[1])
		
		temp = readByte(filecounter)
		filecounter = temp[0]
		TrackPartTex[-1].append(abs(temp[1] - 255))
		
#		print ("BR: ", end = "\t")
		temp = readByte(filecounter)
		filecounter = temp[0]
		TrackPartTex[-1].append(temp[1])
		
		temp = readByte(filecounter)
		filecounter = temp[0]
		TrackPartTex[-1].append(abs(temp[1] - 255))
		
#		print ("???", end = "\t")
		filecounter = readWord(filecounter)[0]
		
	temp = readDword(filecounter)
	filecounter = temp[0]
	if (temp[1] != -1):
		if (temp[1] != 0):
			print ("Error in file. (Track Part ring end != -1.) File may be invalid or corrupt.")
			raise SystemExit
		while(temp[1] != -1):
			temp = readDword(filecounter)
			filecounter = temp[0]

		
print ("No. of Decoration Parts:", end = " ")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1]
print (noParts, hex(filecounter-4))

#raise SystemExit

#filecounter = 0x10bc

for i in range(0, noParts):
	DecoPartVtx.append([])
	DecoPartFace.append([])
	DecoPartTri.append([])
	DecoTriTex.append([])
	DecoQuadTex.append([])
	DecoTexPage.append([])
#	print("\nPart no.", i+1, hex(filecounter))
	
#	print ("Angle?: ")
	filecounter = readDword(filecounter)[0]
	filecounter = readDword(filecounter)[0]
	filecounter = readDword(filecounter)[0]
	filecounter = readDword(filecounter)[0]
	
#	print ("X pos:  ")
	temp = readDword(filecounter)
	filecounter = temp[0]
	AddX = temp[1]
#	print ("Y pos:  ")
	temp = readDword(filecounter)
	filecounter = temp[0]
	AddY = temp[1]
#	print ("Z pos:  ")
	temp = readDword(filecounter)
	filecounter = temp[0]
	AddZ = temp[1]
	
#	print ("Unk: ")
	filecounter = readDword(filecounter)[0]
	filecounter = readWord(filecounter)[0]
	
#	print ("No. ???:")
	temp = readDword(filecounter)
	filecounter = temp[0]
	noPoints = temp[1]
#	print (noPoints)
	
	#Fair sanity checking
	if (noPoints < 0):
		print ("This part has an unreasonable number of points. (<0) File may be corrupt. Exiting!")
		raise SystemExit
	if (noPoints > 2000):
		print ("This part has an unreasonable number of points. (>2000) File may be corrupt. Exiting!")
		raise SystemExit
		
	for j in range(0, noPoints):
#		print ("\nTri no.", j+1) ## Triangles. Triangles. Why'd it have to be triangles?
		
		#print ("A: ", end = "")  
		temp = readWord(filecounter)
		filecounter = temp[0]
		DecoPartTri[-1].append(temp[1])
		#print (temp[1])
		
#		print ("B: ", end = "")
		temp = readWord(filecounter)
		filecounter = temp[0]
		DecoPartTri[-1].append(temp[1])
		
#		print ("C: ", end = "")
		temp = readWord(filecounter)
		filecounter = temp[0]
		DecoPartTri[-1].append(temp[1])

#		print ("TA: ", end = "") 		
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoTriTex[-1].append(temp[1])
		
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoTriTex[-1].append(abs(temp[1] - 255))
#		print ("TB: ", end = "") 
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoTriTex[-1].append(temp[1])
		
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoTriTex[-1].append(abs(temp[1] - 255))
#		print ("TC: ", end = "") 
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoTriTex[-1].append(temp[1])
		
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoTriTex[-1].append(abs(temp[1] - 255))
		#print ("Tex. Page: ", end = "")
		temp = readDword(filecounter)
		filecounter = temp[0]
		DecoTexPage[-1].append(temp[1])
		#print(temp[1], end="\t")
		
		
#	print ("No. Quads:", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	noPoints = temp[1] #They're not points, but eh
#	print (noPoints)
	
	#Fair sanity checking
	if (noPoints < 0):
		print ("This part has an unreasonable number of points. (<0) File may be corrupt. Exiting!")
		raise SystemExit
	if (noPoints > 2000):
		print ("This part has an unreasonable number of points. (>2000) File may be corrupt. Exiting!")
		raise SystemExit
		
	for j in range(0, noPoints):
#		print ("Face no.", j+1, hex(filecounter))
		
#		print ("A: ", end = "\t") ## Vtx no.
		temp = readWord(filecounter)
		filecounter = temp[0]
		DecoPartFace[-1].append(temp[1])
#		print ("B: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		DecoPartFace[-1].append(temp[1])
#		print ("C: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		DecoPartFace[-1].append(temp[1])
#		print ("D: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		DecoPartFace[-1].append(temp[1])
		
#		print ("TA: ", end = "\t")
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoQuadTex[-1].append(temp[1])
		
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoQuadTex[-1].append(abs(temp[1] - 255))
#		print ("TB: ", end = "\t")
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoQuadTex[-1].append(temp[1])
		
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoQuadTex[-1].append(abs(temp[1] - 255))
#		print ("TC: ", end = "\t")
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoQuadTex[-1].append(temp[1])
		
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoQuadTex[-1].append(abs(temp[1] - 255))
#		print ("TD: ", end = "\t")
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoQuadTex[-1].append(temp[1])
		
		temp = readByte(filecounter)
		filecounter = temp[0]
		DecoQuadTex[-1].append(abs(temp[1] - 255))
#		print ("Tex Page: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		DecoTexPage[-1].append(abs(temp[1]))
#		print ("Unknown: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		
#	print ("No. Vertices:", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	noPoints = temp[1]
#	print (noPoints)
	
	if (noPoints < 0):
		print ("This part has an unreasonable number of points. (<0) File may be corrupt. Exiting!")
		raise SystemExit
	if (noPoints > 5000):
		print ("This part has an unreasonable number of points. (>5000) File may be corrupt. Exiting!")
		raise SystemExit
	
	for j in range(0, noPoints):
#		print ("Point no.", j+1, hex(filecounter))
	
#		print ("Unk: ", end = "\t")
		#filecounter = readWord(filecounter)[0]
		
	#		print ("X: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		DecoPartVtx[-1].append(temp[1] + AddX)
	#		print ("Y: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		DecoPartVtx[-1].append(temp[1] + AddY)
	#		print ("Z: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		DecoPartVtx[-1].append(temp[1] + AddZ)
		
		filecounter = readByte(filecounter)[0] # R
		filecounter = readByte(filecounter)[0] # G
		filecounter = readByte(filecounter)[0] # B
		filecounter = readByte(filecounter)[0] # 0
		
	#filecounter = readWord(filecounter)[0] # 0
	
## Other sections
# Section 3
print ("No. of Section 3 Parts:", end = " ")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1]
print (noParts, hex(filecounter-4))

for i in range(0, noParts):
	Sec3Vtx.append([])
	#print ("X: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec3Vtx[-1].append(temp[1])
#	print ("Y: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec3Vtx[-1].append(temp[1])
#	print ("Z: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec3Vtx[-1].append(temp[1])
	
# Section 4
print ("No. of Section 4 Parts:", end = " ")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1]
print (noParts, hex(filecounter-4))

for i in range(0, noParts):
	Sec4Vtx.append([])
	#print ("X: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec4Vtx[-1].append(temp[1])
#	print ("Y: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec4Vtx[-1].append(temp[1])
#	print ("Z: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec4Vtx[-1].append(temp[1])
	
# Section 5
print ("No. of Section 5 Parts:", end = " ")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1]
print (noParts, hex(filecounter-4))

for i in range(0, noParts):
	Sec5Vtx.append([])
	#print ("X: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec5Vtx[-1].append(temp[1])
#	print ("Y: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec5Vtx[-1].append(temp[1])
#	print ("Z: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec5Vtx[-1].append(temp[1])
	
# Section6
print ("No. of Section 6 Parts:", end = " ")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1]
print (noParts, hex(filecounter-4))

for i in range(0, noParts):
	Sec6Vtx.append([])
	#print ("X: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec6Vtx[-1].append(temp[1])
#	print ("Y: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec6Vtx[-1].append(temp[1])
#	print ("Z: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec6Vtx[-1].append(temp[1])
	
# Section7
print ("No. of Section 7 Parts:", end = " ")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1]
print (noParts, hex(filecounter-4))

for i in range(0, noParts):
	Sec7Vtx.append([])
	#print ("X: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec7Vtx[-1].append(temp[1])
#	print ("Y: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec7Vtx[-1].append(temp[1])
#	print ("Z: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec7Vtx[-1].append(temp[1])
	
# Section8
print ("No. of Section 8 Parts:", end = " ")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1]
print (noParts, hex(filecounter-4))

for i in range(0, noParts):
	Sec8Vtx.append([])
	#print ("X: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec8Vtx[-1].append(temp[1])
#	print ("Y: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec8Vtx[-1].append(temp[1])
#	print ("Z: ", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	Sec8Vtx[-1].append(temp[1])
	
## Section9
print ("No. of Section 9 Parts:", end = " ")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1] - 1
print (noParts, hex(filecounter-4))

for i in range(0, noParts):
	Sec9Vtx.append([])
	#print ("X: ", end = "\t")
	temp = readWord(filecounter)
	filecounter = temp[0]
	Sec9Vtx[-1].append(temp[1])
#	print ("Y: ", end = "\t")
	temp = readWord(filecounter)
	filecounter = temp[0]
	Sec9Vtx[-1].append(temp[1])
#	print ("Z: ", end = "\t")
	temp = readWord(filecounter)
	filecounter = temp[0]
	Sec9Vtx[-1].append(temp[1])
	
## Convert
#######################
Out = "" 	# The string where we dump everything.
VertIndex = 1
TexIndex = 1
CurrentTex = -1 # Purposefully invalid
PageIndex = 0
Out += "# srt2obj v0.1\nmtllib track.mtl\nusemtl 0\n"

## Track Parts

for a in range(0, len(TrackPart)):
#	print(a, TrackPart[a], len(TrackPart[a]), len(TrackPart[a])%4, "\n")
	Out += "\no Trk" + str(a) + "\n" 	# Start the group
	for b in range(0, len(TrackPart[a]), 3):
		#print ("\t", b)
		Out += "v "
		Out += str(TrackPart[a][b] / 100) + " "
		Out += str(TrackPart[a][b+1] / 100) + " " 
		Out += str(TrackPart[a][b+2] / 100) + " "
		Out += "\n"
		
	for b in range(0, len(TrackPartTex[a]), 2):
		#print ("\t", b)
		Out += "vt "
		Out += str(TrackPartTex[a][b] / 256) + " "
		Out += str(TrackPartTex[a][b+1] / 256) + " " 
		Out += "\n"
		
#	Out += "usemtl Texture\n"
	
	
	for b in range(0, (len(TrackPart[a]) // 3)-2, 2):
		if (CurrentTex != TrackTexPage[a][PageIndex]):
			CurrentTex = TrackTexPage[a][PageIndex]
			Out += "usemtl " + str(CurrentTex) + "\n"
		Out += "f "
		Out += str(b+1 + VertIndex) + "/" + str(3 + TexIndex) + " "
		Out += str(b + VertIndex) + "/" + str(TexIndex) + " "
		Out += str(b+2 + VertIndex) + "/" + str(1 + TexIndex) + " "
		Out += str(b+3 + VertIndex) + "/" + str(2 + TexIndex)
		Out += "\n"
		TexIndex += 4
		PageIndex += 1
	VertIndex += len(TrackPart[a]) // 3
	PageIndex = 0
	
## Decoration Parts

for a in range(0, len(DecoPartVtx)):
	Out += "\no Dec" + str(a) + "\n" 	# Start the group
#	print (a, len(DecoPartVtx[a]))
	for b in range(0, len(DecoPartVtx[a]), 3):
#		print ("\t", b)
		Out += "v "
		Out += str(DecoPartVtx[a][b] / 100) + " "
		Out += str(DecoPartVtx[a][b+1] / 100) + " " 
		Out += str(DecoPartVtx[a][b+2] / 100) + " "
		Out += "\n"
		
	for b in range(0, len(DecoQuadTex[a]), 2):
		#print ("\t", b)
		Out += "vt "
		Out += str(DecoQuadTex[a][b] / 256) + " "
		Out += str(DecoQuadTex[a][b+1] / 256) + " " 
		Out += "\n"
	for b in range(0, len(DecoTriTex[a]), 2):
		#print ("\t", b)
		Out += "vt "
		Out += str(DecoTriTex[a][b] / 256) + " "
		Out += str(DecoTriTex[a][b+1] / 256) + " " 
		Out += "\n"
		
	for b in range(0, len(DecoPartFace[a]), 4):
		if (CurrentTex != DecoTexPage[a][PageIndex]):
			#print(a, DecoTexPage[a])
			CurrentTex = DecoTexPage[a][PageIndex]
			Out += "usemtl " + str(CurrentTex) + "\n"
		Out += "f "
		Out += str(DecoPartFace[a][b] + VertIndex) + "/" + str(TexIndex) + " "
		Out += str(DecoPartFace[a][b+1] + VertIndex) + "/" + str(TexIndex + 1) + " "
		Out += str(DecoPartFace[a][b+2] + VertIndex) + "/" + str(TexIndex + 2) + " "
		Out += str(DecoPartFace[a][b+3] + VertIndex) + "/" + str(TexIndex + 3)
		TexIndex += 4
		Out += "\n"
	for b in range(0, len(DecoPartTri[a]), 3):
		#print(len(DecoPartTri[a]))
		if (CurrentTex != DecoTexPage[a][PageIndex]):
			CurrentTex = DecoTexPage[a][PageIndex]
			Out += "usemtl " + str(CurrentTex) + "\n"
		Out += "f "
		Out += str(DecoPartTri[a][b] + VertIndex) + "/" + str(TexIndex) + " "
		Out += str(DecoPartTri[a][b+1] + VertIndex) + "/" + str(TexIndex+1) + " "
		Out += str(DecoPartTri[a][b+2] + VertIndex) + "/" + str(TexIndex+2) + " "
		TexIndex += 3
		Out += "\n"
	PageIndex += 0	
	VertIndex += len(DecoPartVtx[a]) // 3
	
# Other sections
Out += "\no Sec3\n" 	# Start the group
for a in range(0, len(Sec3Vtx)):
	for b in range(0, len(Sec3Vtx[a]), 3):
#		print ("\t", b)
		Out += "v "
		Out += str(Sec3Vtx[a][b] / 100) + " "
		Out += str(Sec3Vtx[a][b+1] / 100) + " " 
		Out += str(Sec3Vtx[a][b+2] / 100) + " "
		Out += "\n"
		
Out += "\no Sec4\n" 	# Start the group
for a in range(0, len(Sec4Vtx)):
	for b in range(0, len(Sec4Vtx[a]), 3):
#		print ("\t", b)
		Out += "v "
		Out += str(Sec4Vtx[a][b] / 100) + " "
		Out += str(Sec4Vtx[a][b+1] / 100) + " " 
		Out += str(Sec4Vtx[a][b+2] / 100) + " "
		Out += "\n"

Out += "\no Sec5\n" 	# Start the group
for a in range(0, len(Sec5Vtx)):
	for b in range(0, len(Sec5Vtx[a]), 3):
#		print ("\t", b)
		Out += "v "
		Out += str(Sec5Vtx[a][b] / 100) + " "
		Out += str(Sec5Vtx[a][b+1] / 100) + " " 
		Out += str(Sec5Vtx[a][b+2] / 100) + " "
		Out += "\n"
		
Out += "\no Sec6\n" 	# Start the group
for a in range(0, len(Sec6Vtx)):
	for b in range(0, len(Sec6Vtx[a]), 3):
#		print ("\t", b)
		Out += "v "
		Out += str(Sec6Vtx[a][b] / 100) + " "
		Out += str(Sec6Vtx[a][b+1] / 100) + " " 
		Out += str(Sec6Vtx[a][b+2] / 100) + " "
		Out += "\n"
		
Out += "\no Sec7\n" 	# Start the group
for a in range(0, len(Sec7Vtx)):
	for b in range(0, len(Sec7Vtx[a]), 3):
#		print ("\t", b)
		Out += "v "
		Out += str(Sec7Vtx[a][b] / 100) + " "
		Out += str(Sec7Vtx[a][b+1] / 100) + " " 
		Out += str(Sec7Vtx[a][b+2] / 100) + " "
		Out += "\n"

Out += "\no Sec8\n" 	# Start the group		
for a in range(0, len(Sec8Vtx)):
	for b in range(0, len(Sec8Vtx[a]), 3):
#		print ("\t", b)
		Out += "v "
		Out += str(Sec8Vtx[a][b] / 100) + " "
		Out += str(Sec8Vtx[a][b+1] / 100) + " " 
		Out += str(Sec8Vtx[a][b+2] / 100) + " "
		Out += "\n"

Out += "\no Sec9\n" 	# Start the group		
for a in range(0, len(Sec9Vtx)):
	for b in range(0, len(Sec9Vtx[a]), 3):
#		print ("\t", b)
		Out += "v "
		Out += str(Sec9Vtx[a][b] / 100) + " "
		Out += str(Sec9Vtx[a][b+1] / 100) + " " 
		Out += str(Sec9Vtx[a][b+2] / 100) + " "
		Out += "\n"

if args.output == "screen":
	print (Out)
else:
	objFile = open(args.output, mode='w')
	objFile.write(Out)
	objFile.close()
	if args.silent == False:
		print ("Done!")
