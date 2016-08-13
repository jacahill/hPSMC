#Use of these scripts
All scripts provided here are available for free use for personal or acadmeic usage without any warentee. I have tested these scripts on my own hardware but cannot guarentee that it is compatible with other hardware or software.  If you use this program in a publication we ask that you cite our paper (http://rstb.royalsocietypublishing.org/content/371/1699/20150138.abstract).

# hPSMC
Tools for F1 hybrid PSMC (hPSMC) divergence time inference from whole genomes


1) Create an hPSMC .psmcfa input file from two samples 

haploidize each bam file to a fasta.  I use R. Ed Green's pu2fa program available here- 
https://github.com/Paleogenomics/Chrom-Compare
	
Usage:  For each chromosome run:

	samtools mpileup -s -f REF\_GENOME -q30 -Q60 -r CHROMOSOME BAMFILE.bam | \
	pu2fa -c CHROMOSOME -C MAX\_COVERAGE > haploidized_fasta.fa
	
The very high basequality threshold "-Q60" is useful for minimizing the impact of sequencing error.

Then concatenate all of the single chromosome fastas into a single fasta.

	cat haploidized_fasta_scaffold*.fa > haploidized_fasta_all.fa
	
combine fasta sequences from two individuals into a single .psmcfa file.

	python psmcfa_from_2_fastas.py -b10 -m5 sample1_all.fa sample2_all.fa > hPSMC.psmcfa
	
2) run psmc using the hPSMC.psmcfa

We ran PSMC under default settings. See https://github.com/lh3/psmc

	psmc -N25 -t15 -r5 -p "4+25*2+4+6" -o hPSMC.psmc hPSMC.psmcfa

3) Visualize hPSMC.psmc and estimate pre-diverence population size.
Standard PSMC method.
	
	psmc_directory/utils/psmc_plot.pl hPSMC hPSMC.psmc
		
Alternative script included here. The -s -g and -m flags show their default values.
	
	python hPSMC/PSMC_emit_last_iteration_coord.py -s10 -g25 -m0.000000001 hPSMC.psmc
	
Once we have plotted the psmc result using one of the two above methods estimate the pre-divergence population size which will be input for step 4.
		

4) Run simulations of divergence without post-divergence migration to compare to the hPSMC plot

	In order to interpret hPSMC results we need to compare our data to simulations.  A purely visual interpreation of hPSMC output plots is susceptible to user bias and not replicable. To conduct simulations the user should estimate the ancestral population size (step 3) and estimate a recent and ancient bound for when the sample might have diverged.  
	
		python hPSMC/hPSMC_quantify_split_time.py -OPTIONS
			OPTIONS:
			-h print help message with user options
			-o OUT, --out=OUT     output directory for simulations and prefix all files for the run, default="./hPSMC_sim_"
			-N NE, --Ne=NE        The ancestral population size to simulate, default=10,000
			-l LOWER, --lower=LOWER		lower bound for simulations, the most recent divergence time to be simulated
			-u UPPER, --upper=UPPER		upper bound for simulations, the most ancient divergence time to be simulated
			-s SIMS, --sims=SIMS  the number of simulations to conduct, simulations will evenly split between high and low, minimum value=2, minimum meaningful value=3
			-p PAR, --parallel=PAR		Number of simulations to run simultaneously
			-P PSMC, --PSMC=PSMC  If the psmc executable is not in your path give it's location, default = "psmc"
			-m MS, --ms=MS        If the ms executable is not in your path give it's location, default = "ms"
			-H HPSMC, --hPSMC=HPSMC
			If the hPSMC directory is not in your path give it's location, NOTE:  Just the directory not the script.  default = "./"


5) Plot simulations using either method in step 3, with the orignal data to show the divergence between samples.  
	A) Compare simulations' pre-divergence Ne to your data, if they converge the simulations are appropriate, if not reestimate Ne and repeat steps 3-5
	B) Identify the range of values for divergence time that intersect your hPSMC plot between 1.5 and 10 times pre-divergence Ne.  These are your simulations consistent with data.  Your diverence time estimate is the narrowest range of inconsistent simulations surrounding the consistent simulations. 
	
Important Warning:  When you run simulations with ms be sure that it is set to output enough decimal points for the mutation locations.  By default ms outputs 5 decimal places which is enough to 100,000 bins.  Recent versions of ms include the -p flag which allows you to set the number of decimal places to report.  I recommend using -p8 in most cases.  My most recent versions of these programs assume that you have the most recent ms and that you are using the -p flag.
