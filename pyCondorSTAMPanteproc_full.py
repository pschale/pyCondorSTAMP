#pyCondorSTAMPanteproc_full.py
from __future__ import division

from numpy import argsort, sqrt, arccos, pi, array, object
import scipy.io as sio
import random
import json
import os
from optparse import OptionParser
from copy import deepcopy
from shutil import copy
import ConfigParser

from webdisplay import webpage
from pyCondorSTAMPLib_v2 import *


def main():
    parser = OptionParser()
    
    parser.add_option("-c", "--config-file", dest = "configFilePath",
                      help = "Path to params file")
    parser.add_option("-n", "--name", dest="dirName",
                        default="stamp_analysis_anteproc",
                        help="Name of analysis directory, date will be added")
    parser.add_option("-v", "--verbose", 
                        action = "store_true", dest = "verbose", 
                        default = False,
                        help = "prints out dictionaries to file at end")
    parser.add_option("-p", "--preserve", action = "store_true", 
                        dest = "preserve", default = False,
                        help = "If active, errors will not trigger \
                        deletion of generated files.")
    parser.add_option("-s", "--submit_dag", action = "store_true", 
                        dest = "submitDag", default = False,
                        help = "Submits dag automatically")
    
    (options, args) = parser.parse_args()
    
    configFilePath = options.configFilePath
    
    if configFilePath[0] == ".":
        configFilePath = os.getcwd() + configFilePath[1:]
    elif configFilePath[0] == "~":
        configFilePath = os.path.expanduser('~') + configFilePath[1:]
    elif not configFilePath[0] == "/":
        configFilePath = os.getcwd() + "/" + configFilePath[0:]
        
    configs = ConfigParser.ConfigParser()
    configs.read(configFilePath)
    
    searchType = configs.get('search', 'searchType')
    onsource = searchType == "onsource"
    pseudo_onsource = searchType == "pseudo_onsource"
    upper_limits = searchType == "upper_limits"
    offsource = searchType == "offsource"
    injectionRecovery = searchType == "injectionRecovery"
    
    if (configs.getboolean('injection', 'doInjections') and 
            not configs.getboolean('injection', 'onTheFly') and 
            not os.isfile(injection_file)):
        pyCondorSTAMPanteprocError("Injection file does not exist.  \
            Make onTheFly true if you do not wish to specify injection file")      
        
    if configs.getboolean('injection', 'longTau'):
        wave_tau = 400
    else:
        wave_tau = 150
        
    wave_duration = wave_tau*3
    
    #this might need adjustment for particular triggers
    if configs.getboolean('injection', 'polarizationSmallerResponse'): 
        wave_iota = 120
        wave_psi = 45
    else:
        wave_iota = 0
        wave_psi = 0
    
    if onsource:
        configs.set('injection', 'doInjections', 'False')
        configs.set('search', 'simulated', 'False')
        configs.set('search', 'relativeDirection', 'False')
        
    if pseudo_onsource:
        configs.set('search', 'relativeDirection', 'False')
    
    if not configs.getboolean('injection', 'doInjections'):
        configs.set('injection', 'onTheFly', 'False')
        configs.set('injection', 'polarizationSmallerResponse', 'False')
        configs.set('injection', 'injectionRandomStartTime', 'False')
        configs.set('injection', 'includeVariations', 'False')
        if injectionRecovery:
            raise TypeError("Error: injection recovery requires injections")
        
    if configs.getboolean('singletrack', 'singletrackBool'):
        configs.set('condor', 'numCPU', '1')
        configs.set('condor', 'doGPU', 'False')
        
    if injectionRecovery and (configs.getint('search', 'T') 
            * configs.getint('search', 'F') > 1000000):
        if options.submitDag:
            print("WARNING - This is configured in injection recovery mode \
                    and set to run more than 1,000,000 clusters.  This is \
                    likely a waste of computation time.  Auto-submit dag \
                    has been disabled")
        else:
            print("WARNING - This is configured in injection recovery mode \
                    and set to run more than 1,000,000 clusters.  This is \
                    likely a waste of computation time.")
    
    jobPath = make_file_path_absolute(configs.get('trigger', 'jobFile'))
    configPath = os.path.join(configs.get('dirs', 'outputDir'), 
                              "config_file.txt")
    outputDir = make_file_path_absolute(configs.get('dirs', 'outputDir'))
    outputDir = os.path.join(outputDir, options.dirName)
        
    baseDir = dated_dir(outputDir)
    preserve = options.preserve
    
    supportDir = create_dir(baseDir + "/input_files")
    jobsBaseDir = create_dir(baseDir + "/jobs")
    anteproc_dir = create_dir(baseDir + "/anteproc_data")

    # copy input files to this directory
    copy_input_file(configFilePath, supportDir)
    newJobPath = copy_input_file(jobPath, supportDir)
    if configs.getboolean('search', 'simulated'):
        lho_file = configs.get('search', 'lhoWelchPsd')
        llo_file = configs.get('search', 'lloWelchPsd')
        copy(lho_file, os.path.join(supportDir, "H1_PSD:" + os.path.split(lho_file)[-1]))
        copy(llo_file, os.path.join(supportDir, "L1_PSD:" + os.path.split(llo_file)[-1]))
    
    #adjust job file
    jobFileName = jobPath[len(jobPath)-jobPath[::-1].index('/')::]
    adjustedJobFileName = (jobFileName[:jobFileName.index(".txt")] 
                            + "_postprocessing" 
                            + jobFileName[jobFileName.index(".txt"):])
    newAdjustedJobPath = os.path.join(supportDir, adjustedJobFileName)
    
    CPDict = getCommonParams(configs)
    
    times = [[int(y) for y in x] for x in readFile(jobPath)]

        
        
    # This ensures there's enough data to be able to estimate the background
    # 2+ (buffer seconds),     
    # 9: NumberofSegmentsPerInterval (NSPI), 
    # -1: take out the pixel that's being analyzed 
    # /2: to get one side of those
    # *4: pixel duration
    # +2: window started 2 seconds before trigger time
    if (configs.getboolean('search', 'longPixel') 
            or configs.getboolean('search', 'burstegard')):
        triggerJobStart = (configs.getfloat('trigger', 'triggerTime') 
                            - (2 + (9-1)*4/2 + 2))
    else:
        triggerJobStart = (configs.getfloat('trigger', 'triggerTime') 
                            - (2 + (9-1)/2 + 2))
    
    # analysis starts 2 pixels before trigger time
    trigger_hStart = configs.getfloat('trigger', 'triggerTime') - 2
        
    # Next section finds the job number PAIRS run by stochtrack
    # and job NUMBERS run by anteproc
    
    if upper_limits:
    
        with open(configs.get('upperlimits', 'offSourceJsonPath')) as infile:
            temp_job_data = json.load(infile)
        sortedJobPairs = [x[1:3] for x in temp_job_data if x[1:3] != [34, 34]]
        sortedJobPairs = [[x-1 for x in y] for y in sortedJobPairs] # job num
                                                                # to job index
        source_file_dict = {}
    
        for num in range(len(sortedJobPairs)):
    
            if sortedJobPairs[num][0] not in source_file_dict:
                source_file_dict[sortedJobPairs[num][0]] = {}
                
            if sortedJobPairs[num][1] in \
                        source_file_dict[sortedJobPairs[num][0]]:
                print("Warning, multiple copies of job pair exist.")
                print(sortedJobPairs[num])
            elif sortedJobPairs[num][0] == 33 or sortedJobPairs[num][1] == 33:
                print("Warning, on-source and off-source jobs possibly mixed.")
                print(sortedJobPairs[num])
            else:
                source_file_dict[sortedJobPairs[num][0]] \
                                [sortedJobPairs[num][1]] = temp_job_data[num] \
                                                                        [-1]
        # add on-source jobs and path, it's job number 34, and index number 33
        sortedJobPairs = [[33,33]] + sortedJobPairs
        source_file_dict[33] = {}
        source_file_dict[33][33] = configs.get('upperlimits', 
                                               'onSourceJsonPath')
        if configs.getboolean('upperlimits', 'removeCluster'):
            jobDictionary["grandStochtrackParams"] \
                         ["params"] \
                         ["clusterFile"] = source_file_dict[jobIndex1] \
                                                           [jobIndex2]
        #cut down to max number of jobs (if needed)
        if len(sortedJobPairs) > configs.getint('upperlimits', 
                                                'jobSubsetLimit'):
            sortedJobPairs = sortedJobPairs[:configs.getint(
                                            'upperlimits', 'jobSubsetLimit')]
            
    elif onsource:
        sortedJobPairs = [[0,0]]
    
    elif pseudo_onsource:
        jobIndices1 = [index for index, val in enumerate(times)
                            if triggerJobStart - val[1] >= 3600]
        jobIndices2 = [index for index, val in enumerate(times) 
                            if val[1] - triggerJobStart >= 3600]
        jobIndexList1 = random.sample(
                            jobIndices1, 
                            int(configs.getint('search', maxNumJobPairs)/2))
        jobIndexList2 = random.sample(jobIndices2, 
                            int(configs.getint('search', maxNumJobPairs)/2))
        sortedJobPairs = ([
                          [x,x] for x in jobIndexList1]
                          + [[x,x] for x in jobIndexList2
                         ])
    
    elif offsource or injectionRecovery:
        deltaTotal = []
        jobPairs = []
        for index1, job1 in enumerate(times):
            for index2, job2 in enumerate(times):
                if index1 != index2:
                    deltaTotal += [abs(triggerJobStart - job1[1])
                                    + abs(triggerJobStart - job2[1])]
                    jobPairs += [[index1, index2]]
        sortedIndices = argsort(deltaTotal)[:configs.getint('search', 
                                                            'maxNumJobPairs')]
        sortedJobPairs = [jobPairs[x] for x in sortedIndices]
   
    else:
        print("Error: need to define search type correctly")
        raise
        
    #These are the job indices run by anteproc 
    tempNumbersH = list(set([x[0] for x in sortedJobPairs])) #job indices
    tempNumbersL = list(set([x[1] for x in sortedJobPairs])) #job indices
    
    if configs.getboolean('variations', 'doVariations'):
        if configs.get('variations', 'distribution') == 'logSqrt':
            m = ((configs.getfloat('variations', 'maxval')
                            /configs.getfloat('variations', 'minval'))
                            **(1 / (CPDict['numJobGroups']-1)))
            varyVals = [configs.getfloat('variations', 'minval') * (m**i) 
                            for i in range(0, CPDict['numJobGroups'])]
        elif configs.get('variations', 'distribution') == 'linear':
            varyVals = [((configs.getfloat('variations', 'maxval')
                            - configs.getfloat('variations', 'minval'))
                            / (CPDict['numJobGroups']-1))
                            * i for i in range(0, CPDict['numJobGroups'])]
            varyVals = [i + configs.getfloat('variations', 'minval')
                            for i in varyVals]
        else:
            raise ValueError("Must choose linear or logSqrt for distribution")
    
    # Now build the job-specific parameters for anteproc
    # only needed for injections
    anteprocHParamsList = [[{'stamp': {}} for i in 
                                range(0, max(tempNumbersH) + 1)]
                                for j in range(1, CPDict['numJobGroups'] + 1)]
    anteprocLParamsList = [[{'stamp': {}} for i in 
                                range(0, max(tempNumbersL) + 1)]
                                for j in range(1, CPDict['numJobGroups'] + 1)]
    if configs.getboolean('injection', 'doInjections'):


        for jobGroup in range(1, CPDict['numJobGroups'] + 1):
        
        
            for H1_job_index in tempNumbersH:
                tempName1 = anteprocHParamsList[jobGroup - 1][H1_job_index]
                H1_job = H1_job_index + 1
                job1StartTime = times[H1_job_index][1]
                tempName1['outputfilename'] = "map_g" + str(jobGroup)

    
                if (configs.getboolean('search', 'longPixel') or 
                            configs.getboolean('search', 'burstegard')):
                    job1_hstart = job1StartTime + (9-1)*4/2+2
                else:
                    job1_hstart = job1StartTime + (9-1)/2+2
            
                if (configs.getboolean('search', 'longPixel') or 
                        configs.getboolean('search', 'burstegard')):
                    job1_hstop = job1_hstart + 1602
                else:
                    job1_hstop = job1_hstart + 400

                if not configs.getboolean('search', 'relativeDirection'):
                    tempName1['stamp'] \
                             ['ra'] = configs.getfloat('trigger', 'RA')
                    tempName1['stamp'] \
                             ['decl'] = configs.getfloat('trigger', 'DEC')

                if configs.has_option('injection', 'iota'):
                    tempName1['stamp']['iota'] = configs.get('injection', 
                                                                'iota')
                if configs.has_option('injection', 'psi'):
                    tempName1['stamp']['psi'] = configs.get('injection', 
                                                                'psi')

                if H1_job == 34:
                    anteprocHParamsList[jobGroup - 1] \
                                       [33] \
                                       ['useReferenceAntennaFactors'] = False

                else:
                    tempName1['useReferenceAntennaFactors'] = True

                if configs.getboolean('injection', 'onTheFly'):
                    tempName1['stamp']['start'] = job1_hstart+2  

                else:
                    tempName1['stamp']['startGPS'] = job1_hstart+2
                
                if (configs.getboolean('variations', 'doVariations') and 
                        configs.get('variations', 'paramCat') == 'anteproc'):
                    if configs.get('variations', 'paramName') == 'stamp.alpha':
                        tempName1['stamp']['alpha'] = varyVals[jobGroup - 1]
                    elif configs.get('variations', 'paramName') == 'stamp.iota':
                        tempName1['stamp']['iota'] = varyVals[jobGroup - 1]
                    elif configs.get('variations', 'paramName') == 'stamp.psi':
                        tempName1['stamp']['psi'] = varyVals[jobGroup - 1]
                    elif configs.get('variations', 'paramName') == 'stamp.start':
                        tempName1['stamp']['start'] += varyVals[jobGroup - 1]
                    else:
                        raise ValueError("Only variations in stamp.alpha," + \
                                " iota, psi, and start are supported at this time")
                


            for L1_job_index in tempNumbersL:
                tempName2 = anteprocLParamsList[jobGroup - 1][L1_job_index]
                L1_job = L1_job_index + 1
                job1StartTime = times[L1_job_index][1]
                tempName2['outputfilename'] = "map_g" + str(jobGroup)
    
                if (configs.getboolean('search', 'longPixel') or 
                        configs.getboolean('search', 'burstegard')):
                    job1_hstart = job1StartTime + (9-1)*4/2+2
                else:
                    job1_hstart = job1StartTime + (9-1)/2+2
            
                if (configs.getboolean('search', 'longPixel') or 
                        configs.getboolean('search', 'burstegard')):
                    job1_hstop = job1_hstart + 1602
                else:
                    job1_hstop = job1_hstart + 400
        
                if not configs.getboolean('search', 'relativeDirection'):
                    tempName2['stamp'] \
                             ['ra'] = configs.getfloat('trigger', 'RA')
                    tempName2['stamp'] \
                             ['decl'] = configs.getfloat('trigger', 'DEC')

                if configs.has_option('injection', 'iota'):
                    tempName2['stamp']['iota'] = configs.get('injection', 
                                                                'iota')
                if configs.has_option('injection', 'psi'):
                    tempName2['stamp']['psi'] = configs.get('injection', 
                                                                'psi')
                if L1_job == 34:
                    anteprocLParamsList[jobGroup - 1] \
                                       [33] \
                                       ['useReferenceAntennaFactors'] = False

                else:
                    tempName2['useReferenceAntennaFactors'] = True

                if configs.getboolean('injection', 'onTheFly'):
                    tempName2['stamp']['start'] = job1_hstart+2
                else:
                    tempName2['stamp']['startGPS'] = job1_hstart+2
                    
                if (configs.getboolean('variations', 'doVariations') and 
                        configs.get('variations', 'paramCat') == 'anteproc'):
                    if configs.get('variations', 'paramName') == 'stamp.alpha':
                        tempName2['stamp']['alpha'] = varyVals[jobGroup - 1]
                    elif configs.get('variations', 'paramName') == 'stamp.iota':
                        tempName2['stamp']['iota'] = varyVals[jobGroup - 1]
                    elif configs.get('variations', 'paramName') == 'stamp.psi':
                        tempName2['stamp']['psi'] = varyVals[jobGroup - 1]
                    elif configs.get('variations', 'paramName') == 'stamp.start':
                        tempName2['stamp']['start'] += varyVals[jobGroup - 1]
                    else:
                        raise ValueError("Only variations in stamp.alpha," + \
                                " iota, psi, and start are supported at this time")
    

        if configs.getboolean('injection', 'onTheFly'):
            # Here we put in parameters for the on-the-fly injection, 
            # including waveform, frequency, amplitude sqrt(2)/2, so that
            # they sum in quadrature to 1
            CPDict['anteproc_h']['stamp']['inj_type'] = "fly"
            CPDict['anteproc_l']['stamp']['inj_type'] = "fly"
            if configs.has_option('injection', 'waveform_name'):
                waveform_name = configs.get('injection', 'waveform_name')
                CPDict['anteproc_h']['stamp']['fly_waveform'] = waveform_name
                CPDict['anteproc_l']['stamp']['fly_waveform'] = waveform_name
            else:
                CPDict['anteproc_h']['stamp']['fly_waveform'] = "half_sg"
                CPDict['anteproc_l']['stamp']['fly_waveform'] = "half_sg"
            

            CPDict['anteproc_h']['stamp']['h0'] = sqrt(0.5)
            CPDict['anteproc_h']['stamp']['f0'] = configs.getfloat(
                                                        'injection', 
                                                        'waveFrequency')
            CPDict['anteproc_h']['stamp']['phi0'] = 0
            CPDict['anteproc_h']['stamp']['fdot'] = 0
            CPDict['anteproc_h']['stamp']['duration'] = wave_duration
            CPDict['anteproc_h']['stamp']['tau'] = wave_tau

            CPDict['anteproc_l']['stamp']['h0'] = sqrt(0.5)
            CPDict['anteproc_l']['stamp']['f0'] = configs.getfloat(
                                                        'injection', 
                                                        'waveFrequency')
            CPDict['anteproc_l']['stamp']['phi0'] = 0
            CPDict['anteproc_l']['stamp']['fdot'] = 0
            CPDict['anteproc_l']['stamp']['duration'] = wave_duration
            CPDict['anteproc_l']['stamp']['tau'] = wave_tau

            
        else:
            for waveform in waveformFileNames:
                CPDict["waveform"][waveform] = os.path.join(
                                        waveformDirectory, 
                                        temp_name + waveformFileExtention)
    
    
    if configs.getboolean('search', 'relativeDirection'):
    
        refTime = configs.getfloat('trigger', 'triggerTime') - 2
    
        CPDict['grandStochtrack']['useReferenceAntennaFactors'] = True
        CPDict['grandStochtrack']['referenceGPSTime'] = refTime
        CPDict['anteproc_h']['referenceGPSTime'] = refTime
        CPDict['anteproc_l']['referenceGPSTime'] = refTime

        CPDict['grandStochtrack']['ra'] = configs.getfloat('trigger', 'RA')
        CPDict['grandStochtrack']['dec'] = configs.getfloat('trigger', 'DEC')
        CPDict['anteproc_h']['stamp']['ra'] = configs.getfloat('trigger', 'RA')
        CPDict['anteproc_l']['stamp']['ra'] = configs.getfloat('trigger', 'RA')        
        CPDict['anteproc_h'] \
              ['stamp'] \
              ['decl'] = configs.getfloat('trigger', 'DEC')
        CPDict['anteproc_l'] \
              ['stamp'] \
              ['decl'] = configs.getfloat('trigger', 'DEC')

    if configs.getboolean('search', 'constantFreqMask'):
        CPDict['grandStochtrack'] \
              ['StampFreqsToRemove'] = json.loads(
                                         configs.get('search', 'linesToCut'))
    
    if configs.getboolean('search', 'maskCluster'):
        CPDict['grandStochtrack']['maskCluster'] = True
        CPDict['grandStochtrack'] \
              ['clusterFile'] = configs.get('search', 'clusterFile')
    
    if configs.getboolean('search', 'constantFreqMask'):
        CPDict['varying_injection_start'] = [-2, 1604 - wave_duration - 2]
    
                
    # build dag directory, support directories
    dagDir = create_dir(baseDir + "/dag")
    dagLogDir = create_dir(dagDir + "/dagLogs")
    logDir = create_dir(dagLogDir + "/logs")
    
    job_group = 1

    stochtrackParamsList = []
    H1AnteprocJobNums = set()
    L1AnteprocJobNums = set()
    for jobGroup in range(1, CPDict['numJobGroups'] + 1):
        #this for loop builds each individual job
        current_job = 0

        for [jobIndex1, jobIndex2] in sortedJobPairs:
            jobNum1 = jobIndex1 + 1
            jobNum2 = jobIndex2 + 1
            job1StartTime = times[jobIndex1][1]
            job1EndTime = times[jobIndex1][2]
        
            jobDictionary = {'grandStochtrackParams': 
                                {'params':deepcopy(CPDict['grandStochtrack'])}}
            jobDir = create_dir(jobsBaseDir + "/" + "job_group_" 
                                + str(jobGroup) + "/job_" 
                                + str(current_job + 1))
            GSParams = jobDictionary["grandStochtrackParams"]["params"]

            GSParams["plotdir"] = jobDir + "/grandStochtrackOutput/plots/"
            GSParams["outputfilename"] = jobDir + "/grandStochtrackOutput/map"
            GSParams["ofile"] = jobDir + "/grandStochtrackOutput/bknd"
            GSParams["jobsFile"] = newJobPath
            GSParams['anteproc']['inmats1'] = (anteproc_dir + "/H-H1_map_g" 
                                                + str(jobGroup))
            GSParams['anteproc']['inmats2'] = (anteproc_dir + "/L-L1_map_g" 
                                                + str(jobGroup))
            GSParams['anteproc']["jobfile"] = newAdjustedJobPath

            jobDictionary["jobDir"] = jobDir
            jobDictionary["stochtrackInputDir"] = create_dir(
                                            jobDir + "/grandStochtrackInput")
            jobDictionary["grandstochtrackOutputDir"] = create_dir(
                                            jobDir + "/grandStochtrackOutput")
            jobDictionary["plotDir"] = create_dir(
                                            jobDir + "/grandStochtrackOutput" 
                                            + "/plots")
        
            if CPDict['grandStochtrack']['stochtrack']['saveMat']:
                GSParams['stochtrack']['matfile'] = jobDir + "/snrs.mat"
        
            if "injection_tags" in jobDictionary:
                GSParams['anteproc']['inmats1'] += ("_" 
                                            + jobDictionary["injection_tags"])
                GSParams['anteproc']['inmats2'] += ("_" 
                                            + jobDictionary["injection_tags"])
            if (configs.getboolean('search', 'longPixel') or 
                        configs.getboolean('burstegard')):
                job1_hstart = job1StartTime + (9-1)*4/2+2
            else:
                job1_hstart = job1StartTime + (9-1)/2+2
            
            if (configs.getboolean('search', 'longPixel') or 
                             configs.getboolean('burstegard')):
                job1_hstop = job1_hstart + 1602
            else:
                job1_hstop = job1_hstart + 400        
    
            if (configs.getboolean('injection', 'doInjections') and 
                    not configs.getboolean('search', 'relativeDirection')):
                jobDictionary["preproc"] \
                             ["stamp"] \
                             ["ra"] = configs.getfloat('trigger', 'RA')
    
            if not configs.getboolean('search', 'relativeDirection'):
                GSParams["ra"] = configs.getfloat('trigger', 'RA')
    
            jobDictionary["preprocJobs"] = jobNum1
    
            GSParams["anteproc"]["jobNum1"] = jobNum1
            GSParams["anteproc"]["jobNum2"] = jobNum2
            
            if (configs.getboolean('variations', 'doVariations') and
                    configs.get('variations', 'paramCat') == 'stochtrack'):
                GSParams['stochtrack'][configs.get('variations', 
                                     'paramName')] = varyVals[jobGroup - 1]
                    

    
            if configs.getboolean('search', 'relativeDirection'):
                if jobIndex1 == 33:
                    GSParams["useReferenceAntennaFactors"] = False


            if (configs.getboolean('injection', 'doInjections') and 
                    not configs.getboolean('injection', 'onTheFly')):
                    
                for temp_waveform in waveformFileNames:
                    jobDictionary["injection_tag"] = temp_waveform
                    GSParams['job_group']=  job_group
                    GSParams['jobNumber'] = current_job
                    stochtrackParamsList.append(deepcopy(jobDictionary))
                    
                    H1AnteprocJobNums.add(jobNum1)
                    L1AnteprocJobNums.add(jobNum2)

                    current_job += 1
            else:    
                GSParams['job_group'] = job_group
                GSParams['jobNumber'] = current_job
                stochtrackParamsList.append(deepcopy(jobDictionary))

                H1AnteprocJobNums.add(jobNum1)
                L1AnteprocJobNums.add(jobNum2)
                current_job +=1
            

    #########################################################################
    #########################################################################
    #########################################################################
    #########
    ######### Now moving on to the pyCondorSTAMPanteproc_v4 - like part
    #########
    #########################################################################
    #########################################################################
    #########################################################################

    # paths to executables
    STAMP_setup_script = os.path.join(
                configs.get('dirs', 'stamp2InstallationDir'), 
                "test/stamp_setup.sh")
    anteprocExecutable = os.path.join(
                configs.get('dirs', 'stamp2InstallationDir'), 
                "compilationScripts/anteproc")
    grandStochtrackExecutable = os.path.join(
                configs.get('dirs', 'stamp2InstallationDir'), 
                "compilationScripts/grand_stochtrack")
    grandStochtrackExecutableNoPlots = os.path.join(
                configs.get('dirs', 'stamp2InstallationDir'), 
                "compilationScripts/grand_stochtrack_nojvm")

    
    print("Creating ajusted job file")
    with open(configs.get('trigger', 'jobFile')) as h:
        jobData = [[int(x) for x in line.split()] for line in h]
    JSS = configs.getint('search', 'jobStartShift')
    JD = configs.getint('search', 'jobDuration')
    adjustedJobData = [[x[0], x[1] + JSS, x[1] + JSS + JD, JD]
                         for x in jobData]
    adjustedJobText = "\n".join(" ".join(str(x) for x in line)
                                 for line in adjustedJobData)
    with open(newAdjustedJobPath, "w") as h:   
        print >> h, adjustedJobText 
    
    # create cachefile directory
    print("Creating cache directory")
    CPDict['anteproc_h']["outputfiledir"] = anteproc_dir + "/"
    CPDict['anteproc_l']["outputfiledir"] = anteproc_dir + "/"  
    if not configs.getboolean('search', 'simulated'):
        cacheDir = create_dir(baseDir + "/cache_files") + "/"
        fakeCacheDir = None
        CPDict['anteproc_h']["gpsTimesPath1"] = cacheDir
        CPDict['anteproc_h']["frameCachePath1"] = cacheDir
        CPDict['anteproc_l']["gpsTimesPath1"] = cacheDir
        CPDict['anteproc_l']["frameCachePath1"] = cacheDir        
    else:
        fakeCacheDir = create_dir(baseDir + "/fake_cache_files") + "/"
        cacheDir = None
        CPDict['anteproc_h']["gpsTimesPath1"] = fakeCacheDir
        CPDict['anteproc_h']["frameCachePath1"] = fakeCacheDir
        CPDict['anteproc_l']["gpsTimesPath1"] = fakeCacheDir
        CPDict['anteproc_l']["frameCachePath1"] = fakeCacheDir
    
    #new loop to make anteproc files
    print("Creating anteproc directory and input files")
    for jobGroup in range(1, CPDict['numJobGroups'] + 1):

        for jobNum in H1AnteprocJobNums:
        
            anteprocJobDict = deepcopy(CPDict['anteproc_h'])
            anteprocJobDict = deepupdate(
                                anteprocJobDict, 
                                anteprocHParamsList[jobGroup - 1][jobNum - 1])
            for key, val in anteprocJobDict['stamp'].iteritems():
                anteprocJobDict['stamp.' + key] = val
            anteproc_dict = deepcopy(CPDict['anteproc'])
            anteprocJobDict.pop('stamp')
            anteproc_dict.update(anteprocJobDict)
            anteproc_dict['ifo1'] = "H1"
            anteproc_dict['frameType1'] = "H1_" + configs.get('search', 
                                                                'frameType')
            anteproc_dict['ASQchannel1'] = configs.get('search', 'channel')
            
            outputFileName = ("H1-anteproc_params_group_"
                              + str(jobGroup) + "_" + str(jobNum) + ".txt")
            with open(anteproc_dir + "/" + outputFileName, 'w') as h:
                print >> h, "\n".join([key + ' ' + repr(val).lower() 
                                        if not isinstance(val, basestring) 
                                        else key + ' ' + val 
                                        for key, val in 
                                        sorted(anteproc_dict.iteritems())])
            
        for jobNum in L1AnteprocJobNums:
        
            anteprocJobDict = deepcopy(CPDict['anteproc_l'])
            anteprocJobDict = deepupdate(
                                anteprocJobDict, 
                                anteprocLParamsList[jobGroup - 1][jobNum - 1])
            for key, val in anteprocJobDict['stamp'].iteritems():
                anteprocJobDict['stamp.' + key] = val
            anteprocJobDict.pop('stamp')
        
            anteproc_dict = deepcopy(CPDict['anteproc'])
            anteproc_dict.update(anteprocJobDict)
            anteproc_dict['ifo1'] = "L1"
            anteproc_dict['frameType1'] = "L1_" + configs.get('search', 
                                                                'frameType')
            anteproc_dict['ASQchannel1'] = configs.get('search', 'channel')
        
            outputFileName = ("L1-anteproc_params_group_"
                              + str(jobGroup) + "_" + str(jobNum) + ".txt")
            with open(anteproc_dir + "/" + outputFileName, 'w') as h:
                print >> h, "\n".join([key + ' ' + repr(val).lower() 
                                        if not isinstance(val, basestring) 
                                        else key + ' ' + val 
                                        for key, val in 
                                        sorted(anteproc_dict.iteritems())])
    
    # create grandstochtrack execution script
    print("Creating shell scripts")
    grandStochtrack_script_file = dagDir + "/grand_stochtrack.sh"
    if CPDict['grandStochtrack']['savePlots']:
        write_grandstochtrack_bash_script(
                        grandStochtrack_script_file, 
                        grandStochtrackExecutable, 
                        STAMP_setup_script, 
                        configs.get('dirs', 'matlabSetupScript'))
    else:
        write_grandstochtrack_bash_script(
                        grandStochtrack_script_file, 
                        grandStochtrackExecutableNoPlots, STAMP_setup_script,
                        configs.get('dirs', 'matlabSetupScript'))
    os.chmod(grandStochtrack_script_file, 0o744)
    
    anteprocExecutable_script_file = dagDir + "/anteproc.sh"
    write_anteproc_bash_script(anteprocExecutable_script_file, 
                               anteprocExecutable, STAMP_setup_script)
    os.chmod(anteprocExecutable_script_file, 0o744)
    
    webPageSH = os.path.join(webpage.load_pycondorstamp_dir(), 
                             'webdisplay/resultsJSON.py') 
        
    # Find frame files
    for tempJob in set(tempNumbersH):
        print("Finding frames for job " + str(tempJob + 1) + " for H1")
        if not configs.getboolean('search', 'simulated'):
            temp_frames = create_frame_file_list("H1_"
                             + configs.get('search', 'frameType'), 
                             str(times[tempJob][1] - 2), 
                             str(times[tempJob][1] + 1602), "H")
            archived_H = create_cache_and_time_file(temp_frames, "H", 
                                                    tempJob+1, cacheDir)
        else:
            create_fake_cache_and_time_file(str(times[tempJob][1] - 2), 
                                            str(times[tempJob][1] + 1602), 
                                            "H", tempJob, fakeCacheDir)
            archived_H = False
    for tempJob in set(tempNumbersL):
        print("Finding frames for job " + str(tempJob + 1) + " for L1")
        if not configs.getboolean('search', 'simulated'):
            temp_frames = create_frame_file_list("L1_"
                             + configs.get('search', 'frameType'), 
                             str(times[tempJob][1] - 2), 
                             str(times[tempJob][1] + 1602), "L")
            archived_L = create_cache_and_time_file(temp_frames, "L", 
                                                    tempJob+1, cacheDir)
        else:
            create_fake_cache_and_time_file(str(times[tempJob][1] - 2), 
                    str(times[tempJob][1] + 1602), "L", tempJob, fakeCacheDir)
            archived_L = False
            
    if archived_H or archived_L:
        print("WARNING: some needed frames have been archived \
                and will take longer to read off of tape")
        print(archived_H)
        print(archived_L)
        print("WARNING: these jobs will take a long time")
            
    for job in stochtrackParamsList:
        job['grandStochtrackParams'] = recursive_ints_to_floats(
                                            job['grandStochtrackParams'])
        sio.savemat(job['stochtrackInputDir'] + "/params.mat", 
                    job['grandStochtrackParams'])
        
    print("Creating dag and sub files")
    
    anteprocSub = write_anteproc_sub_file(
                            configs.getint('condor', 'anteprocMemory'), 
                            anteprocExecutable_script_file, dagDir, 
                            configs.get('condor', 'accountingGroup'))
    stochtrackSub = write_stochtrack_sub_file(
                            configs.getint('condor', 'grandStochtrackMemory'), 
                            grandStochtrack_script_file, dagDir, 
                            configs.get('condor', 'accountingGroup'), 
                            configs.getboolean('condor', 'doGPU'), 
                            configs.getint('condor', 'numCPU'))
    webDisplaySub = write_webpage_sub_file(
                            webPageSH, dagDir, 
                            configs.get('condor', 'accountingGroup'))
    write_dag(dagDir, anteproc_dir, newJobPath, H1AnteprocJobNums, 
              L1AnteprocJobNums, CPDict['numJobGroups'], 
              anteprocSub, stochtrackParamsList, stochtrackSub, 
              configs.getint('condor', 'maxJobsAnteproc'), 
              configs.getint('condor', 'maxJobsGrandStochtrack'), 
              webDisplaySub, baseDir)
        
    generate_summary(configs, baseDir)
    
    webpage.load_conf_cp_webfiles(baseDir)
    
    if options.verbose:
        dict_dir = create_dir(os.path.join(baseDir, "intermediate_dictionaries"))
        import pprint
        pprint.pprint(CPDict, 
                open(os.path.join(dict_dir, "commonParams_dict.txt"), "w"))
        pprint.pprint(anteprocHParamsList, 
                open(os.path.join(dict_dir, "anteprocHParams_list.txt"), "w"))
        pprint.pprint(anteprocLParamsList, 
                open(os.path.join(dict_dir, "anteprocLParams_list.txt"), "w"))
        pprint.pprint(stochtrackParamsList, 
                open(os.path.join(dict_dir, "stochtrackParams_list.txt"), "w"))
    
    if options.submitDag:
        import subprocess
        subprocess.call('condor_submit_dag '
                + os.path.join(baseDir, "dag/stampAnalysis.dag"), shell=True)


if __name__ == "__main__":
    try:
        main()
    
    except:
        import inspect
        lvars = inspect.trace()[1][0].f_locals
        baseDir = lvars['baseDir']
        if not lvars['preserve']:
            print("Error has occurred. Deleting all files that were created.")
            from shutil import rmtree
            rmtree(baseDir)
        else:
            try:
                import pprint
                dict_dir = create_dir(os.path.join(baseDir, "intermediate_dictionaries"))
                pprint.pprint(lvars['CPDict'], 
                    open(os.path.join(dict_dir, "commonParams.txt"), "w"))
                pprint.pprint(lvars['anteprocHParamsList'], 
                    open(os.path.join(dict_dir, "anteprocHParams.txt"), "w"))
                pprint.pprint(lvars['anteprocLParamsList'], 
                    open(os.path.join(dict_dir, "anteprocLParams.txt"), "w"))
                pprint.pprint(lvars['stochtrackParamsList'], 
                    open(os.path.join(dict_dir, "stochtrackParams.txt"), "w"))
                print("printed dictionaries to files")
            except KeyError:
                pass
        
        import traceback, sys
        traceback.print_exc(file=sys.stdout)
