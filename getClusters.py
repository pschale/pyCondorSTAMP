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


def returnMatrixFilePath(nameBase, directory):
    files = [x for x in os.listdir(directory) if nameBase in x]
    if len(files) != 1:
        print("WARNING: Number of files in " + directory + " with name base " + nameBase + " is not equal to one. Number of files is " + str(len(files)) + ". Selecting first occurance for rest of script.")
    filePath = directory + "/" + files[0]
    return filePath

def get_attr(inputFile, attr):
    data = sio.loadmat(inputFile)
    return data['stoch_out'][0,0][attr][0,0]

def getSNR(inputFile):
    data = sio.loadmat(inputFile)
    SNR = data['stoch_out'][0,0]['max_SNR'][0,0]
    return (SNR, inputFile)

def getLength(inputFile):
    data = sio.loadmat(inputFile)
    length = data['stoch_out'][0,0]['tmax'][0,0] - data['stoch_out'][0,0]['tmin'][0,0]
    return (length, inputFile)

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

gsoutMats = dict((returnMatrixFilePath("bknd_", baseDir + "/" + x + "/grandstochtrackOutput"), x) for x in jobDirs)

SNRs = [getSNR(fileName) for fileName in gsoutMats]
Lengths = [getLength(fileName) for fileName in gsoutMats]

SNRdict = dict((x[0], x[1]) for x in SNRs)
Lengthsdict = dict((x[0], x[1]) for x in Lengths)

SNRvals = [round(x[0],2) for x in SNRs]
filePaths = [x[1] for x in SNRs]
Lengthvals = [x[0] for x in Lengths]
indices = argsort(SNRvals)
sortedSNRvals = [SNRvals[x] for x in indices]

array_SNRs = [round(get_attr(filename, "max_SNR"),2) for filename in gsoutMats]
array_fmin = [get_attr(filename, "fmin") for filename in gsoutMats]
array_fmax = [get_attr(filename, "fmax") for filename in gsoutMats]
array_length = [get_attr(filename, "tmax") - get_attr(filename, "tmin") for filename in gsoutMats]

out_ar = ["\t".join([str(jobDirs[i]), str(array_SNRs[i]), str(array_fmin[i]), str(array_fmax[i]), str(array_length[i])]) for i in range(0, len(gsoutMats))]

with open(options.targetDirectory + "/LoudestClusters.txt", "w") as h:
    print >> h, "Job Num\tSNR\tMin Freq\tMaxFreq\tLength Of Cluster\n"
    print >> h, "\n".join(out_ar)
#    print >> h, "\n".join(["\t".join(ele) for ele in zip([str(ele) for ele in SNRvals],[str(ele) for ele in Lengthvals])])

N = len(sortedSNRvals)

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.hist(sortedSNRvals)
plt.savefig(options.targetDirectory + "/SNRhistogram", bbox_inches = 'tight')
plt.clf()
