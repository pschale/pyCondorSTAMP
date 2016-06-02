from __future__ import division
from pyCondorSTAMPLib import nested_dict_entry, create_dir
from grandStochtrackSupportLib import load_if_number, load_number
import numpy as np
import random
from os import getcwd

def parse_jobs(raw_data):
    'Helper function to parse jobs for STAMP'
    print("Fix this (grand_stochtrack selection) part to handle numbers properly! And less jumbled if possible!")
    jobs = {}
    commentsToPrintIfVerbose = []
    job_groups = []
    jobDuplicates = False
    anteproc_jobs_1 = []
    anteproc_jobs_2 = []
    seeds = []
    #waveforms = {'default':None}
    waveforms = {}
    varying_anteproc_variables = {"set": {}, "random": {}, "num_space": {}}
    # set is a given set, random is from a uniform distribution, and num_space is evenly spaced as viewed on either a linear or logarithmic axis.

    	# Loop over each line in the config file
    for line in raw_data:
        temp = line[0].lower() 		#makes everything lowercase
            
        #Classify each line:
        if temp[0] in ["#", "%"]: 	#any comments just get carried along
               commentsToPrintIfVerbose.append(line)
            # user set defaults
        elif temp == 'constants': # make this 'general' instead at some point
            job_key = temp
            if job_key not in jobs:
                jobs[job_key] = {}
            if "preprocParams" not in jobs[job_key]:
                jobs[job_key]["preprocParams"] = {}
            if "anteprocParamsH" not in jobs[job_key]:
                jobs[job_key]["anteprocParamsH"] = {}
            if "anteprocHjob_seeds" not in jobs[job_key]:
                jobs[job_key]["anteprocHjob_seeds"] = {}
            if "anteprocH_parameters" not in jobs[job_key]:
                jobs[job_key]["anteprocH_parameters"] = {}
            if "anteprocH_waveforms" not in jobs[job_key]:
                jobs[job_key]["anteprocH_waveforms"] = {}
            if "anteprocParamsL" not in jobs[job_key]:
                jobs[job_key]["anteprocParamsL"] = {}
            if "anteprocLjob_seeds" not in jobs[job_key]:
                jobs[job_key]["anteprocLjob_seeds"] = {}
            if "anteprocL_parameters" not in jobs[job_key]:
                jobs[job_key]["anteprocL_parameters"] = {}
            if "anteprocL_waveforms" not in jobs[job_key]:
                jobs[job_key]["anteprocL_waveforms"] = {}
            if "grandStochtrackParams" not in jobs[job_key]:
                jobs[job_key]["grandStochtrackParams"] = {}
                jobs[job_key]["grandStochtrackParams"]["params"] = {}
        elif len(line) == 1:
            raise pyCondorSTAMPanteprocError("Line " + str(line) + " contains only 1 entry")

        elif temp == 'waveform':
            if len(line) != 3:
                raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 3")

            else:
                wave_id = line[1]
                wave_file_path = line[2]
                waveforms[wave_id] = wave_file_path
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
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 3")
                else:
                    jobNumber = line[2]
                    jobs[job_key]["preprocJobs"] = jobNumber
            else:
                if len(line) != 3:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 3")
                else:
                    jobs[job_key]["preprocParams"][line[1]] = line[2]
                    
        elif temp == "anteproc_h":
            if line[1].lower() == "job":
                if len(line) != 3:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 3")
                else:
                    jobNumber = line[2]
                    jobs[job_key]["preprocJobs"] = jobNumber
            elif line[1] == "job_seed":
                if len(line) != 4:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 3")
                elif line[2] in jobs['constants']["anteprocHjob_seeds"]:
                    raise pyCondorSTAMPanteprocError("Seed for job " + str(line[2]) + "is already recorded.")
                elif line[3] in seeds:
                    raise pyCondorSTAMPanteprocError("Seed " + str(line[3]) + "has already been used in another job.")
                else:
                    jobNumber = int(line[2])
                    seed = int(line[3])
                    jobs['constants']["anteprocHjob_seeds"][jobNumber] = seed
                    seeds += [seed]
            elif line[1] == "anteproc_param":
                if len(line) != 5:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 5")
                else:
                    jobNumber = int(line[2])
                    parameter = line[3]
                    value = load_if_number(line[4])
                    if jobNumber not in jobs['constants']["anteprocH_parameters"]:
                        jobs['constants']["anteprocH_parameters"][jobNumber] = {}
                    jobs['constants']["anteprocH_parameters"][jobNumber][parameter] = value
            elif line[1] == "anteproc_injection":
                if len(line) <4:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains less than than 3 enries")

                else:
                    jobNumber = int(line[2])
                    wave_ids = [x.strip("[]") for group in line[3:] for x in group.split(',')]
                    if jobNumber not in jobs['constants']["anteprocH_waveforms"]:
                        jobs['constants']["anteprocH_waveforms"][jobNumber] = wave_ids
                    else:
                        raise pyCondorSTAMPanteprocError("Duplicate waveform assignemtn on line " + str(line))

            else:
                if len(line) != 3:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 3")
                else:
                    jobs[job_key]["anteprocParamsH"][line[1]] = line[2]
                        
        elif temp == "anteproc_l":
            if line[1].lower() == "job":
                if len(line) != 3:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 3")
                else:
                    jobNumber = line[2]
                    jobs[job_key]["preprocJobs"] = jobNumber
            elif line[1] == "job_seed":
                if len(line) != 4:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 4")
                elif line[2] in jobs['constants']["anteprocLjob_seeds"]:
                    raise pyCondorSTAMPanteprocError("Seed for job " + str(line[2]) + "is already recorded.")
                elif line[3] in seeds:
                    raise pyCondorSTAMPanteprocError("Seed " + str(line[3]) + "has already been used in another job.")
                else:
                    jobNumber = int(line[2])
                    seed = int(line[3])
                    jobs['constants']["anteprocLjob_seeds"][jobNumber] = seed
                    seeds += [seed]
            elif line[1] == "anteproc_param":
                if len(line) != 5:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 5")
                else:
                    jobNumber = int(line[2])
                    parameter = line[3]
                    value = load_if_number(line[4])
                    if jobNumber not in jobs['constants']["anteprocL_parameters"]:
                        jobs['constants']["anteprocL_parameters"][jobNumber] = {}
                    jobs['constants']["anteprocL_parameters"][jobNumber][parameter] = value
            elif line[1] == "anteproc_injection":
                if len(line) <4:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 4")
                else:
                    jobNumber = int(line[2])
                    wave_ids = [x.strip("[]") for group in line[3:] for x in group.split(',')]
                    if jobNumber not in jobs['constants']["anteprocL_waveforms"]:
                        jobs['constants']["anteprocL_waveforms"][jobNumber] = wave_ids
                    else:
                        raise pyCondorSTAMPanteprocError("Duplicate waveform assignment on line " + str(line))
            else:
                if len(line) != 3:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 3")
                else:
                    jobs[job_key]["anteprocParamsL"][line[1]] = line[2]
                        
        elif temp == "injection_tag":
            if len(line) != 2:
                raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 2")
            else:
                    #wave_ids = [x.strip("[]") for group in line[1:] for x in group.split(',')]
                jobs[job_key]["injection_tags"] = line[1]
                    
        elif temp == "anteproc_varying_param":
            temp_variable = line[2]
            if line[1] == "num_jobs_to_vary":
                if int(line[2]) != float(line[2]) or int(line[2]) <= 0:
                    raise pyCondorSTAMPanteprocError("Error, please choose a positive integer value for 'num_jobs_to_vary'. Value chosen was:" + str(line[2]))
                varying_anteproc_variables["num_jobs_to_vary"] = int(line[2])
            elif line[1] == "set":
                varying_anteproc_variables["set"][temp_variable] = [x for x in line[3:]]
            elif line[1] == "random":
                distribution_type = line[3]
                if distribution_type != "uniform":
                    raise pyCondorSTAMPanteprocError("Alert, random varying parameters should be from uniform distribution. Other distributions not yet recognized. Unrecognized option:" + str(distribution_type))
                elif distribution_type == "uniform" and len(line) != 6:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 6")
                else:
                    lower_range = line[4]
                    upper_range = line[5]
                    distribution_info = [distribution_type, lower_range, upper_range]
                    varying_anteproc_variables["random"][temp_variable] = distribution_info
            elif line[1] == "num_space":
                distribution_type = line[3]
                if distribution_type not in ["linear", "logarithmic", "linear_sqrt", "logarithmic_sqrt"]:
                    raise pyCondorSTAMPanteprocError("Random varying parameters should be linear or logarithmic. Other distributions not yet recognized. Unrecognized option:" + str(distribution_type))
                elif distribution_type in ["linear", "linear_sqrt"] and len(line) != 6:
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 6")
                elif distribution_type in ["logarithmic", "logarithmic_sqrt"] and (len(line) != 6 and len(line) != 7):
                    raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 6 or 7")
                else:
                    lower_range = line[4]
                    upper_range = line[5]
                    distribution_info = [distribution_type, lower_range, upper_range]
                    if distribution_type in ["logarithmic", "logarithmic_sqrt"] and len(line) == 7:
                        base = line[6]
                        distribution_info += [base]
                    varying_anteproc_variables["num_space"][temp_variable] = distribution_info
            else:
                raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a non-recognized option for anteproc_varying_param")
        elif temp == "varying_injection_start":
            if len(line) != 3:
                raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 3")
            else:
                jobs["constants"]["varying_injection_start"] = line[1:]

        elif temp == "grandstochtrack":
                #print("Fix this part to handle numbers properly! And less jumbled if possible!")
            if line[1] == "StampFreqsToRemove":
                rawFreqs = [x.split(",") for x in line[2:]] # this part actually just strips the comma. The really frequency splitting is actually due to the list comprehension itself, or rather this part: line[2:]. Since the frequencies were already split in an earlier line.
                    # not a terrible check to have, just in case commas are used and spaces forgotten
                rawFreqs = [item for sublist in rawFreqs for item in sublist]
                rawFreqs = [x.replace("[", "") if "[" in x else x for x in rawFreqs]
                rawFreqs = [x.replace("]", "") if "]" in x else x for x in rawFreqs]
                freqList = [float(x) for x in rawFreqs if x]#[load_number(x) for x in rawFreqs if x]
                    #print("StampFreqsToRemove")
                    #print(freqList)
                jobs[job_key]["grandStochtrackParams"]["params"][line[1]] = freqList
            elif line[1] == "doGPU" and job_key != "constants":
                raise pyCondorSTAMPanteprocError("Current job: " + job_key + "\nnon-default value for 'doGPU' detected. This functionality is not currently supported but may be supported in a future version.")
            elif len(line) != 3:
                raise pyCondorSTAMPanteprocError("Line " + str(line) + "contains a different number of entries than 3")
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

			# If it hasn't been identified, error out
        else:
            raise pyCondorSTAMPanteprocError("Error in config file. Option " + temp + " not recognized. Quitting program.")
                
        # In case constants haven't been defined, define them as blank dictionaries
    if 'constants' not in jobs:
        jobs['constants'] = {}
        jobs['constants']["preprocParams"] = {}
        jobs['constants']["grandStochtrackParams"] = {}
        jobs['constants']["grandStochtrackParams"]["params"] = {}
    return jobs, commentsToPrintIfVerbose, job_groups, jobDuplicates, anteproc_jobs_1, anteproc_jobs_2, waveforms, varying_anteproc_variables

def anteproc_setup(anteproc_directory, anteproc_default_data, job_dictionary, cache_directory):
    anteproc_H = dict((x[0], x[1]) if len(x) > 1 else (x[0], "") for x in anteproc_default_data)
    anteproc_L = dict((x[0], x[1]) if len(x) > 1 else (x[0], "") for x in anteproc_default_data)
    for temp_param in job_dictionary["constants"]["anteprocParamsH"]:
        anteproc_H[temp_param] = job_dictionary["constants"]["anteprocParamsH"][temp_param]
    for temp_param in job_dictionary["constants"]["anteprocParamsL"]:
        anteproc_L[temp_param] = job_dictionary["constants"]["anteprocParamsL"][temp_param]
    """if "doDetectorNoiseSim" in job_dictionary["constants"]["anteprocParamsH"]:
        simulated = job_dictionary["constants"]["anteprocParamsH"]["doDetectorNoiseSim"]
        anteproc_H["doDetectorNoiseSim"] = simulated
        anteproc_L["doDetectorNoiseSim"] = simulated #"""
    anteproc_H["outputfiledir"] = anteproc_directory + "/"
    anteproc_L["outputfiledir"] = anteproc_directory + "/"
    """if "DetectorNoiseFile" in job_dictionary["constants"]["anteprocParamsH"]:
        anteproc_H["DetectorNoiseFile"] = job_dictionary["constants"]["anteprocParamsH"]["DetectorNoiseFile"]
    if "DetectorNoiseFile" in job_dictionary["constants"]["anteprocParamsL"]:
        anteproc_L["DetectorNoiseFile"] = job_dictionary["constants"]["anteprocParamsL"]["DetectorNoiseFile"]

    if "segmentDuration" in job_dictionary["constants"]["anteprocParamsH"]:
        anteproc_H["segmentDuration"] = job_dictionary["constants"]["anteprocParamsH"]["segmentDuration"]
    if "segmentDuration" in job_dictionary["constants"]["anteprocParamsL"]:
        anteproc_L["segmentDuration"] = job_dictionary["constants"]["anteprocParamsL"]["segmentDuration"] #"""
    anteproc_H["gpsTimesPath1"] = cache_directory
    anteproc_H["frameCachePath1"] = cache_directory
    anteproc_L["gpsTimesPath1"] = cache_directory
    anteproc_L["frameCachePath1"] = cache_directory

    anteproc_H["ifo1"] = "H1"
    anteproc_H["ASQchannel1"] = "DCS-CALIB_STRAIN_C01"
    anteproc_H["frameType1"] = "H1_HOFT_C01"
    anteproc_L["ifo1"] = "L1"
    anteproc_L["ASQchannel1"] = "DCS-CALIB_STRAIN_C01"
    anteproc_L["frameType1"] = "L1_HOFT_C01"
    return anteproc_H, anteproc_L

def save_anteproc_paramfile(anteproc_dict, anteproc_name, anteproc_default_data):
    print("Saving anteproc parameter file...")
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

def check_on_the_fly_injection(job_dictionary, specific_job = "constants"):
    on_the_fly_bool = False # When true, this will ignore an waveforms in the waveform bank and use on the fly instead
    if ("stamp.inj_type" in job_dictionary[specific_job]["anteprocParamsH"] or "stamp.inj_type" in job_dictionary[specific_job]["anteprocParamsL"]) and not ("stamp.inj_type" in job_dictionary[specific_job]["anteprocParamsH"] and "stamp.inj_type" in job_dictionary[specific_job]["anteprocParamsL"]):
        raise pyCondorSTAMPanteprocError("WARNING: injection type set in one but not both detectors. Quitting program.")
    elif "stamp.inj_type" in job_dictionary[specific_job]["anteprocParamsH"] and "stamp.inj_type" in job_dictionary[specific_job]["anteprocParamsL"]:
        if job_dictionary[specific_job]["anteprocParamsH"]["stamp.inj_type"] != job_dictionary[specific_job]["anteprocParamsL"]["stamp.inj_type"]:
            raise pyCondorSTAMPanteprocError("WARNING: injection type not the same in both detectors. Quitting program.")
        elif job_dictionary[specific_job]["anteprocParamsH"]["stamp.inj_type"] == "half_sg" and job_dictionary[specific_job]["anteprocParamsL"]["stamp.inj_type"] == "half_sg":
            on_the_fly_bool = True
    return on_the_fly_bool

def convert_cosiota_to_iota(temp_param, temp_val):
    if temp_param == "stamp.iota":
        print("\nWARNING: Parameter " + temp_param + " found. Special case to vary in cos(iota) instead of iota. Edit code to change this option.")
        temp_val = np.degrees(np.arccos(temp_val))
    return temp_val

def space_in_log_space(low, high, number, base = 10):
    if base == 10:
        loglow = np.log10(low)
        loghigh = np.log10(high)
    else:
        loglow = np.log(low)/np.log(base)
        loghigh = np.log(high)/np.log(base)
    temp_space = np.linspace(loglow, loghigh, number)
    temp_space = base**temp_space
    return temp_space


def handle_varying_variables_and_save_anteproc_paramfile(varying_anteproc_variables, anteproc_dict, anteproc_file_name, anteproc_file_names, anteproc_default_data, anteproc_job = None, anteprocJobDictTracker = None, injectionStartTimes = None):
    "This one applies varying variables if needed"
    if "num_jobs_to_vary" in varying_anteproc_variables:
        base_output_file_name = anteproc_dict["outputfilename"]
        num_variations = varying_anteproc_variables["num_jobs_to_vary"]
        for temp_param in varying_anteproc_variables["set"]:
            if len(varying_anteproc_variables["set"][temp_param]) != num_variations:
                raise pyCondorSTAMPanteprocError("ERROR: Number of entries in set for parameter " + temp_param + " is not equal to chosen number of variation (" + str(num_variations) + "). Quitting program.")

        spaces = {}
        for temp_param in varying_anteproc_variables["num_space"]:
            temp_range = [load_number_pi(x) for x in varying_anteproc_variables["num_space"][temp_param][1:]]
            distribution_type = varying_anteproc_variables["num_space"][temp_param][0]
            if len(temp_range) == 3:
                temp_base = temp_range[2]
            else:
                #temp_base = np.e
                temp_base = 10

            if distribution_type == "linear":
                temp_space = np.linspace(temp_range[0], temp_range[1], num_variations)
            elif distribution_type == "linear_sqrt":
                temp_space = np.array([x**2 for x in np.linspace(np.sqrt(temp_range[0]), np.sqrt(temp_range[1]), num_variations)])
                spaces[temp_param] = temp_space
            elif distribution_type == "logarithmic":
                temp_space = space_in_log_space(temp_range[0], temp_range[1], num_variations, base = temp_base)
            elif distribution_type == "logarithmic_sqrt":
                temp_space = space_in_log_space(np.sqrt(temp_range[0]), np.sqrt(temp_range[1]), num_variations, base = temp_base)**2
            temp_space[0] = temp_range[0]
            temp_space[-1] = temp_range[1]
            spaces[temp_param] = temp_space

        for variation_index in range(0, num_variations):
            temp_number = variation_index + 1
            file_name_modifier = "_v" + str(temp_number)

            for temp_param in varying_anteproc_variables["set"]:
                temp_val = load_number_pi(varying_anteproc_variables["set"][temp_param][variation_index])
                temp_val = convert_cosiota_to_iota(temp_param, temp_val)
                anteproc_dict[temp_param] = temp_val

            for temp_param in varying_anteproc_variables["random"]:
                distribution_type = varying_anteproc_variables["random"][temp_param][0]
                temp_range = [load_number_pi(x) for x in varying_anteproc_variables["random"][temp_param][1:]]
                if distribution_type == "uniform":
                    temp_val = np.random.uniform(temp_range[0], temp_range[1])
                else:
                    raise pyCondorSTAMPanteprocError("Distribution type not recognized.")
                temp_val = convert_cosiota_to_iota(temp_param, temp_val)
                anteproc_dict[temp_param] = temp_val

            for temp_param in varying_anteproc_variables["num_space"]:
                temp_val = spaces[temp_param][variation_index]
                temp_val = convert_cosiota_to_iota(temp_param, temp_val)
                anteproc_dict[temp_param] = temp_val

            temp_anteproc_name = anteproc_file_name[:anteproc_file_name.rindex(".")]
            temp_output_name = base_output_file_name + file_name_modifier
            #anteproc_dict["outputfilename"] = base_output_file_name + file_name_modifier

            if injectionStartTimes:
                if "H1-" in temp_anteproc_name:
                    anteproc_job_set = "jobNum1"
                elif "L1-" in temp_anteproc_name:
                    anteproc_job_set = "jobNum2"
                else:
                    raise pyConorSTAMPanteprocError("Warning, unknown IFO used. Please review and fix input or code as needed.")
                for specific_job in anteprocJobDictTracker[anteproc_job_set][anteproc_job]:
                    #print(variation_index)

                    anteproc_dict["outputfilename"] = temp_output_name + "_" + specific_job

                    injection_start_time_shift = injectionStartTimes[specific_job]["variations"][variation_index]
                    temp_start_time = anteproc_dict["stamp.start"]
                    anteproc_dict["stamp.start"] = temp_start_time + injection_start_time_shift

                    temp_anteproc_name = anteproc_file_name[:anteproc_file_name.rindex(".")] + file_name_modifier + "_" + specific_job + ".txt"

                    save_anteproc_paramfile(anteproc_dict, temp_anteproc_name, anteproc_default_data)
                    anteproc_file_names += [temp_anteproc_name]

                    anteproc_dict["stamp.start"] = temp_start_time
            else:
                anteproc_dict["outputfilename"] = temp_output_name
                temp_anteproc_name = anteproc_file_name[:anteproc_file_name.rindex(".")] + file_name_modifier + ".txt"
                save_anteproc_paramfile(anteproc_dict, temp_anteproc_name, anteproc_default_data)
                anteproc_file_names += [temp_anteproc_name]

        anteproc_dict["outputfilename"] = base_output_file_name

    else:

        save_anteproc_paramfile(anteproc_dict, anteproc_file_name, anteproc_default_data)
        anteproc_file_names += [anteproc_file_name]

    return anteproc_file_names

def handle_injections_and_save_anteproc_paramfile(multiple_waveforms, waveform_bank, varying_anteproc_variables, anteproc_dict, anteproc_file_name, anteproc_default_data, on_the_fly_bool, anteproc_job = None, anteprocJobDictTracker = None, injectionStartTimes = None):

    anteproc_file_names = []

    if multiple_waveforms and not on_the_fly_bool:
        print("Handling multiple waveform injection preprocessing...")
        base_output_file_name = anteproc_dict["outputfilename"]

        for waveform_key in waveform_bank:

            if waveform_bank[waveform_key]:
                temp_anteproc_name = anteproc_file_name[:anteproc_file_name.rindex(".")] + "_" + waveform_key + ".txt"
                anteproc_dict["stamp.file"] = waveform_bank[waveform_key]
                anteproc_dict["outputfilename"] = base_output_file_name + "_" + waveform_key
                #save_anteproc_paramfile(anteproc_dict, temp_anteproc_name, anteproc_default_data)
                #anteproc_file_names += [temp_anteproc_name]
                anteproc_file_names = handle_varying_variables_and_save_anteproc_paramfile(varying_anteproc_variables, anteproc_dict, anteproc_file_name, anteproc_file_names, anteproc_default_data)
            else:
                raise pyCondorSTAMPanteprocError("Warning! No waveform in selected waveform key!")

        anteproc_dict["outputfilename"] = base_output_file_name

    else:
        if on_the_fly_bool:
            anteproc_dict["stamp.file"] = "FAKE_WAVEFORM_FILE"
            print("\nSet for on the fly injections.\n\nNOTE: This code is currently not set up to properly handle multiple on the fly injections while varying other parameters unless every injected waveform is expected to be unique.\n")
        #save_anteproc_paramfile(anteproc_dict, anteproc_file_name, anteproc_default_data)
        #anteproc_file_names += [anteproc_file_name]
        anteproc_file_names = handle_varying_variables_and_save_anteproc_paramfile(varying_anteproc_variables, anteproc_dict, anteproc_file_name, anteproc_file_names, anteproc_default_data, anteproc_job, anteprocJobDictTracker, injectionStartTimes)

    return anteproc_file_names

def job_specific_parameters(job_dictionary, ifo, anteproc_dict, used_seed_tracker, organized_seeds, temp_job):

    if job_dictionary["constants"]["anteprocParams"+ifo[0]]["doDetectorNoiseSim"] == "true":

        if temp_job in job_dictionary["constants"]["anteproc"+ifo[0]+"job_seeds"]:
            temp_seed = job_dictionary["constants"]["anteproc"+ifo[0]+"job_seeds"][temp_job]
            anteproc_dict["pp_seed"] = temp_seed
        else:
            temp_seed = random.randint(0,2**32-1)
            while temp_seed in used_seed_tracker:
                temp_seed = random.randint(0,2**32-1)
            used_seed_tracker += [temp_seed]
            anteproc_dict["pp_seed"] = temp_seed
        organized_seeds[ifo][temp_job] = temp_seed

    if temp_job in job_dictionary['constants']["anteproc"+ifo[0]+"_parameters"]:
        for temp_param in job_dictionary['constants']["anteproc"+ifo[0]+"_parameters"][temp_job]:
            anteproc_dict[temp_param] = job_dictionary['constants']["anteproc"+ifo[0]+"_parameters"][temp_job][temp_param]

    return anteproc_dict, used_seed_tracker, organized_seeds

def anteproc_job_specific_setup(job_list, ifo, anteproc_directory, job_dictionary, anteproc_dict, used_seed_tracker, organized_seeds, multiple_waveforms, waveform_bank, anteproc_default_data, anteproc_jobs, varying_anteproc_variables, anteprocJobDictTracker = None, injectionStartTimes = None):

    on_the_fly_bool = check_on_the_fly_injection(job_dictionary)

    for temp_job in job_list:

            anteproc_H_name_temp = anteproc_directory + "/" + ifo + "-anteproc_params_" + str(temp_job) + ".txt"

            if job_dictionary["constants"]["anteprocParams"+ifo[0]]["doDetectorNoiseSim"] == "true":

                if temp_job in job_dictionary["constants"]["anteproc"+ifo[0]+"job_seeds"]:
                    temp_seed = job_dictionary["constants"]["anteproc"+ifo[0]+"job_seeds"][temp_job]
                    anteproc_dict["pp_seed"] = temp_seed
                else:
                    temp_seed = random.randint(0,2**32-1)
                    while temp_seed in used_seed_tracker:
                        temp_seed = random.randint(0,2**32-1)
                    used_seed_tracker += [temp_seed]
                    anteproc_dict["pp_seed"] = temp_seed
                organized_seeds[ifo][temp_job] = temp_seed

            if temp_job in job_dictionary['constants']["anteproc"+ifo[0]+"_parameters"]:
                for temp_param in job_dictionary['constants']["anteproc"+ifo[0]+"_parameters"][temp_job]:
                    anteproc_dict[temp_param] = job_dictionary['constants']["anteproc"+ifo[0]+"_parameters"][temp_job][temp_param]

            anteproc_jobs[ifo][temp_job] = handle_injections_and_save_anteproc_paramfile(multiple_waveforms, waveform_bank, varying_anteproc_variables, anteproc_dict,
                                                anteproc_H_name_temp, anteproc_default_data, on_the_fly_bool, temp_job, anteprocJobDictTracker, injectionStartTimes)
    return anteproc_jobs, used_seed_tracker, organized_seeds

def load_number_pi(number):
    if "pi" in number:
        multiply = 1
        divide = 1
        if "*" in number:
            multiply = float(number[:number.index("*")])
        if "/" in number:
            divide = float(number[number.index("/")+1:])
        return multiply*np.pi/divide
    else:
        return float(number)

def create_job_directories(job_dictionary, base_directory, current_job, suffix = ""):
    # stochtrack_day_job_num (injection? gps time?)
    jobDir = create_dir(base_directory + "/" + "job_group_" + job_dictionary[current_job]["job_group"] + suffix + "/" + current_job)
    job_dictionary[current_job]["jobDir"] += [jobDir]

#			inputs for stochtrack clustermap in text file (put this here or in the "/params" directory)
#			grand_stochtrack inputs
    stochtrackInputDir = create_dir(jobDir + "/grandstochtrackInput")
    job_dictionary[current_job]["stochtrackInputDir"] += [stochtrackInputDir]
#			results
    grandstochtrackOutputDir = create_dir(jobDir + "/grandstochtrackOutput")
    job_dictionary[current_job]["grandstochtrackOutputDir"] += [grandstochtrackOutputDir]
#				overview mat
#				some other thing?
#				plotDir
    plotDir = create_dir(grandstochtrackOutputDir + "/plots")
    job_dictionary[current_job]["plotDir"] += [plotDir]
    return job_dictionary

def createPreprocessingJobDependentDict(job_dictionary):
    temp_dictionary = {}
    temp_dictionary['jobNum1'] = {}
    temp_dictionary['jobNum2'] = {}
    for job in job_dictionary:
        if job != 'constants':
            #print(job_dictionary[job]["grandStochtrackParams"]["params"].keys())
            temp_job_1 = job_dictionary[job]["grandStochtrackParams"]["params"]["anteproc"]["jobNum1"]
            temp_job_2 = job_dictionary[job]["grandStochtrackParams"]["params"]["anteproc"]["jobNum2"]
            if temp_job_1 not in temp_dictionary['jobNum1']:
                temp_dictionary['jobNum1'][temp_job_1] = []
            if temp_job_2 not in temp_dictionary['jobNum2']:
                temp_dictionary['jobNum2'][temp_job_2] = []
            temp_dictionary['jobNum1'][temp_job_1] += [job]
            temp_dictionary['jobNum2'][temp_job_2] += [job]
    return temp_dictionary

def generate_random_start_times(job_dictionary, varying_anteproc_variables, front_start_time, back_start_time):
    random_start_dict = {}
    num_variations = varying_anteproc_variables["num_jobs_to_vary"]
    for job in job_dictionary:
        if job != 'constants':
            job_key = str(job)
            random_start_dict[job_key] = {}
            random_start_dict[job_key]["jobNum1"] = job_dictionary[job]["grandStochtrackParams"]["params"]["anteproc"]["jobNum1"]
            random_start_dict[job_key]["jobNum2"] = job_dictionary[job]["grandStochtrackParams"]["params"]["anteproc"]["jobNum2"]
            random_start_dict[job_key]["variations"] = {}
            for num in range(num_variations):
                #num_key = "_v" + str(num)
                #random_start_dict[job_key]["variations"][num_key] = random.randint(int(front_start_time), int(back_start_time))
                random_start_dict[job_key]["variations"][num] = random.randint(int(front_start_time), int(back_start_time))

    """"random_start_dict = {}
    num_variations = varying_anteproc_variables["num_jobs_to_vary"]
    for job in jobs:
        for num in range(num_variations):
            key = str(job) + "_" + str(num)
            random_start_dict[key] = random.randint(start_time, end_time)"""
    return random_start_dict

class pyCondorSTAMPanteprocError(Exception):
    
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(message)
        
def make_file_path_absolute(file_path):
    
    if file_path[0:2] == "./":
        absolute_path = getcwd() + file_path[1:]
    elif options.configFile[0] != "/":
        absolute_path = getcwd() + "/" + file_path[1:]
    else:
        absolute_path = file_path
    
    return absolute_path