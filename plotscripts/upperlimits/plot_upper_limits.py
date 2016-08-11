from __future__ import division
from optparse import OptionParser
import scipy.io as sio
import os
import json
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['legend.numpoints'] = 1

# command line options
parser = OptionParser()
parser.set_defaults(verbose = False)
parser.set_defaults(polarization = False)
parser.set_defaults(reloadJSONs = False)
parser.set_defaults(lockPlot = False)
parser.set_defaults(pretty_version = False)

parser.add_option("-d", "--baseDir", dest = "baseDir",
                  help = "Path to stamp analysis directory to search for job pairs below threshold",
                  metavar = "DIRECTORY")
parser.add_option("-o", "--outDir", dest = "outputDir",
                  help = "Path to directory to hold analysis output",
                  metavar = "DIRECTORY")
parser.add_option("-s", "--snr", dest = "thresholdSNR",
                  help = "Threshold SNR below which to find job pairs",
                  metavar = "FLOAT")
parser.add_option("-p", "--percent", dest = "thresholdPercent",
                  help = "Threshold percent (1 = 100%)",
                  metavar = "FLOAT")
parser.add_option("-t", "--tag", dest = "tag",
                  help = "Tag to apply to output file name",
                  metavar = "STRING")
parser.add_option("-L", "--labels", dest = "labels",
                  help = "Labels for data sets",
                  metavar = "STRING")
parser.add_option("-m", "--markers", dest = "markers",
                  help = "Markers for data sets",
                  metavar = "STRING")
parser.add_option("-x", "--xlim", dest = "xlim",
                  help = "Limits for x-limits",
                  metavar = "STRING")
parser.add_option("-n", "--onsourceJob", dest = "onsourceJob",
                  help = "Job number with on-source data (optional)",
                  metavar = "INTEGER")

parser.add_option("-v", action="store_true", dest="verbose")
parser.add_option("-P", action="store_true", dest="polarization")
parser.add_option("-R", action="store_true", dest="reloadJSONs")
parser.add_option("-G", action="store_true", dest="lockPlot")
parser.add_option("-V", action="store_true", dest="pretty_version")

(options, args) = parser.parse_args()

polarized_version = options.polarization

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

"""def getSNRandJobPair(file_path):
    temp_mat = sio.loadmat(file_path)
    job_1 = temp_mat['q']['params'][0,0][0,0]['anteproc']['jobNum1'][0,0][0,0]
    job_2 = temp_mat['q']['params'][0,0][0,0]['anteproc']['jobNum2'][0,0][0,0]
    temp_snr = temp_mat['stoch_out']['max_SNR'][0,0][0,0]
    return [temp_snr, job_1, job_2, file_path]"""

def getSNRandAlpha(file_path):
    temp_mat = sio.loadmat(file_path)
    temp_snr = temp_mat['stoch_out']['max_SNR'][0,0][0,0]
    temp_alpha = temp_mat['stoch_out']['params'][0,0][0,0]['stamp']['alpha'][0,0][0,0]
    temp_iota = float(temp_mat['stoch_out']['params'][0,0][0,0]['stamp']['iota'][0,0][0,0])
    return [temp_snr, temp_alpha, temp_iota]

def find_path(directory, temp_tag):
    temp_files = [glueFileLocation(directory, x) for x in os.listdir(directory) if "job_pairs_with_low_SNR_old_version_" in x]
    if temp_files:
        return temp_files
    else:
        temp_path = glueFileLocation(directory, "job_pairs_with_low_SNR_old_version_" + temp_tag + ".txt")
        return [temp_path]

def str_truncate(number, decimal_values = 2):
    power_ten = np.floor(np.log10(number))
    truncated_number = str(int(np.round(number/np.power(10,power_ten)*np.power(10,decimal_values))))
    truncated_number = truncated_number[0] + "." + truncated_number[1:] + "e" + str(int(power_ten))
    return truncated_number

#baseJobDir = glueFileLocation(options.baseDir, "jobs")
#baseDirs = options.baseDir.split(",")
baseDirs = [x.split(",") for x in options.baseDir.split(",,")]
#baseJobDirs = [glueFileLocation(x, "jobs") for x in baseDirs]
baseJobDirs = [[glueFileLocation(x, "jobs") for x in temp_dir] for temp_dir in baseDirs]
#thresholdSNR = float(options.thresholdSNR)
thresholdSNRs = [float(x) for x in options.thresholdSNR.split(",")]
#threshold_percent = float(options.thresholdPercent)
threshold_percentages = [float(x) for x in options.thresholdPercent.split(',')]
outputPath = options.outputDir
labels = options.labels.split(",")
if options.markers:
    markers = options.markers.split(",")
if options.xlim:
    xLimits = [float(x.replace('m','-')) for x in options.xlim.split(",")]
else:
    xLimits = None
if options.onsourceJob:
    onsourceJob = options.onsourceJob
else:
    onsourceJob = None

"""if options.outputDir:
    outputPath = glueFileLocation(options.outputDir, "job_pairs_with_low_SNR_" + options.tag + ".txt")
elif len(baseDirs) == 1:
    outputPath = glueFileLocation(options.baseDir, "job_pairs_with_low_SNR_" + options.tag + ".txt")
else:
    outputPaths = [glueFileLocation(temp_dir, "job_pairs_with_low_SNR_" + options.tag + ".txt") for temp_dir in baseDirs]"""
#jsonPaths = [temp_file for temp_dir in baseDirs for temp_file in find_path(temp_dir, options.tag)]

#jsonPaths = [[temp_file for temp_dir in tempBaseDirs for temp_file in find_path(temp_dir, options.tag)] for tempBaseDirs in baseDirs]
jsonPaths = [[temp_dir for temp_dir in tempBaseDirs] for tempBaseDirs in baseDirs]
print("Information saved in " + str(jsonPaths))
print("Plots saved in " + outputPath)

temp_data_sets = []
for tempJsonPaths in jsonPaths:
    temp_data = []
    #for temp_path in tempJsonPaths:
    for temp_directory in tempJsonPaths:
        temp_files = find_path(temp_directory, options.tag)
        for temp_path in temp_files:
            if os.path.isfile(temp_path) and not options.reloadJSONs:
                with open(temp_path, 'r') as infile:
                    temp_data += [json.load(infile)]
            else:
                target_dir = glueFileLocation(temp_directory, "jobs")
                jobGroupDirs = [glueFileLocation(target_dir, x) for x in os.listdir(target_dir) if "job_group" in x]
                jobDirs = [glueFileLocation(temp_dir, x) for temp_dir in jobGroupDirs for x in os.listdir(temp_dir) if "job" in x]
                gsOutputDirs = [glueFileLocation(temp_dir, "grandstochtrackOutput") for temp_dir in jobDirs]
                bknd_files = [glueFileLocation(temp_dir, x) for temp_dir in gsOutputDirs for x in os.listdir(temp_dir) if "bknd" in x]

                single_temp_data = [getSNRandAlpha(x) for x in bknd_files]
                #single_temp_data = dict((x[x.rindex("/")+1:], getSNRandAlpha(x)) for x in bknd_files)
                """single_temp_dict = {}
                single_temp_dict["SNR data"] = single_temp_data
                if onsourceJob:
                    jobMatName = "bknd_" + onsourceJob + ".mat"
                    onsource_temp_data = [getSNRandAlpha(x) for x in bknd_files if bknd_files[bknd_files.rindex("/"+1):] == jobMatName]
                    single_temp_dict["On-source SNRs"] = onsource_temp_data"""
                temp_data += [single_temp_data]
                #temp_data += [single_temp_dict]
                with open(temp_path, 'w') as outfile:
                    json.dump(single_temp_data, outfile, sort_keys = True, indent = 4)
                    #json.dump(single_temp_dict, outfile, sort_keys = True, indent = 4)
    temp_data_sets += [temp_data]
#print(temp_data_sets)
#print(len(temp_data_sets[0]))
orderedData = {}
for set_num in range(len(temp_data_sets)):
    #for x in temp_data:
    temp_orderedData = {}
    for sub_set in temp_data_sets[set_num]:
        temp_alpha_dictionary = {}
        #print(sub_set)
        #temp_SNR_data = sub_set["SNR data"]
        #print(temp_SNR_data)
        #for x in temp_SNR_data:
        for x in sub_set:
            temp_SNR = x[0]
            temp_alpha = x[1]
            if temp_alpha not in temp_alpha_dictionary:
                temp_alpha_dictionary[temp_alpha] = []
            if temp_SNR not in temp_alpha_dictionary[temp_alpha]:
                temp_alpha_dictionary[temp_alpha] += [temp_SNR]
        for temp_temp_alpha in temp_alpha_dictionary:
            temp_orderedData[temp_temp_alpha] = temp_alpha_dictionary[temp_temp_alpha]
    """for x in temp_data_sets[set_num]:
        temp_SNR = x[0]
        temp_alpha = x[1]
        if temp_alpha not in temp_orderedData:
            temp_orderedData[temp_alpha] = []
        if temp_SNR not in temp_orderedData[temp_alpha]:
            temp_orderedData[temp_alpha] += [temp_SNR]"""
    orderedData[labels[set_num]] = temp_orderedData

#better to start making this structure everytime and saving it instead of the list.
def get_info(ordered_data, threshold_SNR, temp_temp_data):
    test_lengths = [len(ordered_data[x]) for x in ordered_data]
    num_above_threshold = [[len([y for y in ordered_data[x] if y > threshold_SNR]), x] for x in ordered_data]
    #passed_alphas = [x[1] for ind, x in enumerate(num_above_threshold) if x[0]/test_lengths[ind] >= threshold_percent]
    passed_alphas = [[x[1] for ind, x in enumerate(num_above_threshold) if x[0]/test_lengths[ind] >= temp_percent] for temp_percent in threshold_percentages]
    #if isinstance(passed_alphas, list) and len(passed_alphas) > 0:
    #    threshold_alpha = min(passed_alphas)
    #else:
    #    threshold_alpha = None
    if isinstance(passed_alphas, list) and len(passed_alphas) > 0:
        threshold_alphas = [min(x) if len(x) > 0 else None for x in passed_alphas]
    else:
        threshold_alphas = None
    #print([x for x in test_lengths])
    #print([x[0] for x in num_above_threshold])
    percentiles = [num_above_threshold[x][0]/test_lengths[x] for x in range(len(test_lengths))]
    alphas_p = [x[1] for x in num_above_threshold]
    temp_indices = np.argsort(alphas_p)
    sorted_percentiles = [percentiles[x] for x in temp_indices]
    sorted_alphas_p = [alphas_p[x] for x in temp_indices]
    sorted_num_data = [test_lengths[x] for x in temp_indices]

    SNRs = [x[0] for y in temp_temp_data for x in y]#["SNR data"]]
    alphas = [x[1] for y in temp_temp_data for x in y]#["SNR data"]]
    #SNRs = [y[x][0] for y in temp_temp_data for x in y]
    #alphas = [y[x][1] for y in temp_temp_data for x in y]
    #print([len(y) for y in temp_temp_data])
    #print(len(temp_temp_data))

    if onsourceJob:
        onsourceRequiredString = "bknd_" + onsourceJob + ".mat"
        onsourceSNRs = [y[x][0] for y in temp_temp_data for x in y if onsourceRequiredString in x]
        onsourceAlphas = [y[x][1] for y in temp_temp_data for x in y if onsourceRequiredString in x]
        print([x for y in temp_temp_data for x in y])
        onsourceHighSNRs = [x for x in onsourceSNRs if x > threshold_SNR]
        onsourceHighAlphas = [onsourceAlphas[x] for x in range(len(onsourceAlphas)) if onsourceSNRs[x] > threshold_SNR]
        onsourceLowSNRs = [x for x in onsourceSNRs if x <= threshold_SNR]
        onsourceLowAlphas = [onsourceAlphas[x] for x in range(len(onsourceAlphas)) if onsourceSNRs[x] <= threshold_SNR]
    else:
        onsourceHighSNRs = None
        onsourceHighAlphas = None
        onsourceLowSNRs = None
        onsourceLowAlphas = None

    highSNRs = [x for x in SNRs if x > threshold_SNR]
    highAlphas = [alphas[x] for x in range(len(alphas)) if SNRs[x] > threshold_SNR]

    lowSNRs = [x for x in SNRs if x <= threshold_SNR]
    lowAlphas = [alphas[x] for x in range(len(alphas)) if SNRs[x] <= threshold_SNR]
    #return [[sorted_percentiles, sorted_alphas_p, threshold_alpha], [highSNRs, highAlphas, lowSNRs, lowAlphas]]
    return [[sorted_percentiles, sorted_alphas_p, threshold_alphas, sorted_num_data], [highSNRs, highAlphas, lowSNRs, lowAlphas], [onsourceHighSNRs, onsourceHighAlphas, onsourceLowSNRs, onsourceLowAlphas]]

def normal_binomial_approximation_interval(proportion, confidence_level, number_samples):
    error_quantile = 1-confidence_level
    z_stat = 1-error_quantile/2
    half_width = z_stat * np.sqrt(proportion*(1-proportion)/number_samples)
    return half_width

def Wilson_score_interval():
    return None

data_info = [get_info(orderedData[labels[num]], thresholdSNRs[num], temp_data_sets[num]) for num in range(len(labels))]

#outputPath = glueFileLocation(options.baseDir, "job_pairs_with_low_SNR_" + options.tag + ".txt")
#if not os.path.isfile(outputPath):
#    with open(outputPath, 'w') as outfile:
#        json.dump(temp_data, outfile, sort_keys = True, indent = 4)
if not polarized_version:
    for num in range(len(labels)):
        highSNRs = data_info[num][1][0]
        highAlphas = data_info[num][1][1]
        lowSNRs = data_info[num][1][2]
        lowAlphas = data_info[num][1][3]
        highSNRsOnsource = data_info[num][2][0]
        highAlphasOnsource = data_info[num][2][1]
        lowSNRsOnsource = data_info[num][2][2]
        lowAlphasOnsource = data_info[num][2][3]
        #threshold_alpha = data_info[num][0][2]
        threshold_alphas = data_info[num][0][2]
        plt.grid(b=True, which='minor',color='0.85',linestyle='--')
        plt.grid(b=True, which='major',color='0.75',linestyle='-')
        #print(highAlphas)
        #print(highSNRs)
        plt.plot([np.sqrt(x) for x in highAlphas], highSNRs,'rx')#, label = "SNR distribution")
        plt.plot([np.sqrt(x) for x in lowAlphas], lowSNRs,'bx', alpha = 0.5)#, label = "SNR distribution")
        if onsourceJob:
            plt.plot([np.sqrt(x) for x in highAlphasOnsource], highSNRsOnsource,'m+')#, label = "SNR distribution")
            plt.plot([np.sqrt(x) for x in lowAlphasOnsource], lowSNRsOnsource,'g+', alpha = 0.5)#, label = "SNR distribution")
        plt.axhline(y=thresholdSNRs[num], xmin=0, xmax=1, hold=None, linestyle='--', color='g')
        #plt.yscale('log')
        plt.xscale('log')
        plt.xlabel("Square root of scale factor alpha")
        #plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
        #plt.ylabel('Strain [Counts / sqrt(Hz)]')
        plt.ylabel("SNR")
        #plt.title("Threshold alpha = " + str(threshold_alpha) + ", threshold percentile = " + str(threshold_percent))#str(min(highAlphas)))
        plt.title("\n".join("Threshold alpha = " + str(threshold_alphas[x]) + ", threshold percentile = " + str(threshold_percentages[x]) for x in range(len(threshold_percentages))))#str(min(highAlphas)))
        #legend = plt.legend(prop={'size':6})#, framealpha=0.5)
        #legend.get_frame().set_alpha(0.5)
        #plt.show()
        plt.savefig(glueFileLocation(outputPath, "upper_limit_estimate_" + options.tag + "_" + labels[num]), bbox_inches = 'tight')
        plt.clf()

    """temp_indices = np.argsort(alphas_p)
sorted_percentiles = [percentiles[x] for x in temp_indices]
sorted_alphas_p = [alphas_p[x] for x in temp_indices]"""

    plt.grid(b=True, which='minor',color='0.85',linestyle='--')
    plt.grid(b=True, which='major',color='0.75',linestyle='-')
    #print(data_info[0][0][0])
    for num in range(len(labels)):
        sorted_percentiles = data_info[num][0][0]
        sorted_alphas_p = data_info[num][0][1]
        #threshold_alpha = data_info[num][0][2]
        threshold_alphas = data_info[num][0][2]
        print(labels[num])
        #print(sorted_percentiles)
        print(threshold_alphas)
        for index, val in enumerate(sorted_alphas_p):
            if val in threshold_alphas:
                print(val)
                print(sorted_percentiles[index])
        #plt.plot([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, 'x-', label = "Threshold alpha = " + str(threshold_alpha))
        if options.pretty_version:
            plt.plot([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, markers[num]+'-', label = "Threshold alpha = " + ", ".join(str_truncate(temp_threshold)for temp_threshold in threshold_alphas) + " " + labels[num].replace("_"," "))
        else:
            plt.plot([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, 'x-', label = "Threshold alpha = " + ", ".join(str(temp_threshold)for temp_threshold in threshold_alphas))# + " " + labels[num])
        #if threshold_alpha:
        #    plt.axvline(x=np.sqrt(threshold_alpha), ymin=0, ymax=1, hold=None, linestyle='--', color='0.75', alpha = 0.7)
        if threshold_alphas and not options.pretty_version:
            for temp_threshold in threshold_alphas:
                if temp_threshold:
                    plt.axvline(x=np.sqrt(temp_threshold), ymin=0, ymax=1, hold=None, linestyle='--', color='k', alpha = 0.7)
    for temp_percentage in threshold_percentages:
        plt.axhline(y=temp_percentage, xmin=0, xmax=1, hold=None, linestyle='--', color='k', alpha = 0.7)
    #plt.yscale('log')
    plt.xscale('log')
    plt.xlabel("Square root of scale factor alpha")
    if xLimits:
        plt.xlim(xLimits)
    #plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
    #plt.ylabel('Strain [Counts / sqrt(Hz)]')
    plt.ylabel("Efficiency")
    #plt.title("Threshold alpha = " + str(threshold_alpha) + ", threshold percentile = " + str(threshold_percent))#str(min(highAlphas)))
    #plt.title("Threshold percentile = " + str(threshold_percent))#str(min(highAlphas)))
    plt.title("Threshold = " + ", ".join(str(temp_threshold) for temp_threshold in threshold_percentages))#str(min(highAlphas)))
    legend = plt.legend(prop={'size':6},loc='best')#, framealpha=0.5)
    legend.get_frame().set_alpha(0.5)
    if options.lockPlot:
        plt.ylim([0,1])
    #plt.show()
    print(glueFileLocation(outputPath, "detection_efficiency_estimate_" + options.tag))

    if options.pretty_version:
        plt.rc('text', usetex = True)
        plt.rc('font', family = 'sarif')
    #    plt.ylabel("False Alarm Probability")
    #    plt.savefig(dir_name + "/SNRvsFAP_all_clusters_semilogy_average_2.pdf", bbox_inches = 'tight', format='pdf')
    #else:
    plt.savefig(glueFileLocation(outputPath, "detection_efficiency_estimate_" + options.tag), bbox_inches = 'tight')
    plt.clf()

elif polarized_version:
    iotas = []
    SNRs = []
    for set_num in range(len(temp_data_sets)):
    #for x in temp_data:
        temp_orderedData = {}
        for x in temp_data_sets[set_num]["SNR data"]:
            temp_SNR = x[0]
            temp_alpha = x[1]
            temp_iota = x[2]
            iotas+=[temp_iota]
            SNRs+=[temp_SNR]
    cos_iotas = [np.cos(np.deg2rad(x)) for x in iotas]
    sorted_indices = np.argsort(cos_iotas)
    cos_iotas = [cos_iotas[x] for x in sorted_indices]
    SNRs = [SNRs[x] for x in sorted_indices]
    plt.grid(b=True, which='minor',color='0.85',linestyle='--')
    plt.grid(b=True, which='major',color='0.75',linestyle='-')
    plt.plot(cos_iotas, SNRs, 'x')
    #plt.yscale('log')
    #plt.xscale('log')
    plt.xlabel("Cos iota")
    #plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
    #plt.ylabel('Strain [Counts / sqrt(Hz)]')
    plt.ylabel("SNR")
    #plt.title("Threshold alpha = " + str(threshold_alpha) + ", threshold percentile = " + str(threshold_percent))#str(min(highAlphas)))
    #legend = plt.legend(prop={'size':6})#, framealpha=0.5)
    #legend.get_frame().set_alpha(0.5)
    #plt.show()
    plt.savefig(glueFileLocation(outputPath, "SNR_vs_cos_iota_" + options.tag), bbox_inches = 'tight')
    plt.clf()
