from __future__ import division
from optparse import OptionParser
from pyCondorSTAMPLib import *
from pyCondorSTAMPanteprocSupportLib_v2 import *
from preprocSupportLib import *
from grandStochtrackSupportLib import *
from condorSTAMPSupportLib_v2 import *
import webpageGenerateLib as webGen
import scipy.io as sio
import json
import random

print("\nPlease note: Recurring parameters in the input parameter file for the same job or for 'constants' will be overwritten with the last lines value for that job. There likely will NOT be a warning that this is what is happening.\n")

#print("WARNING: code does not currently lock the seed record file. This can lead to a race condition if more than one process is expected to access this file. Only use this code with files that are only expected to
print("Code not currently set up to handle a mix of gpu and non-gpu jobs. A future version should be able to address this.")
print('DEPRECATED: "grandstochtrack job" option in parameter files is deprecated. Please use "preproc job" option istead or this program will fail.')

#### REMINDER: Edit the grand_stochtrack parameter reader such that "." will
# allow easy access to subdirectories in the grand_stochtrack parameter matrix

# include parameter file option eventually to move plots over to get rid of initial black band (located in grand_stochtrack param file)

# command line options
parser = OptionParser()
parser.set_defaults(verbose = False)
parser.set_defaults(restrict_cpus = False)
parser.set_defaults(groupedPreprocessing = True)
parser.set_defaults(burstegard = False)
parser.set_defaults(all_clusters = False)
parser.set_defaults(archived_frames_okay = False)
parser.set_defaults(no_job_retry = False)
parser.set_defaults(extract_from_gpu = False)
parser.set_defaults(anteproc_mode = False)
parser.add_option("-c", "--conf", dest = "configFile",
                  help = "Path to config file detailing analysis for preproc and grand_stochtrack executables (preproc job options can have multiple jobs if separated by a \",\" [may be a good idea to switch to a single directory all preproc jobs are dumped, however this would require them to share many of the same parameters, or not, just don't overlap in time at all, something to think about])",
                  metavar = "FILE")
parser.add_option("-j", "--jobFile", dest = "jobFile",
                  help = "Path to job file detailing job times and durations",
                  metavar = "FILE")
parser.add_option("-d", "--dir", dest = "outputDir",
                  help = "Path to directory to hold analysis output (a new directory \
will be created with appropriate subdirectories to hold analysis)",
                  metavar = "DIRECTORY")
parser.add_option("-p", "--preprocDir", dest = "preprocDir",
                  help = "(Optional) Path to directory holding previous analysis output that contains preproccessed data to use",
                  metavar = "DIRECTORY")
parser.add_option("-v", action="store_true", dest="verbose")
parser.add_option("-g", action="store_false", dest="groupedPreprocessing")
parser.add_option("-r", action="store_true", dest="restrict_cpus")
parser.add_option("-b", action="store_true", dest="burstegard")
parser.add_option("-a", action="store_true", dest="all_clusters")
parser.add_option("-f", action="store_true", dest="archived_frames_okay")
parser.add_option("-q", action="store_true", dest="no_job_retry")
parser.add_option("-e", action="store_true", dest="extract_from_gpu")
parser.add_option("-A", action="store_true", dest="anteproc_mode")


# MAYBE maxjobs will be useful.

parser.add_option("-m", "--maxjobs", dest = "maxjobs",
                  help = "Maximum number of jobs ever submitted at once \
through condor", metavar = "NUMBER")

# add options to load defaults for preproc and grand_stochtrack

(options, args) = parser.parse_args()

# check for minimum commands line arguments to function
if not options.configFile:
    raise pyCondorSTAMPanteprocError("Config File not specified")
if not options.outputDir:
    raise pyCondorSTAMPanteprocError("Output Directory not specified")
if not options.jobFile:
    raise pyCondorSTAMPanteprocError("Job File not specified")
    
if options.groupedPreprocessing:
    print("WARNING: consolidated preproc job option selected.")

#Process file paths
jobPath = make_file_path_absolute(options.jobFile)
configPath = make_file_path_absolute(options.configFile)
outputDir = make_file_path_absolute(options.outputDir)

outputDir += "stamp_analysis_anteproc" if outputDir[-1] == "/" else "/stamp_analysis_anteproc"
baseDir = dated_dir(outputDir)

# constants
# default dictionary json path
defaultDictionaryPath = "/home/quitzow/GIT/Development_Branches/pyCondorSTAMP/defaultStochtrack.json"
anteprocDefault = "/home/quitzow/GIT/Development_Branches/pyCondorSTAMP/anteproc_defaults.txt"

STAMP_setup_script = "/home/paul.schale/STAMP/stamp2/test/stamp_setup.sh"
# set other defaults this way too instead of definining them inside the preprocSupportLib.py file

# paths to executables
anteprocExecutable = "/home/paul.schale/STAMP/stamp2/compilationScripts/anteproc"
grandStochtrackExecutable = "/home/paul.schale/STAMP/stamp2/compilationScripts/grand_stochtrack"
grandStochtrackExecutableNoPlots = "/home/paul.schale/STAMP/stamp2/compilationScripts/grand_stochtrack_nojvm"
matlabMatrixExtractionExectuable = "/home/quitzow/GIT/Development_Branches/MatlabExecutableDuctTape/getSNRandCluster"


# load info from config file
rawData = read_text_file(configPath, ' ')

# load default dictionary if selected
# TODO: fix this for option to exclude default dictionary if wished
defaultDictionary = load_dict_from_json(defaultDictionaryPath)

# load data from jobFile
with open(jobPath, "r") as infile:
    jobDataDict = dict((x.split()[0], x.split()[1:]) for x in infile)

# parse jobs

jobs, commentsToPrintIfVerbose, job_groups, jobDuplicates, H1_jobs, L1_jobs, waveforms, varyingAnteprocVariables = parse_jobs(rawData)
H1_jobs = set(H1_jobs)
L1_jobs = set(L1_jobs)

job_group_iterator = 1
for job in jobs:
    if job != "constants":
        if not jobs[job]["job_group"]:
            while str(job_group_iterator) in job_groups:
                job_group_iterator += 1
            jobs[job]["job_group"] = str(job_group_iterator)
            job_groups += [str(job_group_iterator)]

anteproc_grand_stochtrack_values = {"anteproc.loadFiles": True,
                                    "anteproc.timeShift1": 0,
                                    "anteproc.timeShift2": 0,
                                    "anteproc.jobFileTimeShift": True,
                                    "anteproc.bkndstudy": False,
                                    "anteproc.bkndstudydur": 100}
anteprocOrder = ["anteproc.loadFiles",
                 "anteproc.timeShift1",
                 "anteproc.timeShift2",
                 "anteproc.jobFileTimeShift",
                 "anteproc.bkndstudy",
                 "anteproc.bkndstudydur",
                 "anteproc.inmats1",
                 "anteproc.inmats2",
                 "anteproc.jobfile"]

# set job durations
print("Code currently not set up to handle 'hstart' or 'hstop' individually without the other in specific jobs or 'constants'.")
if not (options.anteproc_mode or anteproc_grand_stochtrack_values["anteproc.jobFileTimeShift"]):
    for job in jobs:
        if (not bool(checkEssentialParameter(jobs[job]["grandStochtrackParams"]["params"], "jobdur"))) and bool(checkEssentialParameter(jobs[job]["grandStochtrackParams"]["params"], "hstart")) and bool(checkEssentialParameter(jobs[job]["grandStochtrackParams"]["params"], "hstop")):
            startTime = float(jobs[job]["grandStochtrackParams"]["params"]["hstart"])
            jobs[job]["grandStochtrackParams"]["params"]["hstart"] = startTime
            endTime = float(jobs[job]["grandStochtrackParams"]["params"]["hstop"])
            jobs[job]["grandStochtrackParams"]["params"]["hstop"] = endTime

            jobs[job]["grandStochtrackParams"]["jobdur"] = endTime - startTime
        if bool(checkEssentialParameter(jobs[job]["grandStochtrackParams"]["params"], "jobdur")):
            jobs[job]["grandStochtrackParams"]["jobdur"] = float(jobs[job]["grandStochtrackParams"]["jobdur"])
    print("Got a lot of float checks here. May want to either have all the float checks occur here, or maybe make them as the data is loaded.")

if commentsToPrintIfVerbose and options.verbose:
    print(commentsToPrintIfVerbose)

# TODO: Warnings and error catching involving default job number and undefined job numbers
print("\n\nRemember: Finish this part.\n\n")

if jobDuplicates:
    ans = raw_input("Duplicate jobs exist.  Continue? (y/n)")
    if not ans == 'y':
        raise pyCondorSTAMPanteprocError("Process Terminated")

# update default dictionary
defaultDictionary = load_default_dict(jobs['constants']['grandStochtrackParams']['params'] , defaultDictionary)

# load default anteproc
with open(anteprocDefault, 'r') as infile:
    anteprocDefaultData = [line.split() for line in infile]

# create directory structure
# Build file system

#create directory structure for jobs:
#	stochtrack_condor_job_group_num
#		README.txt with SNR and other information on all jobs? GPS times as well? Whether there is an injection or not?
#		stochtrack_day_job_num (injection? gps time?)
#			README.txt with job information? json maybe? job type
#			preproc inputs
#			inputs for stochtrack clustermap
#			grand_stochtrack inputs
#			results
#				overview mat
#				some other thing?
#				plotDir

if "num_jobs_to_vary" in varyingAnteprocVariables:
    multiple_job_group_version = True
else:
    multiple_job_group_version = False

cacheFilesCreated = []

anteprocJobs = {}
anteprocJobs["H1"] = {}
anteprocJobs["L1"] = {}
organizedSeeds = {}
organizedSeeds["H1"] = {}
organizedSeeds["L1"] = {}
used_seeds = [jobs["constants"]["anteprocHjob_seeds"][x] for x in jobs["constants"]["anteprocHjob_seeds"]]
used_seeds += [jobs["constants"]["anteprocLjob_seeds"][x] for x in jobs["constants"]["anteprocLjob_seeds"]]
    # Build base analysis directory
    # stochtrack_condor_job_group_num


    # copy input parameter file and jobs file into a support directory here
    # support directory
supportDir = create_dir(baseDir + "/input_files")
    # copy input files to this directory
copy_input_file(options.configFile, supportDir)#, options.configFile)
newJobPath = copy_input_file(options.jobFile, supportDir)#, options.jobFile)
if options.anteproc_mode:
    newAdjustedJobPath = adjust_job_file(options.jobFile, supportDir, jobs)

    # create directory to host all of the jobs. maybe drop the cachefiles in here too?
jobsBaseDir = create_dir(baseDir + "/jobs")

    # create cachefile directory
print("Creating cache directory")

if jobs["constants"]["anteprocParamsH"]["doDetectorNoiseSim"] == "false":
    cacheDir = create_dir(baseDir + "/cache_files") + "/"
    fakeCacheDir = None
else:
    fakeCacheDir = create_dir(baseDir + "/fake_cache_files") + "/"
    cacheDir = None

if options.anteproc_mode:
    print("Creating anteproc directory and input files")
    anteproc_dir = create_dir(baseDir + "/anteproc_data")

    if cacheDir:
        anteproc_H, anteproc_L = anteproc_setup(anteproc_dir, anteprocDefaultData, jobs, cacheDir)
    else:
        anteproc_H, anteproc_L = anteproc_setup(anteproc_dir, anteprocDefaultData, jobs, fakeCacheDir)
    multiple_waveforms = False

    if "stampinj" in anteproc_H and "stampinj" in anteproc_L:
        if len(waveforms) > 0:
            multiple_waveforms = True
        if anteproc_H["stampinj"] != anteproc_L["stampinj"]:
            raise pyCondorSTAMPanteprocError("Warning, injections settings in detectors do not match, one has 'stampinj = true' and one has 'stampinj = false'. Please edit code for further capabilities of this behavior is intentional.")
    elif "stampinj" in anteproc_H or "stampinj" in anteproc_L:
        raise pyCondorSTAMPanteprocError("Warning, injections settings in detectors do not match, one has 'stampinj' and one does not. Please edit code for further capabilities of this behavior is intentional.")
    anteprocJobDictTracker = createPreprocessingJobDependentDict(jobs)
    if "varying_injection_start" in jobs["constants"]:
        frontStartTime = jobs["constants"]["varying_injection_start"][0]
        backStartTime = jobs["constants"]["varying_injection_start"][1]
        injectionStartTimes = generate_random_start_times(jobs, varyingAnteprocVariables, frontStartTime, backStartTime)
    else:
        injectionStartTimes = None

    anteprocJobs, used_seeds, organizedSeeds = anteproc_job_specific_setup(H1_jobs, "H1",
            anteproc_dir, jobs, anteproc_H, used_seeds, organizedSeeds, multiple_waveforms, waveforms, anteprocDefaultData,
            anteprocJobs, varyingAnteprocVariables, anteprocJobDictTracker = anteprocJobDictTracker, injectionStartTimes = injectionStartTimes)

    anteprocJobs, used_seeds, organizedSeeds = anteproc_job_specific_setup(L1_jobs, "L1",
            anteproc_dir, jobs, anteproc_L, used_seeds, organizedSeeds, multiple_waveforms, waveforms, anteprocDefaultData,
            anteprocJobs, varyingAnteprocVariables, anteprocJobDictTracker = anteprocJobDictTracker, injectionStartTimes = injectionStartTimes)

    if jobs["constants"]["anteprocParamsH"]["doDetectorNoiseSim"] == "true" or jobs["constants"]["anteprocParamsL"]["doDetectorNoiseSim"] == "true":
        with open(anteproc_dir + "/seeds_for_simulated_data.txt", "w") as outfile:
            json.dump(organizedSeeds, outfile, sort_keys = True, indent = 4)
    if "num_jobs_to_vary" in varyingAnteprocVariables:
        print("\nVariable parameter option active.\n")
        with open(anteproc_dir + "/varying_parameters_input_record.txt", "w") as outfile:
            json.dump(varyingAnteprocVariables, outfile, sort_keys = True, indent = 4)
    else:
        print("\nVariable parameter option not active.\nIf it's supposed to be active, add 'anteproc_varying_param num_jobs_to_vary' option to input parameter file.\n")

    anteproc_grand_stochtrack_values["anteproc.inmats1"] = anteproc_dir + "/H-H1_map"
    anteproc_grand_stochtrack_values["anteproc.inmats2"] = anteproc_dir + "/L-L1_map"
    anteproc_grand_stochtrack_values["anteproc.jobfile"] = newAdjustedJobPath

    for job in jobs:
            #"adjust inmats entries here maybe if needed? yes."
        for anteprocParameter in anteprocOrder:
            if (anteprocParameter == "anteproc.inmats1" or anteprocParameter == "anteproc.inmats2") and "injection_tags" in jobs[job]:
                jobs[job]["grandStochtrackParams"]["params"] = nested_dict_entry(jobs[job]["grandStochtrackParams"]["params"], anteprocParameter, anteproc_grand_stochtrack_values[anteprocParameter] + "_" + jobs[job]["injection_tags"])
            else:
                jobs[job]["grandStochtrackParams"]["params"] = nested_dict_entry(jobs[job]["grandStochtrackParams"]["params"], anteprocParameter, anteproc_grand_stochtrack_values[anteprocParameter])
else:
    anteproc_dir = None

    # cycle through jobs
print("Creating job directories")
for job in jobs:
    if job != "constants":
        jobs[job]["jobDir"] = []
        jobs[job]["stochtrackInputDir"] = []
        jobs[job]["grandstochtrackOutputDir"] = []
        jobs[job]["plotDir"] = []

        if multiple_job_group_version:
            for index in range(varyingAnteprocVariables["num_jobs_to_vary"]):
                temp_number = index + 1
                temp_suffix = "_v" + str(temp_number)
                jobs = create_job_directories(jobs, jobsBaseDir, job, temp_suffix)
        else:
            jobs = create_job_directories(jobs, jobsBaseDir, job)
            """# stochtrack_day_job_num (injection? gps time?)
            jobDir = create_dir(jobsBaseDir + "/" + "job_group_" + jobs[job]["job_group"] + "/" + job)
            jobs[job]["jobDir"] = jobDir

#			inputs for stochtrack clustermap in text file (put this here or in the "/params" directory)
#			grand_stochtrack inputs
            stochtrackInputDir = create_dir(jobDir + "/grandstochtrackInput")
            jobs[job]["stochtrackInputDir"] = stochtrackInputDir
#			results
            grandstochtrackOutputDir = create_dir(jobDir + "/grandstochtrackOutput")
            jobs[job]["grandstochtrackOutputDir"] = grandstochtrackOutputDir
#				overview mat
#				some other thing?
#				plotDir
            plotDir = create_dir(grandstochtrackOutputDir + "/plots")
            jobs[job]["plotDir"] = plotDir"""

        # NOTE: recording any directories other than the base job directory may not have any value
        # because the internal structure of each job is identical.

    # build dag directory
dagDir = create_dir(baseDir + "/dag")

    # Build support file sub directory for dag logs
dagLogDir = create_dir(dagDir + "/dagLogs")

    # Build support file sub directory for job logs
logDir = create_dir(dagLogDir + "/logs")


# create grandstochtrack execution script

print("Creating shell scripts")
grandStochtrack_script_file = dagDir + "/grand_stochtrack.sh"
if jobs['constants']['grandStochtrackParams']['params']['savePlots']:
    write_grandstochtrack_bash_script(grandStochtrack_script_file, grandStochtrackExecutable, STAMP_setup_script)
else:
    write_grandstochtrack_bash_script(grandStochtrack_script_file, grandStochtrackExecutableNoPlots, STAMP_setup_script)
os.chmod(grandStochtrack_script_file, 0744)

matlabMatrixExtractionExectuable_script_file = dagDir + "/matlab_matrix_extraction.sh"
write_grandstochtrack_bash_script(matlabMatrixExtractionExectuable_script_file, matlabMatrixExtractionExectuable, STAMP_setup_script)
os.chmod(matlabMatrixExtractionExectuable_script_file, 0744)

anteprocExecutable_script_file = dagDir + "/anteproc.sh"
write_anteproc_bash_script(anteprocExecutable_script_file, anteprocExecutable, STAMP_setup_script)
os.chmod(anteprocExecutable_script_file, 0744)

# If relative injection value set, override any existing injection time with calculated relative injection time.

# find frame files
for tempJob in set(H1_jobs):
    print("Finding frames for job " + str(tempJob) + " for H1")
    tempJobData = jobDataDict[str(tempJob)]
    if anteproc_H["doDetectorNoiseSim"] == "false":
        temp_frames = create_frame_file_list("H1_HOFT_C01", tempJobData[0], tempJobData[1], "H")
        create_cache_and_time_file(temp_frames, "H",tempJob,cacheDir, archived_frames_okay = options.archived_frames_okay)
    else:
        create_fake_cache_and_time_file(tempJobData[0], tempJobData[1], "H", tempJob, fakeCacheDir)
for tempJob in set(L1_jobs):
    print("Finding frames for job " + str(tempJob) + " for L1")
    tempJobData = jobDataDict[str(tempJob)]
    if anteproc_L["doDetectorNoiseSim"] == "false":
        temp_frames = create_frame_file_list("L1_HOFT_C01", tempJobData[0], tempJobData[1], "L")
        create_cache_and_time_file(temp_frames, "L",tempJob,cacheDir, archived_frames_okay = options.archived_frames_okay)
    else:
        create_fake_cache_and_time_file(tempJobData[0], tempJobData[1], "L", tempJob, fakeCacheDir)
        
# write preproc parameter files for each job
print("Saving grand_stochtrack paramter files")
for job in jobs:
    if job != "constants":
        jobs[job]["grandStochtrackParams"]["params"]["jobsFile"] = newJobPath
        # write stochtrack parameter files for each job
        jobs[job]['grandStochtrackParams']['params'] = load_default_dict(jobs[job]['grandStochtrackParams']['params'] , defaultDictionary)
        print("The way this following line is done needs to be reviewed.")
        jobs[job]['grandStochtrackParams'] = load_default_dict(jobs[job]['grandStochtrackParams'], jobs["constants"]['grandStochtrackParams'])

        # new for loop to handle possible multiple job group versions due to variable parameters
        for temp_index in range(len(jobs[job]["plotDir"])):
            temp_number = temp_index+1
            if "varying_injection_start" in jobs["constants"]:
                temp_suffix = "_v" + str(temp_number) + "_" + job
            else:
                temp_suffix = "_v" + str(temp_number)

            # put output directories in grand_stochtrack dictionary
            jobs[job]["grandStochtrackParams"]["params"]["plotdir"] = jobs[job]["plotDir"][temp_index] + "/"
            jobs[job]["grandStochtrackParams"]["params"]["outputfilename"] = jobs[job]["grandstochtrackOutputDir"][temp_index] + "/map"
            jobs[job]["grandStochtrackParams"]["params"]["ofile"] = jobs[job]["grandstochtrackOutputDir"][temp_index] + "/bknd"
            if "lonetrack" in jobs["constants"]["grandStochtrackParams"]["params"]["stochtrack"]:
                if jobs["constants"]["grandStochtrackParams"]["params"]["stochtrack"]["lonetrack"] == 1:
                    temp_directory = create_dir(jobs[job]["grandStochtrackParams"]["params"]["plotdir"]+"tmp")
                    jobs[job]["grandStochtrackParams"]["params"]["lonetrackdir"] = temp_directory + "/"

            if multiple_job_group_version:
                base_inmat1 = jobs[job]["grandStochtrackParams"]["params"]["anteproc"]["inmats1"]
                base_inmat2 = jobs[job]["grandStochtrackParams"]["params"]["anteproc"]["inmats2"]
                jobs[job]["grandStochtrackParams"]["params"]["anteproc"]["inmats1"] = base_inmat1 + temp_suffix
                jobs[job]["grandStochtrackParams"]["params"]["anteproc"]["inmats2"] = base_inmat2 + temp_suffix

            sio.savemat(jobs[job]["stochtrackInputDir"][temp_index] + "/" + "params.mat", jobs[job]["grandStochtrackParams"])

            if multiple_job_group_version:
                jobs[job]["grandStochtrackParams"]["params"]["anteproc"]["inmats1"] = base_inmat1
                jobs[job]["grandStochtrackParams"]["params"]["anteproc"]["inmats2"] = base_inmat2

# order plots by job

# This line likely needs fixing if it's going to work with the variable parameters. otherwise it's fine.
jobTempDict = dict((int(job[job.index("_")+1:]),{"job" : job, "job dir" : "job_group_" + jobs[job]["job_group"] + "/" + job}) for job in [x for x in jobs if x != "constants"])

if options.burstegard:
    plotTypeList = ["SNR", "Largest Cluster", "All Clusters", "sig map", "y map", "Xi snr map"]
    plotTypeDict = {"SNR" : "snr.png", "Largest Cluster" : "large_cluster.png", "All Clusters": "all_clusters.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png"}
elif options.all_clusters:
    plotTypeList = ["SNR", "Loudest Cluster (stochtrack)", "Largest Cluster (burstegard)", "All Clusters (burstegard)", "sig map", "y map", "Xi snr map"]
    plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster (stochtrack)" : "rmap.png", "Largest Cluster (burstegard)" : "large_cluster.png", "All Clusters (burstegard)": "all_clusters.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png"}
else:
    plotTypeList = ["SNR", "Loudest Cluster", "sig map", "y map", "Xi snr map"]
    plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster" : "rmap.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png"}

outFile = "pageDisplayTest.html"

jobNumOrder = [jobNum for jobNum in jobTempDict]
jobNumOrder.sort()
jobOrder = [jobTempDict[jobNum]["job"] for jobNum in jobNumOrder]
jobOrderWeb = [jobTempDict[jobNum]["job dir"] for jobNum in jobNumOrder]

#webGen.make_display_page(directory, saveDir, subDirList, subSubDir, plotTypeList, plotTypeDict, outputFileName)
print('DEBUG NOTE: Maybe figure out how to variablize "grandstochtrackOutput/plots" in next line?')
print("Creating webpage")
webGen.make_display_page("jobs", baseDir, jobOrderWeb, "grandstochtrackOutput/plots", plotTypeList, plotTypeDict, outFile)

# build DAGs
# preproc DAG
# build submission file
doGPU = jobs["constants"]["grandStochtrackParams"]["params"]["doGPU"]
if doGPU and not options.burstegard:
    extract_from_gpu = True
else:
    extract_from_gpu = False
extract_from_gpu = options.extract_from_gpu
if "singletrack" in jobs["constants"]["grandStochtrackParams"]["params"]["stochtrack"]:
    do_singletrack = jobs["constants"]["grandStochtrackParams"]["params"]["stochtrack"]["singletrack"]["doSingletrack"]
else:
    do_singletrack = False
print("Creating dag and sub files")
create_anteproc_dag_v6(jobs, grandStochtrack_script_file, matlabMatrixExtractionExectuable_script_file, anteprocExecutable_script_file, dagDir, newJobPath, H1_jobs, L1_jobs, anteprocJobs, multiple_job_group_version, job_order = jobOrder, use_gpu = doGPU, restrict_cpus = options.restrict_cpus, no_job_retry = options.no_job_retry, extract_from_gpu = extract_from_gpu, alternate_preproc_dir = options.preprocDir, do_singletrack = do_singletrack)

print("NOTE: Job ordering is not currently set up to handle multiple jobs of the same number as numbered by this program.")

# create webpage

# run top DAG
