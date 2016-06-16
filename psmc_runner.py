import sys,os
from optparse import OptionParser

### Pipeline:
## bam2fq
#samtools mpileup -C50 -uf ref.fa aln.bam | bcftools view -c - | vcfutils.pl vcf2fq -d 10 -D 100 | gzip > diploid.fq.gz

## psmc main run
#    utils/fq2psmcfa -q20 diploid.fq.gz > diploid.psmcfa
#    psmc -N25 -t15 -r5 -p "4+25*2+4+6" -o diploid.psmc diploid.psmcfa
#    utils/psmc2history.pl diploid.psmc | utils/history2ms.pl > ms-cmd.sh
#    utils/psmc_plot.pl diploid diploid.psmc

## Bootstrapping
#    utils/fq2psmcfa -q20 diploid.fq.gz > diploid.psmcfa
#        utils/splitfa diploid.psmcfa > split.psmcfa
#    psmc -N25 -t15 -r5 -p "4+25*2+4+6" -o diploid.psmc diploid.psmcfa
#        seq 100 | xargs -i echo psmc -N25 -t15 -r5 -b -p "4+25*2+4+6" -o round-{}.psmc split.fa | sh
#    cat diploid.psmc round-*.psmc > combined.psmc
#        utils/psmc_plot.pl -pY50000 combined combined.psmc
 

### DEFINES ###

dir="./"
o_dir="./"
psmc_home="/Users/jamescahill/programs/psmc-master/"
C50=0
ref="/mnt/tank/genomes/Polar_Bear/Ursus_maritimus.scaf.fa"
sampath="/Users/jamescahill/programs/samtools-0.1.19/"
threads=4


### OPTIONS ###
usage = "usage: python %prog [options] FILE_PREFIX"
parser = OptionParser(usage=usage)
parser.add_option("-d", "--dir", type="string", dest="dir", help="directory with fastas, include slash")
parser.add_option("-o", "--out_dir", type="string", dest="o_dir", help="directory for output files, include slash")
parser.add_option("--home", type="string", dest="psmc_home", help="directory where psmc lives, should contian utils subdirectory and argument should include slash")
parser.add_option("--C50", type="int", dest="C50", help="if you want to use C50 enter --C50=1 otherwise by default it is excluded")
parser.add_option("-r", "--ref", type="string", dest="ref", help="full path and name of ref genome.  By default this is set to the polar bear reference on redser")
parser.add_option("-t", "--threads", type="int", dest="threads", help="number of psmc tasks to run in parellel")

(options, args) = parser.parse_args()

### SET OPTIONS ###

if options.dir != None:
	dir=options.dir
	if dir[-1] != "/":
		dir+="/"
if options.o_dir != None:
	o_dir=options.o_dir
	if o_dir[-1] != "/":
		o_dir+="/"
if options.psmc_home != None:
	psmc_home=options.psmc_home
	if psmc_home[-1] != "/":
		psmc_home+="/"
if options.C50 != None:
	C50=1
if options.threads != None:
	threads=options.threads


### BODY ###

## Make i/o names. CLEANING off .bam

PREFIX=o_dir+sys.argv[-1]
if PREFIX[-4:-1]==".bam":
	PREFIX=PREFIX[:-4]
ENTRY=dir+sys.argv[-1]
if ENTRY[-4:-1]==".bam":
	ENTRY=ENTRY[:-4]


### bam2fq ###
if C50==1:
	out="samtools mpileup -C50 -uf "+ref+ " " + ENTRY + ".bam | "+ sampath +"bcftools/bcftools view -c - | "+sampath+"bcftools/vcfutils.pl vcf2fq -d 10 -D 100 | gzip > "+PREFIX+".fq.gz"
elif C50==0:
	out="samtools mpileup -uf "+ref+ " " + ENTRY + ".bam | "+ sampath +"bcftools/bcftools view -c - | "+sampath+"bcftools/vcfutils.pl vcf2fq -d 10 -D 100 | gzip > "+PREFIX+".fq.gz"
 
print out

### psmc_with_bootstrap ###
out=psmc_home+"utils/fq2psmcfa -q20 "+PREFIX+".fq.gz > "+PREFIX+".psmcfa"
print out
out=psmc_home+"utils/splitfa "+PREFIX+".psmcfa > "+PREFIX+".split.psmcfa"
print out
out=psmc_home+"psmc -N25 -t15 -r5 -p \"4+25*2+4+6\" -o "+PREFIX+".psmc "+PREFIX+".psmcfa &"
print out
i=1
while i <= 100:
	out=psmc_home+"psmc -N25 -t15 -r5 -b -p \"4+25*2+4+6\" -o "+PREFIX+".round-"+str(i)+".psmc "+PREFIX+".split.psmcfa &"
	print out
	i+=1
	if i%threads==0:
		print "wait"
if i%threads !=0:
	print "wait"
out="cat "+PREFIX+".psmc "+PREFIX+"*.round-*.psmc > "+PREFIX+".combined.psmc"
print out







