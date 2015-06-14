from __future__ import division
from optparse import OptionParser
import os

# command line options
parser = OptionParser()
parser.set_defaults(verbose = False)
parser.set_defaults(print_only = False)
parser.set_defaults(deprecatedAnalysisVersion = False)
parser.set_defaults(stampAnalysisSearch = False)

parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to directory to cleanup",
                  metavar = "DIRECTORY")
parser.add_option("-v", action="store_true", dest="verbose")
parser.add_option("-p", action="store_true", dest="print_only",
                  help = "Set flag to print files to shell instead of delete")
parser.add_option("-a", action="store_true", dest="deprecatedAnalysisVersion",
                  help = "Set flag to navigate older version of stamp analysis")
parser.add_option("-s", action="store_true", dest="stampAnalysisSearch",
                  help = "Options to search for multiple stamp analyses folders to clean up.")

# add options to load defaults for preproc and grand_stochtrack

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

#preprocDir = glueFileLocation(options.targetDirectory, "preprocessingJobs")

#jobsDir = glueFileLocation(options.targetDirectory, "jobs")

if options.stampAnalysisSearch:
    preprocDirs = [glueFileLocation(glueFileLocation(options.targetDirectory, x), "preprocessingJobs") for x in os.listdir(options.targetDirectory) if "stamp_analysis" in x]
    jobsDirs = [glueFileLocation(glueFileLocation(options.targetDirectory, x), "jobs") for x in os.listdir(options.targetDirectory) if "stamp_analysis" in x]
else:
    preprocDirs = [glueFileLocation(options.targetDirectory, "preprocessingJobs")]
    jobsDirs = [glueFileLocation(options.targetDirectory, "jobs")]

if options.deprecatedAnalysisVersion:
    individualJobDirs = [glueFileLocation(y, x) for y in jobsDirs for x in os.listdir(y) if "job" in x]
    preprocJobDirs = [glueFileLocation(x, "preprocOutput") for x in individualJobDirs]
    mapDirs = [glueFileLocation(y, x) for y in preprocJobDirs for x in os.listdir(y) if "map" in x]
    mapFiles = [glueFileLocation(y, x) for y in mapDirs for x in os.listdir(y) if "map" in x]

    grandstochtrackOutputDirs = [glueFileLocation(x, "grandstochtrackOutput") for x in individualJobDirs]
    mapOutputFiles = [glueFileLocation(y, x) for y in grandstochtrackOutputDirs for x in os.listdir(y) if "map" in x]

else:
    preprocJobGroupDirs = [glueFileLocation(y, x) for y in preprocDirs for x in os.listdir(y) if "job_group" in x]
    preprocJobDirs = [glueFileLocation(glueFileLocation(y, x), "preprocOutput") for y in preprocJobGroupDirs for x in os.listdir(y) if "preproc_job" in x]
    mapDirs = [glueFileLocation(y, x) for y in preprocJobDirs for x in os.listdir(y) if "map" in x]
    mapFiles = [glueFileLocation(y, x) for y in mapDirs for x in os.listdir(y) if "map" in x]

    jobGroupDirs = [glueFileLocation(y, x) for y in jobsDirs for x in os.listdir(y) if "job_group" in x]
    individualJobDirs = [glueFileLocation(glueFileLocation(y, x), "grandstochtrackOutput") for y in jobGroupDirs for x in os.listdir(y) if "job" in x]
    mapOutputFiles = [glueFileLocation(y, x) for y in individualJobDirs for x in os.listdir(y) if "map" in x]

if options.print_only:
    print("\n".join(x for x in mapFiles))
    print("\n".join(x for x in mapOutputFiles))
else:
    if len(mapFiles) > 0:
        for matFile in mapFiles:
            os.remove(matFile)
    if len(mapOutputFiles) > 0:
        for mapFile in mapOutputFiles:
            os.remove(mapFile)