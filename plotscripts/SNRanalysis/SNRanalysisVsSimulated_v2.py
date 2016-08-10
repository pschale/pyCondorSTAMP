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
parser.add_option("-r", "--simDir2", dest = "simulationDirectory2",
                  help = "Path to second directory containing completed simulated STAMP jobs to use for analysis",
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
baseSimDir2 = options.simulationDirectory2

print("Loading data...")
runInfo = search_run_info_no_alphas(baseDir)
print("Data loaded")
print("Loading simulated data...")
simulatedRunInfo = search_run_info_no_alphas(baseSimDir)
print("Simulated data loaded")
print("Loading second simulated data...")
simulatedRunInfo2 = search_run_info_no_alphas(baseSimDir2)
print("Second simulated data loaded")

#loudestSNRs = runInfo.get_high_snrs()
print("Pulling snrs...")
allSNRs = runInfo.get_snrs()
allSimulatedSNRs = simulatedRunInfo.get_snrs()
allSimulatedSNRs2 = simulatedRunInfo2.get_snrs()
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

allSimulatedData2 = simulatedRunInfo2.get_data(False)
allSimulatedDataSorted2 = [[group[2][jobNum], group[0][jobNum], group[1][jobNum]] for group in allSimulatedData2 for jobNum in range(len(group[0]))]
sortedSimulatedIndices2 = argsort([x[0] for x in allSimulatedDataSorted2])
allSimulatedDataSorted2 = [allSimulatedDataSorted2[index] for index in sortedSimulatedIndices2]
allSimulatedDataSorted2 = allSimulatedDataSorted2[::-1]

#print(temp[1][0])
#print(temp[1][2])

# create directory
dir_name = glueFileLocation(options.outputDirectory, "simulated_vs_actual_SNR_comparison")
dir_name = create_dir(dir_name)

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

fileName6 = "runDataSimulated2.txt"
#output_text3 = "\n".join("\n".join(", ".join(str(x) for x in [group[2][jobNum], group[0][jobNum], group[1][jobNum]]) for jobNum in range(len(group[0]))) for group in allData)
output_text6 = "\n".join(", ".join(str(x) for x in line) for line in allSimulatedDataSorted2)#[::-1])
with open(glueFileLocation(dir_name, fileName6), "w") as outfile:
    outfile.write(output_text6)

sortedAllSNRs = allSNRs[:]
sortedAllSNRs.sort()
#all_percentage = [100 - (x)/len(sortedAllSNRs)*100 for x in range(len(sortedAllSNRs))]
all_percentage = [1 - (x)/len(sortedAllSNRs) for x in range(len(sortedAllSNRs))]

sortedAllSimulatedSNRs = allSimulatedSNRs[:]
sortedAllSimulatedSNRs.sort()
#allSimulated_percentage = [100 - (x)/len(sortedAllSimulatedSNRs)*100 for x in range(len(sortedAllSNRs))]
allSimulated_percentage = [1 - (x)/len(sortedAllSimulatedSNRs) for x in range(len(sortedAllSNRs))]

sortedAllSimulatedSNRs2 = allSimulatedSNRs2[:]
sortedAllSimulatedSNRs2.sort()
allSimulated_percentage2 = [1 - (x)/len(sortedAllSimulatedSNRs2) for x in range(len(sortedAllSNRs))]

if options.eventSNR:
    eventSNRs = [float(x) for x in options.eventSNR.split(',')]
    eventPercentages = [max([all_percentage[x] for x in range(len(all_percentage)) if sortedAllSNRs[x] <= y]) for y in eventSNRs]
else:
    eventSNRs = []
    eventPercentages = []

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
if options.dots:
    plt.plot(sortedAllSNRs, all_percentage,'b.-', label = "SNR distribution")
    plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g.--', label = "Monte Carlo Simulations")
    plt.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g.--')
else:
    plt.plot(sortedAllSNRs, all_percentage,'b-', label = "SNR distribution")
    plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g--', label = "Monte Carlo Simulations")
    plt.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g--')
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
    plt.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g.--')
else:
    plt.plot(sortedAllSNRs, all_percentage,'b-', label = "SNR distribution")
    plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g--', label = "Monte Carlo Simulations")
    plt.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g--')
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
