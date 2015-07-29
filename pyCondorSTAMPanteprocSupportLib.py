from __future__ import division
from pyCondorSTAMPLib import nested_dict_entry
from grandStochtrackSupportLib import load_if_number

def parse_jobs(raw_data, quit_program):
    'Helper function to parse jobs for STAMP'
    jobs = {}
    commentsToPrintIfVerbose = []
    job_groups = []
    jobDuplicates = False
    anteproc_jobs_1 = []
    anteproc_jobs_2 = []
    if not quit_program:
        for line in raw_data:
            temp = line[0].lower()
            # user set defaults
            if temp == 'constants': # make this 'general' instead at some point
                job_key = temp
                if job_key not in jobs:
                    jobs[job_key] = {}
                if "preprocParams" not in jobs[job_key]:
                    jobs[job_key]["preprocParams"] = {}
                if "anteprocParamsH" not in jobs[job_key]:
                    jobs[job_key]["anteprocParamsH"] = {}
                if "anteprocParamsL" not in jobs[job_key]:
                    jobs[job_key]["anteprocParamsL"] = {}
                if "grandStochtrackParams" not in jobs[job_key]:
                    jobs[job_key]["grandStochtrackParams"] = {}
                    jobs[job_key]["grandStochtrackParams"]["params"] = {}
            # job specific settings
            elif temp == 'job':
                job_key = temp + "_" + line[1]
                temp_key = job_key
                temp_num = 1
                #print(jobs.keys())
                #print(temp_key)
                while temp_key in jobs:
                    jobDuplicates = True
                    temp_num += 1
                    temp_key = job_key + 'v' + str(temp_num)
                    print(temp_key)
                    if temp_key not in jobs:
                        print("WARNING: Duplicate of job_" + line[1] + ". Renaming " + temp_key + ".")
                job_key = temp_key
                if job_key not in jobs:
                    jobs[job_key] = {}
                jobs[job_key]["jobNum"] = line[1]
                if "preprocParams" not in jobs[job_key]:
                    jobs[job_key]["preprocParams"] = {}
                if "anteprocParamsH" not in jobs[job_key]:
                    jobs[job_key]["anteprocParamsH"] = {}
                if "anteprocParamsL" not in jobs[job_key]:
                    jobs[job_key]["anteprocParamsL"] = {}
                if "grandStochtrackParams" not in jobs[job_key]:
                    jobs[job_key]["grandStochtrackParams"] = {}
                    jobs[job_key]["grandStochtrackParams"]["params"] = {}
                if "job_group" not in jobs[job_key]:
                    jobs[job_key]["job_group"] = None
            # job_group
            elif temp == "job_group":
                jobs[job_key]["job_group"] = line[1]
                job_groups += [line[1]]
            # info for adjusted job file
            elif temp == "job_start_shift":
                jobs[job_key]["job_start_shift"] = line[1]
            elif temp == "job_duration":
                jobs[job_key]["job_duration"] = line[1]
            # preproc settings
            elif temp == "preproc":
                if line[1].lower() == "job":
                    if len(line) != 3:
                        print("Alert, the following line contains a different number of entries than 3:")
                        print(line)
                        quit_program = True
                    else:
                        jobNumber = line[2]
                        jobs[job_key]["preprocJobs"] = jobNumber
                else:
                    if len(line) != 3:
                        print("Alert, the following line contains a different number of entries than 3:")
                        print(line)
                        quit_program = True
                    else:
                        jobs[job_key]["preprocParams"][line[1]] = line[2]
            elif temp == "anteproc_h":
                if line[1].lower() == "job":
                    if len(line) != 3:
                        print("Alert, the following line contains a different number of entries than 3:")
                        print(line)
                        quit_program = True
                    else:
                        jobNumber = line[2]
                        jobs[job_key]["preprocJobs"] = jobNumber
                else:
                    if len(line) != 3:
                        print("Alert, the following line contains a different number of entries than 3:")
                        print(line)
                        quit_program = True
                    else:
                        jobs[job_key]["anteprocParamsH"][line[1]] = line[2]
            elif temp == "anteproc_l":
                if line[1].lower() == "job":
                    if len(line) != 3:
                        print("Alert, the following line contains a different number of entries than 3:")
                        print(line)
                        quit_program = True
                    else:
                        jobNumber = line[2]
                        jobs[job_key]["preprocJobs"] = jobNumber
                else:
                    if len(line) != 3:
                        print("Alert, the following line contains a different number of entries than 3:")
                        print(line)
                        quit_program = True
                    else:
                        jobs[job_key]["anteprocParamsL"][line[1]] = line[2]
            elif temp == "grandstochtrack":
                print("Fix this part to handle numbers properly! And less jumbled if possible!")
                if line[1] == "StampFreqsToRemove":
                    rawFreqs = [x.split(",") for x in line[2:]] # this part actually just strips the comma. The really frequency splitting is actually due to the list comprehension itself, or rather this part: line[2:]. Since the frequencies were already split in an earlier line.
                    # not a terrible check to have, just in case commas are used and spaces forgotten
                    rawFreqs = [item for sublist in rawFreqs for item in sublist]
                    rawFreqs = [x.replace("[", "") if "[" in x else x for x in rawFreqs]
                    rawFreqs = [x.replace("]", "") if "]" in x else x for x in rawFreqs]
                    freqList = [float(x) for x in rawFreqs if x]#[load_number(x) for x in rawFreqs if x]
                    print("StampFreqsToRemove")
                    print(freqList)
                    jobs[job_key]["grandStochtrackParams"]["params"][line[1]] = freqList
                elif line[1] == "doGPU" and job_key != "constants":
                    print("Current job: " + job_key)
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
                    jobs[job_key]["grandStochtrackParams"]["params"] = nested_dict_entry(jobs[job_key]["grandStochtrackParams"]["params"], line[1], True)
                elif line[2].lower() == "false":
                    jobs[job_key]["grandStochtrackParams"]["params"] = nested_dict_entry(jobs[job_key]["grandStochtrackParams"]["params"], line[1], False)
                    # maybe place here if statments to catch if the start and end times are being set, and if so
                    # inform the user that this will overwite the times from the job files and prompt user for input
                    # on whether this is okay. If not, quit program so user can fix input file.
                else:
                    if line[1] == "anteproc.jobNum1":
                        anteproc_jobs_1 += [int(line[2])]
                    if line[1] == "anteproc.jobNum2":
                        anteproc_jobs_2 += [int(line[2])]
                    jobs[job_key]["grandStochtrackParams"]["params"] = nested_dict_entry(jobs[job_key]["grandStochtrackParams"]["params"], line[1], load_if_number(line[2]))
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
    return quit_program, jobs, commentsToPrintIfVerbose, job_groups, jobDuplicates, anteproc_jobs_1, anteproc_jobs_2

def anteproc_setup(anteproc_directory, anteproc_default_data, job_dictionary, cache_directory):
    anteproc_H = dict((x[0], x[1]) if len(x) > 1 else (x[0], "") for x in anteproc_default_data)
    anteproc_L = dict((x[0], x[1]) if len(x) > 1 else (x[0], "") for x in anteproc_default_data)
    if "doDetectorNoiseSim" in job_dictionary["constants"]["anteprocParamsH"]:
        simulated = job_dictionary["constants"]["anteprocParamsH"]["doDetectorNoiseSim"]
        anteproc_H["doDetectorNoiseSim"] = simulated
        anteproc_L["doDetectorNoiseSim"] = simulated
    anteproc_H["outputfiledir"] = anteproc_directory + "/"
    anteproc_L["outputfiledir"] = anteproc_directory + "/"
    if "DetectorNoiseFile" in job_dictionary["constants"]["anteprocParamsH"]:
        anteproc_H["DetectorNoiseFile"] = job_dictionary["constants"]["anteprocParamsH"]["DetectorNoiseFile"]
    if "DetectorNoiseFile" in job_dictionary["constants"]["anteprocParamsL"]:
        anteproc_L["DetectorNoiseFile"] = job_dictionary["constants"]["anteprocParamsL"]["DetectorNoiseFile"]

    if "segmentDuration" in job_dictionary["constants"]["anteprocParamsH"]:
        anteproc_H["segmentDuration"] = job_dictionary["constants"]["anteprocParamsH"]["segmentDuration"]
    if "segmentDuration" in job_dictionary["constants"]["anteprocParamsL"]:
        anteproc_L["segmentDuration"] = job_dictionary["constants"]["anteprocParamsL"]["segmentDuration"]
    anteproc_H["gpsTimesPath1"] = cache_directory
    anteproc_H["frameCachePath1"] = cache_directory
    anteproc_L["gpsTimesPath1"] = cache_directory
    anteproc_L["frameCachePath1"] = cache_directory

    anteproc_H["ifo1"] = "H1"
    anteproc_H["ASQchannel1"] = "LDAS-STRAIN"
    anteproc_H["frameType1"] = "H1_LDAS_C02_L2"
    anteproc_L["ifo1"] = "L1"
    anteproc_L["ASQchannel1"] = "LDAS-STRAIN"
    anteproc_L["frameType1"] = "L1_LDAS_C02_L2"
    return anteproc_H, anteproc_L

def save_anteproc_paramfile(anteproc_dict, anteproc_name, anteproc_default_data):
    default_keys = [x[0] for x in anteproc_default_data]
    output_string = "\n".join(str(key) + " " + str(anteproc_dict[key]) for key in default_keys)
    output_string += "\n" + "\n".join(str(key) + " " + str(anteproc_dict[key]) for key in anteproc_dict if key not in default_keys)
    with open(anteproc_name, "w") as outfile:
        outfile.write(output_string)

def adjusted_job_file_name(filePath, outputDirectory):
    if "/" in filePath:
        reversePath = filePath[::-1]
        reverseName = reversePath[:reversePath.index("/")]
        fileName = reverseName[::-1]
    else:
        fileName = filePath
    fileName_front = fileName[:fileName.index(".")]
    fileName_back = fileName[fileName.index("."):]
    fileName = fileName_front + "_postprocessing" + fileName_back
    if outputDirectory[-1] == "/":
        outputPath = outputDirectory + fileName
    else:
        outputPath = outputDirectory + "/" + fileName
    return outputPath

def adjust_job_file(filePath, outputDirectory, job_dictionary):
    outputPath = adjusted_job_file_name(filePath, outputDirectory)
    #NSPI = int(job_dictionary["constants"]["preprocParams"]["numSegmentsPerInterval"])
    #bufferSecs = int(job_dictionary["constants"]["preprocParams"]["bufferSecs1"])
    #numSegmentsPerInterval
    start_shift = int(job_dictionary["constants"]["job_start_shift"])
    duration = int(job_dictionary["constants"]["job_duration"])
    with open(filePath, "r") as infile:
        data = [[int(x) for x in line.split()] for line in infile]
    data2 = [[x[0], x[1] + start_shift, x[1] + start_shift + duration, duration] for x in data]
    text = "\n".join(" ".join(str(x) for x in line) for line in data2)
    with open(outputPath,"w") as outfile:
        outfile.write(text)
    return outputPath
