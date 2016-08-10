from __future__ import division
from optparse import OptionParser
from scanSNRlibV2 import *
from numpy import argsort
#import webpageGenerateLib as webGen
from plotClustersLib import returnMatrixFilePath, plotClusterInfo_v2, getPixelInfo, getFrequencyInfo
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
#plt.rcParams['legend.numpoints'] = 1

parser = OptionParser()
parser.set_defaults(verbose = False)
#parser.set_defaults(burstegard = False)
#parser.set_defaults(all_clusters = False)
parser.set_defaults(pdf_latex_mode = False)
parser.set_defaults(dots = False)
parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to directory containing completed STAMP jobs to use for analysis",
                  metavar = "DIRECTORY")
parser.add_option("-s", "--simDir", dest = "simulationDirectory",
                  help = "Path to directory containing completed simulated STAMP jobs to use for analysis",
                  metavar = "DIRECTORY")
parser.add_option("-o", "--outputDir", dest = "outputDirectory",
                  help = "Path to directory to create to contain background plots",
                  metavar = "DIRECTORY")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                  help = "Prints internal status messages to terminal as script runs")
#parser.add_option("-N", "--numberRows", dest = "numberRows",
#                  help = "Limits number of rows on generated web page",
#                  metavar = "INTEGER")
parser.add_option("-e", "--eventSNR", dest="eventSNR",
                  help = "Option to set event SNRs from open box search (separate by commas if multiple)")
#parser.add_option("-b", action="store_true", dest="burstegard")
#parser.add_option("-a", action="store_true", dest="all_clusters")
parser.add_option("-L", action="store_true", dest="pdf_latex_mode")
parser.add_option("-D", action="store_true", dest="dots")

(options, args) = parser.parse_args()

print("NOTE: script ignores all files and directories starting with '.'")

print("WARNING: Script is currently not set up to handle directories with multiple files with the name base.")

def verbosePrint(string, switch = options.verbose):
    if switch:
        print(string)

print("Parsing commandline arguments")

baseDir = options.targetDirectory
baseSimDir = options.simulationDirectory

print("Loading data...")
runInfo = search_run_info_no_alphas(baseDir)
print("Data loaded")
print("Loading simulated data...")
simulatedRunInfo = search_run_info_no_alphas(baseSimDir)
print("Simulated data loaded")

#loudestSNRs = runInfo.get_high_snrs()
print("Pulling snrs...")
allSNRs = runInfo.get_snrs()
allSimulatedSNRs = simulatedRunInfo.get_snrs()
#print(allSNRs)
#temp = runInfo.get_data()
print("Done")

allData = runInfo.get_data(False)
allDataSorted = [[group[2][jobNum], group[0][jobNum], group[1][jobNum]] for group in allData for jobNum in range(len(group[0]))]
sortedIndices = argsort([x[0] for x in allDataSorted])
allDataSorted = [allDataSorted[index] for index in sortedIndices]
allDataSorted = allDataSorted[::-1]

allSimulatedData = simulatedRunInfo.get_data(False)
allSimulatedDataSorted = [[group[2][jobNum], group[0][jobNum], group[1][jobNum]] for group in allSimulatedData for jobNum in range(len(group[0]))]
sortedSimulatedIndices = argsort([x[0] for x in allSimulatedDataSorted])
allSimulatedDataSorted = [allSimulatedDataSorted[index] for index in sortedSimulatedIndices]
allSimulatedDataSorted = allSimulatedDataSorted[::-1]

#print(temp[1][0])
#print(temp[1][2])

# create directory
dir_name = glueFileLocation(options.outputDirectory, "simulated_vs_actual_SNR_comparison")
dir_name = create_dir(dir_name)

# create list of highest SNR jobs
"""fileName = "LoudestClusterInfo.txt"
output_text = "\n".join(", ".join(str(y) for y in [x[1], x[0], x[2]]) for x in loudestSNRs)
with open(glueFileLocation(dir_name, fileName), "w") as outfile:
    outfile.write(output_text)"""

# create list of all snrs jobs
"""fileName2 = "AllSnrs.txt"
output_text2 = "\n\n".join(str(x) for x in allSNRs)
with open(glueFileLocation(dir_name, fileName2), "w") as outfile:
    outfile.write(output_text2)"""

# create list of data
"""fileName3 = "runData_group_separated.txt"
print(allData[0])
print(allData[0][0])
#output_text3 = "\n".join("\n".join(", ".join(str(x) for x in [group[2][jobNum], group[0][jobNum], group[1][jobNum]]) for jobNum in range(len(group[0]))) for group in allData)
output_text3 = "\n\n".join("\n".join(", ".join(str(x) for x in [group[2][jobNum], group[0][jobNum], group[1][jobNum]]) for jobNum in range(len(group[0]))) for group in allData)
with open(glueFileLocation(dir_name, fileName3), "w") as outfile:
    outfile.write(output_text3)"""

fileName4 = "runDataActual.txt"
#output_text3 = "\n".join("\n".join(", ".join(str(x) for x in [group[2][jobNum], group[0][jobNum], group[1][jobNum]]) for jobNum in range(len(group[0]))) for group in allData)
output_text4 = "\n".join(", ".join(str(x) for x in line) for line in allDataSorted)#[::-1])
with open(glueFileLocation(dir_name, fileName4), "w") as outfile:
    outfile.write(output_text4)

fileName5 = "runDataSimulated.txt"
#output_text3 = "\n".join("\n".join(", ".join(str(x) for x in [group[2][jobNum], group[0][jobNum], group[1][jobNum]]) for jobNum in range(len(group[0]))) for group in allData)
output_text5 = "\n".join(", ".join(str(x) for x in line) for line in allSimulatedDataSorted)#[::-1])
with open(glueFileLocation(dir_name, fileName5), "w") as outfile:
    outfile.write(output_text5)

# create plot of backgrounds based on loudest clusters (todo)
"""sortedLoudestSNRs = [x[1] for x in loudestSNRs]
sortedLoudestSNRs.sort()
loudest_percentage = [100 - (x)/len(sortedLoudestSNRs)*100 for x in range(len(sortedLoudestSNRs))]"""

sortedAllSNRs = allSNRs[:]
sortedAllSNRs.sort()
#all_percentage = [100 - (x)/len(sortedAllSNRs)*100 for x in range(len(sortedAllSNRs))]
all_percentage = [1 - (x)/len(sortedAllSNRs) for x in range(len(sortedAllSNRs))]

sortedAllSimulatedSNRs = allSimulatedSNRs[:]
sortedAllSimulatedSNRs.sort()
#allSimulated_percentage = [100 - (x)/len(sortedAllSimulatedSNRs)*100 for x in range(len(sortedAllSNRs))]
allSimulated_percentage = [1 - (x)/len(sortedAllSimulatedSNRs) for x in range(len(sortedAllSNRs))]

if options.eventSNR:
    eventSNRs = [float(x) for x in options.eventSNR.split(',')]
    eventPercentages = [max([all_percentage[x] for x in range(len(all_percentage)) if sortedAllSNRs[x] <= y]) for y in eventSNRs]
else:
    eventSNRs = []
    eventPercentages = []

"""plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.plot(sortedLoudestSNRs, loudest_percentage,'b-')#, label = "SNR distribution")
plt.xlabel("SNR")
plt.ylabel("False Alarm Probability [%]")
plt.ylim([0,100])
plt.savefig(dir_name + "/SNRvsFAP_loudest_clusters", bbox_inches = 'tight')
plt.clf()"""

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
if options.dots:
    plt.plot(sortedAllSNRs, all_percentage,'b.-', label = "SNR distribution")
    plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g.--', label = "Monte Carlo Simulations")
else:
    plt.plot(sortedAllSNRs, all_percentage,'b-', label = "SNR distribution")
    plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g--', label = "Monte Carlo Simulations")
if eventSNRs:
    plt.plot(eventSNRs, eventPercentages,'gx', label = "Event SNR")
plt.xlabel("SNR")
#plt.ylim([0,100])
plt.ylim([0,1])
legend = plt.legend(prop={'size':6})#, framealpha=0.5)
legend.get_frame().set_alpha(0.5)
if options.pdf_latex_mode:
    plt.rc('text', usetex = True)
    plt.rc('font', family = 'sarif')
    #plt.ylabel("False Alarm Probability [\%]")
    plt.ylabel("False Alarm Probability")
    plt.savefig(dir_name + "/SNRvsFAP_all_clusters.pdf", bbox_inches = 'tight', format='pdf')
else:
    #plt.ylabel("False Alarm Probability [%]")
    plt.ylabel("False Alarm Probability")
    plt.savefig(dir_name + "/SNRvsFAP_all_clusters", bbox_inches = 'tight')
plt.clf()

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
if options.dots:
    plt.plot(sortedAllSNRs, all_percentage,'b.-', label = "SNR distribution")
    plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g.--', label = "Monte Carlo Simulations")
else:
    plt.plot(sortedAllSNRs, all_percentage,'b-', label = "SNR distribution")
    plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g--', label = "Monte Carlo Simulations")
if eventSNRs:
    plt.plot(eventSNRs, eventPercentages,'gx', label = "Event SNR")
plt.xlabel("SNR")
ymin = min(all_percentage)
plt.ylim([ymin,1])
plt.yscale('log')
legend = plt.legend(prop={'size':6})
legend.get_frame().set_alpha(0.5)
if options.pdf_latex_mode:
    plt.rc('text', usetex = True)
    plt.rc('font', family = 'sarif')
    plt.ylabel("False Alarm Probability")
    plt.savefig(dir_name + "/SNRvsFAP_all_clusters_semilogy.pdf", bbox_inches = 'tight', format='pdf')
else:
    plt.ylabel("False Alarm Probability")
    plt.savefig(dir_name + "/SNRvsFAP_all_clusters_semilogy", bbox_inches = 'tight')
plt.clf()

"""if options.burstegard:
    plotTypeList = ["SNR", "Largest Cluster", "All Clusters", "cluster", "focused cluster", "sig map", "y map", "Xi snr map"]
    plotTypeDict = {"SNR" : "snr.png", "Largest Cluster" : "large_cluster.png", "All Clusters": "all_clusters.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png", "cluster": "cluster_plot.png", "focused cluster": "cluster_focus_plot.png"}
elif options.all_clusters:
    plotTypeList = ["SNR", "Loudest Cluster (stochtrack)", "Largest Cluster (burstegard)", "All Clusters (burstegard)", "cluster", "focused cluster", "sig map", "y map", "Xi snr map"]
    plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster (stochtrack)" : "rmap.png", "Largest Cluster (burstegard)" : "large_cluster.png", "All Clusters (burstegard)": "all_clusters.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png", "cluster": "cluster_plot.png", "focused cluster": "cluster_focus_plot.png"}
else:
    plotTypeList = ["SNR", "Loudest Cluster", "cluster", "focused cluster", "sig map", "y map", "Xi snr map"]
    plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster" : "rmap.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png", "cluster": "cluster_plot.png", "focused cluster": "cluster_focus_plot.png"}

webFile = "highSNRpageDisplayTest.html"
"""

"""def getPlotPath(path):
    temp_path = path[::-1]
    temp_path = temp_path[temp_path.index("/") + 1:]
    #temp_path = temp_path[temp_path.index("/") + 1:]
    temp_path = temp_path[temp_path.index("/"):]
    return path[len(temp_path):]

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
"""
