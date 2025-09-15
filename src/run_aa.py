###
# wrapper script to create AmpliconSuite command to be executed inside the container
# Author: Edwin Huang, Jens Luebeck
# Mesirov Lab, Bafna Lab
###

import argparse
import os
import shutil
import tarfile
import zipfile
import json
import pathlib
import sys

def run_paa_single_sample(args):
    """
    Runs Prepare AA for a single sample.
    """
    print(f"Running PrepareAA for sample: {args.file_prefix}")

    RUN_COMMAND = f"python3 /home/programs/AmpliconSuite-pipeline-master/AmpliconSuite-pipeline.py -s {args.file_prefix} -t {args.n_threads} --ref {args.reference}"
    input_type = ""

    # Handle different input types
    if args.bam:
        RUN_COMMAND += f" --sorted_bam {args.bam}"
        input_type = "bam"
        print(f"BAM input: {args.bam}")
    
    elif args.fastqs:
        input_type = "fastq"
        RUN_COMMAND += f" --fastqs {args.fastqs[0]} {args.fastqs[1]}"
        print(f"FASTQ inputs: {args.fastqs[0]}, {args.fastqs[1]}")
    
    elif args.AA_zipped_output:
        # Handle zipped AA results
        AA_results_location = run_ac_helper(args.AA_zipped_output)
        if AA_results_location != "AA_results folder not found":
            RUN_COMMAND += f" --completed_AA_runs {AA_results_location}"
            print(f'Zipped AA results found at: {AA_results_location}')
            return f"bash /opt/genepatt/download_ref.sh {args.reference} '{RUN_COMMAND}' {args.file_prefix} {args.ref_path} zip {args.path_to_mosek}"
        else:
            return "Invalid input - AA_results folder not found in zipped file."
    
    else:
        return "Error: No valid input provided. Must specify --bam, --fastqs, or --AA_zipped_output"

    # Add optional parameters
    if args.RUN_AA == "Yes":
        RUN_COMMAND += " --run_AA"

    if args.RUN_AC == "Yes":
        RUN_COMMAND += " --run_AC"

    if args.ploidy:
        RUN_COMMAND += f" --ploidy {args.ploidy}"

    if args.purity:
        RUN_COMMAND += f" --purity {args.purity}"

    if args.cnvkit_segmentation != 'none':
        RUN_COMMAND += f" --cnvkit_segmentation {args.cnvkit_segmentation}"

    if args.cnv_bed:
        RUN_COMMAND += f" --cnv_bed {args.cnv_bed}"
    else:
        RUN_COMMAND += " --cnvkit_dir /home/programs/cnvkit.py"

    if args.metadata:
        metadata_helper(args)
        RUN_COMMAND += " --sample_metadata sample_metadata.json"

    if args.normal_bam:
        RUN_COMMAND += f" --normal_bam {args.normal_bam}"
    
    if args.sv_vcf and args.sv_vcf != "" and args.sv_vcf != 'None':
        RUN_COMMAND += f" --sv_vcf {args.sv_vcf}"
    
    if args.sv_vcf_no_filter != "No":
        RUN_COMMAND += " --sv_vcf_no_filter"
    
    if args.AA_runmode:
        RUN_COMMAND += f" --AA_runmode {args.AA_runmode}"
    
    if args.RUN_AA == 'Yes' and args.AA_extendmode != "":
        RUN_COMMAND += f" --AA_extendmode {args.AA_extendmode}"

    if args.AA_insert_sdevs:
        RUN_COMMAND += f" --AA_insert_sdevs {args.AA_insert_sdevs}"
    
    if args.foldback_pair_support_min:
        RUN_COMMAND += f" --foldback_pair_support_min {args.foldback_pair_support_min}"
    
    if args.downsample: 
        RUN_COMMAND += f" --downsample {args.downsample}"

    if args.no_filter != "No":
        RUN_COMMAND += " --no_filter"

    if args.no_QC != 'No':
        RUN_COMMAND += " --no_QC"
    
    if (args.cngain != 4.5) and (args.cngain > 0):
        RUN_COMMAND += f" --cngain {args.cngain}"

    if (args.cnsize_min != 50000) and (args.cnsize_min > 0):
        RUN_COMMAND += f" --cnsize_min {args.cnsize_min}"

    if args.upload:
        RUN_COMMAND += f" --project_uuid {args.project_uuid}  --project_key {args.project_key} --username {args.username}  --upload"

    # Set AA_SEED environment variable
    os.environ['AA_SEED'] = str(args.AA_seed)
    print(f"AA_SEED is set as: {os.environ['AA_SEED']}")

    print(f'\n\nRUN COMMAND IS: \n {RUN_COMMAND}')
    
    # Return the final bash command
    return f"bash /opt/genepatt/download_ref.sh {args.reference} '{RUN_COMMAND}' {args.file_prefix} {args.ref_path} {input_type} {args.path_to_mosek}"


def run_ac_helper(zip_fp):
    """
    Helps to run Amplicon Classifier. Unzips AA_results, looks for AA_results folder
    returns filepath to AA_results folder.
    """
    destination = os.path.join('.')

    if not os.path.exists(destination):
        pathlib.Path(destination).mkdir(parents=True, exist_ok=True)
    
    if ".zip" in zip_fp:
        with zipfile.ZipFile(zip_fp, 'r') as zip_ref:
            zip_ref.extractall(destination)
    elif '.tar' in zip_fp:
        with tarfile.open(zip_fp) as file:
            file.extractall(destination)

    # Look for AA_results folder
    for root, dirs, files in os.walk(destination, topdown=False):
        for name in dirs:
            dir_name = os.path.join(root, name)
            if "_AA_results" in dir_name:
                return dir_name
    
    return "AA_results folder not found"


def metadata_helper(args):
    """
    If metadata provided, this helper is used to parse it.
    input --> Metadata Args
    output --> fp to json file of sample metadata to build on
    """
    if ".json" not in str(args.metadata):
        with open('/opt/genepatt/sample_metadata_skeleton.json', 'r') as json_file:
            json_obj = json.load(json_file)
    else:
        # If a JSON file is provided, load it
        with open(args.metadata[0], 'r') as json_file:
            json_obj = json.load(json_file)

    # Update with provided metadata
    keys = ['metadata_sample_type', 'metadata_sample_source', 'metadata_tissue_of_origin', 
            'metadata_reference_genome', 'metadata_run_metadata_file', 'metadata_number_of_AA_amplicons', 
            'metadata_number_of_AA_features', 'metadata_sample_description']

    for key in keys:
        if hasattr(args, key) and getattr(args, key):
            json_obj[key] = getattr(args, key)

    with open('sample_metadata.json', 'w') as json_file:
        json.dump(json_obj, json_file, indent=4)



###############################
##  Start parsing arguments  ##
###############################
if __name__ == "__main__":
    print("Command line executed:", " ".join(sys.argv))
    print("==================== starting ==================")
    parser = argparse.ArgumentParser(description='Parse arguments for Amplicon Suite - Single Sample Mode')

    # Input group - mutually exclusive
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument("--bam", "--sorted_bam", metavar='FILE', 
                            help="Coordinate sorted BAM file (aligned to an AA-supported reference.)")
    input_group.add_argument("--fastqs", metavar='FILE FILE', nargs=2,
                            help="Fastq files (r1.fq r2.fq)")
    input_group.add_argument("--AA_zipped_output", metavar='PATH',
                            help="Path to a zipped directory containing completed AA runs.")

    # Required arguments
    parser.add_argument('--n_threads', required=True, type=int,
                       help='Number of threads to use for AA')
    parser.add_argument('--reference', required=True,
                       choices=['hg19', 'GRCh37', 'GRCh38', 'mm10', 'GRCh38_viral'],
                       help='Reference genome to use')
    parser.add_argument('--file_prefix', required=True,
                       help='Name of the sample being run')

    # Optional run modes
    parser.add_argument('--RUN_AA', choices=['Yes', 'No'], default='No',
                       help='Run Amplicon Architect after preprocessing?')
    parser.add_argument('--RUN_AC', choices=['Yes', 'No'], default='No',
                       help='Run Amplicon Classifier after Amplicon Architect?')

    # CNV and analysis parameters
    parser.add_argument('--ploidy', type=float,
                       help='Specify a ploidy estimate of the genome for CNVKit')
    parser.add_argument('--purity', type=float,
                       help='Specify a tumor purity estimate for CNVKit')
    parser.add_argument('--cnvkit_segmentation', default='none',
                       choices=['none', 'cbs', 'haar', 'hmm', 'hmm-tumor', 'hmm-germline'],
                       help='Segmentation method for CNVKit')
    parser.add_argument('--cnv_bed', default="",
                       help='BED file (or CNVKit .cns file) of CNV changes')
    
    # AA-specific parameters
    parser.add_argument('--AA_seed', type=int, default=0,
                       help='Seeds that sets randomness for AA')
    parser.add_argument('--cngain', type=float, default=4.5,
                       help='CN gain threshold to consider for AA seeding')
    parser.add_argument('--cnsize_min', type=int, default=50000,
                       help='CN interval size (in bp) to consider for AA seeding')
    parser.add_argument('--downsample', type=float, default=10,
                       help='AA downsample argument')
    parser.add_argument('--AA_runmode', default='FULL',
                       choices=['FULL', 'BPGRAPH', 'CYCLES', 'SVVIEW'],
                       help='AA runmode argument')
    parser.add_argument('--AA_extendmode', default='EXPLORE',
                       choices=["EXPLORE", "CLUSTERED", "UNCLUSTERED", "VIRAL"],
                       help='AA extendmode argument')
    parser.add_argument('--AA_insert_sdevs', type=float, default=3.0,
                       help='Number of standard deviations around the insert size')
    
    parser.add_argument('--foldback_pair_support_min', type=int, default=2,
                   help='Minimum number of read pairs to support a foldback event')
    
    # Additional input files
    parser.add_argument('--normal_bam',
                       help='Path to a matched normal bam for CNVKit (optional)')
    parser.add_argument('--sv_vcf', default="",
                       help='VCF file of externally-called SVs')
    parser.add_argument('--sv_vcf_no_filter', default="No",
                       help='Use all external SV calls without PASS filter')

    # Quality control and filtering
    parser.add_argument('--no_filter', default='No',
                       help='Do not run amplified_intervals.py to identify amplified seeds')
    parser.add_argument('--no_QC', default='No',
                       help='Skip QC on the BAM file')

    # Reference and output options
    parser.add_argument('--ref_path', default="None",
                       help="Path to reference Genome, won't download if provided")
   

    # Mosek license options
    parser.add_argument('--mosek_server_license', 
                       default="/expanse/projects/mesirovlab/genepattern/servers/ucsd.prod/mosek/8/licenses/mosek.lic",
                       help="Server path to mosek license file")
    parser.add_argument('--mosek_license_file',
                       help="User provided mosek license file")

    # Metadata arguments
    parser.add_argument('--metadata', nargs="+", default="",
                       help="Path to a JSON of sample metadata to build on")
    parser.add_argument('--metadata_sample_type')
    parser.add_argument('--metadata_sample_source')
    parser.add_argument('--metadata_tissue_of_origin')
    parser.add_argument('--metadata_reference_genome')
    parser.add_argument('--metadata_run_metadata_file')
    parser.add_argument('--metadata_number_of_AA_amplicons')
    parser.add_argument('--metadata_number_of_AA_features')
    parser.add_argument('--metadata_sample_description')
    parser.add_argument('--upload')
    parser.add_argument('--project_uuid')
    parser.add_argument('--project_key')
    parser.add_argument('--username')
    
    args = parser.parse_args()
    print(f"Using arguments: {args}")

    # Handle reference genome alias
    if args.reference == 'hg38':
        args.reference = "GRCh38"

    # Set mosek path
    if args.mosek_license_file:
        args.path_to_mosek = os.path.dirname(args.mosek_license_file)
    else:
        args.path_to_mosek = os.path.dirname(args.mosek_server_license)

    # Run the main processing
    try:
        command_to_run = run_paa_single_sample(args)
        
        if command_to_run.startswith("Error:") or "not found" in command_to_run:
            print(f"Error: {command_to_run}")
            exit(1)
        
        print(f'\nRunning: {command_to_run}\n')
        result = os.system(command_to_run)
        
        if result != 0:
            print(f"Command failed with exit code: {result}")
            exit(1)
        
       
            
        print('Process finished successfully')
        
    except Exception as e:
        print(f"Error during execution: {e}")
        exit(1)