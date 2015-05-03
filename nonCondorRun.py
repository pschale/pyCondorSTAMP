from __future__ import division
from optparse import OptionParser
import subprocess
from pyCondorSTAMPLib import *

# command line options
parser = OptionParser()
parser.set_defaults(verbose = False)
parser.add_option("-s", "--stampAnalysisDag", dest = "stampAnalysisDag",
                  help = "Path to dag file",
                  metavar = "FILE")
parser.add_option("-p", "--preproc", dest = "preproc",
                  help = "Path to preproc submit file",
                  metavar = "FILE")
parser.add_option("-g", "--grand_stochtrack", dest = "grand_stochtrack",
                  help = "Path to grand_stochtrack submit file",
                  metavar = "FILE")
parser.add_option("-o", "--output_dir", dest = "output_dir",
                  help = "Path to directory to save standard output from executables called by this script",
                  metavar = "DIRECTORY")
parser.add_option("-v", action="store_true", dest="verbose")

(options, args) = parser.parse_args()

dagInfo = read_text_file(options.stampAnalysisDag, None)

preprocInfo = read_text_file(options.preproc, None)
preprocExecutable = [x for x in preprocInfo if x[0] == "executable"][-1][-1]

gsInfo = read_text_file(options.grand_stochtrack, None)
gsExecutable = [x for x in gsInfo if x[0] == "executable"][-1][-1]

jobs = {}
job_order = []
tempJob = None

def pullFromQuotes(tempString):
    outputString = tempString[tempString.find('"') + 1:-1]
    return outputString

output_text = ""

for line in dagInfo:
    if line[0] == "JOB":
        tempJob = line[1]
        job_order += [tempJob]
        jobs[tempJob] = {}
    elif line[0] == "VARS":
        jobs[tempJob]["VARS"] = line
    elif line[0] == "CATEGORY":
        jobs[tempJob]["CATEGORY"] = line[-1]

for job in job_order:
    variables = jobs[job]["VARS"]
    command = None
    if jobs[job]["CATEGORY"] == "PREPROC":
        command = [preprocExecutable, pullFromQuotes(variables[3]), pullFromQuotes(variables[4]), pullFromQuotes(variables[5])]
    elif jobs[job]["CATEGORY"] == "GRANDSTOCKTRACK":
        command = [gsExecutable, pullFromQuotes(variables[3]), pullFromQuotes(variables[4])]
    if command:
        print(command)
        command_output = subprocess.Popen(command, stdout = subprocess.PIPE, stderr=subprocess.PIPE).communicate()#[0]
        output_text += command_output[0] + "\n\n"
        print(command_output[0])
        if command_output[1]:
            output_text += "ERROR\n" + command_output[1] + "\n\n\n"
            print(command_output[1])

if options.output_dir:
    with open(options.output_dir + "/nonCondorRunStampAnalysis.txt", "w") as outfile:
        outfile.write(output_text)
print(output_text)
