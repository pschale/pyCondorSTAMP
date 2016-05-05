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
parser.add_option("-c", "--conf", dest = "configFile",
                  help = "Path to config file detailing analysis for anteproc executable (anteproc job options can have multiple jobs if separated by a \",\" [may be a good idea to switch to a single directory all preproc jobs are dumped, however this would require them to share many of the same parameters, or not, just don't overlap in time at all, something to think about])",
                  metavar = "FILE")
parser.add_option("-j", "--jobFile", dest = "jobFile",
                  help = "Path to job file detailing job times and durations",
                  metavar = "FILE")
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