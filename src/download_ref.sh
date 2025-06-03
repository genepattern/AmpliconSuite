#!/bin/bash
echo This is working


# From jluebeck/PrepareAA repo. Setting environmental arguments
REFERENCE=$1
RUN_COMMAND=$2
SAMPLE_NAME=$3
REF_PATH=$4
INPUT_TYPE=$5
MOSEK_PATH=$6
AA_SRC=/home/programs/AmpliconArchitect-master/src
export AA_SRC
AC_SRC=/home/programs/AmpliconClassifier-main
export AC_SRC
MOSEKLM_LICENSE_FILE=$MOSEK_PATH
export MOSEKLM_LICENSE_FILE
NCM_HOME=/home/programs/NGSCheckMate-master/
export NCM_HOME

if [[ "$REF_PATH" != "None" ]]
then
  AA_DATA_REPO=$REF_PATH
  export AA_DATA_REPO
  echo $AA_DATA_REPO
else
  export REFERENCE
  echo "###############################"
  echo DOWNLOADING $REFERENCE NOW .....
  echo "###############################"
  AA_DATA_REPO=$PWD/data_repo
  export AA_DATA_REPO
  mkdir -p $AA_DATA_REPO
  # Download reference genome based on user input
  if [[ "$INPUT_TYPE" == "bam" ]]
  then
    echo "Downloading $REFERENCE.tar.gz now"
    wget -q -P $AA_DATA_REPO https://datasets.genepattern.org/data/module_support_files/AmpliconArchitect/${REFERENCE}.tar.gz
    wget -q -P $AA_DATA_REPO https://datasets.genepattern.org/data/module_support_files/AmpliconArchitect/${REFERENCE}_md5sum.txt
    tar zxf $AA_DATA_REPO/${REFERENCE}.tar.gz --directory $AA_DATA_REPO
    touch $AA_DATA_REPO/coverage.stats && chmod a+r $AA_DATA_REPO/coverage.stats
    echo "###############################"
    echo DOWNLOADING $REFERENCE COMPLETE
    echo "###############################"
    echo -e "\n"
    echo -e "\n"
  elif [[ "$INPUT_TYPE" == "fastq" ]]
  then
    echo "Downloading $REFERENCE _indexed.tar.gz now"
    wget -q -P $AA_DATA_REPO https://datasets.genepattern.org/data/module_support_files/AmpliconArchitect/${REFERENCE}_indexed.tar.gz
    wget -q -P $AA_DATA_REPO https://datasets.genepattern.org/data/module_support_files/AmpliconArchitect/${REFERENCE}_indexed_md5sum.txt
    tar zxf $AA_DATA_REPO/${REFERENCE}_indexed.tar.gz --directory $AA_DATA_REPO
    touch $AA_DATA_REPO/coverage.stats && chmod a+r $AA_DATA_REPO/coverage.stats
    echo "###############################"
    echo DOWNLOADING $REFERENCE COMPLETE
    echo "###############################"
    echo -e "\n"
    echo -e "\n"
  else
    echo "else statement here"
  fi


fi



# ls /home > $PWD/output/docker_home_manifest.log


echo "###############################"
echo RUNNING $RUN_COMMAND
echo "###############################"

eval $RUN_COMMAND

echo "###############################"
echo FINISHED RUNNING PAA
echo "###############################"

echo -e "\n"
echo -e "\n"

# ls -alrt $AA_DATA_REPO
if [[ "$REF_PATH" == "None" ]]
then
  rm -rf $PWD/data_repo
  echo REMOVED DATA REPO
fi
echo -e "\n"
echo -e "\n"
# ls -alrt
tar --exclude="./programs" --exclude="./testdata" --exclude="./input" --exclude="./output" --exclude="*.bam" --exclude="*.fastq*" --exclude="*.fq*" -zcvf ${SAMPLE_NAME}_outputs.tar.gz .

echo Finished Running