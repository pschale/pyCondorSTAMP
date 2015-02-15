from __future__ import division
from optparse import OptionParser
import os
import scipy.io as sio
import json
import webpageGenerateLib as webGen
#from pyCondorSTAMPLib_V3 import create_dir

# command line options
parser = OptionParser()
parser.set_defaults(verbose = True)
parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to directory containing completed STAMP jobs to use for False Alarm Probability calculation",
                  metavar = "DIRECTORY")
#parser.add_option("-o", "--output", dest = "outputDir",
 #                 help = "Directory for output JSON and text file summarizing results (will create in current directory unless full path specified. will overwrite any existing files)",
  #                metavar = "DIRECTORY")
#parser.add_option("-v", action="store_true", dest="verbose")

(options, args) = parser.parse_args()

print("NOTE: script ignores all files and directories starting with '.'")

baseDir = options.targetDirectory + "/jobs"

jobDirs = [x for x in os.listdir(baseDir) if "job" in x]
nums = dict((x, x[4:]) for x in jobDirs)

#gsoutMats = [baseDir + "/" + x + "/grandstochtrackOutput/bknd_1.mat" for x in jobDirs]
#gsoutMats = [baseDir + "/" + x + "/grandstochtrackOutput/bknd_" + nums[x] + ".mat" for x in jobDirs]
gsoutMats = dict((baseDir + "/" + x + "/grandstochtrackOutput/bknd_" + nums[x] + ".mat", x) for x in jobDirs)

def getSNR(inputFile):
    data = sio.loadmat(inputFile)
    SNR = data['stoch_out'][0,0].max_SNR[0,0]
    return (SNR, inputFile)

SNRs = [getSNR(fileName) for fileName in gsoutMats]

SNRdict = dict((x[0], x[1]) for x in SNRs)

#SNRvals = [x[1] for x in SNRs]
SNRvals = [x[0] for x in SNRs]

SNRvals.sort()

highSNRs = SNRvals[:]
#print(max(SNRvals))
#print(highSNRs)
highSNRsubDirs = dict((gsoutMats[SNRdict[x]], ["Cluster SNR = " + str(x)]) for x in highSNRs[::-1])
#print(highSNRsubDirs)
#for x in highSNRs:
#    print(x)
#for x in highSNRs:
#    print(SNRdict[x])
#for x in highSNRs:
#    print(gsoutMats[SNRdict[x]])

plotRowOrder = [gsoutMats[SNRdict[x]] for x in highSNRs[::-1]]

plotTypeList = ["SNR", "Loudest Cluster", "sig map", "y map", "Xi snr map"]

plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster" : "rmap.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png"}

outFile = "highSNRpageDisplayTest.html"
print(options.targetDirectory + "/" + outFile)

quit_program = False

#print(highSNRsubDirs[0])

if not quit_program:
    #webGen.make_display_page_v2(directory, saveDir, subDirDict, subSubDir, plotTypeList, plotTypeDict, outputFileName)
    webGen.make_display_page_v2("jobs", options.targetDirectory, highSNRsubDirs, "grandstochtrackOutput/plots", plotTypeList, plotTypeDict, outFile, plotRowOrder)
