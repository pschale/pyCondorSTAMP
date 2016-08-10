from plotClustersLib import *
from optparse import OptionParser

# command line options
parser = OptionParser()
parser.set_defaults(verbose = True)
parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to directory containing completed STAMP jobs to use for False Alarm Probability calculation",
                  metavar = "DIRECTORY")
parser.add_option("-v", action="store_true", dest="verbose")

(options, args) = parser.parse_args()

baseDir = options.targetDirectory
analysisDir = glueFileLocation(baseDir, "basic_snr_info")

all_clusters_file = glueFileLocation(analysisDir, "runData.txt")
all_clusters_info = readFile(all_clusters_file)

all_clusters_info = [x for x in all_clusters_info if len(x) > 0]
all_clusters_info = [x for x in all_clusters_info if  x[0] != "None,"]

stochDataFiles = [returnMatrixFilePath("bknd_", x[2] + "/grandstochtrackOutput") for x in all_clusters_info]
mapDataFiles = [returnMatrixFilePath("map_", x[2] + "/grandstochtrackOutput") for x in all_clusters_info]
plotDirs = [glueFileLocation(x[2], "grandstochtrackOutput/plots") for x in all_clusters_info]

#clusterData = [getClusterInfo(val, mapDataFiles[num]) for num, val in enumerate(stochDataFiles)]
clusterData = [plotClusterInfo(val, mapDataFiles[num], plotDirs[num]) for num, val in enumerate(stochDataFiles)]

"""for directory, index in plotDirs:
    print("saving")
    print(directory)
    saveClusterPlot(directory, clusterData[index])"""
