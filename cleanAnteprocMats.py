#cleanAnteprocMats.py
from optparse import OptionParser
import os

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
parser.add_option("-s", action="store_true", dest="stampAnalysisSearch",
                  help = "Option to search for multiple stamp analyses" \
                           + "folders to clean up.")

(options, args) = parser.parse_args()

if options.stampAnalysisSearch:
    list_of_dirs = [ele for ele in os.listdir(options.targetDirectory)
                    if (os.path.isdir(ele) 
                    and os.path.isdir(os.path.join(ele, "anteproc_data")))]
else:
    list of dirs = [options.targetDirectory]
    
for current_dir in list_of_dirs:
    ans = raw_input("Delete all anteproc files from: " 
                        + current_dir + "? [y/n]")
    if ans == "y":
        anteproc_dirs = [ele for ele in os.listdir(os.path.join(
                                            current_dir, "anteproc_data"))
                                if os.path.isdir(ele)]
        for adir in anteproc_dirs:
            files = [ele for ele in os.listdir(adir) if ele[-4:] == ".mat"]
            for file in files:
                os.remove(file)
    
        print("Removed all anteproc mats")
    
    else:
        print("Did not receive 'y', so will not delete")
        continue
        
print("Done!")

