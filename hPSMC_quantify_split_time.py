### General Structure ###
## 1) Run hPSMC
## 2) Look at hPSMC output, what is the approximate Ne before it begins to rise to infinite, what is the approximate time range
## 3) Simulate population of presplit Ne with range of split times covering the observed split
## 4) Determine which simulations bracket the hPSMC plot
###
## We will start here with phase 3

### IMPORTS ###
import sys,os
from optparse import OptionParser
import datetime

### DEFAULTS ###
## Set by Flag ##
out="./hPSMC_sim_"
Ne=10000
lower=0
upper=10000000
sims=11
par=1
PSMC="psmc"
ms="ms"
hPSMC="./"

## Hard Coded ##
## ms command ##
N_CHRMS=4
N_REPS=40
GENERATION_TIME=25
N_SITES=5000000
MU=0.000000001  # 10^-9  Mutation rate per year
RECOMB_S=0.00000001  # 10^-8 1CM/MB per site per generation 

## ms2psmcfa command ##
BIN_SIZE=10

### OPTIONS ###
usage = "usage: python %prog [options] input.psmc > outfile.sh"
parser = OptionParser(usage=usage)

parser.add_option("-o", "--out", type="str", dest="out", help="output directory for simulations and prefix all files for the run, default=\"./hPSMC_sim_\"")
parser.add_option("-N", "--Ne", type="int", dest="Ne", help="The ancestral population size to simulate, default=10,000")
parser.add_option("-l", "--lower", type="int", dest="lower", help="lower bound for simulations, the most recent divergence time to be simulated")
parser.add_option("-u", "--upper", type="int", dest="upper", help="upper bound for simulations, the most ancient divergence time to be simulated")
parser.add_option("-s", "--sims", type="int", dest="sims", help="the number of simulations to conduct, simulations will evenly split between high and low, minimum value=2, minimum meaningful value=3")
parser.add_option("-p", "--parallel", type="int", dest="par", help="Number of simulations to run simultaneously")
parser.add_option("-P", "--PSMC", type="str", dest="PSMC", help="If the psmc executable is not in your path give it's location, default = \"psmc\"")
parser.add_option("-m", "--ms", type="str", dest="ms", help="If the ms executable is not in your path give it's location, default = \"ms\"")
parser.add_option("-H", "--hPSMC", type="str", dest="hPSMC", help="If the hPSMC directory is not in your path give it's location, NOTE:  Just the directory not the script.  default = \"./\"") # make a def to check for "/"

(options, args) = parser.parse_args()

### SET OPTIONS ###
if options.out != None:
	out=options.out
if options.Ne != None:
	Ne=options.Ne
if options.lower != None:
	lower=options.lower
if options.upper != None:
	upper=options.upper
if options.sims != None:
	sims=options.sims
	if sims<2:
		sys.stderr.write("Error:  at least 2 simulations are required to estimate divergence time, please reset -s flag to an int >= 2, exiting")
		sys.exit()
	elif sims<3:
		sys.stderr.write("Warning:  This test will only determine whether the input hPSMC run falls between the lower and upper bound.  For more detailed estimation increase the number of simulations with -s")
if options.par != None:
	par=options.par
	if par<1:
		sys.stderr.write("Hint:  For systems with multiple processors increasing the number of simulations run in parallel will improve runtime.  use the -p flag to reset")
if options.PSMC != None:
	PSMC=options.PSMC
if options.ms != None:
	ms=options.ms
if options.hPSMC != None:
	hPSMC=options.hPSMC


### FUNCTIONS ###	

def ms_command(YEARS):
	THETA = 4 * Ne * GENERATION_TIME * MU * N_SITES	
	RECOMB = 4 * Ne * RECOMB_S * N_SITES
	SPLIT = (float(YEARS) / GENERATION_TIME) / (4 * float(Ne))
	MS_NAME = out+str(YEARS)+".ms_sim"
	print ms, N_CHRMS, N_REPS, "-p 8 -t", THETA, "-r", RECOMB, N_SITES, "-I 2 2 2 -ej", SPLIT, "2 1 >", MS_NAME, "&"
	return MS_NAME



### BODY ###

## make header ###

now = datetime.datetime.now()
print "#!/bin/bash/"
print ""
print "### File created:", now.strftime("%Y-%m-%d %H:%M")
print "### Using Command:", " ".join(sys.argv)
print ""


## build ms simulations ##
print "### Begin ms simulations ###"
step_size=(float(upper)-float(lower))/float(sims-1)
i=0
sim_names=[]   # I'm saving the simulation file names to avoid rounding errors
while i<sims:
	YEARS=lower+int(i*step_size)
	sim_names.append(ms_command(YEARS))
	i+=1
	if i%par==0:
		print "wait"
if i%par!=0:
	print "wait"
print ""


## convert ms to psmcfa ##
print "### Convert ms to psmcfa format ###"
i=0
while i<sims:
	sim_out="python "+hPSMC+"hPSMC_ms2psmcfa.py -b10 -d -c"+str(N_SITES)+" "+sim_names[i]+" > "+sim_names[i]+".psmcfa &"
	print sim_out
	i+=1
	if i%par==0:
		print "wait"
if i%par!=0:
	print "wait"
print ""

## run psmc ##
print "### Run PSMC ###"
i=0
while i<sims:
	sim_out=PSMC+" -N25 -t15 -r5 -p \"4+25*2+4+6\" -o "+sim_names[i]+".psmc "+ sim_names[i] +".psmcfa &"
	print sim_out
	i+=1
	if i%par==0:
		print "wait"
if i%par!=0:
	print "wait"
print ""

## Estimate Divergence time ## 
print "### Estimate Divergence time with hPSMC ###"
# ls 2pop_no_mix_Split_*psmc | python ~/Documents/scripts/hPSMC_compare_sims_to_data.py -i ../../sandbox/ape_shit/bonobo-human.chimp-human.v2.psmc
command = "ls " + out + "*psmc | python " + hPSMC + "hPSMC_compare_sims_to_data.py -i "+ sys.argv[-1] + " > " + out + "result.txt" 
print command
