from __future__ import division
from optparse import OptionParser
#from pyCondorSTAMPLib import *
#from preprocSupportLib import *
#from grandStochtrackSupportLib import *
#from condorSTAMPSupportLib import *
#import webpageGenerateLib as webGen
#import scipy.io as sio
#import json

# command line options
parser = OptionParser()
parser.set_defaults(verbose = False)
parser.set_defaults(archived_frames_okay = False)
parser.set_defaults(no_job_retry = False)
parser.add_option("-j", "--jobFile", dest = "jobFile",
                  help = "Path to job file detailing job times and durations",
                  metavar = "FILE")
parser.add_option("-n", "--jobNums", dest = "jobNums",
                  help = "Job numbers to find cache files for (job numbers can be separated by commas)",
                  metavar = "INTEGERS")
parser.add_option("-d", "--dir", dest = "outputDir",
                  help = "Path to directory to hold analysis output (a new directory \
will be created with appropriate subdirectories to hold analysis)",
                  metavar = "DIRECTORY")
parser.add_option("-v", action="store_true", dest="verbose")
parser.add_option("-f", action="store_true", dest="archived_frames_okay")
parser.add_option("-q", action="store_true", dest="no_job_retry")


# MAYBE maxjobs will be useful.

parser.add_option("-m", "--maxjobs", dest = "maxjobs",
                  help = "Maximum number of jobs ever submitted at once \
through condor", metavar = "NUMBER")

# add options to load defaults for preproc and grand_stochtrack

(options, args) = parser.parse_args()

# create directory for cachefiles

#if not quit_program:
    # Build base analysis directory
    # stochtrack_condor_job_group_num
if options.outputDir[-1] == "/":
    baseDir = dated_dir(options.outputDir + "cache_files")
else:
    baseDir = dated_dir(options.outputDir + "/cache_files")

for jobNum in