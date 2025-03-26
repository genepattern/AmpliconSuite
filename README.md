# AmpliconSuite
Wrapping the Amplicon Architect workflow:
1. Starts with PrepareAA
2. Loads PrepareAA results into Amplicon Architect
3. Loads Amplicon Architect results into Amplicon Classifier. 

# Licenses

The modules wrapped in AmpliconSuite-pipeline use the following licenses. Please note that the AmpliconArchitect license specifies that AmpliconArchitect is for research use and does not give license for commerical for-profit use.

<a href = 'https://github.com/AmpliconSuite/AmpliconSuite-pipeline/blob/master/LICENSE'>AmpliconSuite-pipeline license</a> (BSD 2-Clause) <br>
<a href = 'https://github.com/AmpliconSuite/AmpliconArchitect'>AmpliconArchitect license </a>(University of California software license) <br>
<a href = 'https://github.com/AmpliconSuite/AmpliconClassifier/blob/main/LICENSE'>AmpliconClassifier license </a> (BSD 2-Clause) <br> 
 <br> 
Other dependencies used by these modules (e.g. Mosek, samtools, etc.) have their own set of licensing requirements which users should make themselves aware of as needed. The Mosek license requires that users obtain a copy (which is free for academic use) from the Mosek website. More information is available in the installation section.


# Source Code
Prepare AA: https://github.com/jluebeck/PrepareAA <br>
Amplicon Architect: https://github.com/jluebeck/AmpliconArchitect <br>
Amplicon Classifier: https://github.com/jluebeck/AmpliconClassifier <br>


# Running Locally
- If you wish to run this module as a Docker container locally, here are the steps:
1. Pull the Docker image
    - `docker pull genepattern/amplicon-architect`
    - visit https://hub.docker.com/repository/docker/genepattern/amplicon-architect for versions
2. Start running using 'docker run', REQUIRED flags are required. 
    - `docker run genepattern/amplicon-architect:*version tag* python3 run_aa.py` <br>
      REQUIRED: `--input` *ENTER FILEPATH TO INPUTS HERE (TWO FAST Q FILES, OR ONE BAM, OR ONE COMPLETED AA RUN)* <br>
      REQUIRED: `--n_threads` *ENTER THE NUMBER OF THREADS TO USE* <br>
      REQUIRED: `--reference` *ENTER THE REFERENCE GENOME, CHOICES: hg19, GRCh37, GRCh38, hg38, mm10, GRCm38* <br>
      REQUIRED: `--file_prefix` *ENTER THE FILE PREFIX FOR OUTPUTS* <br>
      REQUIRED: `--RUN_AA` *RUN AA AFTER ALIGNMENT, CHOICES: Yes, No* <br>
      REQUIRED: `--RUN_AC` *RUN AC AFTER AA, Choices: Yes, No* <br>
      `--ploidy` *SPECIFY PLOIDY* <br>
      `--purity` *SPECIFY PURITY* <br>
      `--cnvkit_segmentation` *CHOOSE CNVKIT SEGMENTATION TYPE, CHOICES: cbs, haar, hmm, hmm-tumor, hmm-germline, none.* <br>
      `--AA_seed` *SPECIFY THE SEED USED FOR AA* <br>
      `--cnv_bed` *FILEPATH TO BED FILE* <br>
      `--metadata` *FILEPATH TO METADATA JSON FILE* <br>
      `--normal_bam` *If the bam file provided is sorted or normal. Choices: Yes, No* <br>
    - Example run script: <br> `docker run genepattern/amplicon-architect:v2.11 python3 run_aa.py --input /home/user/edwin5588/SRR8788972_1.fastq /home/user/edwin5588/SRR8788972_2.fastq --n_threads 4 --reference GRCh38 --file_prefix SRR8788972 --RUN_AA Yes --RUN_AC Yes`
    - Example run script using Docker, mounting a local data directory: <br> `docker run -v /local_data:/mount_dir genepattern/amplicon-architect:v2.4 python3 run_aa.py --input /mount_dir/SRR8788972_1.fastq /mount_dir/SRR8788972_2.fastq --n_threads 4 --reference GRCh38 --file_prefix SRR8788972 --RUN_AA Yes --RUN_AC Yes`
3. Running using singularity:
    - Running the Docker image using Singularity is similar to the steps above, simply create an .sif file from the Docker tag: <br>
        - Example: `singularity pull -F --disable-cache docker://genepattern/amplicon-architect:v2.4`
    - Next, run Amplicon Suite using Singularity. The arguments are the same as listed above. <br>
        - Example run using Singularity: `singularity exec amplicon-architect_v2.4.sif python3 /opt/genepatt/run_aa.py --input /home/user/edwin5588/SRR8788972_1.fastq /home/user/edwin5588/SRR8788972_2.fastq --n_threads 4 --reference GRCh38 --file_prefix SRR8788972 --RUN_AA Yes --RUN_AC Yes`
        - Example run using Singularity, mounting a local data directory: <br> `singularity exec --bind /local_data:/mount_dir amplicon-architect_v2.4.sif python3 /opt/genepatt/run_aa.py --input /mount_dir/SRR8788972_1.fastq /mount_dir/SRR8788972_2.fastq --n_threads 4 --reference GRCh38 --file_prefix SRR8788972 --RUN_AA Yes --RUN_AC Yes`

# How to update in case there's a new version of PAA
- Steps:
 1. Clone this repo.
 2. In the Dockerfile, replace the base image (FROM jluebeck/prepareaa:tag) with the latest tag.
 3. Docker build, tag, push to genepattern/amplicon-architect.
 4. Update the manifest, and make a Jenkins release

    
# How to replace Mosek license
- Mosek license has to be replaced every year. We need a new license for it every year and it's copied into the docker image.
- The mosek license used to be on the GPUcsd server, but because AmpliconSuite also has to be ran on Cloud, it was decided it's easier to include it in the Docker image instead so we don't have to do this process on two servers. 
- Steps:
  1. Download the new mosek license.
  2. Clone this repo. 
  3. Copy mosek.lic into the src directory. 
  4. Uncomment lines 21-22 in the dockerfile.
  5. Build Docker image.
  6. Tag and push to genepattern/amplicon-architect
  7. Update Manifest with new image tag
  8. Do a Jenkins release


# Dependencies and Versioning
- Uses Docker Image: genepattern/amplicon-architect:v2.11
- python 3.9

# Contact
- Edwin Huang: edh021@cloud.ucsd.edu
      
