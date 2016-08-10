from __future__ import division
from optparse import OptionParser
from scanSNRlib import *

parser = OptionParser()
parser.set_defaults(verbose = False)
parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to directory containing completed STAMP jobs to use for analysis",
                  metavar = "DIRECTORY")
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                  help = "Prints internal status messages to terminal as script runs")

(options, args) = parser.parse_args()

print("NOTE: script ignores all files and directories starting with '.'")

print("WARNING: Script is currently not set up to handle directories with multiple files with the name base.")

def verbosePrint(string, switch = options.verbose):
    if switch:
        print(string)

runInfo = search_run_info(options.targetDirectory)

loudestSNRs = runInfo.get_high_snrs()
allSNRs = runInfo.get_snrs()
print(allSNRs)
#temp = runInfo.get_data()
temp = runInfo.get_data(False)
print(temp[1][0])
print(temp[1][2])

# create directory
dir_name = glueFileLocation(options.targetDirectory, "basic_snr_info")
#create_dir(dir_name)

# create list of highest SNR jobs
fileName = "LoudestClusterInfo.txt"
output_text = "\n\n".join(": ".join(str(y) for y in x) for x in loudestSNRs)
#with open(glueFileLocation(dir_name, fileName), "w") as outfile:
#    outfile.write(output_text)

# create plot of backgrounds based on loudest clusters (todo)
