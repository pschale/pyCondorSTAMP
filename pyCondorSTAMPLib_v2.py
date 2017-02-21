#pyCondorSTAMPLib_v2

from __future__ import division
import numpy as np
from os import getcwd, path, makedirs
import collections, datetime, random, subprocess
from load_defaults import getDefaultCommonParams
from shutil import copy
import ConfigParser
import json


def dated_dir(name, date = None, iterate_name = True):

    # If date empty, get time and date
    if not date:
        date = datetime.datetime.now()
    # create dated name
    dated_name = name + "-" + str(date.year) + "_" + str(date.month) + \
                 "_" + str(date.day)
    # create directory
    newDir = create_dir(dated_name, iterate_name)

    return newDir
    
def create_dir(name, iterate_name = True):

    # set default directory name
    newDir = name
    # If directory doesn't exist, create
    if not path.exists(name):
        makedirs(name)

    # Otherwise, if iterate_name is set to true, iterate version number
    # to create new directory
    elif iterate_name:
        # Set initial version number
        version = 2
        # set base name to add version number to
        base_name = name + "_v"
        # while directory exists, iterate version number
        while path.exists(base_name + str(version)):
            version += 1
        # overwrite directory name
        newDir = base_name + str(version)
        # make new directory
        makedirs(newDir)

    return newDir
    
def readFile(file_name, delimeter = None):
    with open(file_name, "r") as infile:
        content = [x.split(delimeter) for x in infile]
    return content
    
def copy_input_file(filePath, outputDirectory):
    outputPath = path.join(outputDirectory, path.split(filePath)[-1])
    copy(filePath, outputPath)
    return outputPath

    
def create_frame_file_list(frame_type, start_time, end_time, observatory):

    # search for file location for a given frame type during specified times
    data_find = ['gw_data_find','-s', start_time, '-e', end_time, 
                    '-o', observatory, '--url-type', 'file', 
                    '--lal-cache', '--type', frame_type]

    frame_locations_raw = subprocess.Popen(
                            data_find, stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE).communicate()#[0]
    if frame_locations_raw[1]:
        print(frame_locations_raw[1])
        print("The following shell command caused the above message:")
        raise pyCondorSTAMPanteprocError(str(frame_locations_raw[1]) 
                    + "\nCaused by the following shell command:\n" 
                    + " ".join(data_find))
    #frame_locations = frame_locations_raw.split("\n")
    #print(frame_locations_raw)
    frame_locations = [x[x.find("localhost") + len("localhost"):] 
                            for x in frame_locations_raw[0].split("\n") if x]

    # create frame list
    return frame_locations
    
# Helper function to grab time data from frame name
def frame_start_time(frame_path):
    if "/" in frame_path:
        frame_name = frame_path[::-1]
        frame_name = frame_name[:frame_name.index("/")]
        frame_name = frame_name[::-1]
        #frame_name = frame_path[::-1][:frame_path[::-1].index("/")][::-1] #?
    else:
        frame_name = frame_path
    #print(frame_name)
    #print(len(frame_name))
    frame_time = frame_name[frame_name.index("-") + 1:]
    frame_time = frame_time[frame_time.index("-") + 1:]
    frame_time = frame_time[:frame_time.index("-")]
    #print("Check if number: " + frame_time)
    return frame_time

# Helper function to create a file from the list of frame file locations
def create_cache_and_time_file(frame_list,observatory,jobNumber,jobCacheDir):

    # make list of times
    time_list = [frame_start_time(x) for x in frame_list if x]
    time_string = "\n".join(x for x in time_list)
    # create string to write to file

    output_string = "\n".join(x for x in frame_list)
    # create list to hold list of files in archive directory

    archived = [x for x in frame_list if "archive" in x]

    # create file
    modifier = observatory + "." + str(jobNumber) + ".txt"
    with open(jobCacheDir + "/frameFiles" + modifier, "w") as outfile:
        outfile.write(output_string)
    with open(jobCacheDir + "/gpsTimes" + modifier, "w") as outfile:
        outfile.write(time_string)
        
    return archived

# Helper function to create a file from the list of frame file locations
def create_fake_cache_and_time_file(start_time, end_time, observatory, 
                                    jobNumber, jobCacheDir):

    # calculate job duration
    tempJobDur = str(int(float(end_time) - float(start_time)))
    # create fake frame name and string to write to channel
    output_string = ("/FAKEDATA/" + observatory + "-FAKE-" 
                        + str(int(start_time)) + "-" + tempJobDur + ".gwf\n")
    time_string = str(int(start_time)) + "\n"

    # create file
    modifier = observatory + "." + str(jobNumber) + ".txt"
    with open(jobCacheDir + "/frameFiles" + modifier, "w") as outfile:
        outfile.write(output_string)
    with open(jobCacheDir + "/gpsTimes" + modifier, "w") as outfile:
        outfile.write(time_string)


def convert_cosiota_to_iota(temp_param, temp_val):
    if temp_param == "stamp.iota":
        print("\nWARNING: Parameter " + temp_param + " found. Special case \
                to vary in cos(iota) instead of iota. \
                Edit code to change this option.")
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

class pyCondorSTAMPanteprocError(Exception):
    
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(message)
        
def make_file_path_absolute(file_path):
    
    if file_path[0:2] == "./":
        absolute_path = getcwd() + file_path[1:]
    elif file_path[0] != "/":
        absolute_path = getcwd() + "/" + file_path
    else:
        absolute_path = file_path
    
    return absolute_path

def generate_summary(configs, output_dir):

    defaultConfigs = getDefaultConfigs()
    changed = ""
    unchanged = ""
    for s in configs.sections():
        changed += '[' + s + ']' + '\n'
        unchanged += '[' + s + ']' + '\n'
        for o in configs.options(s):
            if (o in defaultConfigs and 
                    not str(defaultConfigs[o])) == configs.get(s, o):
                changed += o + '\t' + configs.get(s, o) + '\n'
            else:
                unchanged += o + '\t' + configs.get(s, o) + '\n'
                
        changed += "\n"
        unchanged += "\n"
    
    outputStr = ("Parameters of note:\n\n" + changed 
        + "=============================================================\n\n" 
        + unchanged)
    
    with open(path.join(output_dir, 'summary.txt'), "w") as h:
        print >>h, outputStr
                
def recursive_ints_to_floats(in_dict):

    for key, val in in_dict.iteritems():
        if isinstance(val, dict):
            floated_val = recursive_ints_to_floats(val)
        elif isinstance(val, int):
            floated_val = float(val)
        else:
            floated_val = val
            
        in_dict[key] = floated_val
    
    return in_dict
    
def deepupdate(d, u):
    for k, v in u.iteritems():
        if isinstance(v, collections.Mapping):
            r = deepupdate(d.get(k, {}), v)
            d[k] = r
        else:
            d[k] = u[k]
    return d
    
def getCommonParams(configs):
    CPDict = getDefaultCommonParams()   
    
    CPStoch = CPDict['grandStochtrack']['stochtrack']

    CPStoch['T'] = configs.getint('search', 'T')
    CPStoch['F'] = configs.getint('search', 'F')
        
    if configs.getboolean('search', 'burstegard'):
        CPDict['grandStochtrack']['doBurstegard'] = True
        CPDict['grandStochtrack']['doStochtrack'] = False
    else:
        if configs.getboolean('search', 'longPixel'):
            CPDict['anteproc_h']['segmentDuration'] = 4
            CPDict['anteproc_l']['segmentDuration'] = 4
            CPStoch['mindur'] = 25
            CPDict['preproc']['segmentDuration'] = 4
        else:
            CPDict['anteproc_h']['segmentDuration'] = 1
            CPDict['anteproc_l']['segmentDuration'] = 1
            CPStoch['mindur'] = 100
            CPStoch['F'] = 600
            CPDict['job_start_shift'] = 6
            CPDict['job_duration'] = 400
    
    if configs.getboolean('search', 'simulated'):
        CPDict['anteproc_h']['doDetectorNoiseSim'] = True
        CPDict['anteproc_l']['doDetectorNoiseSim'] = True
        CPDict['anteproc_h'] \
              ['DetectorNoiseFile'] = configs.get('search', 'lhoWelchPsd')
        CPDict['anteproc_l'] \
              ['DetectorNoiseFile'] = configs.get('search', 'lloWelchPsd')
        CPDict['anteproc']['cacheFile'] = 'fakefile'

        if not configs.getboolean('search', 'show_plots_when_simulated'):
            CPDict['grandStochtrack']['savePlots'] = False
    else:
        CPDict['anteproc_h']['doDetectorNoiseSim'] = False
        CPDict['anteproc_l']['doDetectorNoiseSim'] = False
    
    
    # Add in injections (if desired)
    if configs.getboolean('injection', 'doInjections'):
        if configs.getboolean('injection', 'polarizationSmallerResponse'):
            wave_iota = 120
            wave_psi = 45
        else:
            wave_iota = 0
            wave_psi = 0
        
        if configs.getboolean('injection', 'onTheFly'):
            # stamp_alpha was waveformPowerAmplitudeScaling here
            CPDict['anteproc_h']['stampinj'] = True
            CPDict['anteproc_h']['stamp'] \
                                ['alpha'] = configs.getfloat('injection', 
                                                             'stampAlpha')
            CPDict['anteproc_h']['stamp']['iota'] = wave_iota
            CPDict['anteproc_h']['stamp']['psi'] = wave_psi         
            CPDict['anteproc_l']['stampinj'] = True
            CPDict['anteproc_l']['stamp'] \
                                ['alpha'] = configs.getfloat('injection', 
                                                             'stampAlpha')
            CPDict['anteproc_l']['stamp']['iota'] = wave_iota
            CPDict['anteproc_l']['stamp']['psi'] = wave_psi
            
            
        else:
            CPDict['anteproc_h']['stampinj'] = True
            CPDict['anteproc_h']['stamp'] \
                                ['alpha'] = configs.getfloat('injection', 
                                                             'stampAlpha')
            CPDict['anteproc_h']['stamp']['iota'] = 0
            CPDict['anteproc_h']['stamp']['psi'] = 0           
            CPDict['anteproc_l']['stampinj'] = True
            CPDict['anteproc_l']['stamp'] \
                                ['alpha'] = configs.getfloat('injection', 
                                                             'stampAlpha')
            CPDict['anteproc_l']['stamp']['iota'] = 0
            CPDict['anteproc_l']['stamp']['psi'] = 0
            CPDict['preproc']['stamp'] \
                             ['file'] = configs.getfloat('injection', 
                                                         'injectionFile')
            CPDict['preproc']['stamp']['alpha'] = 1e-40
        
    if configs.getboolean('variations', 'doVariations'):
        CPDict['numJobGroups'] = configs.getint('variations', 'numJobGroups')
    else:
        CPDict['numJobGroups'] = 1
            
    if configs.getboolean('singletrack', 'singletrackBool'):
        CPStoch['singletrack']['doSingletrack'] = True
        CPStoch['singletrack']['trackInputFiles'] = np.array(json.loads(
                                                    configs.get(
                                                    'singletrack', 
                                                    'singletrackInputFiles')),
                                                    dtype=np.object)
    else:
        CPStoch.pop('singletrack')
        
    if configs.getboolean('search', 'setStochtrackSeed'):
        CPStoch['doSeed'] = True
        CPStoch['seed'] = 2015
        
    if configs.getboolean('search', 'doMaxband'):
        if configs.get('search', 'maxbandMode') == "percent":
            CPStoch['doMaxbandPercentage'] = True
            CPStoch['maxbandPercentage'] = configs.getfloat('search', 'maxband')
            print("WARNING - doMaxbandPercentage is active - "
                    + "this only works with STAMP revision 12522 or later")
        elif configs.get('search', 'maxbandMode') == "absolute":
            CPStoch['doMaxbandPercentage'] = False
            CPStoch['maxband'] = configs.getfloat('search', 'maxband')
        else:
            raise ValueError("Unrecognized option for maxband_mode: " 
                                + configs.get('search', 'maxbandMode') 
                                + ".  Must be either 'percent' or 'absolute'")
    
    
    if (configs.getboolean('search', 'simulated') and 
                configs.get('search', 'searchType') == "onsource" and 
                configs.getboolean('search', 'preSeed')):
        CPDict['anteproc_h']['job_seed'] = 2694478780        
        CPDict['anteproc_h']['job_seed'] = 4222550304
        #NEED TO FIGURE OUT HOW THIS ONE WORKS
    
    if not configs.getboolean('search', 'relativeDirection'):
        CPDict['grandStochtrack']['ra'] = configs.getfloat('trigger', 'RA')
        CPDict['grandStochtrack']['dec'] = configs.getfloat('trigger', 'DEC')
        
    if configs.getboolean('condor', 'doGPU'):
        CPDict['grandStochtrack']['doGPU'] = True
        
    if (not configs.getboolean('search', 'burstegard') and 
                configs.getboolean('search', 'saveStochtrackMats')):
        CPStoch['saveMat'] = True
        
    if configs.get('search', 'searchType') == 'injectionRecovery':
        print("Injection Recovery mode selected.  Stochtrack will be \
                restricted to 5 Hz band around injected frequency")
        injFreq = configs.getfloat('injection', 'waveFrequency')
        CPDict['grandStochtrack']['fmin'] = injFreq - 2
        CPDict['grandStochtrack']['fmax'] = injFreq + 2
        
    
    return CPDict
    
def write_grandstochtrack_bash_script(file_name, executable, 
                                      STAMP_export_script, 
                                      matlab_setup_script, 
                                      memory_limit = 14000000):
    output_string = "#!/bin/bash\n"
    output_string += "source " + STAMP_export_script + "\n"
    output_string += "source " + matlab_setup_script + "\n"
    output_string += "ulimit -v " + str(memory_limit) + "\n"
    output_string += executable + " $1 $2"
    with open(file_name, "w") as outfile:
        print >> outfile, output_string

def write_anteproc_bash_script(file_name, executable, STAMP_export_script, 
                               memory_limit = 14000000):
    output_string = "#!/bin/bash\n"
    output_string += "source " + STAMP_export_script + "\n"
    output_string += "ulimit -v " + str(memory_limit) + "\n"
    output_string += executable + " $1 $2 $3"

    with open(file_name, "w") as outfile:
        print >> outfile, output_string
        
def write_anteproc_sub_file(memory, anteprocSH, dagDir, accountingGroup):

    contents = ("universe = vanilla\ngetenv = True\nrequest_memory = " 
                            + str(memory) + "\n")
    contents += "executable = " + anteprocSH + "\n"
    contents += "log = " + dagDir + "/dagLogs/anteproc$(jobNumber).log\n"
    contents += ("error = " + dagDir 
                        + "/dagLogs/logs/anteproc$(jobNumber).err\n")
    contents += ("output = " + dagDir 
                        + "/dagLogs/logs/anteproc$(jobNumber).out\n")
    contents += 'arguments = " $(paramFile) $(jobFile) $(jobNum) "\n'
    contents += "notification = error\n"
    contents += "accounting_group = " + accountingGroup + "\n"
    contents += "queue 1"
    
    with open(dagDir + "/anteproc.sub", "w") as h:
        print >> h, contents
        
    return dagDir + "/anteproc.sub"
        
def write_stochtrack_sub_file(memory, grandStochtrackSH, dagDir, 
                              accountingGroup, doGPU, numCPU):

    if doGPU:
        memory = 4000
    contents = ("universe = vanilla\ngetenv = True\nrequest_memory = " 
                        + str(memory) + "\n")
    if doGPU:
        contents += "request_gpus = 1\n"
    elif numCPU > 1:
        contents += "request_cpus = " + str(numCPU) + "\n"
    contents += "executable = " + grandStochtrackSH + "\n"
    contents += ("log = " + dagDir 
                        + "/dagLogs/grand_stochtrack$(jobNumber).log\n")
    contents += ("error = " + dagDir 
                        + "/dagLogs/logs/grand_stochtrack$(jobNumber).err\n")
    contents += ("output = " + dagDir 
                        + "/dagLogs/logs/grand_stochtrack$(jobNumber).out\n")
    contents += '''arguments = " $(paramPath) $(jobNum) "\n'''
    contents += "notification = error\n"
    contents += "accounting_group = " + accountingGroup + "\n"
    contents += "queue 1"
    
    with open(dagDir + "/grand_stochtrack.sub", "w") as h:
        print >> h, contents
    
    return dagDir + "/grand_stochtrack.sub"

    
def write_webpage_sub_file(webPageSH, dagDir, accountingGroup):

    contents = "universe = vanilla\ngetenv = True\n"
    contents += "executable = " + webPageSH + "\n"
    contents += "log = " + dagDir + "/dagLogs/web_display$(jobNumber).log\n"
    contents += ("error = " + dagDir 
                        + "/dagLogs/logs/web_display$(jobNumber).err\n")
    contents += ("output = " + dagDir 
                        + "/dagLogs/logs/web_display$(jobNumber).out\n")
    contents += 'arguments = " $(cmd_line_args)"\n'
    contents += "notification = error\n"
    contents += "accounting_group = " + accountingGroup + "\n"
    contents += "queue 1"
    
    with open(dagDir + "/web_display.sub", "w") as h:
        print >> h, contents
    
    return dagDir + "/web_display.sub"

    contents = ("universe = vanilla\ngetenv = True\nrequest_memory = " 
                    + str(memory) + "\n")

    
def write_dag(dagDir, anteprocDir, jobFile, H1AnteprocJobNums, 
              L1AnteprocJobNums, numJobGroups, anteprocSub, 
              stochtrackParamsList, stochtrackSub, maxJobsAnteproc, 
              maxJobsGrandStochtrack, webDisplaySub, baseDir):

    output = ""
    jobCounter = 0
    for jobGroup in range(1, numJobGroups + 1):
        for jobNum in H1AnteprocJobNums:
        
            output += ("JOB " + str(jobCounter) + " " + anteprocSub 
                        + "\nRETRY " + str(jobCounter) + " 2\n")
            output += ("VARS " + str(jobCounter) 
                        + ' jobNumber="' + str(jobCounter) 
                        + '" paramFile="' + anteprocDir 
                        + "/H1-anteproc_params_group_" + str(jobGroup) 
                        + "_" + str(jobNum) + '.txt"')
            output += ('jobFile="' + jobFile 
                        + '" jobNum="' + str(jobNum) + '"\n')
            output += "CATEGORY " + str(jobCounter) + " ANTEPROC\n\n"
            jobCounter += 1
    for jobGroup in range(1, numJobGroups + 1):
        for jobNum in L1AnteprocJobNums:
        
            output += ("JOB " + str(jobCounter) + " " + anteprocSub 
                        + "\nRETRY " + str(jobCounter) + " 2\n")
            output += ("VARS " + str(jobCounter) 
                        + ' jobNumber="' + str(jobCounter) 
                        + '" paramFile="' + anteprocDir 
                        + "/L1-anteproc_params_group_" + str(jobGroup) 
                        + "_" + str(jobNum) + '.txt"')
            output += ('jobFile="' + jobFile 
                        + '" jobNum="' + str(jobNum) + '"\n')
            output += "CATEGORY " + str(jobCounter) + " ANTEPROC\n\n"
            jobCounter += 1
    
    cutoff = jobCounter
    for jobDict in stochtrackParamsList:

        output += ("JOB " + str(jobCounter) + " " + stochtrackSub 
                    + "\nRETRY " + str(jobCounter) + " 2\n")
        output += ("VARS " + str(jobCounter) + ' jobNumber="' 
                    + str(jobCounter) + '" paramPath="' 
                    + jobDict["stochtrackInputDir"] + '/params.mat" ')
        output += 'jobNum="' + str(jobDict['grandStochtrackParams']
                                           ['params']
                                           ['jobNumber']) + '"\n'
        output += "CATEGORY " + str(jobCounter) + " GRANDSTOCHTRACK\n\n"
        jobCounter += 1
        
    output += ("JOB " + str(jobCounter) + " " + webDisplaySub + "\nRETRY "
                    + str(jobCounter) + " 2\n")
    output += ("VARS " + str(jobCounter) + " jobNumber=\"" + str(jobCounter)
                    + '" cmd_line_args=" -d ' + baseDir + '"\n')
    output += "CATEGORY " + str(jobCounter) + " WEBPAGE\n\n"
        
    output += "\n\n"
    
    output += "PARENT " + " ".join([str(i) for i in range(0, cutoff)])
    output += " CHILD " + " ".join([str(i) for i in range(cutoff, jobCounter)])
    output += "\n"
    output += "PARENT " + " ".join([str(i) for i in range(cutoff, jobCounter)])
    output += " CHILD " + " " + str(jobCounter)
    
    output += "\n\n\n\n\n\n"
    
    output += "MAXJOBS ANTEPROC " + str(maxJobsAnteproc) + "\n"
    output += "MAXJOBS GRANDSTOCHTRACK " + str(maxJobsGrandStochtrack) + "\n"
    output += "MAXJOBS WEBPAGE 1"
    
    with open(dagDir + "/stampAnalysis.dag", "w") as h:
        print >> h, output 
        
def getDefaultConfigs():
    return {
    "channel" : "DCS-CALIB_STRAIN_C01",
    "frame_type" : "HOFT_C01",

    "T": 3000,
    "F": 10000,
    
    "relative_direction": True,

    "linesToCut": [52, 53, 57, 58, 59, 60, 61, 62, 63, 64, 85, 108, 119, 120, 
                    121, 178, 179, 180, 181, 182, 239, 240, 241, 300, 360, 
                    372, 400, 404, 480, 1380, 1560, 1740],

    "accountingGroup": "ligo.dev.s6.burst.sgr_qpo.stamp",
    "anteprocMemory": 2048,
    "grandStochtrackMemory": 4000,
    "doGPU": True,
    "numCPU": 1,

    "anteproc_bool": True,
    "burstegard": False,
    "longPixel": True,
    "setStochtrackSeed": False,
    "singletrackBool": False,

    "maxband": 0.10,
    "maxbandMode": False,

    "simulated": False,
    
    "show_plots_when_simulated": True,

    "constantFreqWindow": True,
    "constantFreqMask": True,

    "maskCluster": False,

    "injection_bool": False,
    "onTheFly": True,
    "relativeInjectionDirection": True}

