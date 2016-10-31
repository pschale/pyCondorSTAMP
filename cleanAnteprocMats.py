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
parser.add_option("-p", action="store_true", dest="print_only",
                  help = "Set flag to print files to shell instead of delete")
parser.add_option("-s", action="store_true", dest="stampAnalysisSearch",
                  help = "Option to search for multiple stamp analyses" \
                           + "folders to clean up.")

(options, args) = parser.parse_args()
maindir = options.targetDirectory
if maindir[0] == "~":
    maindir = os.path.expanduser(option.targetDirectory)

if options.stampAnalysisSearch:
    list_of_dirs = [ele for ele in os.listdir(maindir)
                    if (os.path.isdir(os.path.join(maindir, ele))
                    and os.path.isdir(os.path.join(os.path.join(
                    maindir, ele), "anteproc_data")))]
else:
    list_of_dirs = [maindir]

list_of_dirs.sort()

list_of_dirs = [os.path.join(maindir, ele) for ele in list_of_dirs]

for current_dir in list_of_dirs:
    
    anteproc_dir = os.path.join(current_dir, "anteproc_data")
    data_dirs = [ele for ele in os.listdir(anteproc_dir)
                            if os.path.isdir(
                                os.path.join(anteproc_dir, ele))]
    if data_dirs:
        if options.print_only:
            ans = raw_input("List anteproc mats in:" + current_dir
                             + "? [y/n]")
        else:
            ans = raw_input("Delete all anteproc files from: " 
                             + current_dir + "? [y/n]")
        if ans == "y":
        
            for adir in data_dirs:
                adir = os.path.join(anteproc_dir, adir)
                files = [ele for ele in os.listdir(os.path.join(adir)) 
                                if ele[-4:] == ".mat"]
                if options.print_only:
                    print(files)
                else:
                    for file in files:
                        os.remove(file)  
    

            if not options.print_only:
                print("Removed all anteproc mats")
    
        else:
            print("Did not receive 'y', so will not delete")
            continue
        
print("Done!")

