from __future__ import division
from optparse import OptionParser
from scanSNRlibV2 import *
from numpy import argsort
import webpageGenerateLib as webGen
from plotClustersLib import returnMatrixFilePath, plotClusterInfo_v2, getPixelInfo, getFrequencyInfo
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['legend.numpoints'] = 1

parser = OptionParser()
parser.set_defaults(verbose = False)
parser.set_defaults(burstegard = False)
parser.set_defaults(all_clusters = False)
parser.set_defaults(make_plots = True)
parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to directory containing completed STAMP jobs to use for analysis",
                  metavar = "DIRECTORY")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                  help = "Prints internal status messages to terminal as script runs")
parser.add_option("-N", "--numberRows", dest = "numberRows",
                  help = "Limits number of rows on generated web page",
                  metavar = "INTEGER")
parser.add_option("-b", action="store_true", dest="burstegard")
parser.add_option("-a", action="store_true", dest="all_clusters")
parser.add_option("-n", action="store_false", dest="make_plots",
                 help = "Suppresses creation of python cluster plots")

(options, args) = parser.parse_args()

print("NOTE: script ignores all files and directories starting with '.'")

print("WARNING: Script is currently not set up to handle directories with multiple files with the name base.")

def verbosePrint(string, switch = options.verbose):
    if switch:
        print(string)

baseDir = options.targetDirectory
runInfo = search_run_info_no_alphas(baseDir)

loudestSNRs = runInfo.get_high_snrs()
allSNRs = runInfo.get_snrs()
print(allSNRs)
#temp = runInfo.get_data()
allData = runInfo.get_data(False)
allDataSorted = [[group[2][jobNum], group[0][jobNum], group[1][jobNum]] for group in allData for jobNum in range(len(group[0]))]
sortedIndices = argsort([x[0] for x in allDataSorted])
allDataSorted = [allDataSorted[index] for index in sortedIndices]
allDataSorted = allDataSorted[::-1]
print(allData)
#print(temp[1][0])
#print(temp[1][2])

# create directory
dir_name = glueFileLocation(baseDir, "basic_snr_info")
create_dir(dir_name)

# create list of highest SNR jobs
fileName = "LoudestClusterInfo.txt"
output_text = "\n".join(", ".join(str(y) for y in [x[1], x[0], x[2]]) for x in loudestSNRs)
with open(glueFileLocation(dir_name, fileName), "w") as outfile:
    outfile.write(output_text)

# create list of all snrs jobs
fileName2 = "AllSnrs.txt"
output_text2 = "\n\n".join(str(x) for x in allSNRs)
with open(glueFileLocation(dir_name, fileName2), "w") as outfile:
    outfile.write(output_text2)

# create list of data
fileName3 = "runData_group_separated.txt"
print(allData[0])
print(allData[0][0])
#output_text3 = "\n".join("\n".join(", ".join(str(x) for x in [group[2][jobNum], group[0][jobNum], group[1][jobNum]]) for jobNum in range(len(group[0]))) for group in allData)
output_text3 = "\n\n".join("\n".join(", ".join(str(x) for x in [group[2][jobNum], group[0][jobNum], group[1][jobNum]]) for jobNum in range(len(group[0]))) for group in allData)
with open(glueFileLocation(dir_name, fileName3), "w") as outfile:
    outfile.write(output_text3)

fileName4 = "runData.txt"
#output_text3 = "\n".join("\n".join(", ".join(str(x) for x in [group[2][jobNum], group[0][jobNum], group[1][jobNum]]) for jobNum in range(len(group[0]))) for group in allData)
output_text4 = "\n".join(", ".join(str(x) for x in line) for line in allDataSorted)#[::-1])
with open(glueFileLocation(dir_name, fileName4), "w") as outfile:
    outfile.write(output_text4)

# create plot of backgrounds based on loudest clusters (todo)
sortedLoudestSNRs = [x[1] for x in loudestSNRs]
sortedLoudestSNRs.sort()
loudest_percentage = [1 - (x)/len(sortedLoudestSNRs) for x in range(len(sortedLoudestSNRs))]

sortedAllSNRs = allSNRs[:]
sortedAllSNRs.sort()
all_percentage = [1 - (x)/len(sortedAllSNRs) for x in range(len(sortedAllSNRs))]

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.plot(sortedLoudestSNRs, loudest_percentage,'b-')#, label = "SNR distribution")
plt.xlabel("SNR")
plt.ylabel("False Alarm Probability")
plt.ylim([0,1])
plt.savefig(dir_name + "/SNRvsFAP_loudest_clusters", bbox_inches = 'tight')
plt.clf()

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.plot(sortedAllSNRs, all_percentage,'b-')#, label = "SNR distribution")
plt.xlabel("SNR")
plt.ylabel("False Alarm Probability")
plt.ylim([0,1])
plt.savefig(dir_name + "/SNRvsFAP_all_clusters", bbox_inches = 'tight')
plt.clf()

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.plot(sortedAllSNRs, all_percentage,'b-')#, label = "SNR distribution")
plt.xlabel("SNR")
plt.ylabel("False Alarm Probability")
ymin = min(all_percentage)
plt.ylim([ymin,1])
plt.yscale('log')
plt.savefig(dir_name + "/SNRvsFAP_all_clusters_semilogy", bbox_inches = 'tight')
plt.clf()

if options.burstegard:
    plotTypeList = ["SNR", "Largest Cluster", "All Clusters", "cluster", "focused cluster", "sig map", "y map", "Xi snr map"]
    plotTypeDict = {"SNR" : "snr.png", "Largest Cluster" : "large_cluster.png", "All Clusters": "all_clusters.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png", "cluster": "cluster_plot.png", "focused cluster": "cluster_focus_plot.png"}
elif options.all_clusters:
    plotTypeList = ["SNR", "Loudest Cluster (stochtrack)", "Largest Cluster (burstegard)", "All Clusters (burstegard)", "cluster", "focused cluster", "sig map", "y map", "Xi snr map"]
    plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster (stochtrack)" : "rmap.png", "Largest Cluster (burstegard)" : "large_cluster.png", "All Clusters (burstegard)": "all_clusters.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png", "cluster": "cluster_plot.png", "focused cluster": "cluster_focus_plot.png"}
else:
    plotTypeList = ["SNR", "Loudest Cluster", "cluster", "focused cluster", "sig map", "y map", "Xi snr map"]
    plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster" : "rmap.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png", "cluster": "cluster_plot.png", "focused cluster": "cluster_focus_plot.png"}

webFile = "highSNRpageDisplayTest.html"

def getPlotPath(path):
    temp_path = path[::-1]
    temp_path = temp_path[temp_path.index("/") + 1:]
    #temp_path = temp_path[temp_path.index("/") + 1:]
    temp_path = temp_path[temp_path.index("/"):]
    return path[len(temp_path):]

if options.make_plots:
    plotRowOrder = [getPlotPath(x[2]) for x in allDataSorted]

    highSNRsubDirs = dict((plotRowOrder[num], ["Cluster SNR = " + str(allDataSorted[num][0])]) for num in range(len(allDataSorted)))

    if options.numberRows:
        numberPages = int(len(plotRowOrder)/int(options.numberRows))
        for x in range(numberPages):
            webGen.make_display_page_v2("jobs", baseDir, highSNRsubDirs, "grandstochtrackOutput/plots", plotTypeList, plotTypeDict, webFile + "_" + str(x+1), plotRowOrder[x*int(options.numberRows):(x+1)*int(options.numberRows)])
    else:
        webGen.make_display_page_v2("jobs", baseDir, highSNRsubDirs, "grandstochtrackOutput/plots", plotTypeList, plotTypeDict, webFile, plotRowOrder)

    allDataSortedNonZero = [x for x in allDataSorted if x[0] > 0]

    stochDataFiles = [returnMatrixFilePath("bknd_", x[2] + "/grandstochtrackOutput") for x in allDataSortedNonZero]
    #mapDataFiles = [returnMatrixFilePath("map_", x[2] + "/grandstochtrackOutput") for x in allDataSortedNonZero]
    pixelInfo = [getPixelInfo(x[2] + "/grandstochtrackOutput", "pixel_deltaT.txt", "doOverlap.txt") for x in allDataSortedNonZero]
    frequencyInfo = [getFrequencyInfo(x[2] + "/grandstochtrackOutput", "frequencyWindow.txt", "deltaF.txt") for x in allDataSortedNonZero]
    plotDirs = [glueFileLocation(x[2], "grandstochtrackOutput/plots") for x in allDataSortedNonZero]

    #clusterData = [plotClusterInfo(val, mapDataFiles[num], plotDirs[num], options.burstegard) for num, val in enumerate(stochDataFiles)]
    clusterData = [plotClusterInfo_v2(val, pixelInfo[num], frequencyInfo[num], plotDirs[num], options.burstegard) for num, val in enumerate(stochDataFiles)]
