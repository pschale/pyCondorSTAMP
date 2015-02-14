from __future__ import division
import os
from pyCondorSTAMPLib import ask_yes_no_bool

def pathCheckSaveDirty(outputString, fileName):
    # Helper function to create file NOTE: keep in mind the security vulnerability inherent to the
    # possible race condition when using os.path.isfile. This may not be an issue
    # as this is meant for local use.
    fileWritten = False
    if os.path.isfile(fileName):
        if ask_yes_no_bool("File already exists, overwrite?"):
            with open(fileName, 'w') as outfile:
                outfile.write(outputString)
            fileWritten = True
            print("File write completed: previous file " + fileName + " overwritten.")
        else:
            print("Quiting process without writing file.")
    else:
        with open(fileName, 'w') as outfile:
            outfile.write(outputString)
            fileWritten = True
        print("File write completed.")
    print(fileWritten)
    print(fileName)
    return fileWritten

def checkKeys(keyList, dictionary, dictionaryIdentifier):
    # Helper function to check that all the keys in the dicitonary are properly
    # recorded in the appropriate list. Doing this to maintain order for
    # readability and bug checking.
#    keys = dictionary.keys()
#    keyCheck = [key in keyList for key in keys]
    keyCheck = [key in keyList for key in dictionary]
    if False in keyCheck:
        print("Warning, certain keys in the following dictionary are unused: " + dictionaryIdentifier)
#        missingKeys = [key for index, key in enumerate(keys) if not keyCheck[index]]
        #missingKeys = [key for index, key in enumerate(dictonary) if not keyCheck[index]]
        missingKeys = [key for key in dictionary if key not in keyList]
        print("The following parameters in " + dictionaryIdentifier + " are unused:")
        #for index in missingKeys:
         #   print("\t" + keys[index])
        for key in missingKeys:
            print("\t" + key)
        return False
    else:
        return True

def parameterDefaults():
    # Function to create a dictonary with the default parameters to be used
    # with preproc. No inputs taken in order to avoid confusing or possible
    # key pair overwrites.

    defaults = {}

    defaults["stochmap"] = "true"
    defaults["batch"] = "true"
    defaults["mapsize"] = "200"
    defaults["doDetectorNoiseSim"] = "true"
    defaults["DetectorNoiseFile"] = "/home/quitzow/STAMP/stamp2/test/ZERO_DET_high_P_psd.txt"
    defaults["sampleRate"] = "16384"
    defaults["pp_seed"] = "-1"
    defaults["outputfilename"] = "map"
#    defaults["outputfiledir"] = "/home/quitzow/STAMP/stamp2/test/inputDefault/"
    defaults["doFreqMask"] = "false"
    defaults["doHighPass1"] = "true"
    defaults["doHighPass2"] = "true"
    defaults["doOverlap"] = "true"
    defaults["doSidereal"] = "false"
    defaults["minDataLoadLength"] = "300"
    defaults["doBadGPSTimes"] = "false"
    defaults["maxDSigRatio"] = "1.2"
    defaults["minDSigRatio"] = "0.8"
    defaults["doShift1"] = "false"
    defaults["ShiftTime1"] = "0"
    defaults["doShift2"] = "false"
    defaults["ShiftTime2"] = "0"
    defaults["ifo1"] = "H1"
    defaults["ifo2"] = "L1"
    defaults["segmentDuration"] = "1"
    defaults["numSegmentsPerInterval"] = "9"
    defaults["ignoreMidSegment"] = "true"
    defaults["flow"] = "11"
    defaults["fhigh"] = "1800"
    defaults["deltaF"] = "1"
    defaults["alphaExp"] = "0"
    defaults["fRef"] = "100"
    defaults["resampleRate1"] = "4096"
    defaults["resampleRate2"] = "4096"
    defaults["bufferSecs1"] = "2"
    defaults["bufferSecs2"] = "2"
    defaults["ASQchannel1"] = "LSC-STRAIN"
    defaults["ASQchannel2"] = "LSC-STRAIN"
    defaults["frameType1"] = "H1_RDS_C03_L2"
    defaults["frameType2"] = "L1_RDS_C03_L2"
    defaults["frameDuration1"] = "-1"
    defaults["frameDuration2"] = "-1"
    defaults["hannDuration1"] = "1"
    defaults["hannDuration2"] = "1"
    defaults["nResample1"] = "10"
    defaults["nResample2"] = "10"
    defaults["betaParam1"] = "5"
    defaults["betaParam2"] = "5"
    defaults["highPassFreq1"] = "9"
    defaults["highPassFreq2"] = "9"
    defaults["highPassOrder1"] = "16"
    defaults["highPassOrder2"] = "16"
    defaults["freqsToRemove"] = ""
    defaults["nBinsToRemove"] = ""
    defaults["alphaBetaFile1"] = "none"
    defaults["alphaBetaFile2"] = "none"
    defaults["calCavGainFile1"] = "none"
    defaults["calCavGainFile2"] = "none"
    defaults["calResponseFile1"] = "none"
    defaults["calResponseFile2"] = "none"
    defaults["simOmegaRef"] = "0"
    defaults["heterodyned"] = "false"
    defaults["gpsTimesPath1"] = "/home/quitzow/STAMP/stamp2/test/fakecache/"
    defaults["gpsTimesPath2"] = "/home/quitzow/STAMP/stamp2/test/fakecache/"
    defaults["frameCachePath1"] = "/home/quitzow/STAMP/stamp2/test/fakecache/"
    defaults["frameCachePath2"] = "/home/quitzow/STAMP/stamp2/test/fakecache/"
    defaults["stampinj"] = "true"
    defaults["stamp.ra"] = "6.40"
    defaults["stamp.decl"] = "-39.30"
    defaults["stamp.startGPS"] = "1000000015"
    # waveform file (t, hp, hx)
    defaults["stamp.file"] = "/home/quitzow/STAMP/stamp2/test/input/sine_gaussian_sanity_test.dat"
    # power scale factor
    defaults["stamp.alpha"] = "1"

    keyOrder = ["stochmap", "batch", "mapsize", "doDetectorNoiseSim", "DetectorNoiseFile",
               "sampleRate", "pp_seed", "outputfilename", #"outputfiledir",
               "doFreqMask",
               "doHighPass1", "doHighPass2", "doOverlap", "doSidereal", "minDataLoadLength",
               "doBadGPSTimes", "maxDSigRatio", "minDSigRatio", "doShift1", "ShiftTime1",
               "doShift2", "ShiftTime2", "ifo1", "ifo2", "segmentDuration", "numSegmentsPerInterval",
               "ignoreMidSegment", "flow", "fhigh", "deltaF", "alphaExp", "fRef", "resampleRate1",
               "resampleRate2", "bufferSecs1", "bufferSecs2", "ASQchannel1", "ASQchannel2",
               "frameType1", "frameType2", "frameDuration1", "frameDuration2", "hannDuration1",
               "hannDuration2", "nResample1", "nResample2", "betaParam1", "betaParam2",
               "highPassFreq1", "highPassFreq2", "highPassOrder1", "highPassOrder2", "freqsToRemove",
               "nBinsToRemove", "alphaBetaFile1",
               "alphaBetaFile2", "calCavGainFile1", "calCavGainFile2", "calResponseFile1",
               "calResponseFile2", "simOmegaRef", "heterodyned", "gpsTimesPath1", "gpsTimesPath2",
               "frameCachePath1", "frameCachePath2", "stampinj", "stamp.ra", "stamp.decl",
               "stamp.startGPS", "stamp.file", "stamp.alpha"]

    print("Make sure to test that I got all the proper values in the default dictionary!")
    checkKeys(keyOrder, defaults, "Default Preproc Dictionary")

    return defaults, keyOrder

def buildPreprocParamFile(parameterDictionary, fileName, parameterOrder = None, loadDefaults = True):

    # defaults
    parameters = {}
    defaultsOrder = []
    if loadDefaults:
        parameters, defaultsOrder = parameterDefaults()

    # overwrite defaults
    parameters.update(parameterDictionary) # may not be needed, can be tested

    # set parameter order
    if not parameterOrder:
        parameterOrder = defaultsOrder + [key for key in parameterDictionary if key not in defaultsOrder]
    else:
        parameterOrder = [key for key in defaultsOrder if key not in parameterOrder] + parameterOrder

    # write string for parameter file
    output = """% parameters for stochastic search (name/value pairs)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%--------------------user's parameters-----------------------------------------

"""
    '''output += "\n".join(key + " " + parameters[key] for key in defaultsOrder if key not in parameterOrder) + "\n\n"
    print("First keys are:")
    print(defaultsOrder)
    missingKeys = [key for key in defaultsOrder if key not in parameterOrder]
    print("missing keys are:")
    print(missingKeys)

    print("parameterOrder")
    print(parameterOrder)

    if not parameterOrder:
        parameterOrder = parameterDictionary.keys()'''

    '''for  key in parameterOrder:
        print(key)
        print(parameterDictionary[key])'''

    #output += "\n".join(key + " " + parameterDictionary[key] for key in parameterOrder)
    output += "\n".join(key + " " + parameters[key] for key in parameterOrder)
    print("Keys are:")
    print(parameterOrder)

    print("Check that all keys in parameterDictionary are used.")
    checkKeys(parameterOrder, parameterDictionary, "User Defined Preproc Dictionary")

    paramFileBuilt = pathCheckSaveDirty(output, fileName)

    return paramFileBuilt
