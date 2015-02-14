from optparse import OptionParser
from pyCondorSTAMPLib import *
from preprocSupportLib import *
from grandStochtrackSupportLib import *
from condorSTAMPSupportLib import *
import scipy.io as sio

#### REMINDER: Edit the grand_stochtrack parameter reader such that "." will
# allow easy access to subdirectories in the grand_stochtrack parameter matrix

# include parameter file option eventually to move plots over to get rid of initial black band (located in grand_stochtrack param file)

# command line options
parser = OptionParser()
parser.set_defaults(verbose = True)
parser.add_option("-c", "--conf", dest = "configFile",
                  help = "Path to config file detailing analysis for preproc and grand_stochtrack executables",
                  metavar = "FILE")
parser.add_option("-j", "--jobFile", dest = "jobFile",
                  help = "Path to job file detailing job times and durations",
                  metavar = "FILE")
parser.add_option("-d", "--dir", dest = "outputDir",
                  help = "Path to directory to hold analysis output (a new directory \
will be created with appropriate subdirectories to hold analysis)", metavar = "DIRECTORY")
parser.add_option("-v", action="store_true", dest="verbose")

# MAYBE maxjobs will be useful.

parser.add_option("-m", "--maxjobs", dest = "maxjobs",
                  help = "Maximum number of jobs ever submitted at once \
through condor", metavar = "NUMBER")

# add options to load defaults for preproc and grand_stochtrack

(options, args) = parser.parse_args()
if options.outputDir[0:2] == "./":
    options.outputDir = os.getcwd() + options.outputDir[1:]
if options.jobFile[0:2] == "./":
    options.jobFile = os.getcwd() + options.jobFile[1:]

# constants
quit_program = False
# can adjust path from relative to absolute here
configPath = options.configFile
jobPath = options.jobFile
# default dictionary json path
defaultDictionaryPath = "/home/quitzow/STAMP/stamp2/test/condorTesting/pythonWrapper/default/defaultStochtrack.json"
# set other defaults this way too instead of definining them inside the preprocSupportLib.py file

#defaultDictionaryPath = "/Users/Quitzow/Desktop/Magnetar Research/STAMP Condor Related/PythonWrapper/defaultBase3.txt"
shellPath = "#!/bin/bash"

# paths to executables
preprocExecutable = "/home/quitzow/STAMP/stamp2/test/condorTesting/preprocDir/preproc"
grandStochtrackExecutable = "/home/quitzow/STAMP/stamp2/test/condorTesting/grand_stochtrack"

# check for minimum commands line arguments to function
if not options.configFile or not options.outputDir or not options.jobFile:
    print("\nMissing arguments: please specify at least a configuration file, a \
job file and \nan output plot directory to run this program.\n\n")
    quit_program = True
else:
    quit_program = False

# load info from config file
if not quit_program:
    rawData = read_text_file(configPath, ' ')
#    print(read_text_file(options.configFile," "))
else:
    rawData = []

#print(options.configFile)
#print(rawData)

# load info from job file
if not quit_program:
    jobData = read_text_file(jobPath, ' ')
    jobNumbers = [line[0] for line in jobData]
    jobData = [[load_if_number(item) for item in line] for line in jobData]
#    print(read_text_file(options.configFile," "))
else:
    jobData = []

# load default dictionary if selected
# TODO: fix this for option to exclude default dictionary if wished
if not quit_program:
    defaultDictionary = load_dict_from_json(defaultDictionaryPath)
else:
    defaultDictionary = {}

# parse jobs
jobDuplicates = False
jobKey = None
jobNum = 0
jobs = {}
commentsToPrintIfVerbose = []
if not quit_program:
    for line in rawData: # make this rawData?
        temp = line[0].lower()
        # user set defaults
        if temp == 'constants': # make this 'general' instead at some point
            jobKey = temp
            if jobKey not in jobs:
                jobs[jobKey] = {}
            if "preprocParams" not in jobs[jobKey]:
                jobs[jobKey]["preprocParams"] = {}
            if "grandStochtrackParams" not in jobs[jobKey]:
                jobs[jobKey]["grandStochtrackParams"] = {}
                jobs[jobKey]["grandStochtrackParams"]["params"] = {}
        # job specific settings
        elif temp == 'job':
            jobKey = temp + line[1]
            tempKey = jobKey
            tempNum = 1
            print(jobs.keys())
            print(tempKey)
            if tempKey in jobs:
                print("why?")
            while tempKey in jobs:#jobs.keys():
                jobDuplicates = True
                tempNum += 1
                tempKey = jobKey + 'v' + str(tempNum)
                print(tempKey)
                if tempKey not in jobs:
                    print("WARNING: Duplicate of job" + line[1] + ". Renaming " + tempKey + ".")
            print(jobKey)
            jobKey = tempKey # is tempKey really needed then?
            print(jobKey)
            if jobKey not in jobs: # okay, now this if statement seems unnecessary.
                # see note on line above
                jobs[jobKey] = {}
            if "preprocParams" not in jobs[jobKey]:
                jobs[jobKey]["preprocParams"] = {}
            if "grandStochtrackParams" not in jobs[jobKey]:
                jobs[jobKey]["grandStochtrackParams"] = {}
                jobs[jobKey]["grandStochtrackParams"]["params"] = {}
        # preproc settings
        elif temp == "preproc":
#            jobs[jobKey]["preprocParams"][line[1]] = line[2]
#            print(line)
            if len(line) != 3:
                print("Alert, the following line contains a different number of entries than 3:")
                print(line)
                quit_program = True
            else:
                jobs[jobKey]["preprocParams"][line[1]] = line[2]
                #jobs[jobKey]["preprocParams"] = nested_dict_entry(jobs[jobKey]["preprocParams"], line[1], line[2])
        # grand_stochtrack settings
        elif temp == "grandstochtrack":
            print("Fix this part to handle numbers properly! And less jumbled if possible!")
            if line[1].lower() == "job":
                if len(line) != 3:
                    print("Alert, the following line contains a different number of entries than 3:")
                    print(line)
                    quit_program = True
                else:
                    jobNumber = line[2]
                    jobs[jobKey]["grandStochtrackParams"]["job"] = int(jobNumber)
                    #jobs[jobKey]["grandStochtrackParams"]["jobsFile"] = jobPath

                    # find job duration for given job number (currently rounding to indices, but will change to
                    # handle floats as well in the future)
                    index = jobNumbers.index(jobNumber)
                    jobDuration = load_number(jobData[index][3])
                    jobs[jobKey]["grandStochtrackParams"]["jobdur"] = jobDuration
                    # TODO: fix this part to handle floats

                    jobs[jobKey]["grandStochtrackParams"]["h"] = jobData
            else:
                #jobs[jobKey]["grandStochtrackParams"]["params"][line[1]] = load_if_number(line[2])
                if line[1] == "StampFreqsToRemove":
                    rawFreqs = [x.split(",") for x in line[2:]]
                    print(rawFreqs)
                    rawFreqs = [item for sublist in rawFreqs for item in sublist]
                    print(rawFreqs)
#                    rawFreqs = [x.replace(item, "") for item in ["[","]"] if item in x else x for x in rawFreqs]
#                    rawFreqs = [x.replace(item, "") if item in x else x for item in ["[","]"] for x in rawFreqs]
                    rawFreqs = [x.replace("[", "") if "[" in x else x for x in rawFreqs]
                    print(rawFreqs)
                    rawFreqs = [x.replace("]", "") if "]" in x else x for x in rawFreqs]
                    print(rawFreqs)
                    freqList = [load_number(x) for x in rawFreqs if x]
                    print("StampFreqsToRemove")
                    print(line)
                    print(freqList)
#                    print(jobs[jobKey].keys())
                    jobs[jobKey]["grandStochtrackParams"]["params"][line[1]] = freqList
                elif len(line) != 3:
                    print("Alert, the following line contains a different number of entries than 3:")
                    print(line)
                    quit_program = True
                # if statements to catch if attribute is boolean. This may need to be handled another way, but
                # check in the created .mat file to see if this successfully sets the variables to booleans.
                elif line[2].lower() == "true":
                    jobs[jobKey]["grandStochtrackParams"]["params"] = nested_dict_entry(jobs[jobKey]["grandStochtrackParams"]["params"], line[1], True)
                elif line[2].lower() == "false":
                    jobs[jobKey]["grandStochtrackParams"]["params"] = nested_dict_entry(jobs[jobKey]["grandStochtrackParams"]["params"], line[1], False)
                # maybe place here if statments to catch if the start and end times are being set, and if so
                # inform the user that this will overwite the times from the job files and prompt user for input
                # on whether this is okay. If not, quit program so user can fix input file.
                else:
                    jobs[jobKey]["grandStochtrackParams"]["params"] = nested_dict_entry(jobs[jobKey]["grandStochtrackParams"]["params"], line[1], load_if_number(line[2]))
                '''if line[1] == "StampFreqsToRemove":
                    freqList = [load_number(x) for x in line[2:]]
                    print("StampFreqsToRemove")
                    print(line)
                    print(freqList)
#                    print(jobs[jobKey].keys())
                    jobs[jobKey]["grandStochtrackParams"]["params"][line[1]] = freqList
                elif len(line) != 3:
                    print("Alert, the following line contains a different number of entries than 3:")
                    print(line)
                    quit_program = True'''
        elif temp[0] in ["#", "%"]:
            commentsToPrintIfVerbose.append(line)
        else:
            print("WARNING: Error in config file. Option " + temp + " not recognized. Quitting program.")
            quit_program = True
    if 'constants' not in jobs:
        jobs['constants'] = {}
        jobs['constants']["preprocParams"] = {}
        jobs['constants']["grandStochtrackParams"] = {}
        jobs['constants']["grandStochtrackParams"]["params"] = {}

if commentsToPrintIfVerbose and options.verbose:
    print(commentsToPrintIfVerbose)

print(jobs.keys())

# TODO: Warnings and error catching involving default job number and undefined job numbers
print("\n\nRemember: Finish this part.\n\n")

if jobDuplicates and not quit_program:
    quit_program = not ask_yes_no_bool("Duplicate jobs exist. Continue? (y/n)\n")
#print(quit_program)
#dict()

# update default dictionary
print(jobs['constants'].keys())
defaultDictionary = load_default_dict(jobs['constants']['grandStochtrackParams']['params'] , defaultDictionary)

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

if not quit_program:
    # Build base analysis directory
    # stochtrack_condor_job_group_num
    if options.outputDir[-1] == "/":
        baseDir = dated_dir(options.outputDir + "stamp_analysis")
    else:
        baseDir = dated_dir(options.outputDir + "/stamp_analysis")
    print(baseDir)#debug

    # copy input parameter file and jobs file into a support directory here
    # support directory
    supportDir = create_dir(baseDir + "/input_files")
    # copy input files to this directory
    copy_input_file(supportDir, options.configFile)
    copy_input_file(supportDir, options.jobFile)

    # cycle through jobs
    for job in jobs:
        if job != "constants":
            # stochtrack_day_job_num (injection? gps time?)
            #jobs[job]["jobDir"] = create_dir(baseDir + "/" + job)
            jobDir = create_dir(baseDir + "/" + job)
            jobs[job]["jobDir"] = jobDir

#			README.txt with job information? json maybe? job type
#			preproc inputs
            preprocInputDir = create_dir(jobDir + "/input")
            jobs[job]["preprocInputDir"] = preprocInputDir

            # output directory for preproc dictionary
            jobs[job]["preprocParams"]["outputfiledir"] = preprocInputDir + "/" #jobs[job]["preprocInputDir"]

#			inputs for stochtrack clustermap in text file (put this here or in the "/params" directory)
#			grand_stochtrack inputs
            stochtrackInputDir = create_dir(jobDir + "/params")
            jobs[job]["stochtrackInputDir"] = stochtrackInputDir
#			results
            resultsDir = create_dir(jobDir + "/output")
            jobs[job]["resultsDir"] = resultsDir
#				overview mat
#				some other thing?
#				plotDir
            plotDir = create_dir(resultsDir + "/plots")
            jobs[job]["plotDir"] = plotDir

        # NOTE: recording any directories other than the base job directory may not have any value
        # because the internal structure of each job is identical.

    # build dag directory
    dagDir = create_dir(baseDir + "/dag")

    # Build support file sub directory for dag logs
    dagLogDir = create_dir(dagDir + "/dagLogs")

    # Build support file sub directory for job logs
    logDir = create_dir(dagLogDir + "/logs")
else:
    baseDir = None
#    supportDir = None
#    frameListDir = None
#    frameDir = None
#    plotDir = None

print(jobs.keys())
print(jobs["constants"].keys())

# write preproc parameter files for each job
if not quit_program:
    for job in jobs:
        if job != "constants":
            tempDict = {}
            #tempDict.update(jobs[job]["preprocParams"])
            #if "constants" in jobs: # better way to handle this?
             #   tempDict.update(jobs["constants"]["preprocParams"])
            #tempDict.update(jobs[job]["preprocParams"])
            tempDict = load_default_dict(tempDict, jobs[job]["preprocParams"])
            if "constants" in jobs:
                tempDict = load_default_dict(tempDict, jobs["constants"]["preprocParams"])
            outputName = "preprocParams.txt"
            buildPreprocParamFile(tempDict, jobs[job]["preprocInputDir"] + "/" + outputName)

            # put output directories in grand_stochtrack dictionary
            jobs[job]["grandStochtrackParams"]["params"]["plotdir"] = jobs[job]["plotDir"] + "/"
            jobs[job]["grandStochtrackParams"]["params"]["outputfilename"] = jobs[job]["resultsDir"] + "/map"
            jobs[job]["grandStochtrackParams"]["params"]["jobsFile"] = options.jobFile
            jobs[job]["grandStochtrackParams"]["params"]["inmats"] = jobs[job]["preprocInputDir"] + "/map"
            jobs[job]["grandStochtrackParams"]["params"]["ofile"] = jobs[job]["stochtrackInputDir"] + "/bknd"

            # write stochtrack parameter files for each job
            #jobDictionary = load_default_dict(jobs[job]['params'] , defaultDictionary)
            jobs[job]['grandStochtrackParams']['params'] = load_default_dict(jobs[job]['grandStochtrackParams']['params'] , defaultDictionary)
            # the way this following line is done needs to be reviewed.
            jobs[job]['grandStochtrackParams'] = load_default_dict(jobs[job]['grandStochtrackParams'], jobs["constants"]['grandStochtrackParams'])
            # write matrix file
            print(jobs[job].keys())
            for key in jobs[job]:
                if isinstance(jobs[job][key], dict):
                    print("dictionary found")
                    print(key)
                    print(jobs[job][key].keys())
#                    print(jobs[job][key])
            if "job" not in jobs[job]["grandStochtrackParams"]:
                print("\nQuitting Program: 'job' not specified for " + job + ". Please specify job then try\nagain.\n\n")
                quit_program = True
            sio.savemat(jobs[job]["stochtrackInputDir"] + "/" + "params.mat", jobs[job]["grandStochtrackParams"])

# build DAGs
# preproc DAG
if not quit_program:
    # build submission file
    #write_sub_file("preproc", preprocExecutable, dagDir, "$(paramFile) $(jobFile) $(jobNum)")
    create_preproc_dag(jobs, preprocExecutable, grandStochtrackExecutable, dagDir, shellPath, quit_program)
# grand_stochtrack DAG
    # build stochtrack submission file
#    write_sub_file("grand_stochtrack", grandStochtrackExecutable, dagDir, "???")

# run top DAG
