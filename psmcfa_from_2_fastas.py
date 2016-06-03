import sys,os
from optparse import OptionParser

bin=100
min=50
TV=False


### OPTIONS ###
usage = "usage: python %prog [options] sample1_all.fa sample2_all.fa > outfile.psmcfa"
parser = OptionParser(usage=usage)

parser.add_option("-b", "--bin", type="int", dest="bin", help="number of bases to look for a het in")
parser.add_option("-m", "--min", type="int", dest="min", help="minimum number of called sites to not return an N")
parser.add_option("-T", "--TV", action="store_true", dest="TV", help="Run in Transversion only mode, for Ancient DNA")
(options, args) = parser.parse_args()

### SET OPTIONS ###

if options.bin != None:
	bin=options.bin
if options.min != None:
	min=options.min
	

file1=open(sys.argv[-1])
file2=open(sys.argv[-2])
line1=file1.readline()
line2=file2.readline()

### DEFS ###

def make_chromosome(file_in):
	file=open(file_in)
	line=file.readline()
	chr_seqs=[]
	while line:
		if line[0]==">":
			name=line[1:-1]
			seq=""
		line=file.readline()
		try:
			while line[0] !=">" and line:
				seq+=line[:-1]
				line=file.readline()
		except IndexError:
			pass
		chr_seqs.append(seq)
	if seq != chr_seqs[-1]:
		chr_seqs.append(seq)
	file.close()
	return chr_seqs

	
def chr_names(file_in):
	file=open(file_in)
	line=file.readline()
	names=[]
	while line:
		if line[0]==">":
			names.append(line[:-1])
		line=file.readline()
	file.close()
	return names
	
def fa2psmcfa(samp1,samp2,bin,min):
	i=0
	N=0
	K=0
	first="Y"
	psmcfa=""
	while i<len(samp1) and i<len(samp2):
		if samp1[i]=="N" or samp2[i]=="N":
			N+=1
		elif samp1[i]!=samp2[i]:
			if TV==False:
				K+=1
			else:
				if check_TV(samp1[i],samp2[i])=="Yes":
					K+=1
		if i%bin==0 and first!="Y":
			if N>min:
				psmcfa+="N"
			elif K>0:
				psmcfa+="K"
			else:
				psmcfa+="T"
			N=0
			K=0
		elif i%bin==0 and first=="Y":
			first="N"
		i+=1
	return psmcfa
			

def check_TV(indA, indB):
	tc="No" # tc for type of change, transition=No transversion=Yes
	if indA=="A":
		if indB=="C":
			tc="Yes"
		elif indB=="G":
			tc="No"
		elif indB=="T":
			tc="Yes"
	elif indA=="C":
		if indB=="A":
			tc="Yes"
                elif indB=="G":
                        tc="Yes"
                elif indB=="T":
                        tc="No"
	elif indA=="G":
                if indB=="A":
                        tc="No"
                elif indB=="C":
                        tc="Yes"
                elif indB=="T":
                        tc="Yes"
        elif indA=="T":
                if indB=="A":
                        tc="Yes"
                elif indB=="C":
                        tc="No"
                elif indB=="G":
                        tc="Yes"
	return tc



### BODY ###

sample1=make_chromosome(sys.argv[-1])
#print "first"
sample2=make_chromosome(sys.argv[-2])
#print "second"
scaf_names=chr_names(sys.argv[-1])
#print "third"
#print len(sample1), len(sample2), len(scaf_names)

if len(sample1) != len(sample2) or len(sample1) != len(scaf_names) or len(sample2) != len(scaf_names):
	print "error input files appear to be different lengths"
	sys.exit()
	
count=0
while count < len(scaf_names):
	print scaf_names[count]
	out=fa2psmcfa(sample1[count], sample2[count], bin, min)
	print out
	count+=1
	
	
	
	
