###
# wrapper script for AmpliconSuite
# Author: Edwin Huang
# Mesirov lab
###



import argparse
import os
import shutil
import tarfile
import zipfile
import json
import pathlib

global EXCLUSION_LIST
EXCLUSION_LIST = ['.txt', '.bed', '.cns', '.out', '.pdf', '.log', '.stderr', '.json', '.tsv', '.cns.gz']
global EXTENSIONS_LIST
EXTENSIONS_LIST = ['.bam', '.R1.fastq.gz', '.R2.fastq.gz', '.zip', '.fq.gz', '1.fq.gz', '2.fq.gz', '.R1.fq.gz', '.R2.fq.gz', '1.fastq.gz', '2.fastq.gz', '.tar.gz']

def run_paa(input_list, sample_name, args):
    """
    Runs Prepare AA.
    """
# 1. Get the sample names of the inputs 
# 2. with sample name list, go through the input lists again and create a dictionary of: 
# {
#     "sample_name": [input 1, input 2]
# }
# 3. for each sample name, run AA on them, apply the rest of the parameters to each individual job
# 4. if running using BAMs, run mulitthreaded
    

    RUN_COMMAND = f"python3 /home/programs/AmpliconSuite-pipeline-master/PrepareAA.py -s {sample_name} -t {args.n_threads} --ref {args.reference}"
    input_type = ""
    for input_file in input_list:
        if ".bam" in input_file:
            RUN_COMMAND += f" --sorted_bam {input_file}"
            input_type = "bam"
        elif (".fastq" in input_file) or (".fq" in input_file):
            input_type = "fastq"
            if "--fastqs" in RUN_COMMAND:
                RUN_COMMAND += f" {input_file}"
            else:
                RUN_COMMAND += f" --fastqs {input_file}"
        elif (".tar" in input_file) or ('.zip' in input_file):
            ## run AC, run script and stop code here.
            AA_results_location = run_ac_helper(input_file)
            if AA_results_location != "AA_results folder not found":
                RUN_COMMAND += f" --completed_AA_runs {AA_results_location} --cnvkit_dir /home/programs/cnvkit.py"
                print(f'run command is: {RUN_COMMAND}')
                return (RUN_COMMAND)
                # os.system("bash /home/download_ref.sh " + args.reference + f" '{RUN_COMMAND}' {args.file_prefix}" )
            else:
                return "Invalid input."
            

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
        RUN_COMMAND +=  " --sample_metadata sample_metadata.json"

    if args.normal_bam:
        RUN_COMMAND += f" --normal_bam {args.normal_bam}"
    
    if (args.sv_vcf != "") and (args.sv_vcf != 'None') and (args.sv_vcf):
        RUN_COMMAND += f" --sv_vcf {args.sv_vcf}"
    
    if args.sv_vcf_no_filter != "No":
        RUN_COMMAND += f" --sv_vcf_no_filter"
    
    if args.AA_runmode:
        RUN_COMMAND += f" --AA_runmode {args.AA_runmode}"
    
    if args.RUN_AA == 'Yes' and args.AA_extendmode != "":
        RUN_COMMAND += f" --AA_extendmode {args.AA_extendmode}"

    if args.AA_insert_sdevs:
        RUN_COMMAND += f" --AA_insert_sdevs {args.AA_insert_sdevs}"
    
    if args.downsample: 
        RUN_COMMAND += f" --downsample {args.downsample}"

    if args.no_filter != "No":
        RUN_COMMAND += f" --no_filter"

    if args.no_QC != 'No':
        RUN_COMMAND += f" --no_QC"
    
    if (args.cngain != 4.5) and (args.cngain > 0):
        RUN_COMMAND += f" --cngain {args.cngain}"

    if (args.cnsize_min != 50000) and (args.cnsize_min > 0):
        RUN_COMMAND += f" --cnsize_min {args.cnsize_min}"


    os.environ['AA_SEED'] = str(args.AA_seed)

    print(f"AA_SEED is set as: {os.environ['AA_SEED']}, the type is: {type(os.environ['AA_SEED'])}")

    ## download data files
    print(f'\n\nRUN COMMAND IS: \n {RUN_COMMAND}')
    # print(f"before going to the bash script: " + "bash /opt/genepatt/download_ref.sh " + args.reference + " "  + f" '{RUN_COMMAND}' {args.file_prefix} " + args.ref_path)
    # os.system(f"bash /opt/genepatt/download_ref.sh {args.reference} '{RUN_COMMAND}' {args.file_prefix} {args.ref_path} {input_type}")
    

    ## check if user wants minimal outputs, will only output PNGs
    ## testrun:

    # python3 /files/src/run_aa.py --input /files/gpunit/input/TESTX_H7YRLADXX_S1_L001.cs.rmdup.bam --n_threads 1 --reference GRCh38 --file_prefix testproject --RUN_AA Yes --RUN_AC Yes 
    # python3 /opt/genepatt/run_aa.py --input /files/FF-12.fastq.gz /files/FF-12.R2.fastq.gz --n_threads 1 --reference GRCh38 --file_prefix testproject --RUN_AA Yes --RUN_AC Yes 
    
    ## return run command
    return f"bash /opt/genepatt/download_ref.sh {args.reference} '{RUN_COMMAND}' {sample_name} {args.ref_path} {input_type} {args.path_to_mosek}"


def run_ac_helper(zip_fp):
    """
    Helps to run Amplicon Classifier. Unzips AA_results, looks for AA_results folder
    returns filepath to AA_results folder.

    """
    destination = os.path.join('.')

    if not os.path.exists(destination):
        pathlib.Path(destination).mkdir(parents = True, exist_ok = True)
    if ".zip" in zip_fp:
        with zipfile.ZipFile(zip_fp, 'r') as zip_ref:
            zip_ref.extractall(destination)
        zip_ref.close()
    elif '.tar' in zip_fp:
        # open file
        file = tarfile.open(zip_fp)
        # extracting file
        file.extractall(destination)
        file.close()

    for root, dirs, files in os.walk(destination, topdown=False):
        sample_name = ""
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
    
    if ".json" not in args.metadata:
        json_file = open('/opt/genepatt/sample_metadata_skeleton.json', 'r')
        json_obj = json.load(json_file)
        json_file.close()


    keys = ['metadata_sample_type','metadata_sample_source','metadata_tissue_of_origin','metadata_reference_genome','metadata_run_metadata_file', 'metadata_number_of_AA_amplicons', 
            'metadata_number_of_AA_features', 'metadata_sample_description']

    for key in keys:
        json_obj[key] = vars(args)[key]

    with open('sample_metadata.json', 'w') as json_file:
        json.dump(json_obj, json_file, indent = 4)
    json_file.close()


def get_sample_names(filepaths):
    """
    Gets a unique set of sample names from the inputs
    python3 src/run_aa.py --input /directory/to/the/file/FF12.R1.fastq.gz /directory/to/the/file/FF12.R2.fastq.gz /directory/to/the/file/FF13.bam /directory/to/the/file/FF15.R.bam

    /directory/to/the/file/
    """

    sample_names = set()

    for file in filepaths:
        sample_name = ''
        for ext in EXTENSIONS_LIST:
            if ext in file:
                sample_name = os.path.basename(file).replace(ext, '')
        if sample_name != '':
            sample_names.add(sample_name)

    return list(sample_names)

def create_parameter_sets(sample_names, filepaths):
    """
    Creates a dictionary of 

    {
        sample name n : [input file 1, input file 2]
    }
    """
    input_set = {}
    for name in sample_names:

        ## if the sample namei isn't in the input set yet:
        if name not in input_set.keys():
            input_set[name] = []

        for fp in filepaths:
            if name in fp:
                input_set[name].append(fp)

    return input_set

def run_paa_per_sample(input_set, args):
    """
    Given a set of input lists, run prepare AA on each sample
    """
    commands_to_run = []

    for sample in input_set.keys():
        command = run_paa(input_set[sample], sample, args)
        commands_to_run.append(command)
    return commands_to_run



###############################
##  Start parsing arguments  ##
###############################
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description = 'Parse arguments for Amplicon Suite')
    parser.add_argument('--input',
                help = 'Input File, can be BAM, Fastq files, or tar.gz',
                required = True,
                nargs = "+")
    parser.add_argument('--n_threads', help = 'number of threads to use for AA')
    parser.add_argument('--reference', help = 'Reference genome to use',
                choices = ['hg19', 'GRCh37', 'GRCh38','mm10', 'GRCh38_viral'])
    parser.add_argument('--file_prefix',
                help = 'Name of the sample being run')
    parser.add_argument('--RUN_AA',
                help = 'Run Amplicon Architect after preprocessing?',
                choices = ['Yes', 'No'])
    parser.add_argument('--RUN_AC',
                help = 'Run Amplicon Classifier after Amplicon Architect?',
                choices = ['Yes', 'No'])
    parser.add_argument('--ploidy', type=float,
                help = 'Specify a ploidy estimate of the genome for CNVKit')
    
    parser.add_argument('--purity', help =
    'Specify a tumor purity estimate for CNVKit. Not used by AA itself.\
    Note that specifying low purity may lead to many high copy number seed \
    regions after rescaling is applied consider setting a higher --cn_gain \
    threshold for low purity samples undergoing correction.', type = float)

    parser.add_argument('--cnvkit_segmentation',
                help = 'Segmentation method for CNVKit (if used)',
                choices = ['none', 'cbs', 'haar', 'hmm', 'hmm-tumor', 'hmm-germline'],
                default = 'none')
    
    parser.add_argument('--cnv_bed',
                help = 'BED file (or CNVKit .cns file) of CNV changes. \
                 Fields in the bed file should be: chr start end name cngain',
                 default = "")
    
    parser.add_argument('--AA_seed', help = 'Seeds that sets randomness for AA', type = int, default = 0)
    
    parser.add_argument('--metadata', help="Path to a JSON of sample metadata to build on", default = "", nargs = "+")

    parser.add_argument('--normal_bam', help = "Path to a matched normal bam for CNVKit (optional)")

    parser.add_argument('--ref_path', help = "Path to reference Genome, won't download the reference genome", default = "None")

    parser.add_argument('--min_outputs', help = "Minimizing the amount of outputs.")

    parser.add_argument("--sv_vcf",
                        help="Provide a VCF file of externally-called SVs to augment SVs identified by AA internally.")
    
    parser.add_argument("--sv_vcf_no_filter", help="Use all external SV calls from the --sv_vcf arg, even "
                        "those without 'PASS' in the FILTER column.", type = str, default = "No")
    
    parser.add_argument("--cngain", metavar='FLOAT', type=float, help="CN gain threshold to consider for AA seeding",
                        default=4.5)
    parser.add_argument("--cnsize_min", metavar='INT', type=int, help="CN interval size (in bp) to consider for AA seeding",
                        default=50000)
    parser.add_argument("--downsample", metavar='FLOAT', type=float, help="AA downsample argument (see AA documentation)",
                        default=10)
    parser.add_argument("--AA_runmode", metavar='STR', help="If --run_AA selected, set the --runmode argument to AA. Default mode is "
                        "'FULL'", choices=['FULL', 'BPGRAPH', 'CYCLES', 'SVVIEW'], default='FULL')
    parser.add_argument("--AA_extendmode", metavar='STR', help="If --run_AA selected, set the --extendmode argument to AA. Default "
                        "mode is 'EXPLORE'", choices=["EXPLORE", "CLUSTERED", "UNCLUSTERED", "VIRAL"], default='EXPLORE')
    parser.add_argument("--AA_insert_sdevs", help="Number of standard deviations around the insert size. May need to "
                        "increase for sequencing runs with high variance after insert size selection step. (default "
                        "3.0)", metavar="FLOAT", type=float, default=3.0)
    parser.add_argument("--no_filter", help="Do not run amplified_intervals.py to identify amplified seeds", type = str, default = 'No')
    parser.add_argument("--no_QC", help="Skip QC on the BAM file. Do not adjust AA insert_sdevs for poor-quality insert size distribution", type = str, default = 'No')
    #parser.add_argument("--path_to_mosek", help = "Server path to mosek license file", default = "/expanse/projects/mesirovlab/genepattern/servers/ucsd.prod/mosek/8/licenses/")
    parser.add_argument("--mosek_server_license", help = "Server path to mosek license file", default="/expanse/projects/mesirovlab/genepattern/servers/ucsd.prod/mosek/8/licenses/mosek.lic")
    parser.add_argument("--mosek_license_file", help = "User provided mosek license file")
 

    ### Metadata arguments: 
    parser.add_argument("--metadata_sample_type")
    parser.add_argument("--metadata_sample_source")
    parser.add_argument("--metadata_tissue_of_origin")
    parser.add_argument("--metadata_reference_genome")
    parser.add_argument("--metadata_run_metadata_file")
    parser.add_argument("--metadata_number_of_AA_amplicons")
    parser.add_argument("--metadata_number_of_AA_features")
    parser.add_argument("--metadata_sample_description")

    args = parser.parse_args()
    print(f"using arguments: {args}")
    if args.reference == 'hg38':
        args.reference = "GRCh38"

    # Set the value for args.path_to_mosek
    if args.mosek_license_file:
        args.path_to_mosek = os.path.dirname(args.mosek_license_file)
    else:
        args.path_to_mosek = os.path.dirname(args.mosek_server_license)

    ## to do: if txt, then find the samples, if not, then run AA on it. 
    ## 
    # if (len(args.input) == 1) and (".txt" in args.input[0]):
    #     filepaths, sample_name_list = get_sample_names(args)
    #     parameter_sets = create_parameter_sets(sample_name_list, filepaths)
    #     AA_commands = run_paa_per_sample(parameter_sets, args)
    # else:
    #     input_list = args.input
    #     for ext in EXTENSIONS_LIST:
    #         if ext in input_list[0]:
    #             sample_name = os.path.basename(input_list[0]).replace(ext, '')
    #     AA_commands = [run_paa(input_list, sample_name, args)]

    def read_filelist(fp):
        """
        Reads the filelist.txt and returns a list of filepaths. 
        """
        filepaths = []
        with open(fp, 'r') as file:
            for line in file.readlines():
                fp = line.strip()
                if fp != '':
                    filepaths.append(fp)
        return filepaths
                

    all_filepaths = []
    for input in args.input:
        if ".txt" in input: 
            ## most likely a filelist
            ## get the list of filepaths from it
            filepaths = read_filelist(input)
            all_filepaths += filepaths
        else:
            all_filepaths.append(input)
    
    sample_name_list = get_sample_names(all_filepaths)
    parameter_sets = create_parameter_sets(sample_name_list, all_filepaths)
    AA_commands = run_paa_per_sample(parameter_sets, args)


    print('process finished')

    print(AA_commands)
    for cmd in AA_commands:
        print(f'\n running: {cmd} \n \n ')
        os.system(f'{cmd}')

    if args.min_outputs == "Yes":
        print('Will reduce the amount of files outputted')
        for root, dirs, files in os.walk('.'):
            for name in files:
                fp = os.path.join(root, name)
                extension = os.path.splitext(fp)[-1]
                for exclude in EXCLUSION_LIST:
                    if exclude == extension:
                        print('will remove: ' + fp)
                        os.remove(fp)
    # if multiple aa commands, run aa on them individually. 




## docker build --platform linux/amd64 -t ampsuite . && docker tag ampsuite genepattern/amplicon-architect:v2.5 && docker push genepattern/amplicon-architect:v2.5
## python3 src/run_aa.py --input /Users/edwinhuang/Documents/GitHub/AmpliconSuite/src/input_list.txt
