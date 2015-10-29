### JAC 6/4/2014 ###

### ms2psmcfa.py ###
### Objective:  Convert ms output to psmcfa

### Draft 1 assmuptions:
### If there a multiple simulations all chromosomes will be of the same length
### All chromosomes will be simulated twice (once for each chromosome of a diploid individual)




## Main Text

# Imports
import sys,os
from optparse import OptionParser
import random

#Globals
chr_len=10000000
pseudo_chr_number=1
bin_size=100

# Open File
file = open(sys.argv[-1])
line = file.readline()

### OPTIONS ###
parser = OptionParser()
parser.add_option("-b", "--bin_size", type="int", dest="bin_size")
parser.add_option("-d", action="store_true", dest="haploidize", default=False)
parser.add_option("-c", "--chr_len", type="int", dest="chr_len")
(options, args) = parser.parse_args()

### SET OPTIONS ###

if options.bin_size != None:
	bin_size=options.bin_size
if options.chr_len != None:
	chr_len=options.chr_len



### To be added:  
### Loop to test assumptions reads command line and bails if nsamples != 2

# total number of bins to output = chr_size/bin_size
# a bin then is 1/number of bins to output
bin_dist=(1.0/(chr_len/bin_size))

### Read Chromosome ###

def haploidize(ind1,ind2):
	out=""
	i=0
	while i<len(ind1) and i<len(ind2):
		flip=random.randint(0,1)
		if flip==0:
			out+=ind1[i]
		elif flip==1:
			out+=ind2[i]
		i+=1
	return out

def read_chr(line):
	data=[]
	while line[0:10] != "positions:":
		line=file.readline()
	segsites=line.split(" ")  ### Split the line that tells you where the variable sites are into a list
	data.append(segsites[1:-1])
	line=file.readline()
	chrA=line
	line=file.readline()
	chrB=line
	if options.haploidize==True:
		line=file.readline()
		chrC=line
		line=file.readline()
		chrD=line
		chrA=haploidize(chrA,chrB)
		chrB=haploidize(chrC,chrD)
	data.append(chrA[:-1])
	data.append(chrB[:-1])
	return data #[[segsites],chrA,chrB]



### BODY ###
chr_number=1

while line:
	chr=read_chr(line)
	out=""
	spot=0 # where you are in the ms file
	bin=0  # where you are in the chromosome bins range form bin*bin_dist to bin_dist*(bin+1) not including the maximum
	state="T" # have we seen a het site in the bin
	while spot < len(chr[0]):
		if float(chr[0][spot]) > bin_dist*(bin+1):
			out+=state
			state="T"
			bin+=1
		else:
			if chr[1][spot]==chr[2][spot]:
				spot+=1
			elif chr[1][spot]!=chr[2][spot]:
				state="K"
				spot+=1
	while bin_dist*(bin+1)<=1.0:
		out+="T"
		bin+=1
	
	header=">chr"+str(chr_number)
#	print len(header), chr[0][0:10], bin_dist
#	print len(out), out[0:10]
	line=file.readline()
	print header
	print out	

	
