#!/bin/python

from __future__ import division
import os
from optparse import OptionParser
import scipy.io as sio
from numpy import argsort
import json
import numpy as np
import pandas as pd
import ConfigParser

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
        min_f = data['stoch_out']['fmin'][0,0][0,0]
        min_f_string = "Min Freqency = " + str(min_f)
        max_f = data['stoch_out']['fmax'][0,0][0,0]
        max_f_string = "Max Freqency = " + str(max_f)
        cluster_length = data['stoch_out']['tmax'][0,0][0,0] - data['stoch_out']['tmin'][0,0][0,0]
        info = {"SNR": SNR, "label_info": [job_id, SNR_string, min_f_string, max_f_string]}
        if data['stoch_out']['params'][0,0][0,0]['doOverlap'][0,0]:
            overlap_time = data['stoch_out']['params'][0,0][0,0]['segmentDuration'][0,0]/2
            if overlap_time == int(overlap_time):
                overlap_time = int(overlap_time)
            cluster_length += overlap_time
        cluster_length_string = "Cluster Duration = " + str(cluster_length)
        info["label_info"] += [cluster_length_string]
    else:
        info = [None]
    return info

def get_plot_paths(basedir, plotdir = None, plot_types = [".png", ".pdf"]):
    if plotdir:
         targetdir = os.path.join(basedir, plotdir)
    else:
         targetdir = basedir
    infolist = {"plot_subdirs": []}
    dir_contents = os.listdir(targetdir)
    plot_paths = [os.path.join(plotdir, x) for x in dir_contents for y in plot_types if not os.path.isdir(x) and x[-len(y):] == y]
    for item in dir_contents:
        current_path = os.path.join(targetdir, item)
        if "bknd" in current_path:
            # add additional info to show on webpage in getInfo function
            infolist.update(getInfo(current_path))
        if os.path.isdir(current_path):
            new_plotdir = os.path.join(plotdir, item)
            infolist.update(get_plot_paths(basedir, new_plotdir))
    infolist["plot_subdirs"] += plot_paths
    return infolist

def wrapjsonlist(jsonlist):
    plot_subdirs = jsonlist[0]["plot_subdirs"]
    simple_plotnames = [os.path.basename(x).replace("_", " ") for x in plot_subdirs]
    simple_plotnames = [os.path.splitext(x)[0] for x in simple_plotnames]
    output_json = {"simple_plotnames": simple_plotnames, "plot_info": jsonlist}
    return output_json

def main():
    parser = OptionParser()

    parser.add_option("-d", "--dir", dest = "targetDirectory",
                      help = "Path to directory to scan for STAMP plots and create JSON.",
                      metavar = "DIRECTORY")
    parser.add_option("-D", "--debug", action="store_true", dest="debug",
            help = "Prints debug output from script.")

    (options, args) = parser.parse_args()
    
    analysisdir = options.targetDirectory

    dataframe = gather_output(analysisdir)

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
        output_json = wrapjsonlist(decendingplots)
        outputfilename = os.path.join(analysisdir, "plotlisting.json")
        with open(outputfilename, "w") as outfile:
            json.dump(output_json, outfile, indent = 4)
    else:
        print("Check target directory structure. This script does not seems to be set up to properly unpack this directory.")

def get_param_from_anteproc(baseDir, IFO, jg, jn):
    f = os.path.join(baseDir, 'anteproc_data', IFO + "-anteproc_params_group_" + str(jg) + "_" + str(int(jn)) + ".txt")
    outdict = {}
    for line in open(f):
        text = line.split(" ")
        outdict[text[0]] = text[1]
    return outdict

def Round_To_n(x, n):
    return round(x, -int(np.floor(np.sign(x) * np.log10(abs(x)))) + n)

def gather_output(baseDir):
    
    configfile = [ele for ele in os.listdir(os.path.join(baseDir, 'input_files')) if ele[-4:] == '.ini'][0]
    configs = ConfigParser.ConfigParser()
    configs.read(os.path.join(baseDir, 'input_files', configfile))

    variations = configs.getboolean('variations', 'doVariations')
    injection = configs.getboolean('injection', 'doInjections')

    outdata = {}

    if variations:
        numJobGroups = configs.getint('variations', 'numJobGroups')
        varyingParam = configs.get('variations', 'paramName')
        varyingDist = configs.get('variations', 'distribution')
        if varyingParam not in ['stamp.alpha', 'stamp.phi', 'stamp.iota', 'stamp.psi']:
            outdata[varyingParam] = []
    else:
        numJobGroups = 1

    if injection:
        outdata["recov"] = []
        outdata['alpha'] = []
        outdata['h0'] = []
        outdata['InjAmp'] = []
        outdata['phi'] = []
        outdata['iota'] = []
        outdata['psi'] = []
        outdata['injfreq'] = []

    outdata['SNR'] = []
    outdata['tmin'] = []
    outdata['tmax'] = []
    outdata['fmin'] = []
    outdata['fmax'] = []
    outdata['length'] = []
    outdata['jobNumH'] = []
    outdata['jobNumL'] = []
    outdata['Group'] = []
    outdata['Job'] = []
    for i in range(numJobGroups):
        jgdir = os.path.join(baseDir, 'jobs', 'job_group_' + str(i+1))
        jobcounter = 0
        for jobdir in [os.path.join(jgdir, ele) for ele in os.listdir(jgdir)]:
            jobcounter+=1
            try:
                datapoint = pd.DataFrame
                files = os.listdir(os.path.join(jobdir, 'grandStochtrackOutput'))
                matfile = [ele for ele in files if 'mat' in ele][0]
                mat = sio.loadmat(os.path.join(jobdir, 'grandStochtrackOutput', matfile))
                outdata['SNR'].append(mat['stoch_out']['max_SNR'][0,0][0,0])
                outdata['fmin'].append(mat['stoch_out'][0,0]['fmin'][0,0])
                outdata['fmax'].append(mat['stoch_out'][0,0]['fmax'][0,0])
                outdata['tmin'].append(mat['stoch_out'][0,0]['tmin'][0,0])
                outdata['tmax'].append(mat['stoch_out'][0,0]['tmax'][0,0])
                outdata['length'].append(outdata['tmax'][-1] - outdata['tmin'][-1])
                outdata['Group'].append(i+1)
                outdata['Job'].append(jobcounter)
                inmat = sio.loadmat(os.path.join(jobdir, 'grandStochtrackInput', 'params.mat'))
                
                H1num = int(inmat['params']['anteproc'][0][0]['jobNum1'][0][0][0][0])
                L1num = int(inmat['params']['anteproc'][0][0]['jobNum2'][0][0][0][0])

                outdata['jobNumH'].append(H1num)
                outdata['jobNumL'].append(L1num)

                H1anteproc = get_param_from_anteproc(baseDir, 'H1', i+1, H1num)
                L1anteproc = get_param_from_anteproc(baseDir, 'L1', i+1, L1num)


                if variations:
                    hval = H1anteproc[varyingParam]
                    lval = L1anteproc[varyingParam]

                    if varyingParam not in ['stamp.alpha', 'stamp.phi', 'stamp.iota', 'stamp.psi', 'stamp.f0']:
                        outdata[varyingParam].append(hval)

                    if not hval == lval:
                        raise ValueError("Error: Values for parameter {} do not match between H and L; " + \
                                         "job group {}, H job {}, L job {}".format(varyingParam, i+1, 
                                                        H1num, L1num))

                if injection:
                    for key in ['stamp.alpha', 'stamp.phi0', 'stamp.iota', 'stamp.psi']:
                        if not H1anteproc[key] == L1anteproc[key]:
                            raise ValueError("Error: Values for parameter {} do not match between H and L; " + \
                                         "job group {}, H job {}, L job {}".format(key, i+1, 
                                                        H1num, L1num))
                    injfreq = float(H1anteproc['stamp.f0'])
                    outdata['recov'].append( (float(outdata['fmin'][-1]) - injfreq) * (float(outdata['fmax'][-1]) - injfreq) < 0 )
                    outdata['alpha'].append(Round_To_n(float(H1anteproc['stamp.alpha']), 3))
                    outdata['h0'].append(Round_To_n(float(H1anteproc['stamp.h0']),3))
                    outdata['InjAmp'].append(Round_To_n(np.sqrt(2)*float(H1anteproc['stamp.h0'])*np.sqrt(float(H1anteproc['stamp.alpha'])), 3))
                    outdata['phi'].append(float(H1anteproc['stamp.phi0']))
                    outdata['iota'].append(float(H1anteproc['stamp.iota']))
                    outdata['psi'].append(float(H1anteproc['stamp.psi']))
                    outdata['injfreq'] = injfreq
                

            except IndexError:
                print("job " + str(i) + "has not finished yet")

    allkeys = outdata.keys()

    ordered_keys = ['Group', 'Job', 'SNR', 'fmin', 'fmax', 'length', 'tmin', 'tmax', 'jobNumH', 'jobNumL', 'injfreq', 'phi', 'iota', 'psi', 'alpha', 'h0', 'InjAmp', 'recov']
    ordered_keys = [ele for ele in ordered_keys if ele in allkeys]

    if variations and varyingParam not in ['stamp.alpha', 'stamp.phi', 'stamp.iota', 'stamp.psi', 'stamp.f0']:
        ordered_keys.append(varyingParam)

    output_frame = pd.DataFrame(outdata, index=range(1, len(outdata['SNR'])+1))
    output_frame = output_frame.round({'SNR': 2})
    output_frame = output_frame[ordered_keys]
    output_frame.to_csv(os.path.join(baseDir, 'STAMP_output_dataframe.csv'))
    output_frame.to_html(buf=open(os.path.join(baseDir, 'STAMP_output_data.html'), 'w'))

    return output_frame

if __name__ == "__main__":
    main()
