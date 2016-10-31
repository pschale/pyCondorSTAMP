from __future__ import division
from optparse import OptionParser
import os

# command line options
parser = OptionParser()
parser.set_defaults(verbose = False)
parser.set_defaults(print_only = False)
parser.set_defaults(deprecatedAnalysisVersion = False)
parser.set_defaults(stampAnalysisSearch = False)
parser.set_defaults(recursiveCheck = False)

parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to directory to cleanup",
                  metavar = "DIRECTORY")
parser.add_option("-v", action="store_true", dest="verbose")
parser.add_option("-p", action="store_true", dest="print_only",
                  help = "Set flag to print files to shell instead of delete")
parser.add_option("-a", action="store_true", dest="deprecatedAnalysisVersion",
                  help = "Set flag to navigate older version of stamp analysis")
parser.add_option("-s", action="store_true", dest="stampAnalysisSearch",
                  help = "Option to search for multiple stamp analyses folders to clean up.")
parser.add_option("-R", action="store_true", dest="recursiveCheck",
                  help = "Option to recursively search directory and subdirectories for multiple stamp analyses folders to clean up.")

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
def recursive_check(directory, dir_list = None):
    if not dir_list:
        dir_list = []
    temp_dirs = [glueFileLocation(directory, x) for x in os.listdir(directory) if "stamp_analysis" in x]#x != '.' and x != '..']
    temp_dirs_2 = [glueFileLocation(directory, x) for x in os.listdir(directory) if x != '.' and x != '..' and (not ("stamp_analysis" in x)) and os.path.isdir(glueFileLocation(directory, x))]
    if temp_dirs_2:
        temp_dirs += [x for temp_list in [recursive_check(temp_dir) for temp_dir in temp_dirs_2] for x in temp_list]
    dir_list += temp_dirs
    return dir_list

def check_if_job_subdir(directory):
    sub_dirs = [glueFileLocation(directory, x) for x in os.listdir(directory) if "job" in x]
    if sub_dirs:
        return sub_dirs
    else:
        return [directory]

def check_for_folders_of_interest(directory, dir_list = None):
    if not dir_list:
        dir_list = []
    folders_of_interest = ["preprocessingJobs", "job", "preprocOutput", "grandstochtrackOutput", "map", "plots","anteproc_data", "map_v"]
    temp_dirs = [glueFileLocation(directory, x) for x in os.listdir(directory) if [x for temp_x in folders_of_interest if (temp_x in x) and os.path.isdir(glueFileLocation(directory, x))]]#x != '.' and x != '..']
    temp_dirs += [x for temp_list in [check_for_folders_of_interest(temp_dir) for temp_dir in temp_dirs] for x in temp_list]
    temp_dirs_2 = [glueFileLocation(directory, x) for x in os.listdir(directory) if x != '.' and x != '..' and (not [x for temp_x in folders_of_interest if temp_x in x]) and os.path.isdir(glueFileLocation(directory, x))]
    #print(temp_dirs_2)
    #temp_dirs_2 = []
    #for x in os.listdir(directory):
    #    if x != '.':
    #        if x != '..':
    #            if not ([x for temp_x in folders_of_interest if temp_x in x]) and os.path.isdir(glueFileLocation(directory, x)):
    #        temp_dirs_2 += glueFileLocation(directory, x)
    #temp_dirs_2 = [glueFileLocation(directory, x) for x in os.listdir(directory) if x != '.' and x != '..' and (not (if [x for temp_x in folders_of_interest if temp_x in x])) and os.path.isdir(glueFileLocation(directory, x))]
    if temp_dirs_2:
        temp_dirs += [x for temp_list in [check_for_folders_of_interest(temp_dir) for temp_dir in temp_dirs_2] for x in temp_list]
    dir_list += temp_dirs
    return dir_list

def find_files_of_interest(directory):
    #print(directory)
    file_types = ["max_cluster.txt", "eps", "map-", "map_v"]
    possible_files = [glueFileLocation(directory, x) for x in os.listdir(directory) if not os.path.isdir(glueFileLocation(directory, x))]
    #print(possible_files)
    file_of_interest = [x for x in possible_files if [temp_y for temp_y in file_types if temp_y in x[x.rindex('/')+1:]]]
    return file_of_interest

print("Finding directories...")

if options.recursiveCheck:
    analysis_dirs = recursive_check(options.targetDirectory)
    dirs_of_interest = [z for y in [check_for_folders_of_interest(x) for x in analysis_dirs] for z in y]
    #preprocDirs = [glueFileLocation(x, "preprocessingJobs") for x in analysis_dirs]
    #jobsDirs = [glueFileLocation(x, "jobs") for x in analysis_dirs]
    #print(dirs_of_interest)
elif options.stampAnalysisSearch:
    preprocDirs = [glueFileLocation(glueFileLocation(options.targetDirectory, x), "preprocessingJobs") for x in os.listdir(options.targetDirectory) if "stamp_analysis" in x]
    jobsDirs = [glueFileLocation(glueFileLocation(options.targetDirectory, x), "jobs") for x in os.listdir(options.targetDirectory) if "stamp_analysis" in x]
else:
    preprocDirs = [glueFileLocation(options.targetDirectory, "preprocessingJobs")]
    jobsDirs = [glueFileLocation(options.targetDirectory, "jobs")]

print("Directories found")

if options.recursiveCheck:
    print("Finding files...")
    filesOfInterest = [z for y in [find_files_of_interest(x) for x in dirs_of_interest] for z in y]
    print("Files found")
    if options.print_only:
        print("\n".join(x for x in filesOfInterest))
    else:
        if len(filesOfInterest) > 0:
            print(str(len(filesOfInterest)) + " files to delete")
            counter = 0
            for temp_file in filesOfInterest:
                os.remove(temp_file)
                counter += 1
                if counter % 100 == 0:
                    print(str(counter) + " out of " + str(len(filesOfInterest)) + " deleted")
else:
    if options.deprecatedAnalysisVersion:
        individualJobDirs = [glueFileLocation(y, x) for y in jobsDirs for x in os.listdir(y) if "job" in x]
        individualJobDirs = [x for z in [check_if_job_subdir(y) for y in individualJobDirs] for x in z]
        preprocJobDirs = [glueFileLocation(x, "preprocOutput") for x in individualJobDirs if "preprocOutput" in os.listdir(x)]
        mapDirs = [glueFileLocation(y, x) for y in preprocJobDirs for x in os.listdir(y) if "map" in x]
        mapFiles = [glueFileLocation(y, x) for y in mapDirs for x in os.listdir(y) if "map" in x]

        grandstochtrackOutputDirs = [glueFileLocation(x, "grandStochtrackOutput") for x in individualJobDirs]
        plotDirs = [glueFileLocation(x, "plots") for x in grandstochtrackOutputDirs]
        mapOutputFiles = [glueFileLocation(y, x) for y in grandstochtrackOutputDirs for x in os.listdir(y) if "map" in x]
        epsFiles = [glueFileLocation(y, x) for y in plotDirs for x in os.listdir(y) if "eps" in x]
        clusterFiles = [glueFileLocation(y, x) for y in grandstochtrackOutputDirs for x in os.listdir(y) if "max_cluster.txt" in x]

    else:
        preprocJobGroupDirs = [glueFileLocation(y, x) for y in preprocDirs for x in os.listdir(y) if "job_group" in x]
        preprocJobDirs = [glueFileLocation(glueFileLocation(y, x), "preprocOutput") for y in preprocJobGroupDirs for x in os.listdir(y) if "preproc_job" in x]
        mapDirs = [glueFileLocation(y, x) for y in preprocJobDirs for x in os.listdir(y) if "map" in x]
        mapFiles = [glueFileLocation(y, x) for y in mapDirs for x in os.listdir(y) if "map" in x]

        jobGroupDirs = [glueFileLocation(y, x) for y in jobsDirs for x in os.listdir(y) if "job_group" in x]
        individualJobDirs = [glueFileLocation(glueFileLocation(y, x), "grandStochtrackOutput") for y in jobGroupDirs for x in os.listdir(y) if "job" in x]
        plotDirs = [glueFileLocation(x, "plots") for x in individualJobDirs]
        mapOutputFiles = [glueFileLocation(y, x) for y in individualJobDirs for x in os.listdir(y) if "map" in x]
        epsFiles = [glueFileLocation(y, x) for y in plotDirs for x in os.listdir(y) if "eps" in x]
        clusterFiles = [glueFileLocation(y, x) for y in individualJobDirs for x in os.listdir(y) if "max_cluster.txt" in x]

    if options.print_only:
        print("\n".join(x for x in mapFiles))
        print("\n".join(x for x in mapOutputFiles))
        print("\n".join(x for x in epsFiles))
    else:
        if len(mapFiles) > 0:
            for matFile in mapFiles:
                os.remove(matFile)
        if len(mapOutputFiles) > 0:
            for mapFile in mapOutputFiles:
                os.remove(mapFile)
        if len(epsFiles) > 0:
            for epsFile in epsFiles:
                os.remove(epsFile)
        if len(clusterFiles) > 0:
            for clusterFile in clusterFiles:
                os.remove(clusterFile)
