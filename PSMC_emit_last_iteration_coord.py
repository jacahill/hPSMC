import sys,os
from optparse import OptionParser
import datetime

file=open(sys.argv[-1])

### Flag controlled defaults, defined as common values for human analyses ###
MU=0.000000001
GENERATION_TIME=25
STEP=10

### Nonsense values and check flags, these will be reset when the program reaches iteration 25 ###
N0=0
last_itr="F"


### OPTIONS ###
usage = "usage: python %prog [options] input.psmc > outfile.sh"
parser = OptionParser(usage=usage)

parser.add_option("-m", "--mu", type="float", dest="MU", help="Mutation rate per site per year, default=0.000000001, 10^-9")
parser.add_option("-g", "--generation_time", type="int", dest="GENERATION_TIME", help="Generation time in years, default=25")
parser.add_option("-s", "--step", type="int", dest="STEP", help="The bin size used to generate the psmcfa file, default=10, Note: PSMC default is 100, smaller bins recommended for hPSMC")
(options, args) = parser.parse_args()

### SET OPTIONS ###
if options.MU != None:
	MU=options.MU
if options.GENERATION_TIME != None:
	GENERATION_TIME=options.GENERATION_TIME
if options.STEP != None:
	STEP=options.STEP



last_itr="F"

line=file.readline()
while line:
	data=line.split("\t")
	if data==["RD","25\n"]:
		last_itr="T"
	if last_itr=="T" and data[0]=="TR":
		N0=(float(data[1]))/(4*MU*GENERATION_TIME)/STEP
	if last_itr=="T" and data[0]=="RS":
		#T_k = 2N_0 * t_k * Generation time, t_k is column 3 (base 1)
		T_k = 2*N0 * float(data[2]) * GENERATION_TIME

		#N_k = N_0 * \lambda_k, \lambda_k is column 4 (base 1)
		N_k = N0 * float(data[3])
		print T_k, N_k
	line=file.readline()
	
if last_itr=="F":
	sys.stderr.write("Error: Didn't find iteration 25, are you sure PSMC finished running successfully?")
	