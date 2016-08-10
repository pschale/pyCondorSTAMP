from __future__ import division
from optparse import OptionParser
from scanSNRlibV2 import *
import os
import pickle
from numpy import argsort, sqrt#, linspace
#from scipy.interpolate import spline
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
parser.set_defaults(reload_data = False)
parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to directory containing completed STAMP jobs to use for analysis",
                  metavar = "DIRECTORY")
parser.add_option("-s", "--simDir", dest = "simulationDirectory",
                  help = "Path to directory containing completed simulated STAMP jobs to use for analysis",
                  metavar = "DIRECTORY")
#parser.add_option("-r", "--simDir2", dest = "simulationDirectory2",
#                  help = "Path to second directory containing completed simulated STAMP jobs to use for analysis",
#                  metavar = "DIRECTORY")
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
parser.add_option("-E", "--eventSNRdir", dest="eventSNRdir",
                  help = "Path to data with event SNRs from open box search (separate by commas if multiple)")
parser.add_option("-P", "--pseudoEventSNRdir", dest="pseudoEventSNRdir",
                  help = "Path to data with event SNRs from open box search (separate by commas if multiple)")
parser.add_option("-m", "--maxLim", dest="maxLim")
parser.add_option("-n", "--minLim", dest="minLim")
#parser.add_option("-b", action="store_true", dest="burstegard")
#parser.add_option("-a", action="store_true", dest="all_clusters")
parser.add_option("-L", action="store_true", dest="pdf_latex_mode")
parser.add_option("-D", action="store_true", dest="dots")
parser.add_option("-R", action="store_true", dest="reload_data")

(options, args) = parser.parse_args()

print("NOTE: script ignores all files and directories starting with '.'")

print("WARNING: Script is currently not set up to handle directories with multiple files with the name base.")

def verbosePrint(string, switch = options.verbose):
    if switch:
        print(string)

print("Parsing commandline arguments")

def load_snr_object(base_dir):
    snr_file = glueFileLocation(base_dir, "SNR_data/SNR_data.txt")
    directory_exists = os.path.isfile(snr_file)
    if directory_exists and not options.reload_data:
        print("Loading previously saved data...")
        with open(snr_file, "rb") as infile:
            run_info = pickle.load(infile)
    else:
        if not directory_exists:
            os.mkdir(glueFileLocation(base_dir, "SNR_data"))
        run_info = search_run_info_no_alphas_v2(base_dir)
        with open(snr_file, "wb") as outfile:
           pickle.dump(run_info, outfile)
    return run_info

#def interp_line(x_data, y_data, points = 100):
#    y_interp = linspace(min(y_data), max(y_data), points)
#    x_interp = spline(y_data, x_data, y_interp)
#    return x_interp, y_interp

baseDir = options.targetDirectory
baseSimDirs = options.simulationDirectory
#baseSimDir2 = options.simulationDirectory2

eventSNRs = []
pseudoEventSNRs = []

print("Loading data...")
#runInfo = search_run_info_no_alphas_v2(baseDir)
runInfo = load_snr_object(baseDir)
print("Data loaded")
print("Loading simulated data...")
#simulatedRunInfo = [search_run_info_no_alphas_v2(x) for x in baseSimDirs.split(',')]
simulatedRunInfo = [load_snr_object(x) for x in baseSimDirs.split(',')]
#simulatedRunInfo = search_run_info_no_alphas(baseSimDir)
print("Simulated data loaded")
#print("Loading second simulated data...")
#simulatedRunInfo2 = search_run_info_no_alphas(baseSimDir2)
#print("Second simulated data loaded")
if options.eventSNRdir:
    print("Loading event data...")
    eventRunInfo = load_snr_object(options.eventSNRdir)
    print("Event data loaded")
if options.pseudoEventSNRdir:
    print("Loading pseudo event data...")
    pseudoEventRunInfo = load_snr_object(options.pseudoEventSNRdir)
    print("Pseudo event data loaded")

#loudestSNRs = runInfo.get_high_snrs()
print("Pulling snrs...")
allSNRs = runInfo.get_snrs()
allSimulatedSNRs = [x.get_snrs() for x in simulatedRunInfo]
if options.eventSNRdir:
    eventSNRs += eventRunInfo.get_snrs()
if options.pseudoEventSNRdir:
    pseudoEventSNRs += pseudoEventRunInfo.get_snrs()
#allSimulatedSNRs2 = simulatedRunInfo2.get_snrs()
#print(allSNRs)
#temp = runInfo.get_data()
print("Done")

allData = runInfo.get_data(False)
allDataSorted = [[group[2][jobNum], group[0][jobNum], group[1][jobNum]] for group in allData for jobNum in range(len(group[0]))]
sortedIndices = argsort([x[0] for x in allDataSorted])
allDataSorted = [allDataSorted[index] for index in sortedIndices]
allDataSorted = allDataSorted[::-1]

allSimulatedData = [x.get_data(False) for x in simulatedRunInfo]
allSimulatedDataSorted = [[[group[2][jobNum], group[0][jobNum], group[1][jobNum]] for group in x for jobNum in range(len(group[0]))] for x in allSimulatedData]
sortedSimulatedIndices = [argsort([x[0] for x in y]) for y in allSimulatedDataSorted]
allSimulatedDataSorted = [[allSimulatedDataSorted[x][index] for index in sortedSimulatedIndices[x]] for x in range(len(sortedSimulatedIndices))]
allSimulatedDataSorted = [x[::-1] for x in allSimulatedDataSorted]

#allSimulatedData2 = simulatedRunInfo2.get_data(False)
#allSimulatedDataSorted2 = [[group[2][jobNum], group[0][jobNum], group[1][jobNum]] for group in allSimulatedData2 for jobNum in range(len(group[0]))]
#sortedSimulatedIndices2 = argsort([x[0] for x in allSimulatedDataSorted2])
#allSimulatedDataSorted2 = [allSimulatedDataSorted2[index] for index in sortedSimulatedIndices2]
#allSimulatedDataSorted2 = allSimulatedDataSorted2[::-1]

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

for simNum in range(len(allSimulatedDataSorted)):
    fileName5 = "runDataSimulated_" + str(simNum) + ".txt"
    #output_text3 = "\n".join("\n".join(", ".join(str(x) for x in [group[2][jobNum], group[0][jobNum], group[1][jobNum]]) for jobNum in range(len(group[0]))) for group in allData)
    output_text5 = "\n".join(", ".join(str(x) for x in line) for line in allSimulatedDataSorted[simNum])#[::-1])
    with open(glueFileLocation(dir_name, fileName5), "w") as outfile:
        outfile.write(output_text5)

#fileName6 = "runDataSimulated2.txt"
#output_text3 = "\n".join("\n".join(", ".join(str(x) for x in [group[2][jobNum], group[0][jobNum], group[1][jobNum]]) for jobNum in range(len(group[0]))) for group in allData)
#output_text6 = "\n".join(", ".join(str(x) for x in line) for line in allSimulatedDataSorted2)#[::-1])
#with open(glueFileLocation(dir_name, fileName6), "w") as outfile:
#    outfile.write(output_text6)

sortedAllSNRs = allSNRs[:]
sortedAllSNRs.sort()
#all_percentage = [100 - (x)/len(sortedAllSNRs)*100 for x in range(len(sortedAllSNRs))]
all_percentage = [1 - (x)/len(sortedAllSNRs) for x in range(len(sortedAllSNRs))]

sortedAllSimulatedSNRs = [x[:] for x in allSimulatedSNRs]
for x in sortedAllSimulatedSNRs:
    x.sort()
#sortedAllSimulatedSNRs.sort()
#allSimulated_percentage = [100 - (x)/len(sortedAllSimulatedSNRs)*100 for x in range(len(sortedAllSNRs))]
allSimulated_percentage = [[1 - (x)/len(y) for x in range(len(y))] for y in sortedAllSimulatedSNRs]

#sortedAllSimulatedSNRs2 = allSimulatedSNRs2[:]
#sortedAllSimulatedSNRs2.sort()
#allSimulated_percentage2 = [1 - (x)/len(sortedAllSimulatedSNRs2) for x in range(len(sortedAllSNRs))]

numSimulations = len(sortedAllSimulatedSNRs)
numJobs = len(sortedAllSimulatedSNRs[0])
meanSimulatedSNR = [sum([sortedAllSimulatedSNRs[simIndex][jobIndex] for simIndex in range(numSimulations)])/numSimulations for jobIndex in range(numJobs)]
stDevSimulatedSNR = [sqrt(sum([(sortedAllSimulatedSNRs[simIndex][jobIndex] - meanSimulatedSNR[jobIndex])**2 for simIndex in range(numSimulations)])/numSimulations) for jobIndex in range(numJobs)]
sigmaOneSimSNRLow = [meanSimulatedSNR[jobIndex] - stDevSimulatedSNR[jobIndex] for jobIndex in range(numJobs)]
sigmaOneSimSNRHigh = [meanSimulatedSNR[jobIndex] + stDevSimulatedSNR[jobIndex] for jobIndex in range(numJobs)]
sigmaTwoSimSNRLow = [meanSimulatedSNR[jobIndex] - stDevSimulatedSNR[jobIndex]*2 for jobIndex in range(numJobs)]
sigmaTwoSimSNRHigh = [meanSimulatedSNR[jobIndex] + stDevSimulatedSNR[jobIndex]*2 for jobIndex in range(numJobs)]
sigmaThreeSimSNRLow = [meanSimulatedSNR[jobIndex] - stDevSimulatedSNR[jobIndex]*3 for jobIndex in range(numJobs)]
sigmaThreeSimSNRHigh = [meanSimulatedSNR[jobIndex] + stDevSimulatedSNR[jobIndex]*3 for jobIndex in range(numJobs)]

"""sigmaOneSimSNRLow_interp, all_percentage_interp = interp_line(sigmaOneSimSNRLow, all_percentage)
print(min(all_percentage_interp))
print(max(all_percentage_interp))
print(min(sigmaOneSimSNRLow))
print(max(sigmaOneSimSNRLow))
print(min(sigmaOneSimSNRLow_interp))
print(max(sigmaOneSimSNRLow_interp))
sigmaOneSimSNRHigh_interp, all_percentage_interp = interp_line(sigmaOneSimSNRHigh, all_percentage)
sigmaTwoSimSNRLow_interp, all_percentage_interp = interp_line(sigmaTwoSimSNRLow, all_percentage)
sigmaTwoSimSNRHigh_interp, all_percentage_interp = interp_line(sigmaTwoSimSNRHigh, all_percentage)
sigmaThreeSimSNRLow_interp, all_percentage_interp = interp_line(sigmaThreeSimSNRLow, all_percentage)
sigmaThreeSimSNRHigh_interp, all_percentage_interp = interp_line(sigmaThreeSimSNRHigh, all_percentage)"""

if options.eventSNR:
    eventSNRs += [float(x) for x in options.eventSNR.split(',')]
eventPercentages = [min([all_percentage[x] for x in range(len(all_percentage)) if sortedAllSNRs[x] <= y]) for y in eventSNRs]
pseudoEventPercentages = [min([all_percentage[x] for x in range(len(all_percentage)) if sortedAllSNRs[x] <= y]) for y in pseudoEventSNRs]
#else:
#    eventSNRs = []
#    eventPercentages = []

verbosePrint("Lowest SNR of time-shifted data: " + str(min(sortedAllSNRs)))
minimumSimSNRS = [min(x) for x in sortedAllSimulatedSNRs]
minimumSimSNRS.sort()
verbosePrint("Average lowest SNR of simulations: " + str(sum(minimumSimSNRS)/len(minimumSimSNRS)))
verbosePrint("Lowest low SNR of simulations: " + str(min(minimumSimSNRS)))
verbosePrint("Highest low SNR of simulations: " + str(max(minimumSimSNRS)))
verbosePrint("All lowest SNRs of simulations: " + str(minimumSimSNRS))

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
if options.dots:
    plt.plot(sortedAllSNRs, all_percentage,'b.-', label = "Background SNR Distribution")
    plt.plot(meanSimulatedSNR, all_percentage,'k.--', label = "Mean of Simulations")
    plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'g.-', label = "Monte Carlo Simulations", alpha = 0.3)
    if len(sortedAllSimulatedSNRs) > 1:
        for num in range(1,len(sortedAllSimulatedSNRs)):
            plt.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'g.-', alpha = 0.3)
    #plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g.--', label = "Monte Carlo Simulations")
    #plt.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g.--')
else:
    plt.plot(sortedAllSNRs, all_percentage,'b-', label = "Background SNR Distribution")
    plt.plot(meanSimulatedSNR, all_percentage,'k--', label = "Mean of Simulations")
    plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'g-', label = "Monte Carlo Simulations", alpha = 0.3)
    if len(sortedAllSimulatedSNRs) > 1:
        for num in range(1,len(sortedAllSimulatedSNRs)):
            plt.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'g-', alpha = 0.3)
    #plt.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g--')
if pseudoEventSNRs:
    plt.plot(pseudoEventSNRs, pseudoEventPercentages,'b^', label = "Zero-lag pseudo event\n(SNR = " + ", ".join(str(x) for x in pseudoEventSNRs) + " FAP = " + ", ".join(str(x) for x in pseudoEventPercentages) + ")")
if eventSNRs:
    plt.plot(eventSNRs, eventPercentages,'r*', label = "On-source event\n(SNR = " + ", ".join(str(x) for x in eventSNRs) + " FAP = " + ", ".join(str(x) for x in eventPercentages) + ")")
plt.xlabel("SNR")
#plt.ylim([0,100])
plt.ylim([0,1])
legend = plt.legend(prop={'size':12})#, framealpha=0.5)
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
    plt.plot(sortedAllSNRs, all_percentage,'b.-', label = "Background SNR Distribution", linewidth = 2)
    plt.plot(meanSimulatedSNR, all_percentage,'k.--', label = "Mean of Simulations")
    plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'g.-', label = "Monte Carlo Simulations", alpha = 0.3)
    if len(sortedAllSimulatedSNRs) > 1:
        for num in range(1,len(sortedAllSimulatedSNRs)):
            plt.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'g.-', alpha = 0.3)
    #plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g.--', label = "Monte Carlo Simulations")
    #plt.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g.--')
else:
    plt.plot(sortedAllSNRs, all_percentage,'b-', label = "Background SNR Distribution", linewidth = 1.5, zorder = 4)
    plt.plot(meanSimulatedSNR, all_percentage,'k--', label = "Mean of Simulations", zorder = 5)
    #plt.plot(sigmaOneSimSNRLow, all_percentage,'k-', alpha = 0.7)
    #plt.plot(sigmaOneSimSNRHigh, all_percentage,'k-', alpha = 0.7)
    #plt.plot(sigmaTwoSimSNRLow, all_percentage,'k-', alpha = 0.5)
    #plt.plot(sigmaTwoSimSNRHigh, all_percentage,'k-', alpha = 0.5)
    #plt.plot(sigmaThreeSimSNRLow, all_percentage,'k-', alpha = 0.3)
    #plt.plot(sigmaThreeSimSNRHigh, all_percentage,'k-', alpha = 0.3)
    #plt.fill_between(x, y3, y4, color='grey', alpha='0.5')
    """plt.fill_betweenx(all_percentage, sigmaOneSimSNRLow, sigmaOneSimSNRHigh, color='grey', alpha='0.7', zorder = 3)
    plt.fill_betweenx(all_percentage, sigmaTwoSimSNRLow, sigmaOneSimSNRLow, color='grey', alpha='0.5', zorder = 3)
    plt.fill_betweenx(all_percentage, sigmaTwoSimSNRHigh, sigmaOneSimSNRHigh, color='grey', alpha='0.5', zorder = 3)
    plt.fill_betweenx(all_percentage, sigmaTwoSimSNRLow, sigmaThreeSimSNRLow, color='grey', alpha='0.3', zorder = 3)
    plt.fill_betweenx(all_percentage, sigmaTwoSimSNRHigh, sigmaThreeSimSNRHigh, color='grey', alpha='0.3', zorder = 3)"""
    #plt.fill(sigmaOneSimSNRLow + sigmaOneSimSNRHigh, all_percentage+all_percentage, edgecolor = None, color=0.5, alpha='0.5')
    plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'g-', label = "Monte Carlo Simulations", alpha = 0.3, zorder = 3)
    if len(sortedAllSimulatedSNRs) > 1:
        for num in range(1,len(sortedAllSimulatedSNRs)):
            plt.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'g-', alpha = 0.3, zorder = 3)
    #plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g--', label = "Monte Carlo Simulations")
    #plt.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g--')
if pseudoEventSNRs:
    plt.plot(pseudoEventSNRs, pseudoEventPercentages,'b^', label = "Zero-lag pseudo event\n(SNR = " + ", ".join(str(x) for x in pseudoEventSNRs) + " FAP = " + ", ".join(str(x) for x in pseudoEventPercentages) + ")")
if eventSNRs:
    eventSnr, = plt.plot(eventSNRs, eventPercentages,'r*', zorder = 6, markersize = 8, label = "On-source event\n(SNR = " + ", ".join(str(x) for x in eventSNRs) + " FAP = " + ", ".join(str(x) for x in eventPercentages) + ")")
plt.xlabel("SNR")
ymin = min(all_percentage)
plt.ylim([ymin,1])
if options.maxLim:
    plt.ylim([float(options.minLim),1])
if options.minLim:
    plt.xlim([5,float(options.maxLim)])
plt.yscale('log')
legend = plt.legend(prop={'size':12})
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

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
if options.dots:
    plt.plot(sortedAllSNRs, all_percentage,'b.-', label = "Background SNR Distribution", linewidth = 2)
    plt.plot(meanSimulatedSNR, all_percentage,'k.--', label = "Mean of Simulations")
    #simDist, = plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'g.-', label = "Monte Carlo Simulations", alpha = 0.3)
    #if len(sortedAllSimulatedSNRs) > 1:
    #    for num in range(1,len(sortedAllSimulatedSNRs)):
    #        plt.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'g.-', alpha = 0.3)
    #plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g.--', label = "Monte Carlo Simulations")
    #plt.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g.--')
else:
    plt.plot(sortedAllSNRs, all_percentage,'b-', label = "Background SNR Distribution", linewidth = 1.5, zorder = 4)
    plt.plot(meanSimulatedSNR, all_percentage,'k--', label = "Mean of Simulations", zorder = 5)
    #plt.plot(sigmaOneSimSNRLow, all_percentage,'k-', alpha = 0.7)
    #plt.plot(sigmaOneSimSNRHigh, all_percentage,'k-', alpha = 0.7)
    #plt.plot(sigmaTwoSimSNRLow, all_percentage,'k-', alpha = 0.5)
    #plt.plot(sigmaTwoSimSNRHigh, all_percentage,'k-', alpha = 0.5)
    #plt.plot(sigmaThreeSimSNRLow, all_percentage,'k-', alpha = 0.3)
    #plt.plot(sigmaThreeSimSNRHigh, all_percentage,'k-', alpha = 0.3)
    #plt.fill_between(x, y3, y4, color='grey', alpha='0.5')
    plt.fill_betweenx(all_percentage, sigmaOneSimSNRLow, sigmaOneSimSNRHigh, color='grey', alpha='0.7', zorder = 3)
    plt.fill_betweenx(all_percentage, sigmaTwoSimSNRLow, sigmaOneSimSNRLow, color='grey', alpha='0.5', zorder = 3)
    plt.fill_betweenx(all_percentage, sigmaTwoSimSNRHigh, sigmaOneSimSNRHigh, color='grey', alpha='0.5', zorder = 3)
    plt.fill_betweenx(all_percentage, sigmaTwoSimSNRLow, sigmaThreeSimSNRLow, color='grey', alpha='0.3', zorder = 3)
    plt.fill_betweenx(all_percentage, sigmaTwoSimSNRHigh, sigmaThreeSimSNRHigh, color='grey', alpha='0.3', zorder = 3)
    #plt.fill(sigmaOneSimSNRLow + sigmaOneSimSNRHigh, all_percentage+all_percentage, edgecolor = None, color=0.5, alpha='0.5')
    #simDist, = plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'g-', label = "Monte Carlo Simulations", alpha = 0.5)
    #if len(sortedAllSimulatedSNRs) > 1:
    #    for num in range(1,len(sortedAllSimulatedSNRs)):
    #        plt.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'g-', alpha = 0.5)
    #plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g--', label = "Monte Carlo Simulations")
    #plt.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g--')
if pseudoEventSNRs:
    plt.plot(pseudoEventSNRs, pseudoEventPercentages,'b^', label = "Zero-lag pseudo event\n(SNR = " + ", ".join(str(x) for x in pseudoEventSNRs) + " FAP = " + ", ".join(str(x) for x in pseudoEventPercentages) + ")")
if eventSNRs:
    plt.plot(eventSNRs, eventPercentages,'r*', zorder = 6, markersize = 8, label = "On-source event\n(SNR = " + ", ".join(str(x) for x in eventSNRs) + " FAP = " + ", ".join(str(x) for x in eventPercentages) + ")")
plt.xlabel("SNR")
ymin = min(all_percentage)
plt.ylim([ymin,1])
if options.maxLim:
    plt.ylim([float(options.minLim),1])
if options.minLim:
    plt.xlim([5,float(options.maxLim)])
plt.yscale('log')
legend = plt.legend(prop={'size':12})
legend.get_frame().set_alpha(0.5)
if options.pdf_latex_mode:
    plt.rc('text', usetex = True)
    plt.rc('font', family = 'sarif')
    plt.ylabel("False Alarm Probability")
    plt.savefig(dir_name + "/SNRvsFAP_all_clusters_semilogy_average.pdf", bbox_inches = 'tight', format='pdf')
else:
    plt.ylabel("False Alarm Probability")
    plt.savefig(dir_name + "/SNRvsFAP_all_clusters_semilogy_average", bbox_inches = 'tight')
plt.clf()

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
if options.dots:
    plt.plot(sortedAllSNRs, all_percentage,'b.-', label = "Background SNR Distribution", linewidth = 2)
    plt.plot(meanSimulatedSNR, all_percentage,'k.--', label = "Mean of Simulations")
    plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'g.-', label = "Monte Carlo Simulations", alpha = 0.3)
    if len(sortedAllSimulatedSNRs) > 1:
        for num in range(1,len(sortedAllSimulatedSNRs)):
            plt.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'g.-', alpha = 0.3)
    plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g.--', label = "Monte Carlo Simulations")
    plt.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g.--')
else:
    plt.plot(sortedAllSNRs, all_percentage,'b-', label = "Background SNR Distribution", linewidth = 1.5, zorder = 5)
    plt.plot(meanSimulatedSNR, all_percentage,'k--', label = "Mean of Simulations", zorder = 6)
    #plt.plot(sigmaOneSimSNRLow, all_percentage,'k-', alpha = 0.7)
    #plt.plot(sigmaOneSimSNRHigh, all_percentage,'k-', alpha = 0.7)
    #plt.plot(sigmaTwoSimSNRLow, all_percentage,'k-', alpha = 0.5)
    #plt.plot(sigmaTwoSimSNRHigh, all_percentage,'k-', alpha = 0.5)
    #plt.plot(sigmaThreeSimSNRLow, all_percentage,'k-', alpha = 0.3)
    #plt.plot(sigmaThreeSimSNRHigh, all_percentage,'k-', alpha = 0.3)
    #plt.fill_between(x, y3, y4, color='grey', alpha='0.5')
    plt.fill_betweenx(all_percentage, sigmaOneSimSNRLow, sigmaOneSimSNRHigh, color='grey', alpha='0.7', zorder = 3)
    plt.fill_betweenx(all_percentage, sigmaTwoSimSNRLow, sigmaOneSimSNRLow, color='grey', alpha='0.5', zorder = 3)
    plt.fill_betweenx(all_percentage, sigmaTwoSimSNRHigh, sigmaOneSimSNRHigh, color='grey', alpha='0.5', zorder = 3)
    plt.fill_betweenx(all_percentage, sigmaTwoSimSNRLow, sigmaThreeSimSNRLow, color='grey', alpha='0.3', zorder = 3)
    plt.fill_betweenx(all_percentage, sigmaTwoSimSNRHigh, sigmaThreeSimSNRHigh, color='grey', alpha='0.3', zorder = 3)
    plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'r-', label = "Monte Carlo Simulations", alpha = 0.5, zorder = 4)
    if len(sortedAllSimulatedSNRs) > 1:
        for num in range(1,len(sortedAllSimulatedSNRs)):
            plt.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'r-', alpha = 0.5, zorder = 4)
if pseudoEventSNRs:
    plt.plot(pseudoEventSNRs, pseudoEventPercentages,'b^', label = "Zero-lag pseudo event\n(SNR = " + ", ".join(str(x) for x in pseudoEventSNRs) + " FAP = " + ", ".join(str(x) for x in pseudoEventPercentages) + ")")
if eventSNRs:
    plt.plot(eventSNRs, eventPercentages,'r*', zorder = 6, markersize = 8, label = "On-source event\n(SNR = " + ", ".join(str(x) for x in eventSNRs) + " FAP = " + ", ".join(str(x) for x in eventPercentages) + ")")
plt.xlabel("SNR")
ymin = min(all_percentage)
plt.ylim([ymin,1])
plt.yscale('log')
legend = plt.legend(prop={'size':12})
legend.get_frame().set_alpha(0.5)
if options.pdf_latex_mode:
    plt.rc('text', usetex = True)
    plt.rc('font', family = 'sarif')
    plt.ylabel("False Alarm Probability")
    plt.savefig(dir_name + "/SNRvsFAP_all_clusters_semilogy_average_2.pdf", bbox_inches = 'tight', format='pdf')
else:
    plt.ylabel("False Alarm Probability")
    plt.savefig(dir_name + "/SNRvsFAP_all_clusters_semilogy_average_2", bbox_inches = 'tight')
plt.clf()
