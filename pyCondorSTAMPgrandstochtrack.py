#pyCondorSTAMPanteproc_full.py
from __future__ import division

from numpy import argsort, sqrt, arccos, pi, array, object, random
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
    
    outputDir = make_file_path_absolute(configs.get('dirs', 'outputDir'))
    outputDir = os.path.join(outputDir, options.dirName)
        
    baseDir = dated_dir(outputDir)
    preserve = options.preserve
    
    searchType = configs.get('search', 'searchType')
    onsource = searchType == "onsource"
    pseudo_onsource = searchType == "pseudo_onsource"
    upper_limits = searchType == "upper_limits"
    offsource = searchType == "offsource"
    injectionRecovery = False

    if not configs.has_option('search', 'useCustomJobPairs'):
        useCustomJobPairs = False
    else:
        useCustomJobPairs = configs.getboolean('search', 'useCustomJobPairs')

    anteproc_h_dir = configs.get('search', 'anteproc_h_dir')
    anteproc_l_dir = configs.get('search', 'anteproc_l_dir')
        
        
    
    
    if onsource:
        configs.set('search', 'simulated', 'False')
        configs.set('search', 'relativeDirection', 'False')
        
    #if pseudo_onsource:
    #    configs.set('search', 'relativeDirection', 'False')
    
    if configs.getboolean('singletrack', 'singletrackBool'):
        configs.set('condor', 'numCPU', '1')
        configs.set('condor', 'doGPU', 'False')
        
    jobPath = make_file_path_absolute(configs.get('trigger', 'jobFile'))
    configPath = os.path.join(configs.get('dirs', 'outputDir'), 
                              "config_file.txt")
    
    supportDir = create_dir(baseDir + "/input_files")
    jobsBaseDir = create_dir(baseDir + "/jobs")

    # copy input files to this directory
    copy_input_file(configFilePath, supportDir)
    newJobPath = copy_input_file(jobPath, supportDir)
    
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
    
    elif pseudo_onsource and not useCustomJobPairs:
        if any([abs(triggerJobStart - ele[1]) < 500 for ele in times]):
            print("WARNING: Job starts within 500 seconds of trigger!")

        jobIndices = [index for index, val in enumerate(times)]
        random.shuffle(jobIndices)
        croppedJobIndices = jobIndices[:configs.getint('search', 
                                                      'maxNumJobPairs')]
        #jobIndices1 = [index for index, val in enumerate(times)
        #                    if triggerJobStart - val[1] >= 0]
        #jobIndices2 = [index for index, val in enumerate(times) 
        #                    if val[1] - triggerJobStart < 0]

        #random.shuffle(jobIndices1)
        #random.shuffle(jobIndices2)
        #k = len(jobIndices1)
        #jobIndices = jobIndices1 + jobIndices2
        #mn = configs.getint('search', 'maxNumJobPairs')
        #j = [abs(i - (k - mn/2)) for i in range(len(jobIndices))]
        #startIndex = j.index(min(j))
        #croppedJobIndices = jobIndices[startIndex:startIndex+mn]
        sortedJobPairs = [[x,x] for x in croppedJobIndices]

        #lenj1 = min(configs.getint('search', 'maxNumJobPairs')/2, 
        #            len(jobIndices1))
        #lenj2 = min(configs.getint('search', 'maxNumJobPairs')/2, 
        #            len(jobIndices2))
        #jobIndexList1 = random.sample(jobIndices1, lenj1)
        #jobIndexList2 = random.sample(jobIndices2, lenj2)
        #sortedJobPairs = ([
        #                  [x,x] for x in jobIndexList1]
        #                  + [[x,x] for x in jobIndexList2
        #                 ])
    
    elif (offsource or injectionRecovery) and not useCustomJobPairs:
        deltaTotal = []
        jobPairs = []
        for index1, job1 in enumerate(times):
            for index2, job2 in enumerate(times):
                if index1 != index2:
                    deltaTotal += [abs(triggerJobStart - job1[1])
                                    + abs(triggerJobStart - job2[1])]
                    jobPairs += [[index1, index2]]

        if configs.getboolean('search', 'randomizeJobPairs'):
            sortedIndices = np.random.randint(0, len(deltaTotal),
                                              configs.getint(
                                                'search', 'maxNumJobPairs'))
        else:
            sortedIndices = argsort(deltaTotal)[:configs.getint(
                                                  'search', 'maxNumJobPairs')]
        sortedJobPairs = [jobPairs[x] for x in sortedIndices]
   
    elif not (offsource or injectionRecovery or pseudo_onsource):
        print("Error: need to define search type correctly")
        raise

    if useCustomJobPairs:
        jobPairs = []
        with open(configs.get('search', 'customJobPairsFile')) as f:
            for line in f:
                jobPairs.append([int(ele)-1 for ele in line.split()]) #-1 for number to index
        #now to validate
        if not all([len(ele) == 2 for ele in jobPairs]):
            raise ValueError('File does not specify a pair of jobs on each line')

        if not all([ele < len(times) for ele in sum(jobPairs, [])]):
            raise ValueError('Job file does not contain enough jobs for custom job pairs')

        if offsource and any([ele[0] == ele[1] for ele in jobPairs]):
            raise ValueError('specified offsource, but put in onsource jobpair(s)')

        if pseudo_onsource and not all ([ele[0] == ele[1] for ele in jobPairs]):
            raise ValueError('specified pseudo_onsource, but put in offsource jobpair(s)')

        sortedJobPairs = jobPairs


        
    #These are the job indices run by anteproc 
    tempNumbersH = list(set([x[0] for x in sortedJobPairs])) #job indices
    tempNumbersL = list(set([x[1] for x in sortedJobPairs])) #job indices
    
    
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
        #CPDict['varying_injection_start'] = [-2, 1604 - wave_duration - 2]
        pass 
                
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
            GSParams['anteproc']['inmats1'] = (anteproc_l_dir)
            GSParams['anteproc']['inmats2'] = (anteproc_h_dir)
            GSParams['anteproc']["jobfile"] = newJobPath

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


            GSParams['job_group'] = job_group
            GSParams['jobNumber'] = current_job
            stochtrackParamsList.append(deepcopy(jobDictionary))

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
    grandStochtrackExecutable = os.path.join(
                configs.get('dirs', 'stamp2InstallationDir'), 
                "compilationScripts/grand_stochtrack")
    grandStochtrackExecutableNoPlots = os.path.join(
                configs.get('dirs', 'stamp2InstallationDir'), 
                "compilationScripts/grand_stochtrack_nojvm")

    
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
    
    
    webPageSH = os.path.join(webpage.load_pycondorstamp_dir(), 
                             'webdisplay/resultsJSON.py') 
        
    for job in stochtrackParamsList:
        job['grandStochtrackParams'] = recursive_ints_to_floats(
                                            job['grandStochtrackParams'])
        sio.savemat(job['stochtrackInputDir'] + "/params.mat", 
                    job['grandStochtrackParams'])
        
    print("Creating dag and sub files")
    
    stochtrackSub = write_stochtrack_sub_file(
                            configs.getint('condor', 'grandStochtrackMemory'), 
                            grandStochtrack_script_file, dagDir, 
                            configs.get('condor', 'accountingGroup'), 
                            configs.getboolean('condor', 'doGPU'), 
                            configs.getint('condor', 'numCPU'))
    webDisplaySub = write_webpage_sub_file(
                            webPageSH, dagDir, 
                            configs.get('condor', 'accountingGroup'))
    write_only_stochtrack_dag(dagDir, newJobPath, 
              stochtrackParamsList, stochtrackSub, 
              configs.getint('condor', 'maxJobsGrandStochtrack'), 
              webDisplaySub, baseDir)
        
    generate_summary(configs, baseDir)
    webpage.load_conf_cp_webfiles(baseDir)
    
    if options.verbose:
        dict_dir = create_dir(os.path.join(baseDir, "intermediate_dictionaries"))
        import pprint
        pprint.pprint(CPDict, 
                open(os.path.join(dict_dir, "commonParams_dict.txt"), "w"))
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
