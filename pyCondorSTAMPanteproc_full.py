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
from ConfigParser import ConfigParser

def main():
    parser = OptionParser()
    
    parser.add_option("-c", "--config-file", dest = "configFilePath",
                      help = "Path to params file")
    parser.add_option("-v", "--verbose", 
                        action = "store_true", dest = "verbose", default = False,
                        help = "prints out dictionaries to file at end")
    
    (options, args) = parser.parse_args()
    
    configFilePath = options.configFilePath
    
    if configFilePath[0] == ".":
        configFilePath = os.getcwd() + configFilePath[1:]
    elif configFilePath[0] == "~":
        configFilePath = os.path.expanduser('~') + configFilePath[1:]
    elif not configFilePath[0] == "/":
        configFilePath = os.getcwd() + "/" + configFilePath[0:]
        
    configs = ConfigParser()
    configs.read(configFilePath)
    
    #Following lines DISABLED, dictionary now used due to increased security
    #this loads all of the input parameters into local variables.  It's kind of magic
    #for key, val in input_params.iteritems():
    #    exec(key + '=val')
    searchType = configs.get('search', 'searchType')
    onsource = searchType == "onsource"
    pseudo_onsource = searchType == "pseudo_onsource"
    upper_limits = searchType == "upper_limits"
    offsource = searchType == "offsource"
    
    if configs.getboolean('injection', 'doInjections') and not configs.getboolean('injection', 'onTheFly') and not os.isfile(injection_file):
        pyCondorSTAMPanteprocError("Injection file does not exist.  Make onTheFly true if you do not wish to specify an injection file")        
        
    if configs.getboolean('injection', 'longTau'):
        wave_tau = 400
    else:
        wave_tau = 150
        
    wave_duration = wave_tau*3
    
    if configs.getboolean('injection', 'polarizationSmallerResponse'): #this might need adjustment for particular triggers
        wave_iota = 120
        wave_psi = 45
    else:
        wave_iota = 0
        wave_psi = 0
    
    if onsource:
        configs.set('injection', 'doInjections', 'False')#input_params['injection_bool'] = False
        configs.set('search', 'simulated', 'False')#input_params['simulated'] = False
        configs.set('search', 'relativeDirection', 'False')#input_params['relative_direction'] = False
        
    if pseudo_onsource:
        configs.set('search', 'relativeDirection', 'False')
    
    if not configs.get('injection', 'doInjections'):#input_params['injection_bool']:
        configs.set('injection', 'onTheFly', 'False')#input_params['onTheFly'] = False
        configs.set('injection', 'polarizationSmallerResponse', 'False')#input_params['polarization_smaller_response'] = False
        configs.set('injection', 'injectionRandomStartTime', 'False')#input_params['injection_random_start_time'] = False
        configs.set('injection', 'includeVariations', 'False')#input_params['include_variations'] = False
        
    if configs.getboolean('singletrack', 'singletrackBool'):#input_params['singletrack_bool']:
        configs.set('condor', 'numCPU', '1')#input_params['single_cpu'] = True
        configs.set('condor', 'doGPU', 'False')
    
    jobPath = make_file_path_absolute(configs.get('trigger', 'jobFile'))#input_params['jobFile'])
    configPath = os.path.join(configs.get('dirs', 'outputDir'), "config_file.txt")#input_params['outputDir'], "config_file.txt")
    outputDir = make_file_path_absolute(configs.get('dirs', 'outputDir'))#input_params['outputDir'])
    outputDir = os.path.join(outputDir, "stamp_analysis_anteproc")
        
    baseDir = dated_dir(outputDir)
    directory_with_everything = baseDir
    global directory_with_everything
    
    supportDir = create_dir(baseDir + "/input_files")
    jobsBaseDir = create_dir(baseDir + "/jobs")
    anteproc_dir = create_dir(baseDir + "/anteproc_data")

    # copy input files to this directory
    copy_input_file(configFilePath, supportDir)
    newJobPath = copy_input_file(jobPath, supportDir)
    
    #adjust job file
    jobFileName = jobPath[len(jobPath)-jobPath[::-1].index('/')::]
    adjustedJobFileName = jobFileName[:jobFileName.index(".txt")] + "_postprocessing" + jobFileName[jobFileName.index(".txt"):]
    newAdjustedJobPath = os.path.join(supportDir, adjustedJobFileName)
    
    commonParamsDictionary = getCommonParams(configs)
    
    times = [[int(y) for y in x] for x in readFile(jobPath)]

        
        
    #this ensures there's enough data to be able to estimate the background
    # 9-NumberofSegmentsPerInterval (NSPI), -1 (take out the pixel that's being analyzed), /2 to get one side of those
    # *4 (pixel duration) 2 + (buffer seconds), + 2 (window started 2 seconds before trigger time)
    if configs.getboolean('search', 'longPixel') or configs.getboolean('search', 'burstegard'):#input_params['long_pixel'] or input_params['burstegard']:
        triggerJobStart = configs.getfloat('trigger', 'triggerTime') - (2 + (9-1)*4/2 + 2)#input_params['triggerTime'] - (2 + (9-1)*4/2 + 2)
    else:
        triggerJobStart = configs.getfloat('trigger', 'triggerTime') - (2 + (9-1)/2 + 2)#input_params['triggerTime'] - (2 + (9-1)/2 + 2)
    
    # analysis starts 2 pixels before trigger time
    trigger_hStart = configs.getfloat('trigger', 'triggerTime') - 2#input_params['triggerTime'] - 2
        
    #Next section finds the job number PAIRS run by stochtrack, and job NUMBERS run by anteproc
    
    if upper_limits:
    
        with open(configs.get('upperlimits', 'offSourceJsonPath')) as infile:#open(input_params['off_source_json_path'], 'r') as infile:
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
        source_file_dict[33][33] = configs.get('upperlimits', 'onSourceJsonPath')#input_params['on_source_file_path']
        if configs.getboolean('upperlimits', 'removeCluster'):
            jobDictionary["grandStochtrackParams"]["params"]["clusterFile"] = source_file_dict[jobIndex1][jobIndex2]
        #cut down to max number of jobs (if needed)
        if len(sortedJobPairs) > configs.getint('upperlimits', 'jobSubsetLimit'):#input_params['job_subset_limit']:
            sortedJobPairs = sortedJobPairs[:configs.getint('upperlimits', 'jobSubsetLimit')]#input_params['job_subset_limit']]
            
    elif onsource:
        sortedJobPairs = [[0,0]]
    
    elif pseudo_onsource:
        before_possible_job_indices = [index for index, val in enumerate(times) if triggerJobStart - val[1] >= 3600]
        after_possible_job_indices = [index for index, val in enumerate(times) if val[1] - triggerJobStart >= 3600]
        job_index_list_1 = random.sample(before_possible_job_indices, int(configs.getint('search', maxNumJobPairs)/2))
        job_index_list_2 = random.sample(after_possible_job_indices, int(configs.getint('search', maxNumJobPairs)/2))
        sortedJobPairs = [[x,x] for x in job_index_list_1] + [[x,x] for x in job_index_list_2]
    
    elif offsource:
        deltaTotal = []
        jobPairs = []
        for index1, job1 in enumerate(times):
            for index2, job2 in enumerate(times):
                if index1 != index2:
                    deltaTotal += [abs(triggerJobStart - job1[1]) + abs(triggerJobStart - job2[1])]
                    jobPairs += [[index1, index2]]
        sortedIndices = argsort(deltaTotal)[:configs.getint('search', 'maxNumJobPairs')]#input_params['maxNumJobPairs']]
        sortedJobPairs = [jobPairs[x] for x in sortedIndices]
        
    else:
        print("Error: need to define search type correctly")
        raise
        
    #These are the job indices run by anteproc 
    tempNumbersH = list(set([x[0] for x in sortedJobPairs])) #job indices
    tempNumbersL = list(set([x[1] for x in sortedJobPairs])) #job indices
    
    
    
    #Now build the job-specific parameters for anteproc - only needed for injections
    anteprocHParamsList = [[{'stamp':{}} for i in range(0, max(tempNumbersH) + 1)] for j in range(1, commonParamsDictionary['numJobGroups'] + 1)]
    anteprocLParamsList = [[{'stamp':{}} for i in range(0, max(tempNumbersL) + 1)] for j in range(1, commonParamsDictionary['numJobGroups'] + 1)]
    if configs.getboolean('injection', 'doInjections'):#input_params['injection_bool']:
        if configs.getboolean('injection', 'doVariations'):
            multiplier = (configs.getfloat('variations', 'maxStampAlpha')/configs.getfloat('variations', 'minStampAlpha'))**(1/configs.getfloat('variations', 'numJobGroups'))

        for jobGroup in range(1, commonParamsDictionary['numJobGroups'] + 1):
        
            for H1_job_index in tempNumbersH:
                H1_job = H1_job_index + 1
                job1StartTime = times[H1_job_index][1]
                
                if configs.getboolean('injection', 'doVariations'):
                    anteprocHParamsList[jobGroup][H1_job_index]['stamp.alpha'] = configs.getfloat('variations', 'minStampAlpha') * (1 + jobGroup * multiplier)                
    
                if configs.getboolean('search', 'longPixel') or configs.getboolean('search', 'burstegard'):#input_params['long_pixel'] or input_params['burstegard']:
                    job1_hstart = job1StartTime + (9-1)*4/2+2
                else:
                    job1_hstart = job1StartTime + (9-1)/2+2
            
                #job1_hstop = job1_hstart + 1602 if input_params['long_pixel'] or input_params['burstegard'] else job1_hstart + 400
                job1_hstop = job1_hstart + 1602 if configs.getboolean('search', 'long_pixel') or configs.getboolean('search', 'burstegard') else job1_hstart + 400

                if not configs.getboolean('search', 'relativeDirection'):#input_params['relative_direction']:
                    anteprocHParamsList[jobGroup][H1_job_index]['stamp.ra'] = configs.getfloat('trigger', 'RA')#input_params['RA']
                    anteprocHParamsList[jobGroup][H1_job_index]['stamp.decl'] = configs.getfloat('trigger', 'DEC')#input_params['DEC']

                elif H1_job == 34:
                    anteprocHParamsList[jobGroup][33]['useReferenceAntennaFactors'] = False

                else:
                    anteprocHParamsList[jobGroup][H1_job_index]['useReferenceAntennaFactors'] = True

                if configs.getboolean('injection', 'onTheFly'):##input_params['onTheFly']:
                    anteprocHParamsList[jobGroup][H1_job_index]['stamp.start'] = job1_hstart+2  

                else:
                    anteprocHParamsList[jobGroup][H1_job_index]['stamp.startGPS'] = job1_hstart+2


            for L1_job_index in tempNumbersL:
                L1_job = L1_job_index + 1
                job1StartTime = times[L1_job_index][1]
                
                if configs.getboolean('injection', 'doVariations'):
                    anteprocHParamsList[jobGroup][H1_job_index]['stamp.alpha'] = configs.getfloat('variations', 'minStampAlpha') * (1 + jobGroup * multiplier)   
    
                if configs.getboolean('search', 'longPixel') or configs.getboolean('search', 'burstegard'):#input_params['long_pixel'] or input_params['burstegard']:
                    job1_hstart = job1StartTime + (9-1)*4/2+2
                else:
                    job1_hstart = job1StartTime + (9-1)/2+2
            
                #job1_hstop = job1_hstart + 1602 if input_params['long_pixel'] or input_params['burstegard'] else job1_hstart + 400
                job1_hstop = job1_hstart + 1602 if configs.getboolean('search', 'long_pixel') or configs.getboolean('search', 'burstegard') else job1_hstart + 400
        
                if not configs.getboolean('search', 'relativeDirection'):#input_params['relative_direction']:
                    anteprocLParamsList[jobGroup][L1_job_index]['stamp.ra'] = configs.getfloat('trigger', 'RA')#input_params['RA']
                    anteprocLParamsList[jobGroup][L1_job_index]['stamp.decl'] = configs.getfloat('trigger', 'DEC')#input_params['DEC']

                elif L1_job == 34:
                    anteprocLParamsList[jobGroup][33]['useReferenceAntennaFactors'] = False

                else:
                    anteprocLParamsList[jobGroup][L1_job_index]['useReferenceAntennaFactors'] = True

                if configs.getboolean('injection', 'onTheFly'):#input_params['onTheFly']:
                    anteprocLParamsList[jobGroup][L1_job_index]['stamp.start'] = job1_hstart+2
                else:
                    anteprocLParamsList[jobGroup][L1_job_index]['stamp.startGPS'] = job1_hstart+2
    

        if configs.getboolean('injection', 'onTheFly'):#input_params['onTheFly']:
            #here we put in parameters for the on-the-fly injection, including waveform, frequency, amplitude (sqrt(2)/2, so that
            # they sum in quadrature to 1
            commonParamsDictionary['anteproc_h']['stamp']['inj_type'] = "fly"
            commonParamsDictionary['anteproc_h']['stamp']['fly_waveform'] = "half_sg"
            commonParamsDictionary['anteproc_l']['stamp']['inj_type'] = "fly"
            commonParamsDictionary['anteproc_l']['stamp']['fly_waveform'] = "half_sg"

            commonParamsDictionary['anteproc_h']['stamp']['h0'] = sqrt(0.5)
            commonParamsDictionary['anteproc_h']['stamp']['f0'] = configs.getboolean('injection', 'waveFrequency')#input_params['wave_frequency']
            commonParamsDictionary['anteproc_h']['stamp']['phi0'] = 0
            commonParamsDictionary['anteproc_h']['stamp']['fdot'] = 0
            commonParamsDictionary['anteproc_h']['stamp']['duration'] = wave_duration
            commonParamsDictionary['anteproc_h']['stamp']['tau'] = wave_tau

            commonParamsDictionary['anteproc_l']['stamp']['h0'] = sqrt(0.5)
            commonParamsDictionary['anteproc_l']['stamp']['f0'] = configs.getboolean('injection', 'waveFrequency')#input_params['wave_frequency']
            commonParamsDictionary['anteproc_l']['stamp']['phi0'] = 0
            commonParamsDictionary['anteproc_l']['stamp']['fdot'] = 0
            commonParamsDictionary['anteproc_l']['stamp']['duration'] = wave_duration
            commonParamsDictionary['anteproc_l']['stamp']['tau'] = wave_tau

            
        else:
            for waveform in waveformFileNames:
                commonParamsDictionary["waveform"][waveform] = os.path.join(waveformDirectory, temp_name + waveformFileExtention)
    
    
    if configs.getboolean('search', 'relativeDirection'):#input_params['relative_direction']:
    
        refTime = configs.getfloat('trigger', 'triggerTime') - 2#input_params['triggerTime'] - 2
    
        commonParamsDictionary['grandStochtrack']['useReferenceAntennaFactors'] = True
        commonParamsDictionary['grandStochtrack']['referenceGPSTime'] = refTime
        commonParamsDictionary['anteproc_h']['referenceGPSTime'] = refTime
        commonParamsDictionary['anteproc_l']['referenceGPSTime'] = refTime

        commonParamsDictionary['grandStochtrack']['ra'] = configs.getfloat('trigger', 'RA')#input_params['RA']
        commonParamsDictionary['grandStochtrack']['dec'] = configs.getfloat('trigger', 'DEC')#input_params['DEC']
        commonParamsDictionary['anteproc_h']['stamp']['ra'] = configs.getfloat('trigger', 'RA')#input_params['RA']
        commonParamsDictionary['anteproc_h']['stamp']['decl'] = configs.getfloat('trigger', 'DEC')#input_params['DEC']
        commonParamsDictionary['anteproc_l']['stamp']['ra'] = configs.getfloat('trigger', 'RA')#input_params['RA']
        commonParamsDictionary['anteproc_l']['stamp']['decl'] = configs.getfloat('trigger', 'DEC')#input_params['DEC']

    
    if configs.getboolean('search', 'constantFreqWindow'):#input_params['constant_f_window']:
        commonParamsDictionary['grandStochtrack']['fmin'] = 40
        commonParamsDictionary['grandStochtrack']['fmax'] = 2500

    if configs.getboolean('search', 'constantFreqMask'):#input_params['constant_f_mask']:
        commonParamsDictionary['grandStochtrack']['StampFreqsToRemove'] = json.loads(configs.get('search', 'linesToCut'))#input_params['lines_to_cut']
    
    if configs.getboolean('search', 'maskCluster'):#input_params['remove_cluster']:
        commonParamsDictionary['grandStochtrack']['maskCluster'] = True
        commonParamsDictionary['grandStochtrack']['clusterFile'] = configs.get('search', 'clusterFile')
    
    if configs.getboolean('search', 'constantFreqMask'):#input_params['injection_random_start_time']:
        commonParamsDictionary['varying_injection_start'] = [-2, 1604 - wave_duration - 2]
    
                
    # build dag directory, support directories
    dagDir = create_dir(baseDir + "/dag")
    dagLogDir = create_dir(dagDir + "/dagLogs")
    logDir = create_dir(dagLogDir + "/logs")
    
    job_group = 1

    for jobGroup in range(1, commonParamsDictionary['numJobGroups'] + 1):
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
        
            jobDir = create_dir(jobsBaseDir + "/" + "job_group_" + str(jobGroup) + "/job_" + str(current_job + 1))

            jobDictionary["grandStochtrackParams"]["params"]["plotdir"] = jobDir + "/grandStochtrackOutput/plots/"
            jobDictionary["grandStochtrackParams"]["params"]["outputfilename"] = jobDir + "/grandStochtrackOutput/map"
            jobDictionary["grandStochtrackParams"]["params"]["ofile"] = jobDir + "/grandStochtrackOutput/bknd"
            jobDictionary["grandStochtrackParams"]["params"]["jobsFile"] = newJobPath
            jobDictionary['grandStochtrackParams']['params']['anteproc']['inmats1'] = anteproc_dir + "/H-H1_map_group_" + str(jobGroup)
            jobDictionary['grandStochtrackParams']['params']['anteproc']['inmats2'] = anteproc_dir + "/L-L1_map_group_" + str(jobGroup)
            jobDictionary['grandStochtrackParams']['params']['anteproc']["jobfile"] = newAdjustedJobPath

            jobDictionary["jobDir"] = jobDir
            jobDictionary["stochtrackInputDir"] = create_dir(jobDir + "/grandStochtrackInput")
            jobDictionary["grandstochtrackOutputDir"] = create_dir(jobDir + "/grandStochtrackOutput")
            jobDictionary["plotDir"] = create_dir(jobDir + "/grandStochtrackOutput" + "/plots")
        
            if commonParamsDictionary['grandStochtrack']['stochtrack']['saveMat']:
                commonParamsDictionary['grandStochtrack']['stochtrack']['matfile'] = jobDir + "/snrs.mat"
        
            if "injection_tags" in jobDictionary:
                jobDictionary['grandStochtrackParams']['params']['anteproc']['inmats1'] += "_" + jobDictionary["injection_tags"]
                jobDictionary['grandStochtrackParams']['params']['anteproc']['inmats2'] += "_" + jobDictionary["injection_tags"]
            if configs.getboolean('search', 'longPixel') or configs.getboolean('burstegard'):#input_params['long_pixel'] or input_params['burstegard']:
                job1_hstart = job1StartTime + (9-1)*4/2+2
            else:
                job1_hstart = job1StartTime + (9-1)/2+2
            
            #job1_hstop = job1_hstart + 1602 if input_params['long_pixel'] or input_params['burstegard'] else job_hstart + 400
            job1_hstop = job1_hstart + 1602 if configs.getboolean('search', 'longPixel') or configs.getboolean('burstegard') else job_hstart + 400        
    
            if configs.getboolean('injection', 'doInjections') and not configs.getboolean('search', 'relativeDirection'):#input_params['injection_bool'] and not input_params['relative_direction']:
                jobDictionary["preproc"]["stamp"]["ra"] = configs.getfloat('trigger', 'RA')#input_params['RA']
    
            if not configs.getboolean('search', 'relativeDirection'):#input_params['relative_direction']:
                jobDictionary["grandStochtrackParams"]["params"]["ra"] = configs.getfloat('trigger', 'RA')#input_params['RA']                
    
            jobDictionary["preprocJobs"] = jobNum1
    
            jobDictionary["grandStochtrackParams"]["params"]["anteproc"]["jobNum1"] = jobNum1
            jobDictionary["grandStochtrackParams"]["params"]["anteproc"]["jobNum2"] = jobNum2

    
            if configs.getboolean('search', 'relativeDirection'):#input_params['relative_direction']:
                if jobIndex1 == 33:
                    jobDictionary["grandStochtrackParams"]["params"]["useReferenceAntennaFactors"] = False


            if configs.getboolean('injection', 'doInjections') and not configs.getboolean('injection', 'onTheFly'):#input_params['injection_bool'] and not input_params['onTheFly']:
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
    STAMP_setup_script = os.path.join(configs.get('dirs', 'stamp2InstallationDir'), "test/stamp_setup.sh") #input_params['STAMP2_installation_dir'], "test/stamp_setup.sh")    
    anteprocExecutable = os.path.join(configs.get('dirs', 'stamp2InstallationDir'), "compilationScripts/anteproc")#input_params['STAMP2_installation_dir'], "compilationScripts/anteproc")
    grandStochtrackExecutable = os.path.join(configs.get('dirs', 'stamp2InstallationDir'), "compilationScripts/grand_stochtrack")#input_params['STAMP2_installation_dir'], "compilationScripts/grand_stochtrack")
    grandStochtrackExecutableNoPlots = os.path.join(configs.get('dirs', 'stamp2InstallationDir'), "compilationScripts/grand_stochtrack_nojvm")#input_params['STAMP2_installation_dir'], "compilationScripts/grand_stochtrack_nojvm")

    
    print("Creating ajusted job file")
    with open(configs.get('trigger', 'jobFile')) as h:#input_params['jobFile']) as h:
        jobData = [[int(x) for x in line.split()] for line in h]
    #adjustedJobData = [[x[0], x[1] + input_params['job_start_shift'], x[1] + input_params['job_start_shift'] + input_params['job_duration'], input_params['job_duration']] for x in jobData]
    adjustedJobData = [[x[0], x[1] + configs.getint('search', 'jobStartShift'), x[1] + configs.getint('search', 'jobStartShift') + configs.getint('search', 'jobDuration'), configs.getint('search', 'jobDuration')] for x in jobData]
    adjustedJobText = "\n".join(" ".join(str(x) for x in line) for line in adjustedJobData)
    with open(newAdjustedJobPath, "w") as h:   
        print >> h, adjustedJobText 
    
    # create cachefile directory
    print("Creating cache directory")
    commonParamsDictionary['anteproc_h']["outputfiledir"] = anteproc_dir + "/"
    commonParamsDictionary['anteproc_l']["outputfiledir"] = anteproc_dir + "/"  
    if not configs.getboolean('search', 'simulated'):#input_params['simulated']:
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
    for jobGroup in range(1, commonParamsDictionary['numJobGroups'] + 1):

        for jobNum in H1AnteprocJobNums:
        
            temp_anteproc_h_dict = deepcopy(commonParamsDictionary['anteproc_h'])
            temp_anteproc_h_dict = deepupdate(temp_anteproc_h_dict, anteprocHParamsList[jobGroup][jobNum - 1])
            for key, val in temp_anteproc_h_dict['stamp'].iteritems():
                temp_anteproc_h_dict['stamp.' + key] = val
            temp_anteproc_h_dict.pop('stamp')
            anteproc_dict = deepcopy(commonParamsDictionary['anteproc'])
            anteproc_dict.update(temp_anteproc_h_dict)
            anteproc_dict['ifo1'] = "H1"
            anteproc_dict['frameType1'] = "H1_" + configs.get('search', 'frameType')#input_params['frame_type']
            anteproc_dict['ASQchannel1'] = configs.get('search', 'channel')#input_params['channel']
        
            with open(anteproc_dir + "/H1-anteproc_params_group_" + str(jobGroup) + "_" + str(jobNum) + ".txt", 'w') as h:
                print >> h, "\n".join([key + ' ' + str(val).lower() if not isinstance(val, basestring) else key + ' ' + val for key, val in anteproc_dict.iteritems()])
            
        for jobNum in L1AnteprocJobNums:
        
            temp_anteproc_l_dict = deepcopy(commonParamsDictionary['anteproc_l'])
            temp_anteproc_l_dict = deepupdate(temp_anteproc_l_dict, anteprocLParamsList[jobGroup][jobNum - 1])
            for key, val in temp_anteproc_l_dict['stamp'].iteritems():
                temp_anteproc_l_dict['stamp.' + key] = val
            temp_anteproc_l_dict.pop('stamp')
        
            anteproc_dict = deepcopy(commonParamsDictionary['anteproc'])
            anteproc_dict.update(temp_anteproc_l_dict)
            anteproc_dict['ifo1'] = "L1"
            anteproc_dict['frameType1'] = "L1_" + configs.get('search', 'frameType')#input_params['frame_type']
            anteproc_dict['ASQchannel1'] = configs.get('search', 'channel')#input_params['channel']
        
            with open(anteproc_dir + "/L1-anteproc_params_group_" str(jobGroup) + "_" + str(jobNum) + ".txt", 'w') as h:
                print >> h, "\n".join([key + ' ' + str(val).lower() if not isinstance(val, basestring) else key + ' ' + val for key, val in anteproc_dict.iteritems()])        

    
    
    # create grandstochtrack execution script
    
    print("Creating shell scripts")
    grandStochtrack_script_file = dagDir + "/grand_stochtrack.sh"
    if commonParamsDictionary['grandStochtrack']['savePlots']:
        write_grandstochtrack_bash_script(grandStochtrack_script_file, grandStochtrackExecutable, STAMP_setup_script, configs.get('dirs', 'matlabSetupScript'))#input_params['matlab_setup_script'])
    else:
        write_grandstochtrack_bash_script(grandStochtrack_script_file, grandStochtrackExecutableNoPlots, STAMP_setup_script, configs.get('dirs', 'matlabSetupScript'))#input_params['matlab_setup_script'])
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
        if not configs.getboolean('search', 'simulated'):#input_params['simulated']:
            #temp_frames = create_frame_file_list("H1_" + input_params['frame_type'], str(times[tempJob][1] - 2), str(times[tempJob][1] + 1602), "H")
            temp_frames = create_frame_file_list("H1_" + configs.get('search', 'frameType'), str(times[tempJob][1] - 2), str(times[tempJob][1] + 1602), "H")
            archived_H = create_cache_and_time_file(temp_frames, "H",tempJob+1, cacheDir)
        else:
            create_fake_cache_and_time_file(str(times[tempJob][1] - 2), str(times[tempJob][1] + 1602), "H", tempJob, fakeCacheDir)
    for tempJob in set(tempNumbersL):
        print("Finding frames for job " + str(tempJob) + " for L1")
        if not configs.getboolean('search', 'simulated'):#input_params['simulated']:
            #temp_frames = create_frame_file_list("L1_" + input_params['frame_type'], str(times[tempJob][1] - 2), str(times[tempJob][1] + 1602), "L")
            temp_frames = create_frame_file_list("L1_" + configs.get('search', 'frameType'), str(times[tempJob][1] - 2), str(times[tempJob][1] + 1602), "L")
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
        
    print("Creating dag and sub files")
    
    #anteprocSub = write_anteproc_sub_file(input_params['anteprocMemory'], anteprocExecutable_script_file, dagDir, input_params['accountingGroup'])
    #stochtrackSub = write_stochtrack_sub_file(input_params['grandStochtrackMemory'], grandStochtrack_script_file, dagDir, input_params['accountingGroup'], input_params['doGPU'], input_params['numCPU'])
    #webDisplaySub = write_webpage_sub_file(webPageSH, dagDir, input_params['accountingGroup'])
    #write_dag(dagDir, anteproc_dir, newJobPath, H1AnteprocJobNums, L1AnteprocJobNums, anteprocSub, stochtrackParamsList, stochtrackSub, input_params['maxJobsAnteproc'], input_params['maxJobsGrandStochtrack'], webDisplaySub, baseDir)

    anteprocSub = write_anteproc_sub_file(configs.getint('condor', 'anteprocMemory'), anteprocExecutable_script_file, dagDir, configs.get('condor', 'accountingGroup'))
    stochtrackSub = write_stochtrack_sub_file(configs.getint('condor', 'grandStochtrackMemory'), grandStochtrack_script_file, dagDir, configs.get('condor', 'accountingGroup'), configs.getboolean('condor', 'doGPU'), configs.getint('condor', 'numCPU'))
    webDisplaySub = write_webpage_sub_file(webPageSH, dagDir, configs.get('condor', 'accountingGroup'))
    write_dag(dagDir, anteproc_dir, newJobPath, H1AnteprocJobNums, L1AnteprocJobNums, anteprocSub, stochtrackParamsList, stochtrackSub, configs.getint('condor', 'maxJobsAnteproc'), configs.getint('condor', 'maxJobsGrandStochtrack'), webDisplaySub, baseDir)
        
    #create summary of parameters
    generate_summary(configs, baseDir)
    
    webpage.load_conf_cp_webfiles(baseDir)
    
    if options.verbose:
        import pprint
        pprint.pprint(commonParamsDictionary, open(os.path.join(baseDir, "commonParams_dict.txt"), "w"))
        pprint.pprint(anteprocHParamsList, open(os.path.join(baseDir, "anteprocHParams_list.txt"), "w"))
        pprint.pprint(anteprocLParamsList, open(os.path.join(baseDir, "anteprocLParams_list.txt"), "w"))
        pprint.pprint(stochtrackParamsList, open(os.path.join(baseDir, "stochtrackParams_list.txt"), "w"))

if __name__ == "__main__":
    try:
        main()
    except:
        print("Error has occurred.  Deleting all files that were created.")
        from shutil import rmtree
        rmtree(directory_with_everything)
        from sys import exc_info
        exc_type, exc_obj, exc_tb = sys.exc_info()
        print(repr(exc_type) + repr(exc_obj) + "at line " + repr(exc_tb))
