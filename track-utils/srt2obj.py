##############################################################################
##                                                                          ##
## SRT2OBJ - Sonic R Track Converter (vanilla)                              ##
## (c) InvisibleUp 2014                                                     ##
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
	temp = unpack('l', temp)
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
DecoPart = []
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

print ("No. of Track Parts:", end = "\t")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1]
print (noParts, hex(filecounter-4))
#print(hex(temp[0]), "\t", hex(temp[1]))

for i in range(0, noParts):
	TrackPart.append([])
	TrackPartTex.append([])
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
		
#		print ("C Tint: ", end = "\t")
		filecounter = readWord(filecounter)[0]
#		print ("M Tint: ", end = "\t")
		filecounter = readWord(filecounter)[0]
#		print ("Y Tint: ", end = "\t")
		filecounter = readWord(filecounter)[0]
	
#	print ("No. Faces:", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	noPoints = temp[1]
#	print (noPoints, hex(filecounter-4))
	
	for j in range(0, noPoints):
#		print ("Face no.", j+1, hex(filecounter))
		
#		print ("Tex Page: ", end = "\t")
		## NOTE: We NEED this. Figure that out.
		filecounter = readWord(filecounter)[0]
		
#		print ("TL: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		TrackPartTex[-1].append(temp[1])
#		print ("BL: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		TrackPartTex[-1].append(temp[1])	
#		print ("TR: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		TrackPartTex[-1].append(temp[1])
#		print ("BR: ", end = "\t")
		temp = readWord(filecounter)
		filecounter = temp[0]
		TrackPartTex[-1].append(temp[1])
		
#		print ("??: ", end = "\t")
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
## Let's skip this for now. Sorry. :/
'''			
print ("\nNo. of Decoration Parts:", end = "\t")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1]

#raise SystemExit

#filecounter = 0x10bc

for i in range(0, noParts):
	print("\nPart no.", i+1)
	
	print ("Angle?: ", end = "\t")
	filecounter = readDword(filecounter)[0]
	filecounter = readDword(filecounter)[0]
	filecounter = readDword(filecounter)[0]
	filecounter = readDword(filecounter)[0]
	
	print ("X pos:  ", end = "\t")
	filecounter = readDword(filecounter)[0]
	print ("Y pos:  ", end = "\t")
	filecounter = readDword(filecounter)[0]
	print ("Z pos:  ", end = "\t")
	filecounter = readDword(filecounter)[0]
	
	print ("Unk: ", end = "\t")
	filecounter = readDword(filecounter)[0]
	filecounter = readWord(filecounter)[0]
	
	print ("No. ???:", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	noPoints = temp[1] #WHAT ARE THESE?
	print (noPoints)
	
	#Fair sanity checking
	if (noPoints < 0):
		raise SystemExit
	if (noPoints > 1000):
		raise SystemExit
		
	for j in range(0, noPoints):
		print ("??? no.", j+1)
		
		print ("A: ", end = "\t")
		filecounter = readDword(filecounter)[0]
		print ("B: ", end = "\t")
		filecounter = readDword(filecounter)[0]
		print ("C: ", end = "\t")
		filecounter = readDword(filecounter)[0]
		print ("D: ", end = "\t")
		filecounter = readDword(filecounter)[0]
		
		
	print ("No. Quads:", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	noPoints = temp[1] #They're not points, but eh
	print (noPoints)
	
	#Fair sanity checking
	if (noPoints < 0):
		raise SystemExit
	if (noPoints > 1000):
		raise SystemExit
		
	for j in range(0, noPoints):
		print ("Face no.", j+1)
		
		print ("A: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("B: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("C: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("D: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("TA: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("TB: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("TC: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("TD: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("Tex Page: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("Unknown: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		
	print ("No. Vertices:", end = "\t")
	temp = readWord(filecounter)
	filecounter = temp[0]
	noPoints = temp[1]
	
	if (noPoints < 0):
		raise SystemExit
	if (noPoints > 1000):
		raise SystemExit
	
	for j in range(0, noPoints):
		print ("Point no.", j+1)
		
		print ("Unk: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("X: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("Y: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("Z: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("Unk: ", end = "\t")
		filecounter = readWord(filecounter)[0]
	print ("Unk: ", end = "\t")
	filecounter = readWord(filecounter)[0]
'''
## Convert
#######################
Out = "" 	# The string where we dump everything.
VertIndex = 1
TexIndex = 1
Out += "# srt2obj v0.1\n\n"

for a in range(0, len(TrackPart)):
#	print(a, TrackPart[a], len(TrackPart[a]), len(TrackPart[a])%4, "\n")
	Out += "\no Grp" + str(a) + "\n" 	# Start the group
	for b in range(0, len(TrackPart[a]), 3):
		#print ("\t", b)
		Out += "v "
		Out += str(TrackPart[a][b] / 100) + " "
		Out += str(TrackPart[a][b+1] / 100) + " " 
		Out += str(TrackPart[a][b+2] / 100) + " "
		Out += "\n"
		
##	Out += "usemtl Texture\n"
##	Out += "s off\n"
	
	
	for b in range(0, (len(TrackPart[a]) // 3)-2, 2):
		Out += "f "
		Out += str(b+1 + VertIndex) + " "
		Out += str(b + VertIndex) + " "
		Out += str(b+2 + VertIndex) + " "
		Out += str(b+3 + VertIndex)
##		TexIndex += 4
		Out += "\n"
	VertIndex += len(TrackPart[a]) // 3

##if args.output == "screen":
#	print (Out)
else:
	objFile = open(args.output, mode='w')
	objFile.write(Out)
	objFile.close()
	if args.silent == False:
		print ("Done!")