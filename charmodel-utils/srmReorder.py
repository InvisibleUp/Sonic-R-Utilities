##############################################################################
##                                                                          ##
## SRMReorder: Reorders SRM files because no OBJ exporter                   ##
##     in the world is logical enough to let me do this beforehand.         ##
## (c) InvisibleUp 2014                                                     ##
##                                                                          ##
##############################################################################
import argparse
from struct import *
import os.path
import array


## Defines
#######################
VertexCounts = []
TriCounts = []
QuadCounts = []
StartPos = [0]
ModelFileSize = 0

def comboRead(byte1, byte2): # Totally not stolen from my GB emulator. Totally.
	length1 = len(hex(byte1))-2
	length2 = len(hex(byte1))-2
	if length1 != length2:
		raise SystemExit	# Might be a bit harsh
		return -1
	else:
		return (byte1 * (0x10 ** length1))+byte2

## Init
#######################
parser = argparse.ArgumentParser(
	description='Reorders Sonic R character models.')
parser.add_argument('model',
	help='.BIN file containing model (usually XXX_h.bin)')
parser.add_argument('output', nargs='?',
	help='.BIN file to output to. (overwrites input if blank)')
parser.add_argument('order', nargs='+',
	help='Order of parts seperated by spaces. EX: "3 1 2". DO NOT type --order.')
args = parser.parse_args()
if args.output == None:
	args.output = args.model
	
# Load model
print ("Loading model ", args.model, "...", sep="")
try:
	SRMfile = open(args.model, mode='rb')
except OSError:
	print ("Error loading model", args.model)
	# Dump back to command line
	raise SystemExit

ModelFileSize = os.stat(args.model).st_size
#if args.silent == False:
#	print ("Checking validity...")
if (ModelFileSize % 4 != 0):
	print ("Bad model! (Size should be divisible by 4.)")
	raise SystemExit
	
SRM = array.array('B')
SRMfile.seek(0x00,0)
SRM.fromfile(SRMfile, ModelFileSize) 
SRMfile.close()

## Counting
#######################
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
	
	StartPos.append(i)
	
if len(VertexCounts) == 0:
	print ("Bad model! (There should be more than 0 groups.)")
	raise SystemExit
	
## Output
#######################
if (len(args.order) != len(VertexCounts)):
	print ("Bad input! Your order list should match the number of parts in the file. (",len(VertexCounts),")" )
	raise SystemExit

# Debugging
for i in range(0, len(args.order)):
	j = int(args.order[i])
	print(j)
	print(StartPos[i], StartPos[i+1], StartPos[i+1] - StartPos[i])
	print(StartPos[j], StartPos[j+1], StartPos[j+1] - StartPos[j])
	print()

# Write out
try:
	SRMfile = open(args.output, mode='wb')
except OSError:
	print ("ERROR: Output is on read-only disk. Please copy this program\n",
	"and any related files to a disk with write access and try again.")
	# Dump back to command line
	raise SystemExit
	
for i in range(0, len(args.order)):
	j = int(args.order[i])
	for k in range(0, StartPos[j+1] - StartPos[j]):
		SRMfile.write(pack('B', SRM[StartPos[j]+k]))
	
print ("Done!")	
SRMfile.write(pack('l', -1))
SRMfile.close()