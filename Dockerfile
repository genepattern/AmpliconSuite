# Parent image is the Amplicon-Architect-Environment
# https://hub.docker.com/r/jluebeck/prepareaa/tags
FROM jluebeck/prepareaa:v1.3.7

USER root
RUN mkdir -p /opt/genepatt
RUN mkdir -p /opt/genepatt/extracted
# COPY the wrapper script over
COPY src/run_aa.py /opt/genepatt
COPY src/download_ref.sh /opt/genepatt
COPY src/sample_metadata_skeleton.json /opt/genepatt
# ENV MOSEKLM_LICENSE_FILE=/expanse/projects/mesirovlab/genepattern/servers/ucsd.prod/mosek/8/licenses/
RUN mkdir -p /home/aa_user/mosek
RUN chmod -R 777 /opt/genepatt/*
RUN chmod -R 777 /opt/genepatt/extracted
RUN chmod -R 777 /home/*
RUN chmod -R 777 /home/aa_user/


# Copy local mosek.lic file, for testing only
# COPY src/mosek.lic /home/mosek/
# COPY src/mosek.lic /home/aa_user/mosek/

# ENV MOSEKLM_LICENSE_FILE=/home/mosek

## python3 /files/src/run_aa.py --input /files/AA_bam_files_test/input_list.txt --n_threads 2 --reference hg19 --RUN_AA Yes --RUN_AC Yes --AA_runmode FULL
