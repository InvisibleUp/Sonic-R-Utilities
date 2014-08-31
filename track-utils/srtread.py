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
	description='Reads Sonic R tracks and dumps info about them to the screen.')
parser.add_argument('model',
	help='.BIN file containing track (usually XXX_h.bin)')
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
if (ModelFileSize % 4 != 0):
	print ("Bad model! (Size should be divisible by 4.)")
	raise SystemExit
	
SRT = array.array('B')
SRTfile.seek(0x00,0)
SRT.fromfile(SRTfile, ModelFileSize) 
SRTfile.close()

def readDword(filecounter):
	temp = []
	for k in range(0, 4):
		temp.append(SRT[filecounter])
		filecounter += 1
	#print(temp)
	temp = bytes(temp)
	temp = unpack('l', temp)
	temp = temp[0]
	print(hex(filecounter - 4), temp)
	return [filecounter, temp]
	
def readWord(filecounter):
	temp = []
	for k in range(0, 2):
		temp.append(SRT[filecounter])
		filecounter += 1
	temp = bytes(temp)
	temp = unpack('h', temp)
	temp = temp[0]
	print(hex(filecounter - 2), temp)
	return [filecounter, temp]

temp = readDword(filecounter)
filecounter = temp[0]

filecounter += (temp[-1] * 0x80) # Skip header/whatever

print ("No. of Track Parts:", end = "\t")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1]

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
	if (temp[1] != -1):
		if (temp[1] != 0):
			print ("That is incorrect, Master Belch.")
			raise SystemExit
		while(temp[1] != -1):
			temp = readDword(filecounter)
			filecounter = temp[0]
			
print ("\nNo. of Decoration Parts:", end = "\t")
temp = readDword(filecounter)
filecounter = temp[0]
noParts = temp[1]

# TODO: Research this.

raise SystemExit