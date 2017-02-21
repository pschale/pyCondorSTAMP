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

i = 0
while True:
    try:
        current_dir = list_of_dirs[i]
    except IndexError:
        break
    anteproc_dir = os.path.join(current_dir, "anteproc_data")
    data_dirs = [ele for ele in os.listdir(anteproc_dir)
                            if os.path.isdir(
                                os.path.join(anteproc_dir, ele))]
    if data_dirs:
        ans = raw_input("Delete all anteproc files from: " 
                             + current_dir + "? [y/n/p]")
        
        if ans == "y" or ans == "p":
        
            for adir in data_dirs:
                adir = os.path.join(anteproc_dir, adir)
                files = [ele for ele in os.listdir(os.path.join(adir)) 
                                if ele[-4:] == ".mat"]
                if ans == "p":
                    print(files)
                    continue
                else:
                    for f in files:
                        os.remove(os.path.join(adir, f))  
    
            if ans == "y":
                print("Removed all anteproc mats")
                i += 1
    
        elif ans == "n":
            i+=1
            continue
        else:
            print("must type 'y' to delete, 'n' to not delete, or 'p' to print list")
            continue
    else:
        i+=1
print("Done!")

