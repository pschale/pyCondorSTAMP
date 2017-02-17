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
mpl.rc('text', usetex=True)
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
parser.add_option("-j", dest = "numJobs", help = "number of jobs per group")
(options, args) = parser.parse_args()

print("NOTE: Script ignores all files and directories starting with '.'")
print("NOTE: Common functions such as 'create_dir' should eventually be in a separate common python module.")
out_str = "Job Num\tSNR\tMin Freq\tMaxFreq\tLength Of Cluster\n"
SNRs = []
xvals = []
for j in range(1, int(options.numJobGroups) + 1):
    
    out_str += "\n"
    out_str += "Job Group " + str(j)
    out_str += "\n"
    baseDir = options.targetDirectory + "jobs/job_group_" + str(j)
    for k in range(1, int(options.numJobs) + 1):

        jobDir = "job_" + str(k)
        outMat = os.path.join(baseDir, jobDir,  "grandStochtrackOutput/bknd_" + str(k-1) + ".mat")
        
        data = sio.loadmat(outMat)
        SNR = round(data['stoch_out'][0,0]['max_SNR'][0,0], 2)
        length = data['stoch_out'][0,0]['tmax'][0,0] - data['stoch_out'][0,0]['tmin'][0,0]
        fmin = data['stoch_out'][0,0]['fmin'][0,0]
        fmax = data['stoch_out'][0,0]['fmax'][0,0]

        out_str += "\t".join([str(jobDir), str(SNR), str(fmin), str(fmax), str(length)])
        out_str += "\n"

        SNRs.append(SNR)
        xvals.append(j*180/20)

plt.scatter(xvals, SNRs)
plt.xlim([0, 180])
plt.xlabel(r'$\psi$', fontsize=18)
plt.ylabel('SNR')
plt.title(r'SNR vs $\psi$ with $\iota = 45$')
plt.savefig(os.path.join(options.targetDirectory, "SNR_scatter.png"))


with open(os.path.join(options.targetDirectory, "LoudestClusters2.txt"), "w") as h:
    print >> h, out_str

