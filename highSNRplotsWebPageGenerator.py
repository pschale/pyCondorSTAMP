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
#parser.add_option("-o", "--output", dest = "outputDir",
 #                 help = "Directory for output JSON and text file summarizing results (will create in current directory unless full path specified. will overwrite any existing files)",
  #                metavar = "DIRECTORY")
#parser.add_option("-v", action="store_true", dest="verbose")

(options, args) = parser.parse_args()

print("NOTE: script ignores all files and directories starting with '.'")

baseDir = options.targetDirectory + "/jobs"

jobDirs = [x for x in os.listdir(baseDir) if "job" in x]
#nums = dict((x, x[4:]) for x in jobDirs)

print("WARNING: Script is currently not set up to handle directories with multiple files with the name base.")
def returnMatrixFilePath(nameBase, directory):
    files = [x for x in os.listdir(directory) if nameBase in x]
    if len(files) != 1:
        print("WARNING: Number of files in " + directory + " with name base " + nameBase + " is not equal to one. Number of files is " + str(len(files)) + ". Selecting first occurance for rest of script.")
    filePath = directory + "/" + files[0]
    return filePath

#gsoutMats = [baseDir + "/" + x + "/grandstochtrackOutput/bknd_1.mat" for x in jobDirs]
#gsoutMats = [baseDir + "/" + x + "/grandstochtrackOutput/bknd_" + nums[x] + ".mat" for x in jobDirs]
#gsoutMats = dict((baseDir + "/" + x + "/grandstochtrackOutput/bknd_" + nums[x] + ".mat", x) for x in jobDirs)
gsoutMats = dict((returnMatrixFilePath("bknd_", baseDir + "/" + x + "/grandstochtrackOutput"), x) for x in jobDirs)

def getSNR(inputFile):
    data = sio.loadmat(inputFile)
    SNR = data['stoch_out'][0,0].max_SNR[0,0]
    return (SNR, inputFile)

SNRs = [getSNR(fileName) for fileName in gsoutMats]

SNRdict = dict((x[0], x[1]) for x in SNRs)

#SNRvals = [x[1] for x in SNRs]
SNRvals = [x[0] for x in SNRs]
filePaths = [x[1] for x in SNRs]
indices = argsort(SNRvals)
sortedSNRvals = [SNRvals[x] for x in indices]
sortedFilePaths = [filePaths[x] for x in indices]

#SNRvals.sort()

#highSNRs = SNRvals[:]
#print(max(SNRvals))
#print(highSNRs)
#print(highSNRs[::-1])
#for x in highSNRs:
#    print(x)
#    print(SNRdict[x])
#print(SNRdict)
#highSNRsubDirs = dict((gsoutMats[SNRdict[x]], ["Cluster SNR = " + str(x)]) for x in highSNRs[::-1])
N = len(sortedSNRvals)
highSNRsubDirs = dict((gsoutMats[sortedFilePaths[index]], ["Cluster SNR = " + str(sortedSNRvals[index])]) for index in reversed(range(N)))
#print(highSNRsubDirs)
#for x in highSNRs:
#    print(x)
#for x in highSNRs:
#    print(SNRdict[x])
#for x in highSNRs:
#    print(gsoutMats[SNRdict[x]])

#print(N)
#print(len(sortedFilePaths))
#print(len(gsoutMats.keys()))
#test = None
#for x in sortedFilePaths:
#    try:
#        test = gsoutMats[x]
#    except:
#        print(x)

#for x in range(N):
#    try:
#        test = gsoutMats[sortedFilePaths[N-x]

plotRowOrder = [gsoutMats[sortedFilePaths[x]] for x in reversed(range(N))]

#test2 = plotRowOrder[:]
#test2.sort()
#print(len(highSNRsubDirs.keys()))
#print(highSNRsubDirs.keys())
#for x in test2:
#    print(x)
#    print(highSNRsubDirs[x])

#test = []
#for row in plotRowOrder:
#    if row in test:
#        print(row)
#    test.append(row)

#print(len(set(SNRvals)))

#print("testing gsoutMats dictionary")
#test2 = []
#for key in gsoutMats.keys():
#    if key in test2:
#        print(key)
#    test2.append(key)
#print(gsoutMats.keys())

#print("testing os.listdir() now")
#test3 = []
#for x in jobDirs:
#    if x in test3:
#        print(x)
#    test3.append(x)

#print(len(SNRvals))
#print(len(plotRowOrder))
#print(len(gsoutMats.keys()))

plotTypeList = ["SNR", "Loudest Cluster", "sig map", "y map", "Xi snr map"]

plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster" : "rmap.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png"}

outFile = "highSNRpageDisplayTest.html"
print(options.targetDirectory + "/" + outFile)

quit_program = False

#print(highSNRsubDirs[0])

if not quit_program:
    #webGen.make_display_page_v2(directory, saveDir, subDirDict, subSubDir, plotTypeList, plotTypeDict, outputFileName)
    webGen.make_display_page_v2("jobs", options.targetDirectory, highSNRsubDirs, "grandstochtrackOutput/plots", plotTypeList, plotTypeDict, outFile, plotRowOrder)

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
#plt.plot(SNRranking,percentageRanks,'b-')#, label = "SNR distribution")
#print("make histogram here!")
plt.hist(sortedSNRvals)
#plt.plot(specificSNR, rank*100, 'ro', label = "FAP = " + str(100*rank) + "%\nSNR = " + str(specificSNR))
#plt.yscale('log')
#plt.xscale('log')
#plt.xlabel("SNR")
#plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
#plt.ylabel('Strain [Counts / sqrt(Hz)]')
#plt.ylabel("False Alarm Probability [%]")
#plt.ylim([0,100])
#plt.title("")
#legend = plt.legend(prop={'size':6})#, framealpha=0.5)
#legend.get_frame().set_alpha(0.5)
#plt.show()
plt.savefig(options.targetDirectory + "/SNRhistogram", bbox_inches = 'tight')
plt.clf()
