from __future__ import division
from pyCondorSTAMPLib import nested_dict_entry
from grandStochtrackSupportLib import load_if_number

def parse_jobs(raw_data, quit_program):
    'Helper function to parse jobs for STAMP'
    jobs = {}
    commentsToPrintIfVerbose = []
    job_groups = []
    jobDuplicates = False
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
                if "anteprocParams" not in jobs[job_key]:
                    jobs[job_key]["anteprocParams"] = {}
                if "grandStochtrackParams" not in jobs[job_key]:
                    jobs[job_key]["grandStochtrackParams"] = {}
                    jobs[job_key]["grandStochtrackParams"]["params"] = {}
            # job specific settings
            elif temp == 'job':
                job_key = temp + "_" + line[1]
                temp_key = job_key
                temp_num = 1
                print(jobs.keys())
                print(temp_key)
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
                if "anteprocParams" not in jobs[job_key]:
                    jobs[job_key]["anteprocParams"] = {}
                if "grandStochtrackParams" not in jobs[job_key]:
                    jobs[job_key]["grandStochtrackParams"] = {}
                    jobs[job_key]["grandStochtrackParams"]["params"] = {}
                if "job_group" not in jobs[job_key]:
                    jobs[job_key]["job_group"] = None
            # job_group
            elif temp == "job_group":
                jobs[job_key]["job_group"] = line[1]
                job_groups += [line[1]]
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
            elif temp == "anteproc":
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
    return quit_program, jobs, commentsToPrintIfVerbose, job_groups, jobDuplicates

def basic_create_anteproc_file(anteproc_dir, anteproc_name, anteproc_default_file, observatory, frame_type, channel, cache_dir, detector_noise_file, simulated = False):
    with open(anteproc_default_file, "r") as infile:
        anteproc_params = [line.split() for line in infile]
    if simulate:
        anteproc_params += ["doDetectorNoiseSim", "true"]
    else:
        anteproc_params += ["doDetectorNoiseSim", "false"]
    anteproc_params += ["ifo1", observatory]
    anteproc_params += ["ASQchannel1", channel]
    anteproc_params += ["frameType1", frame_type]
    anteproc_params += ["gpsTimesPath1", cache_dir]
    anteproc_params += ["frameCachePath1", cache_dir]
    anteproc_params += ["DetectorNoiseFile", detector_noise_file]
    anteproc_params += ["outputfiledir", anteproc_dir]
    output_string = "\n".join(" ".join(x for x in line) for line in anteproc_params)
    with open(anteproc_name, "r") as outfile:
        outfile.write(output_string)
