from __future__ import division
from optparse import OptionParser
import subprocess
#from pyCondorSTAMPLib import *
import os

# command line options
parser = OptionParser()
parser.set_defaults(verbose = False)
parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to job directory",
                  metavar = "DIRECTORY")
parser.add_option("-o", "--output_dir", dest = "output_dir",
                  help = "Path to directory to save standard output from executables called by this script",
                  metavar = "DIRECTORY")
parser.add_option("-v", action="store_true", dest="verbose")

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

mmeExecutable = "/home/quitzow/GIT/Development_Branches/MatlabExecutableDuctTape/getSNRandCluster"

jobsDir = glueFileLocation(options.targetDirectory, "jobs")
jobGroupDirs = [glueFileLocation(jobsDir, x) for x in os.listdir(jobsDir) if "job_group" in x]
individualJobDirs = [glueFileLocation(glueFileLocation(y, x), "grandstochtrackOutput") for y in jobGroupDirs for x in os.listdir(y) if "job" in x]
bkndOutputFiles = [glueFileLocation(y, x) for y in individualJobDirs for x in os.listdir(y) if "bknd" in x]

jobs = {}
job_order = []
tempJob = None

output_text = ""

for num in range(len(bkndOutputFiles)):
    command = [mmeExecutable, bkndOutputFiles[num], individualJobDirs[num]]
    printable_command = " ".join(x for x in command)
    print(printable_command)
    output_text += printable_command
    command_output = subprocess.Popen(command, stdout = subprocess.PIPE, stderr=subprocess.PIPE).communicate()#[0]
    output_text += command_output[0]
    print(command_output[0])
    if command_output[1]:
        output_text += "ERROR\n" + command_output[1] + "\n\n\n"
        print(command_output[1])
    else:
        print("Success")
        output_text += "\nSuccess\n\n"

if options.output_dir:
    with open(options.output_dir + "/nonCondorMatlabReader_output.txt", "w") as outfile:
        outfile.write(output_text)
print(output_text)
