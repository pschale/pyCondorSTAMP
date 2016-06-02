# Written by Ryan Quitzow-James

from __future__ import division
from generateInputFileLib import *
from numpy import argsort, sqrt, arccos, pi
import random
import json

#updated for O1 by Paul Schale



################################################
#Stuff you will edit often
################################################

triggerNumber = 1001
search_type = "offsource" #needs to be "upper_limits", "onsource", "offsource",  or "pseudo_onsource"

#requirements:
#onsource - job file looks like: "1 <start time> <end time> <length of segment>"
#           simulated - False, remove_cluster - False, injection_bool - False

#offsource - job file looks like:
#           simulated - False, remove_cluster - False, injection_bool - False


onsource = search_type == "onsource"
pseudo_onsource = search_type == "pseudo_onsource"
upper_limits = search_type == "upper_limits"
offsource = search_type == "offsource"

#search configuration
anteproc_bool = True                        #false - uses preproc, probably remove this
burstegard = False                          #burstegard is better for short stuff, usually keep this False to use stochtrack
long_pixel = True                           #4 second long pixels (True), 1 second long pixels (False)
set_stochtrack_seed = False                  #uses same seed every time for reproducibility, False gives random seed based on system time
pseudo_random_jobs_per_side = 1             #(check this)
pre_seed = False                            # (check this) True lets you set the seed for anteproc, similar to set_stochtrack_seed
singletrack_bool = False                     # gives the cluster(s) for grandstrochtrack to look for, speeds up analysis, used mostly for upper limits

simulated = False                           #if True, simulates data instead of taking real data
show_plots_when_simulated = True            #set to false when doing tons of jobs, doesn't matter if simulated is False

#look in S6_magnetar_window - search_window_lib (check this)
constant_f_window = True
constant_f_mask = True

#this should be True if doing upper limits, it removes the loudest cluster in background to make sure
#that the loudest cluster doesn't contribute to the result of the upper limits
remove_cluster = False



# options for number of jobs (background jobs, include on-source if upper limits)
job_subset_limit = 2  #set to None or 0 if a limit is not desired

#injection config
injection_bool = False                        #if doing injections, if doing upper limits this needs to be true
onTheFly = True                             #STAMP makes this injections if True, otherwise need to give it the injections data

long_tau = True                            # or short tau, 400 s vs 150 s
polarization_smaller_response = False     # Sets the polarization to the alternate polarizations, a minimum in the case of 2471, and a small alternative that should still be sensitive to injections in the case of the other triggers.
injection_random_start_time = False       # Randomizes the injection start time according to the rules given below in the relevant if statement.
stamp_alpha = 1e-40#6e-44                 #amplitude squared of the injection (h_0), if waveform is normalized
wave_frequency = 150
relativeInjectionDirection = True             #(check this) something about using direction relative to surface of the earth, rather than fixed frame
include_variations = False
number_variation_jobs = 2#4
anteproc_varying_param = [
    ["num_space", "stamp.alpha", "logarithmic_sqrt", 1.296E-43, 1.369E-43]#6.25E-44, 7.84E-44]#1.1025E-44, 1.44E-44]#1.44E-44, 1.69E-44]
    ]#""" #stamp.alpha is h_0 ^2
    #(check this) in pyCondorSTAMPanteprocSupportLib_v2.py

#renamed from upper_limit_parameters

#1st - distribution type to vary across
#2nd - thing that's being varied
#3rd - distribution specifier (not used for "set" distribution)
#4th-end - parameters (usually edges, can be all values (not inside its own list))

    #######################################
    # File Paths
    #######################################

config_file_dest_dir = "/Users/pschale/ligo/STAMP/SGR_trigger_files/sgr_trigger_" + str(triggerNumber) + "/" + search_type

#defaults
default_config_file = "../SettingUpSearch/inputFileBase_v6_job_shift.txt"

#dir w/ dirs of job files
job_dirs_dir = "/Users/pschale/ligo/STAMP/job_files/"

if upper_limits:
    # on_source_file_path is the output from running the on-source
    on_source_file_path = "/home/quitzow/public_html/Magnetar/open_box/sgr_trigger_2469/stochtrack/stamp_analysis_anteproc-2015_9_11/jobs/job_group_1/job_1/grandstochtrackOutput/bknd_1.mat"
    
    off_source_json_path = "/Users/pschale/ligo/STAMP/SGR_trigger_files/sgr_trigger_2469/upper_limits/job_pairs_with_low_SNR_sgr_trigger_2469_ref_dir.txt"
if simulated:
    LHO_Welch_PSD_file = "/home/quitzow/public_html/Magnetar/closed_box/sgr_trigger_2469/power_curve/PSD_estimates/LHO_Welch_PSD_for_940556300-940557106GPS.txt"
    LLO_Welch_PSD_file = "/home/quitzow/public_html/Magnetar/closed_box/sgr_trigger_2469/power_curve/PSD_estimates/LLO_Welch_PSD_for_940556300-940557106GPS.txt"
    
if singletrack_bool:
    #get these files by doing injections, running off-source, can do more than 1 (so it's not really "single" track)    
    singletrack_input_files = """/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/stamp_analysis_anteproc-2015_10_13/jobs/job_group_1_v4/job_39/grandstochtrackOutput/bknd_39.mat,/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/stamp_analysis_anteproc-2015_10_13/jobs/job_group_1_v4/job_6/grandstochtrackOutput/bknd_6.mat,/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/stamp_analysis_anteproc-2015_10_13/jobs/job_group_1_v3/job_4/grandstochtrackOutput/bknd_4.mat,/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/stamp_analysis_anteproc-2015_10_13/jobs/job_group_1_v4/job_11/grandstochtrackOutput/bknd_11.mat"""
    
if injection_bool and not onTheFly:
    injection_file = "INSERT PATH TO INJECTION FILE HERE"
    

##################################################
#Stuff to edit sometimes
##################################################

triggers = [1001, 2001, 3001]
triggerTimes = [1132012817, 949827104, 957191879]

initial_RA = 18 + 8/60 + 39.337/3600
declination = -(20+24/60+39.85/3600)

if long_tau:
    wave_tau = 400
else:
    wave_tau = 150
    
wave_duration = wave_tau*3

if polarization_smaller_response: #this might need adjustment for particular triggers
    wave_iota = 120
    wave_psi = 45
else:
    wave_iota = 0
    wave_psi = 0
    
if injection_random_start_time:
    start_variation_line = "varying_injection_start -2 " + str(1604 - wave_duration - 2) #check what this does exactly

O1_lines_to_cut = [52, 53, 57, 58, 59, 60, 61, 62, 63, 64, 85, 108, 119, 120, 121, 178, 179, 180, 181, 182, 239, 240, 241, 300, 360, 372, 400, 404, 480, 1380, 1560, 1740]



##################################################
#Stuff that should never need to be edited
##################################################

#This makes sure options chosen are consistent
if onsource:
    injection_bool = False
    simulated = False

if not injection_bool:
    onTheFly = False
    polarization_smaller_response = False
    injection_random_start_time = False
    relativeInjectionDirection = False
    include_variations = False


    


#load default file
inputFileData = readFile(default_config_file)
inputFileString = "\n".join(" ".join(x for x in line) for line in inputFileData)

triggerIndex = triggers.index(triggerNumber)
triggerTime = triggerTimes[triggerIndex]


#job file selection
jobDirPath = job_dirs_dir + search_type
jobFile = glueFileLocation(jobDirPath, "sgr_trigger_" + str(triggerNumber) + "_" + search_type + "_jobs.txt")

times = [[int(y) for y in x] for x in readFile(jobFile)]

if burstegard:
    inputFileString += "\n\n" + "grandStochtrack doBurstegard true"
else:
    if long_pixel:
        inputFileString += "\n\n" + "anteproc_h segmentDuration 4"
        inputFileString += "\n\n" + "anteproc_l segmentDuration 4"
    else:
        inputFileString += "\n\n" + "anteproc_h segmentDuration 1"
        inputFileString += "\n\n" + "anteproc_l segmentDuration 1"
    inputFileString += "\n\n" + "grandStochtrack doStochtrack true"
    if long_pixel:
        inputFileString += "\n\n" + "grandStochtrack stochtrack.mindur 25"
        inputFileString += "\n\n" + "preproc segmentDuration 4"
    else:
        inputFileString += "\n\n" + "grandStochtrack stochtrack.mindur 100"
        inputFileString += "\n\n" + "grandStochtrack stochtrack.F 600"

if simulated:
    inputFileString += "\n\n" + "anteproc_h doDetectorNoiseSim true"
    inputFileString += "\n\n" + "anteproc_l doDetectorNoiseSim true"
    inputFileString += "\n\n" + "anteproc_h DetectorNoiseFile " + LHO_Welch_PSD_file
    inputFileString += "\n\n" + "anteproc_l DetectorNoiseFile " + LLO_Welch_PSD_file
    if not show_plots_when_simulated:
        inputFileString += "\n\n" + "grandStochtrack savePlots false"
else:
    inputFileString += "\n\n" + "anteproc_h doDetectorNoiseSim false"
    inputFileString += "\n\n" + "anteproc_l doDetectorNoiseSim false"


# Add in injections (if desired)
if injection_bool:
    if onTheFly:
        # stamp_alpha was waveformPowerAmplitudeScaling here
        inputFileString += "\n\n" + """anteproc_h stampinj true
anteproc_h stamp.alpha """ + str(stamp_alpha) + """

anteproc_h stamp.iota """ + str(wave_iota) + """
anteproc_h stamp.psi """ + str(wave_psi) + """

anteproc_l stampinj true
anteproc_l stamp.alpha """ + str(stamp_alpha) + """

anteproc_l stamp.iota """ + str(wave_iota) + """
anteproc_l stamp.psi """ + str(wave_psi)
    else:
        inputFileString += "\n\n" + """anteproc_h stampinj true
anteproc_h stamp.alpha """ + str(stamp_alpha) + """

anteproc_h stamp.iota 0
anteproc_h stamp.psi 0

anteproc_l stampinj true
anteproc_l stamp.alpha """ + str(stamp_alpha) + """

anteproc_l stamp.iota 0
anteproc_l stamp.psi 0"""


if singletrack_bool:
    inputFileString += '\n\n' + "grandStochtrack stochtrack.singletrack.doSingletrack true"
    inputFileString += "\n" + "grandStochtrack stochtrack.singletrack.trackInputFiles " + singletrack_input_files
    
if set_stochtrack_seed:
    inputFileString += "\n\n" + "grandStochtrack stochtrack.doSeed true"
    inputFileString += "\n\n" + "grandStochtrack stochtrack.seed 2015"

if not long_pixel:
    inputFileString += "\n\n" + "job_start_shift 6"
    inputFileString += "\n\n" + "job_duration 400"

if simulated and onsource and pre_seed:
    inputFileString += "\n\n" + "anteproc_h job_seed 1 2694478780"
    inputFileString += "\n\n" + "anteproc_l job_seed 1 4222550304"

job_group = 1

params = {}

if not relativeInjectionDirection:
    params["preproc stamp.decl"] = declination
    params["grandStochtrack dec"] = declination

if injection_bool and not onTheFly:
    params["preproc stamp.file"] = injection_file
    params["preproc stamp.alpha"] = 1e-40


#this ensures there's enough data to be able to estimate the background
# 9-NumberofSegmentsPerInterval (NSPI), -1 (take out the pixel that's being analyzed), /2 to get one side of those
# *4 (pixel duration) 2 + (buffer seconds), + 2 (window started 2 seconds before trigger time)
if long_pixel or burstegard:
    triggerJobStart = triggerTime - (2 + (9-1)*4/2 + 2)
else:
    triggerJobStart = triggerTime - (2 + (9-1)/2 + 2)

# analysis starts 2 pixels before trigger time
trigger_hStart = triggerTime - 2

deltaTotal = []
jobPairs = []
jobPairsTotal = 1000 #number of background job pairs set

if upper_limits:

    with open(off_source_json_path, 'r') as infile:
        temp_job_data = json.load(infile)
    sortedJobPairs = [x[1:3] for x in temp_job_data if x[1:3] != [34, 34]]
    sortedJobPairs = [[x-1 for x in y] for y in sortedJobPairs] # goes from job number to job index
    source_file_dict = {}

    for num in range(len(sortedJobPairs)):

        if sortedJobPairs[num][0] not in source_file_dict:
            source_file_dict[sortedJobPairs[num][0]] = {}
            
        if sortedJobPairs[num][1] in source_file_dict[sortedJobPairs[num][0]]:
            print("Warning, multiple copies of job pair exist.")
            print(sortedJobPairs[num])
        elif sortedJobPairs[num][0] == 33 or sortedJobPairs[num][1] == 33:
            print("Warning, on-source and off-source jobs possibly mixed.")
            print(sortedJobPairs[num])
        else:
            source_file_dict[sortedJobPairs[num][0]][sortedJobPairs[num][1]] = temp_job_data[num][-1]
        # add on-source jobs and path, it's job number 34, and index number 33
    sortedJobPairs = [[33,33]] + sortedJobPairs
    source_file_dict[33] = {}
    source_file_dict[33][33] = on_source_file_path
    
    #cut down to max number of jobs (if needed)
    if len(sortedJobPairs) > job_subset_limit:
        sortedJobPairs = sortedJobPairs[:job_subset_limit]
    else:
        job_subset_limit = None
        
elif onsource:
    sortedJobPairs = [[0,0]]

elif pseudo_onsource:
    before_possible_job_indices = [index for index, val in enumerate(times) if triggerJobStart - val[1] >= 3600]
    after_possible_job_indices = [index for index, val in enumerate(times) if val[1] - triggerJobStart >= 3600]
    job_index_list_1 = random.sample(before_possible_job_indices, pseudo_random_jobs_per_side)
    job_index_list_2 = random.sample(after_possible_job_indices, pseudo_random_jobs_per_side)
    sortedJobPairs = [[x,x] for x in job_index_list_1] + [[x,x] for x in job_index_list_2]

elif offsource:
    for index1, job1 in enumerate(times):
        for index2, job2 in enumerate(times):
            if index1 != index2:
                deltaTotal += [abs(triggerJobStart - job1[1]) + abs(triggerJobStart - job2[1])]
                jobPairs += [[index1, index2]]
    sortedIndices = argsort(deltaTotal)[:jobPairsTotal]
    sortedJobPairs = [jobPairs[x] for x in sortedIndices]
    
else:
    print("Error: need to define search type correctly")
    raise
    
tempNumbersH = list(set([x[0] for x in sortedJobPairs])) #job indices
tempNumbersL = list(set([x[1] for x in sortedJobPairs])) #job indices



    
for H1_job_index in tempNumbersH:
    H1_job = H1_job_index + 1
    job1StartTime = times[H1_job_index][1]
    sidereal_day_length = 23.9344696
    temp_RA = (initial_RA +  (24/sidereal_day_length)*(job1StartTime - triggerJobStart)/3600) % 24
    if long_pixel or burstegard:
        job1_hstart = job1StartTime + (9-1)*4/2+2
    else:
        job1_hstart = job1StartTime + (9-1)/2+2
        
    job1_hstop = job1_hstart + 1602 if long_pixel or burstegard else job1_hstart + 400

    if injection_bool:
        if not relativeInjectionDirection:
            inputFileString += "\n\n" + "anteproc_h anteproc_param "+str(H1_job)+" stamp.ra " + str(temp_RA)
            inputFileString += "\n" + "anteproc_h anteproc_param "+str(H1_job)+" stamp.decl " + str(declination)
        elif H1_job == 34:
            inputFileString += "\n\nanteproc_h anteproc_param 34 useReferenceAntennaFactors false"
        else:
            inputFileString += "\n\nanteproc_h anteproc_param " + str(H1_job) + " useReferenceAntennaFactors true"
        if onTheFly:
            inputFileString += "\n" + "anteproc_h anteproc_param " + str(H1_job) + " stamp.start " + str(job1_hstart+2)
        else:
            inputFileString += "\n" + "anteproc_h stamp.startGPS " + str(job1_hstart+2)


for L1_job_index in tempNumbersL:
    L1_job = L1_job_index + 1
    job1StartTime = times[L1_job_index][1]
    sidereal_day_length = 23.9344696
    temp_RA = (initial_RA +  (24/sidereal_day_length)*(job1StartTime - triggerJobStart)/3600) % 24
    if long_pixel or burstegard:
        job1_hstart = job1StartTime + (9-1)*4/2+2
    else:
        job1_hstart = job1StartTime + (9-1)/2+2
        
    job1_hstop = job1_hstart + 1602 if long_pixel or burstegard else job1_hstart + 400
    
    if injection_bool:
        if not relativeInjectionDirection:
            inputFileString += "\n\n" + "anteproc_l anteproc_param "+str(L1_job)+" stamp.ra " + str(temp_RA)
            inputFileString += "\n" + "anteproc_l anteproc_param "+str(L1_job)+" stamp.decl " + str(declination)
        elif L1_job == 34:
            inputFileString += "\n\nanteproc_l anteproc_param 34 useReferenceAntennaFactors false"
        else:
            inputFileString += "\n\nanteproc_l anteproc_param " + str(L1_job) + " useReferenceAntennaFactors true"
        if onTheFly:
            inputFileString += "\n" + "anteproc_l anteproc_param " + str(L1_job) + " stamp.start " + str(job1_hstart+2)
        else:
            inputFileString += "\n" + "anteproc_l stamp.startGPS " + str(job1_hstart+2)

if injection_bool:
    if onTheFly:
        #here we put in parameters for the on-the-fly injection, including waveform, frequency, amplitude (sqrt(2)/2, so that
        # they sum in quadrature to 1
        inputFileString += """

anteproc_h stamp.inj_type fly
anteproc_h stamp.fly_waveform half_sg
anteproc_l stamp.inj_type fly
anteproc_l stamp.fly_waveform half_sg

anteproc_h stamp.h0 """ + str(sqrt(0.5)) + """
anteproc_h stamp.f0 """ + str(wave_frequency) + """
anteproc_h stamp.phi0 0
anteproc_h stamp.fdot 0
anteproc_h stamp.duration """ + str(wave_duration) + """
anteproc_h stamp.tau """ + str(wave_tau) + """

anteproc_l stamp.h0 """ + str(sqrt(0.5)) + """
anteproc_l stamp.f0 """ + str(wave_frequency) + """
anteproc_l stamp.phi0 0
anteproc_l stamp.fdot 0
anteproc_l stamp.duration """ + str(wave_duration) + """
anteproc_l stamp.tau """ + str(wave_tau)
    elif not onTheFly:
        inputFileString += "\n\n" + "\n".join(" ".join(x for x in ["waveform", temp_name, glueFileLocation(waveformDirectory, temp_name + waveformFileExtention)]) for temp_name in waveformFileNames)


if relativeInjectionDirection:

    refTime = triggerTime - 2

    inputFileString += "\n\ngrandStochtrack useReferenceAntennaFactors true"
    inputFileString += "\n\ngrandStochtrack referenceGPSTime " + str(refTime)
    inputFileString += "\nanteproc_h referenceGPSTime " + str(refTime)
    inputFileString += "\nanteproc_l referenceGPSTime " + str(refTime)

    inputFileString += "\n\ngrandStochtrack ra " + str(initial_RA)
    inputFileString += "\ngrandStochtrack dec " + str(declination)
    inputFileString += "\n\nanteproc_h stamp.ra " + str(initial_RA)
    inputFileString += "\nanteproc_h stamp.decl " + str(declination)
    inputFileString += "\n\nanteproc_l stamp.ra " + str(initial_RA)
    inputFileString += "\nanteproc_l stamp.decl " + str(declination)


if constant_f_window:
    inputFileString += "\n\ngrandStochtrack fmin 40"
    inputFileString += "\ngrandStochtrack fmax 2500"
if constant_f_mask:
    inputFileString += "\n\ngrandStochtrack StampFreqsToRemove [" + ", ".join(str(x) for x in O1_lines_to_cut) + "]"

if remove_cluster:
    inputFileString += "\n\ngrandStochtrack maskCluster true"

if include_variations:
    inputFileString += "\n\nanteproc_varying_param num_jobs_to_vary " + str(number_variation_jobs)
    inputFileString += "".join("\nanteproc_varying_param " + " ".join(str(y) for y in x) for x in anteproc_varying_param)

if injection_random_start_time:
    inputFileString += "\n" + start_variation_line

text_output = inputFileString


#this for loop builds each individual job
current_job = 0

for [jobIndex1, jobIndex2] in sortedJobPairs:#[jobNum1, jobNum2] in sortedJobPairs:
    jobNum1 = jobIndex1 + 1
    jobNum2 = jobIndex2 + 1
    job1StartTime = times[jobIndex1][1]
    job1EndTime = times[jobIndex1][2]

    if long_pixel or burstegard:
        job1_hstart = job1StartTime + (9-1)*4/2+2
    else:
        job1_hstart = job1StartTime + (9-1)/2+2
        
    job1_hstop = job1_hstart + 1602 if long_pixel or burstegard else job_hstart + 400

    sidereal_day_length = 23.9344696
    temp_RA = (initial_RA +  (24/sidereal_day_length)*(job1StartTime - triggerJobStart)/3600) % 24

    if injection_bool and not relativeInjectionDirection:
        #params["preproc stamp.startGPS"] = int(jobH1StartTime)
        params["preproc stamp.ra"] = temp_RA

    if not relativeInjectionDirection:
        params["grandStochtrack ra"] = temp_RA

    if remove_cluster:
        params["grandStochtrack clusterFile"] = source_file_dict[jobIndex1][jobIndex2]

    params["preproc job"] = jobNum1#this needed anymore?

    if anteproc_bool:
        params["grandStochtrack anteproc.jobNum1"] = jobNum1
        params["grandStochtrack anteproc.jobNum2"] = jobNum2

    else:
        params["preproc doShift1"] = 0
        params["preproc ShiftTime1"] = 0
        params["preproc doShift2"] = 1
        params["preproc ShiftTime2"] = base_shift + timeShift - 1

    if relativeInjectionDirection:
        if jobIndex1 == 33:
            params["grandStochtrack useReferenceAntennaFactors"] = "false"
        elif "grandStochtrack useReferenceAntennaFactors" in params:
            del params["grandStochtrack useReferenceAntennaFactors"]

    if injection_bool and not onTheFly:
        for temp_waveform in waveformFileNames:
            params["injection_tag"] = temp_waveform
            current_job += 1
            temp_output = ""
            temp_output += "job " + str(current_job) + "\n"
            temp_output += "job_group " + str(job_group) + "\n"
            temp_output += "\n".join([str(x) + " " + str(params[x]) for x in params])    
            text_output += "\n\n" + temp_output
    else:
        current_job +=1
        temp_output = ""
        temp_output += "job " + str(current_job) + "\n"
        temp_output += "job_group " + str(job_group) + "\n"
        temp_output += "\n".join([str(x) + " " + str(params[x]) for x in params])
        text_output += "\n\n" + temp_output


#Now the filename
pyCondorSTAMP_input_file_name = "sgr_trigger_" + str(triggerNumber) + "_"

#Now add options to the filename
if onsource:
    if burstegard:
        pyCondorSTAMP_input_file_name += "burstegard_open_box_search"
    else:
        pyCondorSTAMP_input_file_name += "stochtrack_open_box_search"#_370
        if long_pixel:
            pyCondorSTAMP_input_file_name += "_4_s"
elif pseudo_onsource:
    if burstegard:
        pyCondorSTAMP_input_file_name += "burstegard_pseudo_open_box_search"
    else:
        pyCondorSTAMP_input_file_name += "stochtrack_pseudo_open_box_search"#_370
        if long_pixel:
            pyCondorSTAMP_input_file_name += "_4_s"
elif upper_limits:
    if singletrack_bool:
        pyCondorSTAMP_input_file_name += "singletrack_upper_limits"
    elif burstegard:
        pyCondorSTAMP_input_file_name += "burstegard_upper_limits"
    else:
        pyCondorSTAMP_input_file_name += "stochtrack_upper_limits"#_370
        if long_pixel:
            pyCondorSTAMP_input_file_name += "_4_s"

else:
    if burstegard:
        pyCondorSTAMP_input_file_name += "burstegard_closed_box_search"
    else:
        pyCondorSTAMP_input_file_name += "stochtrack_closed_box_search"#_370
        if long_pixel:
            pyCondorSTAMP_input_file_name += "_4_s"

if simulated:
    pyCondorSTAMP_input_file_name += "_simulated"

if job_subset_limit:
    pyCondorSTAMP_input_file_name += "_jobSubsetLimit_" + str(job_subset_limit)

if include_variations:
    pyCondorSTAMP_input_file_name += "_varyingParameters"

if remove_cluster:
    pyCondorSTAMP_input_file_name += "_maskCluster"

if injection_random_start_time:
    pyCondorSTAMP_input_file_name += "_randomized_injection_time"


if injection_bool:
    if onTheFly:
        pyCondorSTAMP_input_file_name += "_onTheFly_f_" + str(wave_frequency) + "_tau_" + str(wave_tau)
        if wave_iota != 0:
            pyCondorSTAMP_input_file_name += "_iota_" + str(wave_iota)
        if wave_psi != 0:
            pyCondorSTAMP_input_file_name += "_psi_" + str(wave_psi)
        pyCondorSTAMP_input_file_name += ".txt"#_f" + str(frequency".txt"
    else:
        pyCondorSTAMP_input_file_name += "_injectionTrue_multiple_waveforms.txt"
else:
    pyCondorSTAMP_input_file_name += ".txt"

saveText(glueFileLocation(config_file_dest_dir, pyCondorSTAMP_input_file_name), text_output)

print(pyCondorSTAMP_input_file_name)
