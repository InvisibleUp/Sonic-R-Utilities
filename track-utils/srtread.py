##############################################################################
##                                                                          ##
## SRTREAD - Sonic R Track Parser                                           ##
## (c) InvisibleUp 2014                                                     ##
##                                                                          ##
##############################################################################
import os.path
import argparse
import array
from struct import *
		

## Defines
#######################
ModelFileSize = 0
filecounter = 0
noParts = 0

## Init
#######################
parser = argparse.ArgumentParser(
	description='Reads Sonic R tracks and dumps it to the screen.')
parser.add_argument('model',
	help='.BIN file containing track (usually XXX_h.bin)')
#parser.add_argument('animation',
#	help='.BIN file containing animation (usually XanX.bin)')
#parser.add_argument('-f', metavar="FRAME", default=0, nargs='?', type=int,
#	help='Frame # to render. Default 0')
args = parser.parse_args()
	
# Load model
print ("Loading track ", args.model, "...", sep="")
try:
	SRTfile = open(args.model, mode='rb')
except OSError:
	print ("Error loading track", args.model)
	# Dump back to command line
	raise SystemExit

ModelFileSize = os.stat(args.model).st_size
#if args.silent == False:
#	print ("Checking validity...")
if (ModelFileSize % 2 != 0):
	print ("Bad model! (Size should be divisible by 2.)")
	raise SystemExit
	
SRT = array.array('B')
SRTfile.seek(0x00,0)
SRT.fromfile(SRTfile, ModelFileSize) 
SRTfile.close()

def readDword(filecounter):
	temp = []
	for k in range(0, 4):
		temp.append(SRT[filecounter])
		#print(temp, hex(filecounter))
		filecounter += 1
	temp = bytes(temp)
	temp = unpack('L', temp)
	temp = temp[0]
	print(hex(filecounter - 4), hex(temp))
	return [filecounter, temp]
	
def readWord(filecounter):
	temp = []
	for k in range(0, 2):
		temp.append(SRT[filecounter])
		filecounter += 1
	#print(temp)
	temp = bytes(temp)
	temp = unpack('H', temp)
	temp = temp[0]
	print(hex(filecounter - 2), hex(temp))
	return [filecounter, temp]
	
def readByte(filecounter):
	temp = []
	temp.append(SRT[filecounter])
	filecounter += 1
	temp = bytes(temp)
	temp = unpack('B', temp)
	temp = temp[0]
	print(hex(filecounter - 1), hex(temp))
	return [filecounter, temp]

temp = readDword(filecounter)
filecounter = temp[0]
#print(hex(temp[0]), "\t", hex(temp[1]))

filecounter += (temp[-1] * 0x80) # Skip header/whatever

print ("No. of Track Parts:", end = "\t")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1]
#print(hex(temp[0]), "\t", hex(temp[1]))

for i in range(0, noParts):
	print("\nPart no.", i+1)
	
	print ("X pos:  ", end = "\t")
	filecounter = readDword(filecounter)[0]
	print ("Y pos:  ", end = "\t")
	filecounter = readDword(filecounter)[0]
	print ("Z pos:  ", end = "\t")
	filecounter = readDword(filecounter)[0]
	print ("Angle?: ", end = "\t")
	filecounter = readDword(filecounter)[0]
	print ("No. Points:", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	noPoints = temp[1]
	#print ("Unknown: ", end = "\t")
	#filecounter = readDword(filecounter)[0]
	
	for j in range(0, noPoints):
		print ("Point no.", j+1)
		
		print ("X pos: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("Y pos: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("Z pos: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		
		print ("C Tint: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("M Tint: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("Y Tint: ", end = "\t")
		filecounter = readWord(filecounter)[0]
	
	print ("No. Faces:", end = "\t")
	temp = readDword(filecounter)
	filecounter = temp[0]
	noPoints = temp[1]
	
	for j in range(0, noPoints):
		print ("Face no.", j+1)
		
		print ("Tex Page: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("TL: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("BL: ", end = "\t")
		filecounter = readWord(filecounter)[0]		
		print ("TR: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("BR: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		print ("??: ", end = "\t")
		filecounter = readWord(filecounter)[0]
		
	temp = readDword(filecounter)
	filecounter = temp[0]
	if (temp[1] != 0xffffffff):
		if (temp[1] != 0):
			print ("That is incorrect, Master Belch.")
			raise SystemExit
		while(temp[1] != 0xffffffff):
			temp = readDword(filecounter)
			filecounter = temp[0]
			
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
		