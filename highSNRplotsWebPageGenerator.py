from __future__ import division
from optparse import OptionParser
import os
import scipy.io as sio
import json
import webpageGenerateLib as webGen
from numpy import argsort
#from pyCondorSTAMPLib_V3 import create_dir
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['legend.numpoints'] = 1

# command line options
parser = OptionParser()
parser.set_defaults(verbose = True)
parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to directory containing completed STAMP jobs to use for False Alarm Probability calculation",
                  metavar = "DIRECTORY")
parser.add_option("-v", action="store_true", dest="verbose")

(options, args) = parser.parse_args()

print("NOTE: Script ignores all files and directories starting with '.'")
print("NOTE: Common functions such as 'create_dir' should eventually be in a separate common python module.")

baseDir = options.targetDirectory + "/jobs/job_group_1"

jobDirs = [x for x in os.listdir(baseDir) if "job" in x]

print("WARNING: Script is currently not set up to handle directories with multiple files with the name base.")
def returnMatrixFilePath(nameBase, directory):
    files = [x for x in os.listdir(directory) if nameBase in x]
    if len(files) != 1:
        print("WARNING: Number of files in " + directory + " with name base " + nameBase + " is not equal to one. Number of files is " + str(len(files)) + ". Selecting first occurance for rest of script.")
    filePath = directory + "/" + files[0]
    return filePath

gsoutMats = dict((returnMatrixFilePath("bknd_", baseDir + "/" + x + "/grandstochtrackOutput"), x) for x in jobDirs)

def getSNR(inputFile):
    data = sio.loadmat(inputFile)
    SNR = data['stoch_out'][0,0]['max_SNR'][0,0]
    return (SNR, inputFile)

SNRs = [getSNR(fileName) for fileName in gsoutMats]

SNRdict = dict((x[0], x[1]) for x in SNRs)

SNRvals = [x[0] for x in SNRs]
filePaths = [x[1] for x in SNRs]
indices = argsort(SNRvals)
sortedSNRvals = [SNRvals[x] for x in indices]
sortedFilePaths = [filePaths[x] for x in indices]

N = len(sortedSNRvals)
highSNRsubDirs = dict((gsoutMats[sortedFilePaths[index]], ["Cluster SNR = " + str(sortedSNRvals[index])]) for index in reversed(range(N)))

plotRowOrder = [gsoutMats[sortedFilePaths[x]] for x in reversed(range(N))]

plotTypeList = ["SNR", "Loudest Cluster", "sig map", "y map", "Xi snr map"]

plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster" : "rmap.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png"}

outFile = "highSNRpageDisplayTest.html"
print(options.targetDirectory + "/" + outFile)

quit_program = False

if not quit_program:
    webGen.make_display_page_v2("jobs", options.targetDirectory, highSNRsubDirs, "grandstochtrackOutput/plots", plotTypeList, plotTypeDict, outFile, plotRowOrder)

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.hist(sortedSNRvals)
plt.savefig(options.targetDirectory + "/SNRhistogram", bbox_inches = 'tight')
plt.clf()
