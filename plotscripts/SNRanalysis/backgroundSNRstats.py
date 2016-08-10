from __future__ import division
from optparse import OptionParser
import os
import scipy.io as sio
import json
import webpageGenerateLib as webGen
from pyCondorSTAMPLib import create_dir
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['legend.numpoints'] = 1

parser = OptionParser()
parser.set_defaults(verbose = False)
parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to directory containing completed STAMP jobs to use for analysis",
                  metavar = "DIRECTORY")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                  help = "Prints internal status messages to terminal as script runs")

(options, args) = parser.parse_args()

def glueFileLocation(directory, filename):
    output = None
    if directory[-1] == "/":
        if filename[0] == "/":
            output = directory + filename[1:]
        else:
            output = directory + filename
    else:
        if filename[0] == "/":
            output = directory + filename
        else:
            output = directory + "/" + filename
    return output

def readFile(file_name, delimeter = None):
    with open(file_name, "r") as infile:
        content = [x.split(delimeter) for x in infile]
    return content

baseDir = options.targetDirectory
analysisDir = glueFileLocation(baseDir, "basic_snr_info")

loudest_cluster_file = glueFileLocation(analysisDir, "LoudestClusterInfo.txt")
all_clusters_file = glueFileLocation(analysisDir, "runData.txt")

loudest_cluster_info = readFile(loudest_cluster_file)
all_clusters_info = readFile(all_clusters_file)

loudest_cluster_info = [x for x in loudest_cluster_info if len(x) > 0]

loudest_snrs = [float(x[0].strip(",")) for x in loudest_cluster_info if x[0] != "None,"]
loudest_snrs.sort()
loudest_percentage = [100 - (x)/len(loudest_snrs)*100 for x in range(len(loudest_snrs))]
#percentageRanks = [x*100 for x in ranks]

all_clusters_info = [x for x in all_clusters_info if len(x) > 0]
all_clusters_info = [x for x in all_clusters_info if  x[0] != "None,"]

all_snrs = [float(x[0].strip(",")) for x in all_clusters_info]
all_snrs.sort()
all_percentage = [100 - (x)/len(all_snrs)*100 for x in range(len(all_snrs))]

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.plot(loudest_snrs, loudest_percentage,'b-')#, label = "SNR distribution")
#plt.plot(loudest_snrs, loudest_percentage, 'ro', label = "FAP = " + str(100*rank) + "%\nSNR = " + str(specificSNR))
#plt.yscale('log')
#plt.xscale('log')
plt.xlabel("SNR")
#plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
#plt.ylabel('Strain [Counts / sqrt(Hz)]')
plt.ylabel("False Alarm Probability [%]")
plt.ylim([0,100])
#plt.title("")
#legend = plt.legend(prop={'size':6})#, framealpha=0.5)
#legend.get_frame().set_alpha(0.5)
#plt.show()
plt.savefig(analysisDir + "/SNRvsFAP_loudest_clusters", bbox_inches = 'tight')
plt.clf()

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.plot(all_snrs, all_percentage,'b-')#, label = "SNR distribution")
#plt.plot(all_snrs, all_percentage, 'ro', label = "FAP = " + str(100*rank) + "%\nSNR = " + str(specificSNR))
#plt.yscale('log')
#plt.xscale('log')
plt.xlabel("SNR")
#plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
#plt.ylabel('Strain [Counts / sqrt(Hz)]')
plt.ylabel("False Alarm Probability [%]")
plt.ylim([0,100])
#plt.title("")
#legend = plt.legend(prop={'size':6})#, framealpha=0.5)
#legend.get_frame().set_alpha(0.5)
#plt.show()
plt.savefig(analysisDir + "/SNRvsFAP_all_clusters", bbox_inches = 'tight')
plt.clf()

plotTypeList = ["SNR", "Loudest Cluster", "cluster", "focused cluster", "sig map", "y map", "Xi snr map"]

plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster" : "rmap.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png", "cluster": "cluster_plot.png", "focused cluster": "cluster_focus_plot.png"}

#webFile = glueFileLocation(analysisDir, "highSNRpageDisplayTest.html")
webFile = "highSNRpageDisplayTest.html"

def getPlotPath(path):
    temp_path = path[::-1]
    temp_path = temp_path[temp_path.index("/") + 1:]
    #temp_path = temp_path[temp_path.index("/") + 1:]
    temp_path = temp_path[temp_path.index("/"):]
    return path[len(temp_path):]

all_clusters_paths = [getPlotPath(x[2]) for x in all_clusters_info]
plotRowOrder = all_clusters_paths

#highSNRsubDirs = dict((gsoutMats[sortedFilePaths[index]], ["Cluster SNR = " + str(sortedSNRvals[index])]) for index in reversed(range(N)))
highSNRsubDirs = dict((plotRowOrder[num], ["Cluster SNR = " + str(all_clusters_info[num][0])]) for num in range(len(all_clusters_info)))

webGen.make_display_page_v2("jobs", baseDir, highSNRsubDirs, "grandstochtrackOutput/plots", plotTypeList, plotTypeDict, webFile, plotRowOrder)
