from __future__ import division
from optparse import OptionParser
import subprocess
from pyCondorSTAMPLib import *

# command line options
parser = OptionParser()
parser.set_defaults(verbose = False)
parser.add_option("-j", "--jobFile", dest = "jobFile",
                  help = "Path to job file",
                  metavar = "FILE")
parser.add_option("-c", "--config", dest = "config",
                  help = "Path to parameter files for anteproc jobs (separate by commas to run all jobs with multiple parameters)",
                  metavar = "FILE")
parser.add_option("-n", "--jobNumbers", dest = "jobNumbers",
                  help = "Job numbers to run separated by commas, no jobs specified means run every job in the job file",
                  metavar = "NUMBER_STRING")
parser.add_option("-o", "--output_dir", dest = "output_dir",
                  help = "Path to directory to save standard output from executables called by this script",
                  metavar = "DIRECTORY")
parser.add_option("-v", action="store_true", dest="verbose")

(options, args) = parser.parse_args()

anteprocExecutablePath = '/home/quitzow/STAMP/STAMP_6_21_2015/stamp2/compiledScripts/anteproc/anteproc'

jobInfo = read_text_file(options.jobFile, None)

jobFileData = read_text_file(options.jobFile, None)
jobFileNumbers = [x[0] for x in jobFileData]

parameterFiles = options.config.split(",")

if options.jobNumbers:
    jobNumbers = options.jobNumbers.split(',')
else:
    jobNumbers = jobFileNumbers[:]

quit_program = False
output_text = ""

for job in jobNumbers:
    if job not in jobFileNumbers:
        print("WARNING: job number " + job + " not in jobfile " + options.jobFile + ". Quitting program.")
        quit_program = True
    elif not quit_program:
        for configFile in parameterFiles:
            command = [anteprocExecutablePath, configFile, options.jobFile, job]
            print(command)
            command_output = subprocess.Popen(command, stdout = subprocess.PIPE, stderr=subprocess.PIPE).communicate()#[0]
            output_text += command_output[0] + "\n\n"
            print(command_output[0])
            if command_output[1]:
                output_text += "ERROR\n" + command_output[1] + "\n\n\n"
                print(command_output[1])

if options.output_dir:
    with open(options.output_dir + "/anteprocProcessingStdout.txt", "w") as outfile:
        outfile.write(output_text)
print(output_text)
