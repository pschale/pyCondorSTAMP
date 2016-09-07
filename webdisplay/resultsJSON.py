import os
from optparse import OptionParser
import scipy.io as sio
from numpy import argsort
import json

# search pycondorstamp directory file structure
# build json of file locations
    # file types
    # different plots
    # bknd file location? no, max_cluster SNR instead
# save json

def return_filepaths(basedir):
    dir_contents = os.listdir(basedir)
    #print(dir_contents)
    output_paths = []
    cond_1 = "plots" in dir_contents
    cond_2 = any(["bknd_" == x[:5] and ".mat" == x[-4:] for x in dir_contents])
    if cond_1 and cond_2:
        #print("truth!")
        #print(dir_contents)
        output_paths = [basedir]
    else:
        for item in dir_contents:
            current_path = os.path.join(basedir, item)
            if os.path.isdir(current_path):
                output_paths += return_filepaths(current_path)
    return output_paths

def getSNR(inputFile):
    if inputFile:
        data = sio.loadmat(inputFile)
        SNR = data['stoch_out']['max_SNR'][0,0][0,0]
    else:
        SNR = None
    return SNR

def getInfo(inputFile):
    if inputFile:
        data = sio.loadmat(inputFile)
        SNR = data['stoch_out']['max_SNR'][0,0][0,0]
        info = [SNR]
    else:
        info = [None]
    return info

##def get_plot_paths(basedir, plotdir = None, plot_types = [".pdf"]):
#def get_plot_paths(basedir, plotdir = None, plot_types = [".png"]):
#    if plotdir:
#        targetdir = os.path.join(basedir, plotdir)
#    else:
#        targetdir = basedir
#    dir_contents = os.listdir(targetdir)
#    output_paths = [x for x in dir_contents for y in plot_types if not os.path.isdir(x) and x[-len(y):] == y]
#    #for x in dir_contents:
#        #for y in plot_types:
#            #if x[-len(y):] == y:
#                #print(x)
#            #else:
#                #print("huh")
#                #print(x)
#    for item in dir_contents:
#        current_path = os.path.join(targetdir, item)
#        print("testing")
#        print("item")
#        print(item)
#        print(current_path)
#        print(os.path.isdir(current_path))
#        print("testing")
#        if "bknd" in current_path:
#            print(getSNR(current_path))
#        if os.path.isdir(current_path):
#            output_paths += get_plot_paths(current_path)
#    return output_paths

#def get_job_plots(basedir, plotdir = None, plot_types = [".png"]):
def get_plot_paths(basedir, plotdir = None, plot_types = [".png"]):
    if plotdir:
         targetdir = os.path.join(basedir, plotdir)
    else:
         targetdir = basedir
    infolist = []
    dir_contents = os.listdir(targetdir)
    plot_paths = [os.path.join(plotdir, x) for x in dir_contents for y in plot_types if not os.path.isdir(x) and x[-len(y):] == y]
    for item in dir_contents:
        current_path = os.path.join(targetdir, item)
        if "bknd" in current_path:
            # add additional info to show on webpage in getInfo function
            #infolist += [getSNR(current_path)]
            infolist += [getInfo(current_path)]
        if os.path.isdir(current_path):
            new_plotdir = os.path.join(plotdir, item)
            plot_paths += get_plot_paths(basedir, new_plotdir)
    infolist += plot_paths
    return infolist

def main():
    parser = OptionParser()

    parser.add_option("-d", "--dir", dest = "targetDirectory",
                      help = "Path to directory to scan for STAMP plots and create JSON.",
                      metavar = "DIRECTORY")
    parser.add_option("-D", "--debug", action="store_true", dest="debug",
            help = "Prints debug output from script.")

    (options, args) = parser.parse_args()
    
    analysisdir = options.targetDirectory
    if analysisdir[-1] != "/":
        print("WARNING: The functionality of this if statement is only tested on Linux. Windows paths probably will have issues with this specific part of this script.")
        analysisdir += "/"
    if "jobs" in os.listdir(analysisdir):
        base_job_dir = os.path.join(analysisdir, "jobs")
        plotdirs = return_filepaths(base_job_dir)
        plotdirs = [x.replace(analysisdir, "") for x in plotdirs]
        if options.debug:
            print("Printing 1st four items from 'plotdirs'.")
            print(plotdirs[:4])
        plotinfo = [get_plot_paths(analysisdir, x) for x in plotdirs]
        if options.debug:
            print("Printing 1st four items from 'plotinfo'.")
            print(plotinfo[:4])
        SNRs = [x[0][0] for x in plotinfo]
        indices = argsort(SNRs)
        indices = indices[::-1]
        decendingplots = [plotinfo[x] for x in indices]
        outputfilename = os.path.join(analysisdir, "plotlisting.json")
        with open(outputfilename, "w") as outfile:
            json.dump(decendingplots, outfile, indent = 4)
    else:
        print("Check target directory structure. This script does not seems to be set up to properly unpack this directory.")

if __name__ == "__main__":
    main()
