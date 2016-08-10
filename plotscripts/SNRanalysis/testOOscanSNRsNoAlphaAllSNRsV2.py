from __future__ import division
from optparse import OptionParser
from scanSNRlibV2 import *
from numpy import argsort

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

runInfo = search_run_info_no_alphas(options.targetDirectory)

loudestSNRs = runInfo.get_high_snrs()
allSNRs = runInfo.get_snrs()
print(allSNRs)
#temp = runInfo.get_data()
allData = runInfo.get_data(False)
allDataSorted = [[group[2][jobNum], group[0][jobNum], group[1][jobNum]] for group in allData for jobNum in range(len(group[0]))]
sortedIndices = argsort([x[0] for x in allDataSorted])
allDataSorted = [allDataSorted[index] for index in sortedIndices]
print(allData)
#print(temp[1][0])
#print(temp[1][2])

# create directory
dir_name = glueFileLocation(options.targetDirectory, "basic_snr_info")
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
output_text4 = "\n".join(", ".join(str(x) for x in line) for line in allDataSorted[::-1])
with open(glueFileLocation(dir_name, fileName4), "w") as outfile:
    outfile.write(output_text4)

# create plot of backgrounds based on loudest clusters (todo)
