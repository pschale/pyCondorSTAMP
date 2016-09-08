import os
from optparse import OptionParser
import scipy.io as sio
from numpy import argsort
import json

def return_filepaths(basedir):
    dir_contents = os.listdir(basedir)
    output_paths = []
    cond_1 = "plots" in dir_contents
    cond_2 = any(["bknd_" == x[:5] and ".mat" == x[-4:] for x in dir_contents])
    if cond_1 and cond_2:
        output_paths = [basedir]
    else:
        for item in dir_contents:
            current_path = os.path.join(basedir, item)
            if os.path.isdir(current_path):
                output_paths += return_filepaths(current_path)
    return output_paths

def getInfo(inputFile):
    if inputFile:
        data = sio.loadmat(inputFile)
        job_id = "/".join(inputFile.split("/")[2:-2])
        SNR = data['stoch_out']['max_SNR'][0,0][0,0]
        SNR_string = "SNR = " + str(round(SNR, 2))
        info = {"SNR": SNR, "label_info": [job_id, SNR_string]}
    else:
        info = [None]
    return info

def get_plot_paths(basedir, plotdir = None, plot_types = [".png", ".pdf"]):
    if plotdir:
         targetdir = os.path.join(basedir, plotdir)
    else:
         targetdir = basedir
    #infolist = []
    infolist = {"plot_subdirs": []}
    dir_contents = os.listdir(targetdir)
    plot_paths = [os.path.join(plotdir, x) for x in dir_contents for y in plot_types if not os.path.isdir(x) and x[-len(y):] == y]
    for item in dir_contents:
        current_path = os.path.join(targetdir, item)
        if "bknd" in current_path:
            # add additional info to show on webpage in getInfo function
            #infolist += [getInfo(current_path)]
            infolist.update(getInfo(current_path))
        if os.path.isdir(current_path):
            new_plotdir = os.path.join(plotdir, item)
            #plot_paths += get_plot_paths(basedir, new_plotdir)
            infolist.update(get_plot_paths(basedir, new_plotdir))
    infolist["plot_subdirs"] += plot_paths
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
        SNRs = [x["SNR"] for x in plotinfo]
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
