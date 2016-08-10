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
parser.set_defaults(burstegard = False)
parser.set_defaults(all_clusters = False)
parser.set_defaults(pdf_latex_mode = False)
parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to directory containing completed STAMP jobs to use for analysis (if multiple, separate with ','",
                  metavar = "DIRECTORY")
parser.add_option("-o", "--outputDir", dest = "outputDirectory",
                  help = "Path to directory to create to contain background plots",
                  metavar = "DIRECTORY")
parser.add_option("-p", "--percentage", dest="percentageThreshold",
                  help = "Sets threshold value to calculate SNR for")
parser.add_option("-s", "--snr", dest="SNRThreshold",
                  help = "Sets threshold value to calculate percentage for")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                  help = "Prints internal status messages to terminal as script runs")
parser.add_option("-b", action="store_true", dest="burstegard")
parser.add_option("-a", action="store_true", dest="all_clusters")
parser.add_option("-L", action="store_true", dest="pdf_latex_mode")

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

# Helper function to make new directory
def create_dir(name, iterate_name = True):

    # Set default directory name
    newDir = name
    # If directory doesn't exist, create
    if not os.path.exists(name):
        os.makedirs(name)

    # Otherwise, if iterate_name is set to true, iterate version number
    # to create new directory
    elif iterate_name:
        # Set initial version number
        version = 2
        # set base name to add version number to
        base_name = name + "_v"
        # while directory exists, iterate version number
        while os.path.exists(base_name + str(version)):
            version += 1
        # overwrite directory name
        newDir = base_name + str(version)
        # make new directory
        os.makedirs(newDir)

    return newDir

baseDirs = options.targetDirectory.split(",")
analysisDirs = [glueFileLocation(directory, "basic_snr_info") for directory in baseDirs]

loudest_cluster_files = [glueFileLocation(directory, "LoudestClusterInfo.txt") for directory in analysisDirs]
all_clusters_files = [glueFileLocation(directory, "runData.txt") for directory in analysisDirs]

loudest_cluster_info = [readFile(filename) for filename in loudest_cluster_files]
all_clusters_info = [readFile(filename) for filename in all_clusters_files]

loudest_cluster_info = [x for y in loudest_cluster_info for x in y]
all_clusters_info = [x for y in all_clusters_info for x in y]

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

SNRThreshold = None
if options.SNRThreshold:
    SNRThreshold = float(options.SNRThreshold)
percentageThreshold = None
if options.percentageThreshold:
    percentageThreshold = float(options.percentageThreshold)
threshold_string = ""

threshold_exists = False

if SNRThreshold:
    threshold_exists = True
    if SNRThreshold in all_snrs:
        snr_index = all_snrs.index[SNRThreshold]
        #percentage_derived_threshold = = all_percentage[snr_index]
        derived_from_snr_threshold = (all_snrs[snr_index], all_percentage[snr_index])
    elif SNRThreshold > max(all_snrs):
        #percentage_derived_threshold = min(all_percentage)
        derived_from_snr_threshold = (max(all_snrs), min(all_percentage))
    else:
        passedSNRs = [(all_snrs[x-1], all_percentage[x-1]) for x in range(1,len(all_snrs)) if all_snrs[x] > SNRThreshold]
        derived_from_snr_threshold = passedSNRs[0]
    threshold_string += "From SNR target threshold of " + str(options.SNRThreshold) + ":\n    SNR = " + str(derived_from_snr_threshold[0]) + "\n    FAP = " + str(derived_from_snr_threshold[1]) + "\n\n"

if percentageThreshold:
    threshold_exists = True
    if percentageThreshold in all_percentage:
        percentage_index = all_percentage.index[percentageThreshold]
        #snr_derived_threshold = = all_snrs[snr_index]
        derived_from_percentage_threshold = (all_snrs[percentage_index], all_percentage[percentage_index])
    elif percentageThreshold < min(all_percentage):
        #snr_derived_threshold = max(all_snrs)
        derived_from_percentage_threshold = (max(all_snrs), min(all_percentage))
    else:
        passedPercentages = [(all_snrs[x-1], all_percentage[x-1]) for x in range(1,len(all_snrs)) if all_percentage[x] < percentageThreshold]
        derived_from_percentage_threshold = passedPercentages[0]

    threshold_string += "From percentage target threshold of " + str(options.percentageThreshold) + ":\n    SNR = " + str(derived_from_percentage_threshold[0]) + "\n    FAP = " + str(derived_from_percentage_threshold[1]) + "\n\n"

outputDir = create_dir(glueFileLocation(options.outputDirectory, "backgroundEstimation"))

if threshold_exists:
    with open(glueFileLocation(outputDir, "threshold_info.txt"), "w") as outfile:
        outfile.write(threshold_string)

with open(glueFileLocation(outputDir, "all_clusters_info.txt"), "w") as outfile:
    outfile.write("\n".join(" ".join(str(x) for x in line) for line in all_clusters_info))

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.plot(loudest_snrs, loudest_percentage,'b-')#, label = "SNR distribution")
#plt.plot(loudest_snrs, loudest_percentage, 'ro', label = "FAP = " + str(100*rank) + "%\nSNR = " + str(specificSNR))
#plt.yscale('log')
#plt.xscale('log')
plt.xlabel("SNR")
#plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
#plt.ylabel('Strain [Counts / sqrt(Hz)]')
#plt.ylabel("False Alarm Probability [%]")
plt.ylim([0,100])
#plt.title("")
#legend = plt.legend(prop={'size':6})#, framealpha=0.5)
#legend.get_frame().set_alpha(0.5)
#plt.show()
if options.pdf_latex_mode:
    plt.rc('text', usetex = True)
    plt.rc('font', family = 'sarif')
    plt.ylabel("False Alarm Probability [\%]")
    plt.savefig(outputDir + "/SNRvsFAP_loudest_clusters.pdf", bbox_inches = 'tight', format='pdf')
else:
    plt.ylabel("False Alarm Probability [%]")
    plt.savefig(outputDir + "/SNRvsFAP_loudest_clusters", bbox_inches = 'tight')
plt.clf()

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.plot(all_snrs, all_percentage,'b-')#, label = "SNR distribution")
if SNRThreshold:
    plt.plot([derived_from_snr_threshold[0], derived_from_snr_threshold[0]], [0, 100], 'g-', label = "SNR target threshold = " + str(options.SNRThreshold) + "\nSNR = " + str(derived_from_snr_threshold[0]) + ", FAP = " + str(derived_from_snr_threshold[1]))
    plt.plot([derived_from_snr_threshold[0]], [derived_from_snr_threshold[1]], 'g.')
if percentageThreshold:
    plt.plot([derived_from_percentage_threshold[0], derived_from_percentage_threshold[0]], [0, 100], 'r-', label = "Percentage target threshold = " + str(options.percentageThreshold) + "\nSNR = " + str(derived_from_percentage_threshold[0]) + ", FAP = " + str(derived_from_percentage_threshold[1]))
    plt.plot([derived_from_percentage_threshold[0]], [derived_from_percentage_threshold[1]], 'r.')
#plt.plot(all_snrs, all_percentage, 'ro', label = "FAP = " + str(100*rank) + "%\nSNR = " + str(specificSNR))
#plt.yscale('log')
#plt.xscale('log')
plt.xlabel("SNR")
#plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
#plt.ylabel('Strain [Counts / sqrt(Hz)]')
#plt.ylabel("False Alarm Probability [%]")
plt.ylim([0,100])
plt.title("SNR vs False Alarm Probability")
if threshold_exists:
    legend = plt.legend(prop={'size':6})#, framealpha=0.5)
    legend.get_frame().set_alpha(0.5)
#plt.show()
if options.pdf_latex_mode:
    plt.rc('text', usetex = True)
    plt.rc('font', family = 'sarif')
    plt.ylabel("False Alarm Probability [\%]")
    plt.savefig(outputDir + "/SNRvsFAP_all_clusters.pdf", bbox_inches = 'tight', format='pdf')
else:
    plt.ylabel("False Alarm Probability [%]")
    plt.savefig(outputDir + "/SNRvsFAP_all_clusters", bbox_inches = 'tight')
#plt.savefig(outputDir + "/SNRvsFAP_all_clusters", bbox_inches = 'tight')
plt.clf()

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.plot(all_snrs, all_percentage,'b-')#, label = "SNR distribution")
minY = min(all_percentage)
if SNRThreshold:
    plt.plot([derived_from_snr_threshold[0], derived_from_snr_threshold[0]], [minY, 100], 'g-', label = "SNR target threshold = " + str(options.SNRThreshold) + "\nSNR = " + str(derived_from_snr_threshold[0]) + ", FAP = " + str(derived_from_snr_threshold[1]))
    plt.plot([derived_from_snr_threshold[0]], [derived_from_snr_threshold[1]], 'g.')
if percentageThreshold:
    plt.plot([derived_from_percentage_threshold[0], derived_from_percentage_threshold[0]], [minY, 100], 'r-', label = "Percentage target threshold = " + str(options.percentageThreshold) + "\nSNR = " + str(derived_from_percentage_threshold[0]) + ", FAP = " + str(derived_from_percentage_threshold[1]))
    plt.plot([derived_from_percentage_threshold[0]], [derived_from_percentage_threshold[1]], 'r.')
#plt.plot(all_snrs, all_percentage, 'ro', label = "FAP = " + str(100*rank) + "%\nSNR = " + str(specificSNR))
#plt.yscale('log')
#plt.xscale('log')
plt.xlabel("SNR")
#plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
#plt.ylabel('Strain [Counts / sqrt(Hz)]')
#plt.ylabel("False Alarm Probability [%]")
plt.title("SNR vs False Alarm Probability")
if threshold_exists:
    legend = plt.legend(prop={'size':6})#, framealpha=0.5)
    legend.get_frame().set_alpha(0.5)
#plt.show()
plt.yscale('log')
plt.ylim([minY,100])
if options.pdf_latex_mode:
    plt.rc('text', usetex = True)
    plt.rc('font', family = 'sarif')
    plt.ylabel("False Alarm Probability [\%]")
    plt.savefig(outputDir + "/SNRvsFAP_all_clusters_semilogy.pdf", bbox_inches = 'tight', format='pdf')
else:
    plt.ylabel("False Alarm Probability [%]")
    plt.savefig(outputDir + "/SNRvsFAP_all_clusters_semilogy", bbox_inches = 'tight')
#plt.savefig(outputDir + "/SNRvsFAP_all_clusters_semilogy", bbox_inches = 'tight')
plt.clf()

#plotTypeList = ["SNR", "Loudest Cluster", "cluster", "focused cluster", "sig map", "y map", "Xi snr map"]

#plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster" : "rmap.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png", "cluster": "cluster_plot.png", "focused cluster": "cluster_focus_plot.png"}

if options.burstegard:
    plotTypeList = ["SNR", "Largest Cluster", "All Clusters", "cluster", "focused cluster", "sig map", "y map", "Xi snr map"]
    plotTypeDict = {"SNR" : "snr.png", "Largest Cluster" : "large_cluster.png", "All Clusters": "all_clusters.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png", "cluster": "cluster_plot.png", "focused cluster": "cluster_focus_plot.png"}
elif options.all_clusters:
    plotTypeList = ["SNR", "Loudest Cluster (stochtrack)", "Largest Cluster (burstegard)", "All Clusters (burstegard)", "cluster", "focused cluster", "sig map", "y map", "Xi snr map"]
    plotTypeDict = {"SNR" : "snr.png", "Loudest Cluster (stochtrack)" : "rmap.png", "Largest Cluster (burstegard)" : "large_cluster.png", "All Clusters (burstegard)": "all_clusters.png", "sig map" : "sig_map.png", "y map" : "y_map.png", "Xi snr map" : "Xi_snr_map.png", "cluster": "cluster_plot.png", "focused cluster": "cluster_focus_plot.png"}
else:
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

webGen.make_display_page_v2("jobs", outputDir, highSNRsubDirs, "grandstochtrackOutput/plots", plotTypeList, plotTypeDict, webFile, plotRowOrder)
