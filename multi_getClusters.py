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
parser.add_option("-n", dest = "numJobGroups", help = "number of job groups")

(options, args) = parser.parse_args()

print("NOTE: Script ignores all files and directories starting with '.'")
print("NOTE: Common functions such as 'create_dir' should eventually be in a separate common python module.")
for j in range(1, int(options.numJobGroups) + 1):
    baseDir = options.targetDirectory + "/jobs/job_group_" + str(j)

    jobDirs = [x for x in os.listdir(baseDir) if "job" in x and len(os.listdir(baseDir + '/' + x + '/grandStochtrackOutput')) > 1]


    gsoutMats = dict((x, returnMatrixFilePath("bknd_", baseDir + "/" + x + "/grandStochtrackOutput")) for x in jobDirs)
    SNRs = [getSNR(gsoutMats[dirName]) for dirName in jobDirs]
    Lengths = [getLength(gsoutMats[dirName]) for dirName in jobDirs]


    SNRvals = [round(x[0],2) for x in SNRs]
    filePaths = [x[1] for x in SNRs]
    Lengthvals = [x[0] for x in Lengths]
    indices = argsort(SNRvals)
    sortedSNRvals = [SNRvals[x] for x in indices]

    array_SNRs = [round(get_attr(gsoutMats[dirName], "max_SNR"),2) for dirName in jobDirs]
    array_fmin = [get_attr(gsoutMats[dirName], "fmin") for dirName in jobDirs]
    array_fmax = [get_attr(gsoutMats[dirName], "fmax") for dirName in jobDirs]
    array_length = [get_attr(gsoutMats[dirName], "tmax") - get_attr(gsoutMats[dirName], "tmin") for dirName in jobDirs]

    out_ar = ["\t".join([str(jobDirs[i]), str(array_SNRs[i]), str(array_fmin[i]), str(array_fmax[i]), str(array_length[i])]) for i in range(0, len(gsoutMats))]

    with open(options.targetDirectory + "/LoudestClusters.txt", "a") as h:
        if i==1:
            print >> h, "Job Num\tSNR\tMin Freq\tMaxFreq\tLength Of Cluster\n"
        h.write('Job Group ' + str(j) + '\n')
        h.write("\n".join(out_ar))
        h.write('\n')
#    print >> h, "\n".join(["\t".join(ele) for ele in zip([str(ele) for ele in SNRvals],[str(ele) for ele in Lengthvals])])

