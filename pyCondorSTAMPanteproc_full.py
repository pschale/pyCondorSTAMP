#pyCondorSTAMPanteproc_full.py
from __future__ import division
from numpy import argsort, sqrt, arccos, pi, array, object
from pyCondorSTAMPLib_v2 import *
import scipy.io as sio
import random
import json
import os
from optparse import OptionParser
from copy import deepcopy
from webdisplay import webpage

def main():
    parser = OptionParser()
    
    parser.add_option("-p", "--params-file", dest = "params_file",
                      help = "Path to params file")
    parser.add_option("-v", "--verbose", 
                        action = "store_true", dest = "verbose", default = False,
                        help = "prints out dictionaries to file at end")
    
    (options, args) = parser.parse_args()
    
    params_file_path = options.params_file
    
    if params_file_path[0] == ".":
        params_file_path = os.getcwd() + params_file_path[1:]
    elif params_file_path[0] == "~":
        params_file_path = os.path.expanduser('~') + params_file_path[1:]
    elif not params_file_path[0] == "/":
        params_file_path = os.getcwd() + "/" + params_file_path[0:]
        
    
    input_params = json.load(open(params_file_path))
    
    #Following lines DISABLED, dictionary now used due to increased security
    #this loads all of the input parameters into local variables.  It's kind of magic
    #for key, val in input_params.iteritems():
    #    exec(key + '=val')
        
    onsource = input_params['search_type'] == "onsource"
    pseudo_onsource = input_params['search_type'] == "pseudo_onsource"
    upper_limits = input_params['search_type'] == "upper_limits"
    offsource = input_params['search_type'] == "offsource"
    
    if input_params['injection_bool'] and not input_params['onTheFly'] and not os.isfile(injection_file):
        pyCondorSTAMPanteprocError("Injection file does not exist.  Make onTheFly true if you do not wish to specify an injection file")
        
    if input_params['long_tau']:
        wave_tau = 400
    else:
        wave_tau = 150
        
    wave_duration = wave_tau*3
    
    if input_params['polarization_smaller_response']: #this might need adjustment for particular triggers
        wave_iota = 120
        wave_psi = 45
    else:
        wave_iota = 0
        wave_psi = 0
    
    if onsource:
        input_params['injection_bool'] = False
        input_params['simulated'] = False
        input_params['relative_direction'] = False
        
    if pseudo_onsource:
        relative_directoin = False
    
    if not input_params['injection_bool']:
        input_params['onTheFly'] = False
        input_params['polarization_smaller_response'] = False
        input_params['injection_random_start_time'] = False
        input_params['include_variations'] = False
        
    if input_params['singletrack_bool']:
        input_params['single_cpu'] = True
    
    jobPath = make_file_path_absolute(input_params['jobFile'])
    configPath = os.path.join(input_params['outputDir'], "config_file.txt")
    outputDir = make_file_path_absolute(input_params['outputDir'])
    outputDir += "stamp_analysis_anteproc" if input_params['outputDir'][-1] == "/" else "/stamp_analysis_anteproc"
    
    baseDir = dated_dir(outputDir)
    
    supportDir = create_dir(baseDir + "/input_files")
    jobsBaseDir = create_dir(baseDir + "/jobs")
    anteproc_dir = create_dir(baseDir + "/anteproc_data")

    # copy input files to this directory
    copy_input_file(configPath, supportDir)
    copy_input_file(params_file_path, supportDir)
    newJobPath = copy_input_file(jobPath, supportDir)
    
    #adjust job file
    jobFileName = jobPath[len(jobPath)-jobPath[::-1].index('/')::]
    adjustedJobFileName = jobFileName[:jobFileName.index(".txt")] + "_postprocessing" + jobFileName[jobFileName.index(".txt"):]
    newAdjustedJobPath = os.path.join(supportDir, adjustedJobFileName)
    
    commonParamsDictionary = getCommonParams(input_params)
    
    times = [[int(y) for y in x] for x in readFile(input_params['jobFile'])]

        
    job_group = 1
        
    #this ensures there's enough data to be able to estimate the background
    # 9-NumberofSegmentsPerInterval (NSPI), -1 (take out the pixel that's being analyzed), /2 to get one side of those
    # *4 (pixel duration) 2 + (buffer seconds), + 2 (window started 2 seconds before trigger time)
    if input_params['long_pixel'] or input_params['burstegard']:
        triggerJobStart = input_params['triggerTime'] - (2 + (9-1)*4/2 + 2)
    else:
        triggerJobStart = input_params['triggerTime'] - (2 + (9-1)/2 + 2)
    
    # analysis starts 2 pixels before trigger time
    trigger_hStart = input_params['triggerTime'] - 2
        
    #Next section finds the job number PAIRS run by stochtrack, and job NUMBERS run by anteproc
    
    if upper_limits:
    
        with open(input_params['off_source_json_path'], 'r') as infile:
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
        source_file_dict[33][33] = input_params['on_source_file_path']
        
        #cut down to max number of jobs (if needed)
        if len(sortedJobPairs) > input_params['job_subset_limit']:
            sortedJobPairs = sortedJobPairs[:input_params['job_subset_limit']]
        else:
            input_params['job_subset_limit'] = None
            
    elif onsource:
        sortedJobPairs = [[0,0]]
    
    elif pseudo_onsource:
        before_possible_job_indices = [index for index, val in enumerate(times) if triggerJobStart - val[1] >= 3600]
        after_possible_job_indices = [index for index, val in enumerate(times) if val[1] - triggerJobStart >= 3600]
        job_index_list_1 = random.sample(before_possible_job_indices, input_params['pseudo_random_jobs_per_side'])
        job_index_list_2 = random.sample(after_possible_job_indices, input_params['pseudo_random_jobs_per_side'])
        sortedJobPairs = [[x,x] for x in job_index_list_1] + [[x,x] for x in job_index_list_2]
    
    elif offsource:
        deltaTotal = []
        jobPairs = []
        for index1, job1 in enumerate(times):
            for index2, job2 in enumerate(times):
                if index1 != index2:
                    deltaTotal += [abs(triggerJobStart - job1[1]) + abs(triggerJobStart - job2[1])]
                    jobPairs += [[index1, index2]]
        sortedIndices = argsort(deltaTotal)[:input_params['maxNumJobPairs']]
        sortedJobPairs = [jobPairs[x] for x in sortedIndices]
        
    else:
        print("Error: need to define search type correctly")
        raise
        
    #These are the job indices run by anteproc 
    tempNumbersH = list(set([x[0] for x in sortedJobPairs])) #job indices
    tempNumbersL = list(set([x[1] for x in sortedJobPairs])) #job indices
    
    
    
    #Now build the job-specific parameters for anteproc - only needed for injections
    anteprocHParamsList = [{'stamp':{}} for i in range(0, max(tempNumbersH) + 1)]
    anteprocLParamsList = [{'stamp':{}} for i in range(0, max(tempNumbersL) + 1)]
    if input_params['injection_bool']:

        for H1_job_index in tempNumbersH:
            H1_job = H1_job_index + 1
            job1StartTime = times[H1_job_index][1]
    
            if input_params['long_pixel'] or input_params['burstegard']:
                job1_hstart = job1StartTime + (9-1)*4/2+2
            else:
                job1_hstart = job1StartTime + (9-1)/2+2
            
            job1_hstop = job1_hstart + 1602 if input_params['long_pixel'] or input_params['burstegard'] else job1_hstart + 400
    
            if not input_params['relative_direction']:
                anteprocHParamsList[H1_job_index]['stamp.ra'] = input_params['RA']
                anteprocHParamsList[H1_job_index]['stamp.decl'] = input_params['DEC']

            elif H1_job == 34:
                anteprocHParamsList[33]['useReferenceAntennaFactors'] = False

            else:
                anteprocHParamsList[H1_job_index]['useReferenceAntennaFactors'] = True

            if input_params['onTheFly']:
                anteprocHParamsList[H1_job_index]['stamp.start'] = job1_hstart+2  

            else:
                anteprocHParamsList[H1_job_index]['stamp.startGPS'] = job1_hstart+2


        for L1_job_index in tempNumbersL:
            L1_job = L1_job_index + 1
            job1StartTime = times[L1_job_index][1]
    
            if input_params['long_pixel'] or input_params['burstegard']:
                job1_hstart = job1StartTime + (9-1)*4/2+2
            else:
                job1_hstart = job1StartTime + (9-1)/2+2
            
            job1_hstop = job1_hstart + 1602 if input_params['long_pixel'] or input_params['burstegard'] else job1_hstart + 400
        
            if not input_params['relative_direction']:
                anteprocLParamsList[L1_job_index]['stamp.ra'] = input_params['RA']
                anteprocLParamsList[L1_job_index]['stamp.decl'] = input_params['DEC']

            elif L1_job == 34:
                anteprocLParamsList[33]['useReferenceAntennaFactors'] = False

            else:
                anteprocLParamsList[L1_job_index]['useReferenceAntennaFactors'] = True

            if input_params['onTheFly']:
                anteprocLParamsList[L1_job_index]['stamp.start'] = job1_hstart+2
            else:
                anteprocLParamsList[L1_job_index]['stamp.startGPS'] = job1_hstart+2
    

        if input_params['onTheFly']:
            #here we put in parameters for the on-the-fly injection, including waveform, frequency, amplitude (sqrt(2)/2, so that
            # they sum in quadrature to 1
            commonParamsDictionary['anteproc_h']['stamp']['inj_type'] = "fly"
            commonParamsDictionary['anteproc_h']['stamp']['fly_waveform'] = "half_sg"
            commonParamsDictionary['anteproc_l']['stamp']['inj_type'] = "fly"
            commonParamsDictionary['anteproc_l']['stamp']['fly_waveform'] = "half_sg"

            commonParamsDictionary['anteproc_h']['stamp']['h0'] = sqrt(0.5)
            commonParamsDictionary['anteproc_h']['stamp']['f0'] = input_params['wave_frequency']
            commonParamsDictionary['anteproc_h']['stamp']['phi0'] = 0
            commonParamsDictionary['anteproc_h']['stamp']['fdot'] = 0
            commonParamsDictionary['anteproc_h']['stamp']['duration'] = wave_duration
            commonParamsDictionary['anteproc_h']['stamp']['tau'] = wave_tau

            commonParamsDictionary['anteproc_l']['stamp']['h0'] = sqrt(0.5)
            commonParamsDictionary['anteproc_l']['stamp']['f0'] = input_params['wave_frequency']
            commonParamsDictionary['anteproc_l']['stamp']['phi0'] = 0
            commonParamsDictionary['anteproc_l']['stamp']['fdot'] = 0
            commonParamsDictionary['anteproc_l']['stamp']['duration'] = wave_duration
            commonParamsDictionary['anteproc_l']['stamp']['tau'] = wave_tau

            
        else:
            for waveform in waveformFileNames:
                commonParamsDictionary["waveform"][waveform] = os.path.join(waveformDirectory, temp_name + waveformFileExtention)
    
    
    if input_params['relative_direction']:
    
        refTime = input_params['triggerTime'] - 2
    
        commonParamsDictionary['grandStochtrack']['useReferenceAntennaFactors'] = True
        commonParamsDictionary['grandStochtrack']['referenceGPSTime'] = refTime
        commonParamsDictionary['anteproc_h']['referenceGPSTime'] = refTime
        commonParamsDictionary['anteproc_l']['referenceGPSTime'] = refTime

        commonParamsDictionary['grandStochtrack']['ra'] = input_params['RA']
        commonParamsDictionary['grandStochtrack']['dec'] = input_params['DEC']
        commonParamsDictionary['anteproc_h']['stamp']['ra'] = input_params['RA']
        commonParamsDictionary['anteproc_h']['stamp']['decl'] = input_params['DEC']
        commonParamsDictionary['anteproc_l']['stamp']['ra'] = input_params['RA']
        commonParamsDictionary['anteproc_l']['stamp']['decl'] = input_params['DEC']

    
    if input_params['constant_f_window']:
        commonParamsDictionary['grandStochtrack']['fmin'] = 40
        commonParamsDictionary['grandStochtrack']['fmax'] = 2500

    if input_params['constant_f_mask']:
        commonParamsDictionary['grandStochtrack']['StampFreqsToRemove'] = input_params['lines_to_cut']
    
    if input_params['remove_cluster']:
        commonParamsDictionary['grandStochtrack']['maskCluster'] = True
    
    if input_params['include_variations']:
        commonParamsDictionary['grandStochtrack']['maskCluster'] = True
    
    if input_params['injection_random_start_time']:
        commonParamsDictionary['varying_injection_start'] = [-2, 1604 - wave_duration - 2]
    
                
    # build dag directory, support directories
    dagDir = create_dir(baseDir + "/dag")
    dagLogDir = create_dir(dagDir + "/dagLogs")
    logDir = create_dir(dagLogDir + "/logs")
    
    #this for loop builds each individual job
    current_job = 0
    stochtrackParamsList = []
    H1AnteprocJobNums = set()
    L1AnteprocJobNums = set()
    for [jobIndex1, jobIndex2] in sortedJobPairs:#[jobNum1, jobNum2] in sortedJobPairs:
        jobNum1 = jobIndex1 + 1
        jobNum2 = jobIndex2 + 1
        job1StartTime = times[jobIndex1][1]
        job1EndTime = times[jobIndex1][2]
        
        jobDictionary = {'grandStochtrackParams': {'params':deepcopy(commonParamsDictionary['grandStochtrack'])}}
        job_dir = baseDir + "/jobs/job_group_1/job_" + str(current_job + 1)
        jobDictionary["grandStochtrackParams"]["params"]["plotdir"] = job_dir + "/grandStochtrackOutput/plots/"
        jobDictionary["grandStochtrackParams"]["params"]["outputfilename"] = job_dir + "/grandStochtrackOutput/map"
        jobDictionary["grandStochtrackParams"]["params"]["ofile"] = job_dir + "/grandStochtrackOutput/bknd"
        jobDictionary["grandStochtrackParams"]["params"]["jobsFile"] = newJobPath
        jobDictionary['grandStochtrackParams']['params']['anteproc']['inmats1'] = anteproc_dir + "/H-H1_map"
        jobDictionary['grandStochtrackParams']['params']['anteproc']['inmats2'] = anteproc_dir + "/L-L1_map"
        jobDictionary['grandStochtrackParams']['params']['anteproc']["jobfile"] = newAdjustedJobPath
        
        jobDir = create_dir(jobsBaseDir + "/" + "job_group_" + str(job_group) + "/job_" + str(i + 1))
        jobDictionary["jobDir"] = jobDir
        jobDictionary["stochtrackInputDir"] = create_dir(jobDir + "/grandStochtrackInput")
        jobDictionary["grandstochtrackOutputDir"] = create_dir(jobDir + "/grandStochtrackOutput")
        jobDictionary["plotDir"] = create_dir(jobDir + "/grandStochtrackOutput" + "/plots")
        
        if "injection_tags" in jobDictionary:
            jobDictionary['grandStochtrackParams']['params']['anteproc']['inmats1'] += "_" + jobDictionary["injection_tags"]
            jobDictionary['grandStochtrackParams']['params']['anteproc']['inmats2'] += "_" + jobDictionary["injection_tags"]
        if input_params['long_pixel'] or input_params['burstegard']:
            job1_hstart = job1StartTime + (9-1)*4/2+2
        else:
            job1_hstart = job1StartTime + (9-1)/2+2
            
        job1_hstop = job1_hstart + 1602 if input_params['long_pixel'] or input_params['burstegard'] else job_hstart + 400
    
        if input_params['injection_bool'] and not input_params['relative_direction']:
            jobDictionary["preproc"]["stamp"]["ra"] = input_params['RA']
    
        if not input_params['relative_direction']:
            jobDictionary["grandStochtrackParams"]["params"]["ra"] = input_params['RA']

        if input_params['remove_cluster']:
            jobDictionary["grandStochtrackParams"]["params"]["clusterFile"] = source_file_dict[jobIndex1][jobIndex2]
    
        jobDictionary["preprocJobs"] = jobNum1
    
        if input_params['anteproc_bool']:
            jobDictionary["grandStochtrackParams"]["params"]["anteproc"]["jobNum1"] = jobNum1
            jobDictionary["grandStochtrackParams"]["params"]["anteproc"]["jobNum2"] = jobNum2
    
        else:
            jobDictionary["preproc"]["doShift1"] = 0
            jobDictionary["preproc"]["ShiftTime1"] = 0
            jobDictionary["preproc"]["doShift2"] = 1
            jobDictionary["preproc"]["ShiftTime2"] = base_shift + timeShift - 1

    
        if input_params['relative_direction']:
            if jobIndex1 == 33:
                jobDictionary["grandStochtrackParams"]["params"]["useReferenceAntennaFactors"] = False


        if input_params['injection_bool'] and not input_params['onTheFly']:
            for temp_waveform in waveformFileNames:
                jobDictionary["injection_tag"] = temp_waveform
                stochtrackParamsList.append(deepcopy(jobDictionary))
                stochtrackParamsList[current_job]["grandStochtrackParams"]["params"]['job_group']=  job_group
                stochtrackParamsList[current_job]["grandStochtrackParams"]["params"]['jobNumber'] = current_job
                H1AnteprocJobNums.add(jobNum1)
                L1AnteprocJobNums.add(jobNum2)

                current_job += 1
        else:    
            stochtrackParamsList.append(deepcopy(jobDictionary))
            stochtrackParamsList[current_job]["grandStochtrackParams"]["params"]['job_group'] = job_group
            stochtrackParamsList[current_job]["grandStochtrackParams"]["params"]['jobNumber'] = current_job

            H1AnteprocJobNums.add(jobNum1)
            L1AnteprocJobNums.add(jobNum2)
            current_job +=1
            

    ###################################################################################
    ###################################################################################
    ###################################################################################
    #########
    ######### Now moving on to the pyCondorSTAMPanteproc_v4 - like part
    #########
    ###################################################################################
    ###################################################################################
    ###################################################################################    

    # paths to executables
    STAMP_setup_script = os.path.join(input_params['STAMP2_installation_dir'], "test/stamp_setup.sh")    
    anteprocExecutable = os.path.join(input_params['STAMP2_installation_dir'], "compilationScripts/anteproc")
    grandStochtrackExecutable = os.path.join(input_params['STAMP2_installation_dir'], "compilationScripts/grand_stochtrack")
    grandStochtrackExecutableNoPlots = os.path.join(input_params['STAMP2_installation_dir'], "compilationScripts/grand_stochtrack_nojvm")

    
    print("Creating ajusted job file")
    with open(input_params['jobFile']) as h:
        jobData = [[int(x) for x in line.split()] for line in h]
    adjustedJobData = [[x[0], x[1] + input_params['job_start_shift'], x[1] + input_params['job_start_shift'] + input_params['job_duration'], input_params['job_duration']] for x in jobData]
    adjustedJobText = "\n".join(" ".join(str(x) for x in line) for line in adjustedJobData)
    with open(newAdjustedJobPath, "w") as h:   
        print >> h, adjustedJobText 
    
    # create cachefile directory
    print("Creating cache directory")
    commonParamsDictionary['anteproc_h']["outputfiledir"] = anteproc_dir + "/"
    commonParamsDictionary['anteproc_l']["outputfiledir"] = anteproc_dir + "/"  
    if not input_params['simulated']:
        cacheDir = create_dir(baseDir + "/cache_files") + "/"
        fakeCacheDir = None
        commonParamsDictionary['anteproc_h']["gpsTimesPath1"] = cacheDir
        commonParamsDictionary['anteproc_h']["frameCachePath1"] = cacheDir
        commonParamsDictionary['anteproc_l']["gpsTimesPath1"] = cacheDir
        commonParamsDictionary['anteproc_l']["frameCachePath1"] = cacheDir        
    else:
        fakeCacheDir = create_dir(baseDir + "/fake_cache_files") + "/"
        cacheDir = None
        commonParamsDictionary['anteproc_h']["gpsTimesPath1"] = fakeCacheDir
        commonParamsDictionary['anteproc_h']["frameCachePath1"] = fakeCacheDir
        commonParamsDictionary['anteproc_l']["gpsTimesPath1"] = fakeCacheDir
        commonParamsDictionary['anteproc_l']["frameCachePath1"] = fakeCacheDir
    

    
    #new loop to make anteproc files
    print("Creating anteproc directory and input files")

    for jobNum in H1AnteprocJobNums:
        
        temp_anteproc_h_dict = deepcopy(commonParamsDictionary['anteproc_h'])
        temp_anteproc_h_dict = deepupdate(temp_anteproc_h_dict, anteprocHParamsList[jobNum - 1])
        for key, val in temp_anteproc_h_dict['stamp'].iteritems():
            temp_anteproc_h_dict['stamp.' + key] = val
        temp_anteproc_h_dict.pop('stamp')
        anteproc_dict = deepcopy(commonParamsDictionary['anteproc'])
        anteproc_dict.update(temp_anteproc_h_dict)
        anteproc_dict['ifo1'] = "H1"
        anteproc_dict['frameType1'] = "H1_" + input_params['frame_type']
        anteproc_dict['ASQchannel1'] = input_params['channel']
        
        with open(anteproc_dir + "/H1-anteproc_params_" + str(jobNum) + ".txt", 'w') as h:
            print >> h, "\n".join([key + ' ' + str(val).lower() if not isinstance(val, basestring) else key + ' ' + val for key, val in anteproc_dict.iteritems()])
            
    for jobNum in L1AnteprocJobNums:
        
        temp_anteproc_l_dict = deepcopy(commonParamsDictionary['anteproc_l'])
        temp_anteproc_l_dict = deepupdate(temp_anteproc_l_dict, anteprocLParamsList[jobNum - 1])
        for key, val in temp_anteproc_l_dict['stamp'].iteritems():
            temp_anteproc_l_dict['stamp.' + key] = val
        temp_anteproc_l_dict.pop('stamp')
        
        anteproc_dict = deepcopy(commonParamsDictionary['anteproc'])
        anteproc_dict.update(temp_anteproc_l_dict)
        anteproc_dict['ifo1'] = "L1"
        anteproc_dict['frameType1'] = "L1_" + input_params['frame_type']
        anteproc_dict['ASQchannel1'] = input_params['channel']
        
        with open(anteproc_dir + "/L1-anteproc_params_" + str(jobNum) + ".txt", 'w') as h:
            print >> h, "\n".join([key + ' ' + str(val).lower() if not isinstance(val, basestring) else key + ' ' + val for key, val in anteproc_dict.iteritems()])        

    
    
    # create grandstochtrack execution script
    
    print("Creating shell scripts")
    grandStochtrack_script_file = dagDir + "/grand_stochtrack.sh"
    if commonParamsDictionary['grandStochtrack']['savePlots']:
        write_grandstochtrack_bash_script(grandStochtrack_script_file, grandStochtrackExecutable, STAMP_setup_script, input_params['matlab_setup_script'])
    else:
        write_grandstochtrack_bash_script(grandStochtrack_script_file, grandStochtrackExecutableNoPlots, STAMP_setup_script, input_params['matlab_setup_script'])
    os.chmod(grandStochtrack_script_file, 0o744)
    
    #matlabMatrixExtractionExectuable_script_file = dagDir + "/matlab_matrix_extraction.sh"
    #write_grandstochtrack_bash_script(matlabMatrixExtractionExectuable_script_file, input_params['matlabMatrixExtractionExectuable'], STAMP_setup_script)
    #os.chmod(matlabMatrixExtractionExectuable_script_file, 0o744)
    
    anteprocExecutable_script_file = dagDir + "/anteproc.sh"
    write_anteproc_bash_script(anteprocExecutable_script_file, anteprocExecutable, STAMP_setup_script)
    os.chmod(anteprocExecutable_script_file, 0o744)
    
    webPageSH = os.path.join(webpage.load_pycondorstamp_dir(), 'webdisplay/resultsJSON.py') #this one has already been created
    
    # If relative injection value set, override any existing injection time with calculated relative injection time.
    
    # find frame files
    for tempJob in set(tempNumbersH):
        print("Finding frames for job " + str(tempJob) + " for H1")
        if not input_params['simulated']:
            temp_frames = create_frame_file_list("H1_" + input_params['frame_type'], str(times[tempJob][1] - 2), str(times[tempJob][1] + 1602), "H")
            archived_H = create_cache_and_time_file(temp_frames, "H",tempJob+1, cacheDir)
        else:
            create_fake_cache_and_time_file(str(times[tempJob][1] - 2), str(times[tempJob][1] + 1602), "H", tempJob, fakeCacheDir)
    for tempJob in set(tempNumbersL):
        print("Finding frames for job " + str(tempJob) + " for L1")
        if not input_params['simulated']:
            temp_frames = create_frame_file_list("L1_" + input_params['frame_type'], str(times[tempJob][1] - 2), str(times[tempJob][1] + 1602), "L")
            archived_L = create_cache_and_time_file(temp_frames, "L",tempJob+1, cacheDir)
        else:
            create_fake_cache_and_time_file(str(times[tempJob][1] - 2), str(times[tempJob][1] + 1602), "L", tempJob, fakeCacheDir)
            
    if archived_H or archived_L:
        print("WARNING: some needed frames have been archived and will take longer to read off of tape")
        print(archived_H)
        print(archived_L)
        print("WARNING: these jobs will take a long time")
            
    for job in stochtrackParamsList:
        job['grandStochtrackParams'] = recursive_ints_to_floats(job['grandStochtrackParams'])
        sio.savemat(job['stochtrackInputDir'] + "/params.mat", job['grandStochtrackParams'])
        
    
    doGPU = input_params["doGPU"]
    if doGPU and not input_params['burstegard']:
        extract_from_gpu = True
    else:
        extract_from_gpu = False

    print("Creating dag and sub files")
    
    anteprocSub = write_anteproc_sub_file(input_params['anteprocMemory'], anteprocExecutable_script_file, dagDir, input_params['accountingGroup'])
    stochtrackSub = write_stochtrack_sub_file(input_params['grandStochtrackMemory'], grandStochtrack_script_file, dagDir, input_params['accountingGroup'], input_params['doGPU'], input_params['numCPU'])
    webDisplaySub = write_webpage_sub_file(webPageSH, dagDir, input_params['accountingGroup'])
    write_dag(dagDir, anteproc_dir, newJobPath, H1AnteprocJobNums, L1AnteprocJobNums, anteprocSub, stochtrackParamsList, stochtrackSub, input_params['maxJobsAnteproc'], input_params['maxJobsGrandStochtrack'], webDisplaySub, baseDir)
        
    #create summary of parameters
    generate_summary(input_params, baseDir)
    
    webpage.load_conf_cp_webfiles(baseDir)
    
    if options.verbose:
        import pprint
        pprint.pprint(commonParamsDictionary, open(os.path.join(baseDir, "commonParams_dict.txt"), "w"))
        pprint.pprint(anteprocHParamsList, open(os.path.join(baseDir, "anteprocHParams_list.txt"), "w"))
        pprint.pprint(anteprocLParamsList, open(os.path.join(baseDir, "anteprocLParams_list.txt"), "w"))
        pprint.pprint(stochtrackParamsList, open(os.path.join(baseDir, "stochtrackParams_list.txt"), "w"))

if __name__ == "__main__":
    main()
