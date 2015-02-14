from __future__ import division
from optparse import OptionParser
from pyCondorSTAMPLib_V3 import *
from preprocSupportLib_V2 import *
from grandStochtrackSupportLib_V2 import *
from condorSTAMPSupportLib_V3 import *
import webpageGenerateLib as webGen
import scipy.io as sio

print("Code not currently set up to handle a mix of gpu and non-gpu jobs. A future version should be able to address this.")

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
parser.add_option("-t", "--timeLength", dest = "gsTimeLength",
                  help = "(optional) Duration limit for data input to grandstochtrack (will not run correctly \
                  if longer than non-null preproc data output)", metavar = "INT")
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

# load data from jobFile
with open(jobPath, "r") as infile:
    #jobFileData = [x.split() for x in infile]
    jobDataDict = dict((x.split()[0], x.split()[1:]) for x in infile)

# parse jobs
jobDuplicates = False
jobKey = None
jobNum = 0
jobs = {}
currentJob = None
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
            jobKey = temp + "_" + line[1]
            tempKey = jobKey
            tempNum = 1
            print(jobs.keys())
            print(tempKey)
            if tempKey in jobs:
                print("why?")
                print("seems to be a duplicate")
            while tempKey in jobs:#jobs.keys():
                jobDuplicates = True
                tempNum += 1
                tempKey = jobKey + 'v' + str(tempNum)
                print(tempKey)
                if tempKey not in jobs:
                    print("WARNING: Duplicate of job_" + line[1] + ". Renaming " + tempKey + ".")
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
                    #debug removal#jobDuration = load_number(jobData[index][3])

                    print("DEBUG: why not use load number?")
                    jobs[jobKey]["grandStochtrackParams"]["params"]["hstart"] = float(jobData[index][1])#load_number(jobData[index][1])
                    jobs[jobKey]["grandStochtrackParams"]["params"]["hstop"] = float(jobData[index][2])#load_number(jobData[index][2])

                    jobs[jobKey]["grandStochtrackParams"]["jobdur"] = float(jobData[index][2]) - float(jobData[index][1])#load_number(jobData[index][2]) - load_number(jobData[index][1])#jobDuration
                    # TODO: fix this part to handle floats

                    #debug removal#jobs[jobKey]["grandStochtrackParams"]["h"] = jobData
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
                    freqList = [float(x) for x in rawFreqs if x]#[load_number(x) for x in rawFreqs if x]
                    print("StampFreqsToRemove")
                    print(line)
                    print(freqList)
#                    print(jobs[jobKey].keys())
                    jobs[jobKey]["grandStochtrackParams"]["params"][line[1]] = freqList
                elif line[1] == "doGPU" and jobKey != "constants":
                    print("Current job: " + jobKey)
                    quit_program = True
                    print("WARNING: non-default value for 'doGPU' detected. This functionality is not currently supported but may be supported in a future version. Quitting script. \n\nPress enter to exit.")
                    version_input("")
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

#def loadEssentialParameter(parameter, dictionary, defaultDict):
#    if checkEssentialParameter(dictionary, parameter):
#        return

# check job lengths after parameters are entered
if options.gsTimeLength:
    tempDefaultDictionary = jobs["constants"]["grandStochtrackParams"]
    tempPreprocDefaultDictionary = jobs["constants"]["preprocParams"]
    defaultMaxBuffer1, quit_program = getEssentialParameter(tempPreprocDefaultDictionary, "bufferSecs1", "constants", quit_program)
    defaultMaxBuffer2, quit_program = getEssentialParameter(tempPreprocDefaultDictionary, "bufferSecs2", "constants", quit_program)
    defaultMaxBuffer = max([float(defaultMaxBuffer1),float(defaultMaxBuffer2)])
    defaultValNSPI, quit_program = getEssentialParameter(tempPreprocDefaultDictionary, "numSegmentsPerInterval", "constants", quit_program)
    defaultSpecificJobdur, quit_program = getEssentialParameter(tempDefaultDictionary, "jobdur", "constants", quit_program)
    defaultEffectiveJobLength = defaultSpecificJobdur - defaultMaxBuffer*2 - (float(defaultValNSPI) - 1) - 0.5 #0.5 due to 50 percent overlap
    if float(options.gsTimeLength) > defaultEffectiveJobLength:
        quit_program = True
        print("WARNING: Quitting program. Duration of " + job + " is shorter than required length of " + options.gsTimeLength + " seconds. Please correct this and try running program again.")
        print(jobkey + " length: " + str(effectiveJobLength))
        version_input("\n\nPress enter to quit program")
    else:
        jobs["constants"]["grandStochtrackParams"]["params"]["hstart"] += (float(defaultValNSPI) - 1)/2 + defaultMaxBuffer
        jobs["constants"]["grandStochtrackParams"]["params"]["hstop"] = jobs["constants"]["grandStochtrackParams"]["params"]["hstart"] + float(options.gsTimeLength)
        jobs["constants"]["grandStochtrackParams"]["jobdur"] = float(options.gsTimeLength)
    for job in jobs:
        specificQuantities1 = ["hstart", "hstop"]
        specificQuantities2 = ["jobdur"]
        specificQuantities3 = ["bufferSecs1", "bufferSecs2", "numSegmentsPerInterval"]
        tempDictionary = jobs[job]["grandStochtrackParams"]
        tempPreprocDictionary = jobs[job]["preprocParams"]
        specificQuantities1Check = [checkEssentialParameter(tempDictionary["params"], x) for x in specificQuantities1]
        specificQuantities2Check = [checkEssentialParameter(tempDictionary, x) for x in specificQuantities2]
        specificQuantities3Check = [checkEssentialParameter(tempPreprocDictionary, x) for x in specificQuantities3]
        if True in specificQuantities1Check + specificQuantities2Check + specificQuantities3Check:
            specificQuantitiesCheck = True
        else:
            specificQuantitiesCheck = False
        if specificQuantitiesCheck:
            maxBuffer1, quit_program = getEssentialParameter(tempPreprocDictionary, "bufferSecs1", job, quit_program, defaultMaxBuffer1)
            maxBuffer2, quit_program = getEssentialParameter(tempPreprocDictionary, "bufferSecs2", job, quit_program, defaultMaxBuffer2)
            maxBuffer = max([float(maxBuffer1),float(maxBuffer1)])
            valNSPI, quit_program = getEssentialParameter(tempPreprocDictionary, "numSegmentsPerInterval", job, quit_program, defaultValNSPI)
            specificJobDur = getEssentialParameter(tempDictionary, "jobdur", job, quit_program, defaultSpecificJobdur)
            effectiveJobLength = specificJobDur - maxBuffer*2 - (valNSPI - 1) - 0.5 #0.5 due to 50 percent overlap
            if float(options.gsTimeLength) > effectiveJobLength:
                quit_program = True
                print("WARNING: Quitting program. Duration of " + job + " is shorter than required length of " + options.gsTimeLength + " seconds. Please correct this and try running program again.")
                print(jobkey + " length: " + str(effectiveJobLength))
                version_input("\n\nPress enter to quit program")
            else:
                jobs[job]["grandStochtrackParams"]["params"]["hstart"] += (float(valNSPI) - 1)/2 + maxBuffer
                jobs[job]["grandStochtrackParams"]["params"]["hstop"] = jobs[job]["grandStochtrackParams"]["params"]["hstart"] + float(options.gsTimeLength)
                jobs[job]["grandStochtrackParams"]["jobdur"] = float(options.gsTimeLength)

if commentsToPrintIfVerbose and options.verbose:
    print(commentsToPrintIfVerbose)

print(jobs.keys())

# TODO: Warnings and error catching involving default job number and undefined job numbers
print("\n\nRemember: Finish this part.\n\n")

if jobDuplicates and not quit_program:
    quit_program = not ask_yes_no_bool("Duplicate jobs exist. Continue? (y/n)\n")
#print(quit_program)
#dict()

# check for and find real data if applicable
realDataJobs = {}
# check if real data is default
if "doDetectorNoiseSim" in jobs["constants"]["preprocParams"]:
    if jobs["constants"]["preprocParams"]["doDetectorNoiseSim"].lower() == "false":
        real_data_default = True
    elif jobs["constants"]["preprocParams"]["doDetectorNoiseSim"].lower() == "true":
        real_data_default = False
    else:
        quit_program = True
        print("Error in 'constants': 'doDetectorNoiseSim' value is not boolean. please fix.\n\nPress enter to quit.")
        version_input("")
    defaultJobNumber = checkEssentialParameter(jobs["constants"]["grandStochtrackParams"], "job")
    if defaultJobNumber:
#        print(defaultJobNumber)
#        print(type(defaultJobNumber))
#        print(len(jobNumbers))
        index = jobNumbers.index(str(defaultJobNumber))
        defaultStartTime = float(jobData[index][1])
        defaultEndTime = float(jobData[index][2])
    else:
        defaultStartTime = None
        defaultEndTime = None
    print("must be a more robust way to do this, but for now take the first char of the observatory string")
    defaultObservatory1 = checkEssentialParameter(jobs["constants"]["preprocParams"], "ifo1")[0]
    defaultObservatory2 = checkEssentialParameter(jobs["constants"]["preprocParams"], "ifo2")[0]
    defaultFrameType1 = checkEssentialParameter(jobs["constants"]["preprocParams"], "frameType1")
    defaultFrameType2 = checkEssentialParameter(jobs["constants"]["preprocParams"], "frameType2")
for job in jobs:
    # make sure to handle the default case as well
    real_data = real_data_default
#    if "doDetectorNoiseSim" in jobs[job]["preprocParams"]: and jobs[job]["preprocParams"]["doDetectorNoiseSim"].lower() == "false":
    if "doDetectorNoiseSim" in jobs[job]["preprocParams"]:
        if jobs[job]["preprocParams"]["doDetectorNoiseSim"].lower() == "false":
            real_data = True
        elif jobs[job]["preprocParams"]["doDetectorNoiseSim"].lower() == "true":
            real_data = False
        else:
            quit_program = True
            print("Error in '" + job + "': 'doDetectorNoiseSim' value is not boolean. please fix.\n\nPress enter to quit.")
            version_input("")
    if real_data:
#        print(job)
        realDataJobs[job] = {}
        # check for needed entries
        #startTime, quit_program = getEssentialParameter(jobs[job]["preprocParams"], "hstart", job, quit_program)
        jobNumber = checkEssentialParameter(jobs[job]["grandStochtrackParams"], "job")
        if jobNumber:
            index = jobNumbers.index(str(jobNumber))
            startTime = float(jobData[index][1])#load_number(jobData[index][1])
            endTime = float(jobData[index][2])
        else:
            startTime = defaultStartTime
            endTime = defaultEndTime
#        startTime = jobs[job]["preprocParams"]["hstart"]
        #endTime, quit_program = getEssentialParameter(jobs[job]["preprocParams"], "hstop", job, quit_program)
#        endTime = jobs[job]["preprocParams"]["hstop"]
        observatoryTemp1, quit_program = getEssentialParameter(jobs[job]["preprocParams"], "ifo1", job, quit_program, defaultObservatory1)
        realDataJobs[job]["observatory1"] = observatoryTemp1[0]
#        observatory1 = jobs[job]["preprocParams"]["ifo1"]
        observatoryTemp2, quit_program = getEssentialParameter(jobs[job]["preprocParams"], "ifo2", job, quit_program, defaultObservatory2)
        realDataJobs[job]["observatory2"] = observatoryTemp2[0]
#        observatory2 = jobs[job]["preprocParams"]["ifo2"]
        frameType1, quit_program = getEssentialParameter(jobs[job]["preprocParams"], "frameType1", job, quit_program, defaultFrameType1)
#        frameType1 = jobs[job]["preprocParams"]["frameType1"]
        frameType2, quit_program = getEssentialParameter(jobs[job]["preprocParams"], "frameType2", job, quit_program, defaultFrameType2)
#        frameType2 = jobs[job]["preprocParams"]["frameType2"]
        # create gps time file and frame cache file
        #print([frameType1, startTime, endTime, realDataJobs[job]["observatory1"], quit_program])
        realDataJobs[job]["frame_file_list1"], quit_program = create_frame_file_list(frameType1, str(startTime), str(endTime), realDataJobs[job]["observatory1"], quit_program)
        realDataJobs[job]["frame_file_list2"], quit_program = create_frame_file_list(frameType2, str(startTime), str(endTime), realDataJobs[job]["observatory2"], quit_program)

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
    copy_input_file(options.configFile, supportDir)#, options.configFile)
    newJobPath = copy_input_file(options.jobFile, supportDir)#, options.jobFile)
    #print(newJobPath)

    # create directory to host all of the jobs. maybe drop the cachefiles in here too?
    jobsBaseDir = create_dir(baseDir + "/jobs")

    # create cachefile directory
    if job in realDataJobs:
        cacheDir = create_dir(baseDir + "/cache_files") + "/"

    # cycle through jobs
    for job in jobs:
        if job != "constants":
            # stochtrack_day_job_num (injection? gps time?)
            #jobs[job]["jobDir"] = create_dir(baseDir + "/" + job)
            jobDir = create_dir(jobsBaseDir + "/" + job)
            jobs[job]["jobDir"] = jobDir

#			README.txt with job information? json maybe? job type
#			preproc inputs
            preprocInputDir = create_dir(jobDir + "/preprocInput")
            jobs[job]["preprocInputDir"] = preprocInputDir
            preprocOutputDir = create_dir(jobDir + "/preprocOutput")
            jobs[job]["preprocOutputDir"] = preprocOutputDir

            # output directory for preproc dictionary
            jobs[job]["preprocParams"]["outputfiledir"] = preprocOutputDir + "/" #jobs[job]["preprocInputDir"]

#			inputs for stochtrack clustermap in text file (put this here or in the "/params" directory)
#			grand_stochtrack inputs
            stochtrackInputDir = create_dir(jobDir + "/grandstochtrackInput")
            jobs[job]["stochtrackInputDir"] = stochtrackInputDir
#			results
            resultsDir = create_dir(jobDir + "/grandstochtrackOutput")
            jobs[job]["resultsDir"] = resultsDir
#				overview mat
#				some other thing?
#				plotDir
            plotDir = create_dir(resultsDir + "/plots")
            jobs[job]["plotDir"] = plotDir
            if job in realDataJobs:
                #cacheDir = create_dir(jobDir + "/cacheFiles")
                #realDataJobs[job]["cacheDir"] = cacheDir
                if "job" in jobs[job]["grandStochtrackParams"]:
                    jobNum = jobs[job]["grandStochtrackParams"]["job"]
                else:
                    jobNum = jobs["constants"]["grandStochtrackParams"]["job"]
                quit_program = create_cache_and_time_file(realDataJobs[job]["frame_file_list1"],realDataJobs[job]["observatory1"],jobNum,cacheDir,quit_program)
                quit_program = create_cache_and_time_file(realDataJobs[job]["frame_file_list2"],realDataJobs[job]["observatory2"],jobNum,cacheDir,quit_program)
                # add to parameters
                jobs[job]["preprocParams"]["gpsTimesPath1"] = cacheDir
                jobs[job]["preprocParams"]["gpsTimesPath2"] = cacheDir
                jobs[job]["preprocParams"]["frameCachePath1"] = cacheDir
                jobs[job]["preprocParams"]["frameCachePath2"] = cacheDir

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
#            jobs[job]["grandStochtrackParams"]["params"]["jobsFile"] = options.jobFile
            jobs[job]["grandStochtrackParams"]["params"]["jobsFile"] = newJobPath
            jobs[job]["grandStochtrackParams"]["params"]["inmats"] = jobs[job]["preprocOutputDir"] + "/map"
            jobs[job]["grandStochtrackParams"]["params"]["ofile"] = jobs[job]["resultsDir"] + "/bknd"

            # write start and end times
 #           jobs[job]["grandStochtrackParams"]["params"]["hstart"] =
#            jobs[job]["grandStochtrackParams"]["params"]["hend"] =

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

# order plots by job
#jobDirs = [job for job in jobs]

jobTempDict = dict((int(job[job.index("_")+1:]),job) for job in [x for x in jobs if x != "constants"])

plotTypeList = ["SNR", "Loudest Cluster", "sig map", "y map", "Xi snr map"]

plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster" : "rmap.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png"}

outFile = "pageDisplayTest.html"

jobNumOrder = [jobNum for jobNum in jobTempDict]
jobNumOrder.sort()
jobOrder = [jobTempDict[jobNum] for jobNum in jobNumOrder]

#webGen.make_display_page(directory, saveDir, subDirList, subSubDir, plotTypeList, plotTypeDict, outputFileName)
print('DEBUG NOTE: Maybe figure out how to variablize "grandstochtrackOutput/plots" in next line?')
webGen.make_display_page("jobs", baseDir, jobOrder, "grandstochtrackOutput/plots", plotTypeList, plotTypeDict, outFile)

# build DAGs
# preproc DAG
if not quit_program:
    # build submission file
    #write_sub_file("preproc", preprocExecutable, dagDir, "$(paramFile) $(jobFile) $(jobNum)")
    doGPU = jobs["constants"]["grandStochtrackParams"]["params"]["doGPU"]
    create_preproc_dag(jobs, preprocExecutable, grandStochtrackExecutable, dagDir, shellPath, quit_program, job_order = jobOrder)
# grand_stochtrack DAG
    # build stochtrack submission file
#    write_sub_file("grand_stochtrack", grandStochtrackExecutable, dagDir, "???")

print("NOTE: Job ordering is not currently set up to handle multiple jobs of the same number as numbered by this program.")

# create webpage

# run top DAG
