from __future__ import division
from optparse import OptionParser
import os
import scipy.io as sio
import json
from pyCondorSTAMPLib_V3 import create_dir
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
parser.add_option("-p", "--percentile", dest = "percentile",
                  help = "Number between 0 and 100 to set as threshold percentile to find the percentage of SNRs at or above (will adjust to next lowest percentile if point not available at exact percentage request)",
                  metavar = "NUMBER")
parser.add_option("-o", "--output", dest = "outputDir",
                  help = "Directory for output JSON and text file summarizing results (will create in current directory unless full path specified. will overwrite any existing files)",
                  metavar = "DIRECTORY")
#parser.add_option("-v", action="store_true", dest="verbose")

(options, args) = parser.parse_args()

print("NOTE: script ignores all files and directories starting with '.'")

baseDir = options.targetDirectory + "/jobs"

jobDirs = [x for x in os.listdir(baseDir) if "job" in x]
nums = dict((x, x[4:]) for x in jobDirs)

#gsoutMats = [baseDir + "/" + x + "/grandstochtrackOutput/bknd_1.mat" for x in jobDirs]
gsoutMats = [baseDir + "/" + x + "/grandstochtrackOutput/bknd_" + nums[x] + ".mat" for x in jobDirs]

def getSNR(inputFile):
    data = sio.loadmat(inputFile)
    SNR = data['stoch_out'][0,0].max_SNR[0,0]
    return (SNR, inputFile)

SNRs = [getSNR(fileName) for fileName in gsoutMats]

workingDir = create_dir(options.outputDir + "/backgroundEstimation")

SNRvals = [x[0] for x in SNRs]
SNRvals.sort()

SNRranking = SNRvals[::-1]

N = len(SNRs)
ranks = [x/N for x in range(1,N+1)]

SNRinfo = {}
SNRinfo["rawData"] = SNRs
SNRinfo["rankedSNRs"] = SNRranking
SNRinfo["ranks"] = ranks

percentage = float(options.percentile)

highSNRs = [x for index, x in enumerate(SNRranking) if ranks[index]*100 <= percentage]
highRanks = [x for x in ranks if x*100 <= percentage]

rank = highRanks[-1]
specificSNR = highSNRs[-1]

SNRinfo["thresholdPercentile"] = rank*100
SNRinfo["thresholdSNR"] = specificSNR

with open(workingDir + "/SNRs.json","w") as outFile:
    json.dump(SNRinfo, outFile, indent = 4, sort_keys = True)

percentageRanks = [x*100 for x in ranks]

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.plot(SNRranking,percentageRanks,'b-')#, label = "SNR distribution")
plt.plot(specificSNR, rank*100, 'ro', label = "FAP = " + str(100*rank) + "%\nSNR = " + str(specificSNR))
#plt.yscale('log')
#plt.xscale('log')
plt.xlabel("SNR")
#plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
#plt.ylabel('Strain [Counts / sqrt(Hz)]')
plt.ylabel("False Alarm Probability [%]")
plt.ylim([0,100])
#plt.title("")
legend = plt.legend(prop={'size':6})#, framealpha=0.5)
legend.get_frame().set_alpha(0.5)
#plt.show()
plt.savefig(workingDir + "/SNRvsFAP", bbox_inches = 'tight')
plt.clf()