#pyCondorSTAMPLib_v2

from __future__ import division
import numpy as np
import random
from os import getcwd
import collections


def glueFileLocation(directory, filename):
    output = None
    if directory[-1] == "/":
        if filename[0] == "/":
            output = directory + filename[1:]
        else:
            output = directory + filename
    else:
        if filename[0] == "/":
            output = directory + filename
        else:
            output = directory + "/" + filename
    return output

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

def generate_summary(params_dict, output_dir):

    output_str = "Summary of Parameters\n\nThe following parameters have been changed from default values:\n\n"
    
    params_dict.pop("_comment", None)
    
    default_params_dict = get_default_params()

    for ele in default_params_dict['list_of_important_settings']:
        output_str += ele + "\t" + str(params_dict[ele]) + "\n"
        params_dict.pop(ele, None)
        default_params_dict.pop(ele, None)
    
    output_str += "\n\nThe rest of the parameters\n\n"
    
    for key in params_dict:
        try:
            if not params_dict[key] == default_params_dict[key]:
                output_str += key + "\t" + str(params_dict[key]) + "\n"
        except KeyError:
            output_str += key + "\t" + str(params_dict[key]) + "\n"        
    with open(glueFileLocation(output_dir, 'summary.txt'), "w") as h:
        print >> h, output_str
        
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
        
def write_anteproc_sub_file(memory, anteprocSH, dagDir, accountingGroup):

    contents = "universe = vanilla\ngetenv = True\nrequest_memory = " + str(memory) + "\n"
    contents += "executable = " + anteprocSH + "\n"
    contents += "log = " + dagDir + "/dagLogs/anteproc$(jobNumber).log\n"
    contents += "error = " + dagDir + "/dagLogs/logs/anteproc$(jobNumber).err\n"
    contents += "output = " + dagDir + "/dagLogs/logs/anteproc$(jobNumber).out\n"
    contents += '''arguments = " $(paramFile) $(jobFile) $(jobNum) "\n'''
    contents += "notification = error\n"
    contents += "accounting_group = " + accountingGroup + "\n"
    contents += "queue 1"
    
    with open(dagDir + "/anteproc.sub", "w") as h:
        print >> h, contents
        
    return dagDir + "/anteproc.sub"
        
def write_stochtrack_sub_file(memory, grandStochtrackSH, dagDir, accountingGroup, doGPU, numCPU):

    if doGPU:
        memory = 4000
    contents = "universe = vanilla\ngetenv = True\nrequest_memory = " + str(memory) + "\n"
    if doGPU:
        contents += "request_gpus = 1"
    elif numCPU > 1:
        contents += "request_cpus = " + str(numCPU)
    contents += "executable = " + grandStochtrackSH + "\n"
    contents += "log = " + dagDir + "/dagLogs/grand_stochtrack$(jobNumber).log\n"
    contents += "error = " + dagDir + "/dagLogs/logs/grand_stochtrack$(jobNumber).err\n"
    contents += "output = " + dagDir + "/dagLogs/logs/grand_stochtrack$(jobNumber).out\n"
    contents += '''arguments = " $(paramPath) $(jobNum) "\n'''
    contents += "notification = error\n"
    contents += "accounting_group = " + accountingGroup + "\n"
    contents += "queue 1"
    
    with open(dagDir + "/grand_stochtrack.sub", "w") as h:
        print >> h, contents
    
    return dagDir + "/grand_stochtrack.sub"
    
def write_dag(dagDir, anteprocDir, jobFile, H1AnteprocJobNums, L1AnteprocJobNums, anteprocSub, stochtrackParamsList, stochtrackSub, maxJobsAnteproc, maxJobsGrandStochtrack):

    output = ""
    jobCounter = 0
    for jobNum in H1AnteprocJobNums:
        
        output += "JOB " + str(jobCounter) + " " + anteprocSub + "\nRETRY " + str(jobCounter) + " 2\n"
        output += "VARS " + str(jobCounter) + " jobNumber=\"" + str(jobCounter) + "\" paramFile=\"" + anteprocDir + "/H1-anteproc_params_" + str(jobNum) + "new.txt\""
        output += "jobFile=\"" + jobFile + "\" jobNum=\"" + str(jobNum) + "\"\n"
        output += "CATEGORY " + str(jobCounter) + " ANTEPROC\n\n"
        jobCounter += 1
        
    for jobNum in L1AnteprocJobNums:
        
        output += "JOB " + str(jobCounter) + " " + anteprocSub + "\nRETRY " + str(jobCounter) + " 2\n"
        output += "VARS " + str(jobCounter) + " jobNumber=\"" + str(jobCounter) + "\" paramFile=\"" + anteprocDir + "/L1-anteproc_params_" + str(jobNum) + "new.txt\""
        output += "jobFile=\"" + jobFile + "\" jobNum=\"" + str(jobNum) + "\"\n"
        output += "CATEGORY " + str(jobCounter) + " ANTEPROC\n\n"
        jobCounter += 1
    
    cutoff = jobCounter
        
    for jobDict in stochtrackParamsList:
    
        output += "JOB " + str(jobCounter) + " " + stochtrackSub + "\nRETRY " + str(jobCounter) + " 2\n"
        output += "VARS " + str(jobCounter) + " jobNumber=\"" + str(jobCounter) + "\" paramPath=\"" + jobDict["stochtrackInputDir"] + "/params_new.mat\" "
        output += "jobNum=\"" + str(jobDict['grandStochtrackParams']['params']['jobNumber']) + "\"\n"
        output += "CATEGORY " + str(jobCounter) + " GRANDSTOCHTRACK\n\n"
        jobCounter += 1
        
    output += "\n\n"
    
    output += "PARENT " + " ".join([str(i) for i in range(0, cutoff)])
    output += " CHILD " + " ".join([str(i) for i in range(cutoff, jobCounter)])
    
    output += "\n\n\n\n\n\n"
    
    output += "MAXJOBS ANTEPROC " + str(maxJobsAnteproc) + "\n"
    output += "MAXJOBS GRANDSTOCHTRACK " + str(maxJobsGrandStochtrack)
    
    with open(dagDir + "/stampAnalysis.dag", "w") as h:
        print >> h, output 
        
def get_default_params():
    return {"outputDir" : "/home/paul.schale/public_html/STAMP_outputs",

    "default_config_file" : "inputFileBase_v6_job_shift.txt",
    "defaultDictionaryPath" : "/home/quitzow/GIT/Development_Branches/pyCondorSTAMP/defaultStochtrack.json",
    "anteprocDefault" : "/home/quitzow/GIT/Development_Branches/pyCondorSTAMP/anteproc_defaults.txt",
    "STAMP2_installation_dir" : "/home/paul.schale/STAMP/stamp2/",
    "matlabMatrixExtractionExectuable" : "/home/quitzow/GIT/Development_Branches/MatlabExecutableDuctTape/getSNRandCluster",



    "jobFile" : "/home/paul.schale/job_files/oct_7_O1_job.txt",
    "triggerNumber" : 1003,
    "triggerTime" : 1132012817,
    "RA" : 18.01093806,
    "DEC" : -20.0110694,

    "channel" : "DCS-CALIB_STRAIN_C01",
    "frame_type" : "HOFT_C01",

    "T" : 1000,
    "F" : 3000,
    
    "single_cpu" : True,

    "relative_direction" : True,

    "lines_to_cut" : [52, 53, 57, 58, 59, 60, 61, 62, 63, 64, 85, 108, 119, 120, 121, 178, 179, 180, 181, 182, 239, 240, 241, 300, 360, 372, 400, 404, 480, 1380, 1560, 1740],

    "accountingGroup": "ligo.dev.s6.burst.sgr_qpo.stamp",
    "anteprocMemory": 2048,
    "grandStochtrackMemory": 4000,
    "doGPU": False,
    "numCPU" : 1,
    "maxJobsAnteproc": 20,
    "maxJobsGrandStochtrack" : 100,

    "anteproc_bool" : True,
    "burstegard" : False,
    "long_pixel" : True,
    "set_stochtrack_seed" : False,
    "pseudo_random_jobs_per_side" : 1,
    "pre_seed" : False,
    "singletrack_bool" : False,
    "singletrack_input_files" : "EXAMPLES AT /home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/stamp_analysis_anteproc-2015_10_13/jobs/job_group_1_v4/job_39/grandstochtrackOutput/bknd_39.mat,/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/stamp_analysis_anteproc-2015_10_13/jobs/job_group_1_v4/job_6/grandstochtrackOutput/bknd_6.mat,/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/stamp_analysis_anteproc-2015_10_13/jobs/job_group_1_v3/job_4/grandstochtrackOutput/bknd_4.mat,/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/stamp_analysis_anteproc-2015_10_13/jobs/job_group_1_v4/job_11/grandstochtrackOutput/bknd_11.mat",

    "maxband" : 0.10,
    "maxband_mode" : False,

    "simulated": False,
    "LHO_Welch_PSD_file" : "EXAMPLE FILE AT /home/quitzow/public_html/Magnetar/closed_box/sgr_trigger_2469/power_curve/PSD_estimates/LHO_Welch_PSD_for_940556300-940557106GPS.txt",
    "LLO_Welch_PSD_file" : "EXAMPLE FILE AT /home/quitzow/public_html/Magnetar/closed_box/sgr_trigger_2469/power_curve/PSD_estimates/LLO_Welch_PSD_for_940556300-940557106GPS.txt",

    "on_source_file_path" : "EXAMPLE FILE AT /home/quitzow/public_html/Magnetar/open_box/sgr_trigger_2469/stochtrack/stamp_analysis_anteproc-2015_9_11/jobs/job_group_1/job_1/grandstochtrackOutput/bknd_1.mat",
    "off_source_json_path" : "EXAMPLE FILE AT /Users/pschale/ligo/STAMP/SGR_trigger_files/sgr_trigger_2469/upper_limits/job_pairs_with_low_SNR_sgr_trigger_2469_ref_dir.txt",

    "show_plots_when_simulated" : True,

    "constant_f_window" : True,
    "constant_f_mask" : True,

    "remove_cluster" : False,

    "job_subset_limit" : 2,

    "injection_bool" : False,
    "onTheFly" : True,
    "long_tau" : True,
    "injection_file" : "NEED FILE HERE IF NOT onTheFly",


    "polarization_smaller_response" : False,
    "injection_random_start_time" : False,
    "stamp_alpha" : 1e-40,
    "wave_frequency" : 150,
    "relativeInjectionDirection" : True,

    "include_variations" : False,
    "number_variation_jobs" : 2,
    "anteproc_varying_param" : [["num_space", "stamp.alpha", "logarithmic_sqrt", 1.296e-43, 1.369e-43]],

    "list_of_important_settings" : ["triggerNumber", "injection_bool", "maxband_mode", "T", "F"]}

