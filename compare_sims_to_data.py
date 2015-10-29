### IMPORTS ###
import sys,os
from optparse import OptionParser
import datetime

### DEFAULTS ###
## Set by Flag ##
out="./hPSMC_result.txt"
Ne=10000
input=""
GENERATION_TIME=25

## Hard Coded ##
STEP=10
N_SITES=10000000
MU=0.000000001  # 10^-9  Mutation rate per year
RECOMB_S=0.00000001  # 10^-8 1CM/MB per site per generation 



### OPTIONS ###
usage = "usage: ls Simulation_Prefix_*.psmc | python %prog [options]"
parser = OptionParser(usage=usage)

parser.add_option("-o", "--out", type="str", dest="out", help="output file wiht full name and path, default=\"./hPSMC_result.txt\"")
parser.add_option("-N", "--Ne", type="int", dest="Ne", help="The ancestral population size to simulate, default=10,000")
parser.add_option("-i", "--input", type="str", dest="input", help="The original psmc file to be compared with simulations")
parser.add_option("-g", "--generation_time", type="int", dest="GENERATION_TIME", help="Estimated Generation time in years, default=25")

(options, args) = parser.parse_args()

### SET OPTIONS ###
if options.out != None:
	out=options.out
if options.Ne != None:
	Ne=options.Ne
if options.input != None:
	input=options.input
if options.GENERATION_TIME != None:
	GENERATION_TIME=options.GENERATION_TIME
	
### FUNCTIONS ###
def parse_psmc(sim):
	plot=[[],[],[]]
	plot[0].append(sim)
	file=open(sim)
	line=file.readline()
	while line:
		data=line.split("\t")
		if data[0]=="RD" and data[1]=="25\n":
			while line:
				data=line.split("\t")
				if data[0]=="TR":
					N0=(float(data[1]))/(4*MU*GENERATION_TIME)/STEP
				if data[0]=="RS":
					#T_k = 2N_0 * t_k
					T_k = 2*N0 * float(data[2]) * GENERATION_TIME
					plot[1].append(T_k)
					#N_k = N_0 * \lambda_k
					N_k = N0 * float(data[3])
					plot[2].append(N_k)				
				line=file.readline()
		line=file.readline()
	return plot
	file.close()
		

### BODY ###
original=parse_psmc(input)
simtable=[]
for sim in sys.stdin:
	simtable.append(parse_psmc(sim[:-1]))
print original[1]
print simtable
for sim in simtable:
	print sim
	i=0
	less="F"
	more="F"
	while i<64:
		if Ne*1.5 < float(sim[2][i]) < Ne*10:
			j=0
			min=1000000000000.0
			while j<64:
				best=[0,0]
				dist=float(original[2][j])-float(sim[2][i])
				print dist
				if dist<0:
					dist=dist*-1
				#print dist,min
				if dist<min:
					best=[float(original[1][j]),float(original[2][j])]
					min = dist
					#print min, best[1], float(sim[1][i])
				if float(original[2][j])<Ne*1.5:
					break
				j+=1
			print min, best, float(sim[1][i]), float(sim[2][i])
			if best[0] <= float(sim[1][i]):
				more="T"
			if best[0] >= float(sim[1][i]):
				less="T"
		i+=1
	print sim[0], less, more
		

	
	
