from __future__ import division
import scipy.io as sio
import os
import json
import numpy as np
import matplotlib as mpl
mpl.use('Agg')
from matplotlib.ticker import FormatStrFormatter
import matplotlib.pyplot as plt
plt.rcParams['legend.numpoints'] = 1

trigger_number = 2471

background_based_upper_limits = True

alternate_polarization = True#False#True
polarized_version = False#True#False#True
polarized_separate = False#True
polarized_test = False#True

plot_mode = "shaded"#"plain"#"errorbar"#"shaded"
show_legend = False# controls if legend is shown if 'plot_mode' is set to 'plain'

additional_plots = True#True#False

x_Limits = True#True#False

pretty_version = True

reloadJSONs = False#True#False

lockPlot = True#False

check_mat_files_onsource = False#False#True

abs_version = True#False#True#False

plot_interpolated_points = False#True#False

if alternate_polarization:
    x_Limits = False
    #plot_interpolated_points = True

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
    temp_files = [glueFileLocation(directory, x) for x in os.listdir(directory) if "job_pairs_with_low_SNR_" in x]
    if temp_files:
        return temp_files
    else:
        temp_path = glueFileLocation(directory, "job_pairs_with_low_SNR_" + temp_tag + ".txt")
        return [temp_path]

def str_truncate(number, decimal_values = 2):
    power_ten = np.floor(np.log10(number))
    truncated_number = str(int(np.round(number/np.power(10,power_ten)*np.power(10,decimal_values))))
    truncated_number = truncated_number[0] + "." + truncated_number[1:] + "e" + str(int(power_ten))
    return truncated_number

def color_conversion(R, G, B):
    return (R/256, G/256, B/256)

def find_surrounding_values(target_value, iota_values, SNR_values):
    max_SNR_value = max(SNR_values)
    min_SNR_value = min(SNR_values)
    if not (max_SNR_value >= target_value) or not (min_SNR_value <= target_value) or min(iota_values) > 0:
        print("No values")
    else:
        SNR_lower_split = [SNR_values[x] for x in range(len(SNR_values)) if SNR_values[x] < target_value and iota_values[x] < 90]
        SNR_upper_split = [SNR_values[x] for x in range(len(SNR_values)) if SNR_values[x] >= target_value and iota_values[x] < 90]
        iota_lower_split = [iota_values[x] for x in range(len(SNR_values)) if SNR_values[x] < target_value and iota_values[x] < 90]
        iota_upper_split = [iota_values[x] for x in range(len(SNR_values)) if SNR_values[x] >= target_value and iota_values[x] < 90]
        #if len(iota_lower_split) > 0:
        #    print(max(iota_lower_split))
        lower_values = [[SNR_lower_split[ind], iota_lower_split[ind]] for ind, value in enumerate(SNR_lower_split) if value == max(SNR_lower_split)]
        upper_values = [[SNR_upper_split[ind], iota_upper_split[ind]] for ind, value in enumerate(SNR_upper_split) if value == min(SNR_upper_split)]
        #print(min(SNR_values))
        print("lower values")
        print(lower_values)
        print("upper values")
        print(upper_values)

        #print(lower_values)
        #print(lower_values[0])
        #print(lower_values[1])
        transformed_lower = [lower_values[0][0], np.cos(np.radians(lower_values[0][1]))]
        transformed_upper = [upper_values[0][0], np.cos(np.radians(upper_values[0][1]))]
        cos_iota_slope = (transformed_upper[1] - transformed_lower[1])/(transformed_upper[0] - transformed_lower[0])
        shift_ammount = (target_SNR_value - transformed_lower[0])*cos_iota_slope
        cos_iota_target = transformed_lower[1]+shift_ammount
        iota_target = np.degrees(np.arccos(cos_iota_target))
        #print(shift_ammount)
        #print(cos_iota_target)
        #print(np.arccos(cos_iota_target))
        print("target values")
        print([target_value, iota_target])
#        upper_index = None
 #       lower_inde
  #      print("SNR values")
   #     print(SNR_lower_split[0])
    #    print(SNR_upper_split[
        #for x in range(len(iota_values)):
         #   if SNR_values[x] == max_SNR_value or SNR_values == min_SNR_value:
          #      print("SNR value")
           #     print(SNR_values[x])
            #    print("iota value")
             #   print(iota_values[x])

#plot_mode = "plain"#"plain"#"errorbar"#"shaded"

outputPath = "/home/quitzow/public_html/Magnetar/upper_limits/"

#x_Limits = False
if trigger_number == 2469:
    thresholdSNRs = [5.73448522466, 5.73448522466, 5.73448522466, 5.73448522466, 5.73448522466, 5.73448522466]
    #x_Limits = False
    if polarized_version:
        baseDirs = [['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/polarization_overview/stamp_analysis_anteproc-2015_12_3'],
                    ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/polarization_overview/stamp_analysis_anteproc-2016_1_3']]#"""

        name_tag = "sgr_trigger_2469_variable_polarization"
        if abs_version:
            name_tag += "_abs"
        outputPath = glueFileLocation(outputPath, "sgr_trigger_2469/polarization_overview")
        #x_Limits = False
    elif alternate_polarization:
        thresholdSNRs = [6.06371569253, 6.06371569253, 6.06371569253, 6.06371569253, 6.06371569253, 6.06371569253]
        #baseDirs = [['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_8', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_10'],
        #        ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_8', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_10']]
        baseDirs = [['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_13',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_13_v2',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_2_11',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_2_12_v2',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_2_12_v3',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_3_10/'],
                    ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_13',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_13_v2',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_2_12',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_2_12_v2',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_2_12_v3']]

        name_tag = "sgr_trigger_2469_alternate_polarization"
        outputPath = glueFileLocation(outputPath, "sgr_trigger_2469/plot/alternate_polarization/")
        #xLimits = [7e-23, 6e-22]#[9e-23, 6e-22]#[1e-22, 3e-21]#4e-21]#[6e-23, 1e-21]
    else:
        baseDirs = [['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_10_23',# '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_10_31',
                 '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_1', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_1_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_1_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_1_v4',#],
                 '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_18', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_18_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_18_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_18_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_18_v5', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_19'],
                #['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_10_23',
                # '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_10_31', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_1', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_1_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_1_v3'],#, '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_400/stamp_analysis_anteproc-2015_11_1_v4'],

                #['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_21_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_25', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_26', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_26_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v5', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v6', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v7', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v8'],
                ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_21_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_25', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_26', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_26_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v5', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v6', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v7', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v8',#],
                 '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_11_18', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_11_19'],
                #['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_21_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_25', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_26', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_26_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v5', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v6'],#, '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v7'],#, '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_400/stamp_analysis_anteproc-2015_10_29_v8'],

                #['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_22', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_29', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_29_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30_v5'],
                ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_22', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_29', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_29_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30_v5',#],
                 '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_11_18', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_11_19'],
                #['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_22',
                # '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_29', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_29_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30_v4'],#, '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_400/stamp_analysis_anteproc-2015_10_30_v5'],

                #['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_10_23', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_10_31', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_5', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_5_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v4'],
                #['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_10_23', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_10_31', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_5', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_5_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v3'],#, '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v4'],
                ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_10_23', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_10_31', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_5', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_5_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/variation_test/stamp_analysis_anteproc-2015_11_15_v2',
                 '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/variation_test/stamp_analysis_anteproc-2015_11_18', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_18', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_18_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_18_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_19', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_19_v2'],
                #, '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v4'],
                #['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_10_23', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_10_31', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_1_v4',# '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_5',
                # '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_5_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v3'],#, '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v4'],

                #['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_21_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_25', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_26', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_26_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_29'],
                #['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_21_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_25', #'/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_26',
                # '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_26_v2'],#, '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_29'],
                ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_21_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_25', #'/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_26',
                 '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_26_v2',#],#, '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_10_29'],
                 '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/variation_test/stamp_analysis_anteproc-2015_11_18', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/variation_test/stamp_analysis_anteproc-2015_11_18_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_11_18', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_450/tau_150/stamp_analysis_anteproc-2015_11_19'],

                #['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/stamp_analysis_anteproc-2015_10_21_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/stamp_analysis_anteproc-2015_10_30', #'/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/stamp_analysis_anteproc-2015_10_30_v2',
                # '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/stamp_analysis_anteproc-2015_10_30_v3']]#, '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/stamp_analysis_anteproc-2015_10_30_v4']]
                ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/stamp_analysis_anteproc-2015_10_21_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/stamp_analysis_anteproc-2015_10_30', #'/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/stamp_analysis_anteproc-2015_10_30_v2',
                 '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/stamp_analysis_anteproc-2015_10_30_v3',#]]#, '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/stamp_analysis_anteproc-2015_10_30_v4']]
                 '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/variation_test/stamp_analysis_anteproc-2015_11_18', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/variation_test/stamp_analysis_anteproc-2015_11_18_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/stamp_analysis_anteproc-2015_11_19', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/f0_750/tau_150/stamp_analysis_anteproc-2015_11_19_v2']]

        name_tag = "sgr_trigger_2469_testing_focus_40"
        outputPath += "sgr_trigger_2469/plot/"
        xLimits = [6e-23, 1e-21]#[9e-23, 6e-22]#[1e-22, 3e-21]#4e-21]#[6e-23, 1e-21]

elif trigger_number == 2471:
    if not background_based_upper_limits:
        # for upper limits based on open box
        thresholdSNRs = [5.78991295767, 5.78991295767, 5.78991295767, 5.78991295767, 5.78991295767, 5.78991295767]
    else:
        # for upper limits based on background only
        thresholdSNRs = [7.21733013944, 7.21733013944, 7.21733013944, 7.21733013944, 7.21733013944, 7.21733013944]
    if polarized_version:
#        baseDirs = [['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/polarization_test/stamp_analysis_anteproc-2015_10_17',
#                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/polarization_test/stamp_analysis_anteproc-2015_10_17_v2']]#"""

        baseDirs = [['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/stamp_analysis_anteproc-2015_10_19'],
                    ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/stamp_analysis_anteproc-2015_10_19_v2']]#"""

        name_tag = "sgr_trigger_2471_variable_polarization_plus"
        outputPath = glueFileLocation(outputPath, "sgr_trigger_2471/plot/polarization_variation")
        x_Limits = False
    elif alternate_polarization:
        baseDirs = [['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2015_12_1',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_31',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_2_1',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_2_1_v2',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_5_27'],
                    ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_2_1',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_2_11']]

        name_tag = "sgr_trigger_2471_alternate_polarization"
        outputPath = glueFileLocation(outputPath, "sgr_trigger_2471/plot/alternate_polarization/")#"""
    else:
        baseDirs = [['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_400/stamp_analysis_anteproc-2015_11_6', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_400/stamp_analysis_anteproc-2015_11_6_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_400/stamp_analysis_anteproc-2015_11_6_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_400/stamp_analysis_anteproc-2015_11_6_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_400/stamp_analysis_anteproc-2015_11_8', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_400/stamp_analysis_anteproc-2015_11_8_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_400/stamp_analysis_anteproc-2015_11_8_v3'],
            ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_450/tau_400/stamp_analysis_anteproc-2015_10_22', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_450/tau_400/stamp_analysis_anteproc-2015_10_22_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_450/tau_400/stamp_analysis_anteproc-2015_11_8', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_450/tau_400/stamp_analysis_anteproc-2015_11_8_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_450/tau_400/stamp_analysis_anteproc-2015_11_8_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_450/tau_400/stamp_analysis_anteproc-2015_11_8_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_450/tau_400/stamp_analysis_anteproc-2016_5_12'],
            ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_400/stamp_analysis_anteproc-2015_10_22', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_400/stamp_analysis_anteproc-2015_10_22_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_400/stamp_analysis_anteproc-2015_11_8_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_400/stamp_analysis_anteproc-2015_11_9', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_400/stamp_analysis_anteproc-2015_11_9_v2'],
            ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/stamp_analysis_anteproc-2015_10_18_v5', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_150/stamp_analysis_anteproc-2015_11_6_v3','/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_150/tau_150/stamp_analysis_anteproc-2016_5_27'],
            ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_450/tau_150/stamp_analysis_anteproc-2015_10_22', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_450/tau_150/stamp_analysis_anteproc-2015_10_22_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_450/tau_150/stamp_analysis_anteproc-2015_11_8', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_450/tau_150/stamp_analysis_anteproc-2015_11_8_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_450/tau_150/stamp_analysis_anteproc-2015_11_8_v3'],
            ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_150/stamp_analysis_anteproc-2015_10_22', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_150/stamp_analysis_anteproc-2015_10_22_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_150/stamp_analysis_anteproc-2015_11_9', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_150/stamp_analysis_anteproc-2015_11_9_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_150/stamp_analysis_anteproc-2015_11_9_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_150/stamp_analysis_anteproc-2015_11_9_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2471/f0_750/tau_150/stamp_analysis_anteproc-2015_11_9_v5']]#"""

        #thresholdSNRs = [5.78991295767, 5.78991295767, 5.78991295767, 5.78991295767, 5.78991295767, 5.78991295767]
        name_tag = "sgr_trigger_2471_testing_focus_40"
        outputPath += "sgr_trigger_2471/plot/"
        #xLimits = [1e-22, 2e-21]
        xLimits = [1e-22, 4e-21]

elif trigger_number == 2475:
    thresholdSNRs = [6.2449653625, 6.2449653625, 6.2449653625, 6.2449653625, 6.2449653625, 6.2449653625]
    if polarized_version:
        baseDirs = [['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/stamp_analysis_anteproc-2015_10_18_v9', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/stamp_analysis_anteproc-2015_10_19'],
                    ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/stamp_analysis_anteproc-2015_10_19_v3']]#"""

        name_tag = "sgr_trigger_2475_variable_polarization"
        if abs_version:
            name_tag += "_abs"
        outputPath = glueFileLocation(outputPath, "sgr_trigger_2475/plot/polarization_variation")
        x_Limits = False
    elif alternate_polarization:
        baseDirs = [['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_27',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_27_v2',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_28'],
                    ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_24_v2',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_27',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_27_v2',
                     '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_1_28']]#,
                     #'/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/polarization_version/stamp_analysis_anteproc-2016_2_12']]

        name_tag = "sgr_trigger_2475_alternate_polarization"
        outputPath = glueFileLocation(outputPath, "sgr_trigger_2475/plot/alternate_polarization/")
    else:
        baseDirs = [['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_400/stamp_analysis_anteproc-2015_11_9', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_400/stamp_analysis_anteproc-2015_11_11_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_400/stamp_analysis_anteproc-2015_11_11_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_400/stamp_analysis_anteproc-2015_11_11_v4'],
           #[['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_400/stamp_analysis_anteproc-2015_11_9', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_400/stamp_analysis_anteproc-2015_11_11', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_400/stamp_analysis_anteproc-2015_11_11_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_400/stamp_analysis_anteproc-2015_11_11_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_400/stamp_analysis_anteproc-2015_11_11_v4'],
            ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_450/tau_400/stamp_analysis_anteproc-2015_10_22', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_450/tau_400/stamp_analysis_anteproc-2015_10_22_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_450/tau_400/stamp_analysis_anteproc-2015_11_11', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_450/tau_400/stamp_analysis_anteproc-2015_11_11_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_450/tau_400/stamp_analysis_anteproc-2015_11_11_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_450/tau_400/stamp_analysis_anteproc-2015_11_11_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_450/tau_400/stamp_analysis_anteproc-2015_11_11_v5'],
            ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/stamp_analysis_anteproc-2015_10_22', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/stamp_analysis_anteproc-2015_10_22_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/stamp_analysis_anteproc-2015_11_11', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/stamp_analysis_anteproc-2015_11_11_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/stamp_analysis_anteproc-2015_11_12', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/stamp_analysis_anteproc-2015_11_12_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/stamp_analysis_anteproc-2015_11_12_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/stamp_analysis_anteproc-2015_11_12_v4', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_400/stamp_analysis_anteproc-2015_11_12_v5'],
            ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_150/stamp_analysis_anteproc-2015_11_10', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_150/stamp_analysis_anteproc-2015_11_10_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_150/tau_150/stamp_analysis_anteproc-2015_11_11'],
            ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_450/tau_150/stamp_analysis_anteproc-2015_10_22', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_450/tau_150/stamp_analysis_anteproc-2015_10_22_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_450/tau_150/stamp_analysis_anteproc-2015_11_11'],
            ['/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_150/stamp_analysis_anteproc-2015_10_22', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_150/stamp_analysis_anteproc-2015_11_11', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_150/stamp_analysis_anteproc-2015_11_11_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_150/stamp_analysis_anteproc-2015_11_12', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_150/stamp_analysis_anteproc-2015_11_12_v2', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_150/stamp_analysis_anteproc-2015_11_12_v3', '/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2475/f0_750/tau_150/stamp_analysis_anteproc-2015_11_12_v4']]#"""

        name_tag = "sgr_trigger_2475_testing_focus_40"
        outputPath += "sgr_trigger_2475/plot/"
        xLimits = [6e-23, 1e-21]



if plot_mode == "shaded":
    name_tag += "_shaded"
else:
    name_tag += "_thresholds"
# final save modifier
if trigger_number == 2469:
    name_tag += "_20"
elif trigger_number == 2471:
    if not background_based_upper_limits:
        # open box
        name_tag += "_20"
    else:
        # background only
        #name_tag += "_20_background"
        #name_tag += "_21_background"
        name_tag += "_22_background"
elif trigger_number == 2475:
    name_tag += "_20"
else:
    name_tag += "_4"#"_2"

threshold_percentages = [0.5, 0.9]
#outputPath = "/home/quitzow/public_html/Magnetar/upper_limits/sgr_trigger_2469/plot"

#additional_plots = False#True#False

"""labels = ['f0_150_tau_400',
          'f0_450_tau_400',
          'f0_750_tau_400',
          'f0_150_tau_150',
          'f0_450_tau_150',
          'f0_750_tau_150']"""
if polarized_version:
    labels = ['plus', 'cross']
elif alternate_polarization:
    labels = [r'$f_0 = 150 \, \mathrm{Hz}, \tau = 400 \, \mathrm{s}$',
          r'$f_0 = 750 \, \mathrm{Hz}, \tau = 400 \, \mathrm{s}$']
else:
    labels = [r'$f_0 = 150 \, \mathrm{Hz}, \tau = 400 \, \mathrm{s}$',
          r'$f_0 = 450 \, \mathrm{Hz}, \tau = 400 \, \mathrm{s}$',
          r'$f_0 = 750 \, \mathrm{Hz}, \tau = 400 \, \mathrm{s}$',
          r'$f_0 = 150 \, \mathrm{Hz}, \tau = 150 \, \mathrm{s}$',
          r'$f_0 = 450 \, \mathrm{Hz}, \tau = 150 \, \mathrm{s}$',
          r'$f_0 = 750 \, \mathrm{Hz}, \tau = 150 \, \mathrm{s}$']
#else:
#    labels = ['plus', 'cross']

markers = ['bx', 'b^', 'bo', 'gx', 'g^', 'go']
#colours = ['b', 'g', 'r', 'c', 'm', 'y']
colours = ['b', 'g', 'r', 'c', 'm', 'y']

"""colours = [color_conversion(31, 119, 180),
#174, 199, 232
color_conversion(255, 127, 14),
#255, 187, 120
color_conversion(44, 160, 44),
#152, 223, 138
color_conversion(214, 39, 40),
#255, 152, 150
color_conversion(148, 103, 189),
#197, 176, 213
color_conversion(140, 86, 75),
#196, 156, 148
color_conversion(227, 119, 194),
#247, 182, 210
color_conversion(127, 127, 127),
#199, 199, 199
color_conversion(188, 189, 34),
#219, 219, 141
color_conversion(23, 190, 207)]
#158, 218, 229#"""

# color blind 10
colours = [color_conversion(0, 107, 164),
color_conversion(255, 128, 14),
color_conversion(171, 171, 171),
color_conversion(89, 89, 89),
color_conversion(95, 158, 209),
color_conversion(200, 82, 0),
color_conversion(137, 137, 137),
color_conversion(162, 200, 236),
color_conversion(255, 188, 121),
color_conversion(207, 207, 207)]#"""

# arrange colors
#colours = [colours[4], colours[1], colours[2], colours[0], colours[5], colours[3]]
colours = [colours[0], colours[5], colours[3], colours[4], colours[1], colours[2]]

#-x 1em22,4em21

##baseDirs = [x.split(",") for x in options.baseDir.split(",,")]
baseJobDirs = [[glueFileLocation(x, "jobs") for x in temp_dir] for temp_dir in baseDirs]
##thresholdSNRs = [float(x) for x in options.thresholdSNR.split(",")]
##threshold_percentages = [float(x) for x in options.thresholdPercent.split(',')]
#outputPath = options.outputDir
#labels = options.labels.split(",")
#if options.markers:
#    markers = options.markers.split(",")

if not x_Limits:
    xLimits = None

onsourceJob = True
if onsourceJob:
    onsourceJob = "1"
else:
    onsourceJob = None

error_confidence_level = 0.95

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
        temp_files = find_path(temp_directory, name_tag)
        for temp_path in temp_files:
            if os.path.isfile(temp_path) and not reloadJSONs:
                if "tau_400" in temp_path and "f0_150" in temp_path and "sgr_trigger_2469" in temp_path:
                    with open(temp_path, 'r') as infile:
                        data_to_check = json.load(infile)
                    #print(data_to_check)
                    if not alternate_polarization:
                        data_to_check = dict((key, data_to_check[key]) for key in data_to_check if data_to_check[key][1] < 3e-44)
                    temp_data += [data_to_check]
                else:
                    with open(temp_path, 'r') as infile:
                        temp_data += [json.load(infile)]
            else:
                target_dir = glueFileLocation(temp_directory, "jobs")
                jobGroupDirs = [glueFileLocation(target_dir, x) for x in os.listdir(target_dir) if "job_group" in x]
                jobDirs = [glueFileLocation(temp_dir, x) for temp_dir in jobGroupDirs for x in os.listdir(temp_dir) if "job" in x]
                gsOutputDirs = [glueFileLocation(temp_dir, "grandstochtrackOutput") for temp_dir in jobDirs]
                bknd_files = [glueFileLocation(temp_dir, x) for temp_dir in gsOutputDirs for x in os.listdir(temp_dir) if "bknd" in x]

                #single_temp_data = [getSNRandAlpha(x) for x in bknd_files]
                #single_temp_data = dict((x[x.rindex("/")+1:], getSNRandAlpha(x)) for x in bknd_files)
                single_temp_data = dict((x, getSNRandAlpha(x)) for x in bknd_files)
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
##print(temp_data_sets[0][0])
for set_num in range(len(temp_data_sets)):
    #for x in temp_data:
    temp_orderedData = {}
    for sub_set in temp_data_sets[set_num]:
        temp_alpha_dictionary = {}
        #print(sub_set)
        #temp_SNR_data = sub_set["SNR data"]
        #print(temp_SNR_data)
        #for x in temp_SNR_data:
        #print(sub_set)
        #print(x)
        for x in sub_set:
            ##print(x)
            temp_SNR = sub_set[x][0]
            temp_alpha = sub_set[x][1]
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
    #print('test')
    #print(ordered_data)
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
    #print("test")
    print(test_lengths)
    #print([x for x in ordered_data])
    #print(ordered_data)
    #print([x[0] for x in num_above_threshold])
    percentiles = [num_above_threshold[x][0]/test_lengths[x] for x in range(len(test_lengths))]
    alphas_p = [x[1] for x in num_above_threshold]
    temp_indices = np.argsort(alphas_p)
    sorted_percentiles = [percentiles[x] for x in temp_indices]
    sorted_alphas_p = [alphas_p[x] for x in temp_indices]
    sorted_num_data = [test_lengths[x] for x in temp_indices]

    #SNRs = [x[0] for y in temp_temp_data for x in y["SNR data"]]
    #alphas = [x[1] for y in temp_temp_data for x in y["SNR data"]]
    SNRs = [y[x][0] for y in temp_temp_data for x in y]
    alphas = [y[x][1] for y in temp_temp_data for x in y]
    ##print([len(y) for y in temp_temp_data])
    ##print(len(temp_temp_data))

    if onsourceJob:
        onsourceRequiredString = "bknd_" + onsourceJob + ".mat"
        onsourceSNRs = [y[x][0] for y in temp_temp_data for x in y if onsourceRequiredString in x]
        onsourceAlphas = [y[x][1] for y in temp_temp_data for x in y if onsourceRequiredString in x]
        if check_mat_files_onsource:
            print([x for y in temp_temp_data for x in y if onsourceRequiredString in x])
            print(onsourceRequiredString)
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
    if 1-error_quantile/2 == 0.975:
        z_stat = 1.96
    else:
        print("error")
    #z_stat = 1-error_quantile/2
    delta = z_stat * np.sqrt(proportion*(1-proportion)/number_samples)
    return delta

def Wilson_score_interval(proportion, confidence_level, number_samples):
    error_quantile = 1-confidence_level
    if 1-error_quantile/2 == 0.975:
        z_stat = 1.96
    else:
        print("error")
    #z_stat = 1-error_quantile/2
    delta = z_stat * np.sqrt(proportion*(1-proportion)/number_samples + z_stat**2/(4*number_samples**2))
    upper_limit = (proportion + z_stat**2/(2*number_samples) + delta)/(1+z_stat**2/number_samples)
    lower_limit = (proportion + z_stat**2/(2*number_samples) - delta)/(1+z_stat**2/number_samples)
    return delta, upper_limit, lower_limit

def Wilson_score_interval_correction(proportion, confidence_level, number_samples):
    error_quantile = 1-confidence_level
    if 1-error_quantile/2 == 0.975:
        z_stat = 1.96
    else:
        print("error")
    #z_stat = 1-error_quantile/2
    delta = z_stat * np.sqrt(proportion*(1-proportion)/number_samples + z_stat**2/(4*number_samples**2))
    lower_limit = max([0, (2*number_samples*proportion + z_stat**2 - (z_stat*np.sqrt(z_stat**2 - 1/number_samples +4*number_samples*proportion*(1 - proportion) + (4*proportion - 2)) + 1))/(2*(number_samples+z_stat**2))])
    upper_limit = min([1, (2*number_samples*proportion + z_stat**2 + (z_stat*np.sqrt(z_stat**2 - 1/number_samples +4*number_samples*proportion*(1 - proportion) - (4*proportion - 2)) + 1))/(2*(number_samples+z_stat**2))])
    return delta, upper_limit, lower_limit

def frequentist_error_bars(proportion, number_samples):
    delta = np.sqrt(proportion*(1-proportion)/number_samples)
    return delta

def bayesian_error_bars(proportion, number_samples):
    number_found = number_samples*proportion
    expectation_proportion = (number_found + 1)/(number_samples + 2)
    variance = expectation_proportion*(1 - expectation_proportion)/(number_samples + 3)
    sigma = np.sqrt(variance)
    upper_limit = expectation_proportion + sigma
    lower_limit = expectation_proportion - sigma
    return sigma, upper_limit, lower_limit, expectation_proportion

def interpolate_threshold(proportions, alpha_values, threshold_proportion):
    if threshold_proportion in proportions:
        threshold_alpha = alpha_values[proportions.index(threshold_proportion)]
        interpolated = "Actual threshold"
    elif min(proportions) <= threshold_proportion <= max(proportions):
        proportion_above = min([x for x in proportions if x > threshold_proportion])
        proportion_below = max([x for x in proportions if x < threshold_proportion])
        alpha_above = alpha_values[proportions.index(proportion_above)]
        alpha_below = alpha_values[proportions.index(proportion_below)]
        log_h_above = np.log10(np.sqrt(alpha_above))
        log_h_below = np.log10(np.sqrt(alpha_below))
        #target_log_h = log_h_below + (log_h_above - log_h_below)/2
        # linear in log(x) space
        difference = (threshold_proportion - proportion_below)*(log_h_above - log_h_below)/(proportion_above - proportion_below)
        target_log_h = log_h_below + difference#(log_h_above - log_h_below)*(threshold_proportion - proportion_below)*diff_scaling
        threshold_alpha = np.power(10, target_log_h)**2
        # simple linear
        #difference = (threshold_proportion - proportion_below)*(alpha_above - alpha_below)/(proportion_above - proportion_below)
        #threshold_alpha = alpha_below + difference
        interpolated = "Interpolated threshold"
    else:
        threshold_alpha = None
        interpolated = "No threshold"
    return threshold_proportion, threshold_alpha, interpolated

"""def custom_fill_between(x_vals, y_vals_1, y_vals_2):
    actual_x_vals = [np.sqrt(x) for x in x_vals]
    plt.fill_between(actual_x_vals, y_vals_1, y_vals_2, zorder = 7, alpha = 0.5, color = colours[num], linewidth = 0.0)
    plt.plot(actual_x_vals, y_vals_1, zorder = 7, alpha = 0.5, color = colours[num])
    plt.plot(actual_x_vals, y_vals_2, zorder = 7, alpha = 0.5, color = colours[num])#"""

print(labels)
data_info = [get_info(orderedData[labels[num]], thresholdSNRs[num], temp_data_sets[num]) for num in range(len(labels))]

#outputPath = glueFileLocation(options.baseDir, "job_pairs_with_low_SNR_" + options.tag + ".txt")
#if not os.path.isfile(outputPath):
#    with open(outputPath, 'w') as outfile:
#        json.dump(temp_data, outfile, sort_keys = True, indent = 4)
if not polarized_version:
    if additional_plots:
        for num in range(len(labels)):
            required_margins = 1.25
            page_width = 8.5
            plot_width = page_width - 2*required_margins
            fig = plt.figure(figsize=(plot_width, plot_width*3/4))
            ax = fig.add_subplot(111)
            ax.grid(b=True, which='minor',linestyle=':', alpha = 1-0.85)
            ax.grid(b=True, which='major',linestyle='-', alpha = 1-0.75)

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
                plt.plot([np.sqrt(x) for x in highAlphasOnsource], highSNRsOnsource,'mo')#, label = "SNR distribution")
                plt.plot([np.sqrt(x) for x in lowAlphasOnsource], lowSNRsOnsource,'go', alpha = 0.5)#, label = "SNR distribution")
            plt.axhline(y=thresholdSNRs[num], xmin=0, xmax=1, hold=None, linestyle='--', color='g')
            #plt.yscale('log')
            plt.xscale('log')
            #plt.xlabel("Square root of scale factor alpha")
            plt.xlabel(r"Injected Strain ($h_0$)")
            #plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
            #plt.ylabel('Strain [Counts / sqrt(Hz)]')
            plt.ylabel("SNR")
            #plt.title("Threshold alpha = " + str(threshold_alpha) + ", threshold percentile = " + str(threshold_percent))#str(min(highAlphas)))
            #####plt.title("\n".join("Threshold alpha = " + str(threshold_alphas[x]) + ", threshold percentile = " + str(threshold_percentages[x]) for x in range(len(threshold_percentages))))#str(min(highAlphas)))
            #legend = plt.legend(prop={'size':6})#, framealpha=0.5)
            #legend.get_frame().set_alpha(0.5)
            #plt.show()
            if pretty_version:
                plt.rc('text', usetex = True)
                plt.rc('font', family = 'sarif')
                plt.rc('font', serif = 'Computer Modern')
            plt.savefig(glueFileLocation(outputPath, "upper_limit_estimate_" + name_tag + "_" + labels[num]), bbox_inches = 'tight')
            plt.savefig(glueFileLocation(outputPath, "upper_limit_estimate_" + name_tag + "_" + labels[num])+ '.pdf', bbox_inches = 'tight', format='pdf')
            plt.clf()

    """temp_indices = np.argsort(alphas_p)
sorted_percentiles = [percentiles[x] for x in temp_indices]
sorted_alphas_p = [alphas_p[x] for x in temp_indices]"""

    required_margins = 1.25
    page_width = 8.5
    plot_width = page_width - 2*required_margins
    fig = plt.figure(figsize=(plot_width, plot_width*3/4))
    ax = fig.add_subplot(111)
    ax.grid(b=True, which='minor',linestyle=':', alpha = 1-0.85)
    ax.grid(b=True, which='major',linestyle='-', alpha = 1-0.75)
    #####plt.figure()
    #####ax = plt.subplot(111)
    #ax.spines["top"].set_visible(False)
    #ax.spines["right"].set_visible(False)
    ###ax.spines["top"].set_zorder(10)
    ###ax.spines["bottom"].set_zorder(10)
    ###ax.spines["left"].set_zorder(10)
    ####ax.spines["right"].set_zorder(10)
    #ax.get_xaxis().tick_bottom()
    #ax.get_yaxis().tick_left()
    ####plt.grid(b=True, which='minor',linestyle='--', linewidth = 0.25)
    ####plt.grid(b=True, which='major',linestyle='-', linewidth = 0.25)
    #ax.grid(b=True, which='minor',linestyle='--', linewidth = 0.125)
    #ax.grid(b=True, which='major',linestyle='-', linewidth = 0.125)
    ###ax.grid(b=True, which='minor',color='0.85',linestyle='--', zorder = 0)
    ###ax.grid(b=True, which='major',color='0.75',linestyle='-', zorder = 0)
    #####ax.xaxis.grid(b=True, which='minor',linestyle='--', linewidth = 0.125)
    #####ax.xaxis.grid(b=True, which='major',linestyle='-', linewidth = 0.125)
    #print(data_info[0][0][0])
    threshold_list = []
    for num in range(len(labels)):
        sorted_percentiles = data_info[num][0][0]
        sorted_alphas_p = data_info[num][0][1]
        num_data = data_info[num][0][3]

        if 0 in sorted_percentiles:
            sorted_percentiles_min_index = [index for index, val in enumerate(sorted_percentiles) if val == 0][-1]
        else:
            sorted_percentiles_min_index = 0
        if 1 in sorted_percentiles:
            sorted_percentiles_max_index = [index for index, val in enumerate(sorted_percentiles) if val == 1][0]
        else:
            sorted_percentiles_max_index = len(sorted_percentiles) - 1
        sorted_percentiles = sorted_percentiles[sorted_percentiles_min_index:sorted_percentiles_max_index + 1]
        sorted_alphas_p = sorted_alphas_p[sorted_percentiles_min_index:sorted_percentiles_max_index + 1]
        num_data = num_data[sorted_percentiles_min_index:sorted_percentiles_max_index + 1]

        deltas = [normal_binomial_approximation_interval(x, error_confidence_level, num_data[index]) for index, x in enumerate(sorted_percentiles)]
        #wilson_intervals = [Wilson_score_interval_correction(x, error_confidence_level, num_data[index]) for index, x in enumerate(sorted_percentiles)]
        bayesion_intervals = [bayesian_error_bars(x, num_data[index]) for index, x in enumerate(sorted_percentiles)]
        print(bayesion_intervals)#print(wilson_intervals)
    #wilson_intervals = [Wilson_score_interval_correction(x, error_confidence_level, 100) for index, x in enumerate(sorted_percentiles)]
        upper_limits = [sorted_percentiles[x]+deltas[x] for x in range(len(sorted_percentiles))]
        lower_limits = [sorted_percentiles[x]-deltas[x] for x in range(len(sorted_percentiles))]
        upper_limits_2 = [x[2] for x in bayesion_intervals]#[x[2] for x in wilson_intervals]
        lower_limits_2 = [x[1] for x in bayesion_intervals]#[x[1] for x in wilson_intervals]
        bayesian_averages = [x[3] for x in bayesion_intervals]
        upper_deltas = [upper_limits_2[x] - sorted_percentiles[x] for x in range(len(sorted_percentiles))]
        lower_deltas = [sorted_percentiles[x] - lower_limits_2[x] for x in range(len(sorted_percentiles))]
        #threshold_alpha = data_info[num][0][2]
        threshold_alphas = data_info[num][0][2]
        print(labels[num])
        #print(sorted_percentiles)
        print(threshold_alphas)
        #print(sorted_alphas_p)
        threshold_pairs = []
        print("test interpolating")
        interp_thresholds = (interpolate_threshold(sorted_percentiles, sorted_alphas_p, 0.5), interpolate_threshold(sorted_percentiles, sorted_alphas_p, 0.9))
        threshold_list += [[labels[num], interp_thresholds]]
        print(interp_thresholds[0])
        print(interp_thresholds[1])
        #print(interpolate_threshold(sorted_percentiles, sorted_alphas_p, 0.5))
        #print(interpolate_threshold(sorted_percentiles, sorted_alphas_p, 0.9))
        print("tested interpolating")
        for index, val in enumerate(sorted_alphas_p):
            if val in threshold_alphas:
                print(val)
                print(sorted_percentiles[index])
                #print("test")
                threshold_pairs += [[val, sorted_percentiles[index]]]
        #plt.plot([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, 'x-', label = "Threshold alpha = " + str(threshold_alpha))
        if pretty_version:
            #plt.plot([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, markers[num]+'-', label = "Threshold alpha = " + ", ".join(str_truncate(temp_threshold)for temp_threshold in threshold_alphas) + " " + labels[num].replace("_"," "))
            ##plt.errorbar([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, fmt = markers[num]+'-', yerr = [lower_deltas, upper_deltas], label = "Threshold alpha = " + ", ".join(str_truncate(temp_threshold)for temp_threshold in threshold_alphas) + " " + labels[num].replace("_"," "))# + " " + labels[num])
            ###plt.errorbar([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, fmt = 'x-', yerr = [lower_deltas, upper_deltas], label = "Threshold alpha = " + ", ".join(str_truncate(temp_threshold)for temp_threshold in threshold_alphas) + " " + labels[num].replace("_"," "))# + " " + labels[num])
            ####plt.plot([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, fmt = 'x-', yerr = [lower_deltas, upper_deltas], label = labels[num])# + " " + labels[num])
        ##plt.plot([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, color = colours[num], zorder = 8, label = labels[num])# + " " + labels[num])
        ####plt.plot([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, color = colours[num], label = labels[num])# + " " + labels[num])
        ##plt.errorbar([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, fmt = 'x-', yerr = [lower_deltas, upper_deltas], label = "Threshold alpha = " + ", ".join(str_truncate(temp_threshold)for temp_threshold in threshold_alphas) + " " + labels[num].replace("_"," "))# + " " + labels[num])
            ##plt.errorbar([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, fmt = 'x-', yerr = [lower_deltas, upper_deltas], label = "Threshold alpha = " + ", ".join(str_truncate(temp_threshold[0]) + " (" + str(temp_threshold[1]) + ")" for temp_threshold in threshold_pairs) + " " + labels[num].replace("_"," "))# + " " + labels[num])
            if plot_mode == "plain":
                plt.plot([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, 'x-', label = "Threshold alpha = " + ", ".join(str(temp_threshold[0]) + " (" + str(temp_threshold[1]) + ")" for temp_threshold in threshold_pairs) + " " + labels[num].replace("_"," "))# + " " + labels[num])
            elif plot_mode == "errorbar":
                plt.errorbar([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, fmt = 'x-', yerr = [lower_deltas, upper_deltas], label = "Threshold alpha = " + ", ".join(str(temp_threshold[0]) + " (" + str(temp_threshold[1]) + ")" for temp_threshold in threshold_pairs) + " " + labels[num].replace("_"," "))# + " " + labels[num])
            elif plot_mode == "shaded":
                plt.plot([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, color = colours[num], label = labels[num])# + " " + labels[num])
                #plt.plot([np.sqrt(x) for x in sorted_alphas_p], bayesian_averages, '--', color = colours[num])#, label = labels[num])
                plt.fill_between([np.sqrt(x) for x in sorted_alphas_p], lower_limits_2, upper_limits_2, alpha = 0.5, color = colours[num], linewidth = 0.0)# Make this a custom function with the proper edge made with an actual plot line instead of the fill_between edge in ordre to get the proper alpha. #, edgecolor = (0,0,0,0))
            else:
                print("Warning: plot type uncertain")
            if plot_interpolated_points:
                for x in interp_thresholds:
                    print(x[1])
                    plt.plot(np.sqrt(x[1]), x[0], "xk")
            #plt.fill_between([np.sqrt(x) for x in sorted_alphas_p], lower_limits_2, upper_limits_2, zorder = 1, alpha = 0.5, color = "yellow")
            ##plt.fill_between([np.sqrt(x) for x in sorted_alphas_p], lower_limits_2, upper_limits_2, zorder = 7, alpha = 0.5, color = colours[num], linewidth = 0.0)# Make this a custom function with the proper edge made with an actual plot line instead of the fill_between edge in ordre to get the proper alpha. #, edgecolor = (0,0,0,0))
        ##plt.fill_between([np.sqrt(x) for x in sorted_alphas_p], lower_limits_2, upper_limits_2, zorder = 7, alpha = 0.5, color = colours[num], linewidth = 0.0)# Make this a custom function with the proper edge made with an actual plot line instead of the fill_between edge in ordre to get the proper alpha. #, edgecolor = (0,0,0,0))
        ####plt.fill_between([np.sqrt(x) for x in sorted_alphas_p], lower_limits_2, upper_limits_2, alpha = 0.5, color = colours[num], linewidth = 0.0)# Make this a custom function with the proper edge made with an actual plot line instead of the fill_between edge in ordre to get the proper alpha. #, edgecolor = (0,0,0,0))
            #custom_fill_between(sorted_alphas_p, lower_limits_2, upper_limits_2)
        else:
            ##print(upper_limits)
            #plt.errorbar([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, fmt = 'x-', yerr = deltas, label = "Threshold alpha = " + ", ".join(str(temp_threshold)for temp_threshold in threshold_alphas))# + " " + labels[num])
            plt.errorbar([np.sqrt(x) for x in sorted_alphas_p], sorted_percentiles, fmt = 'x-', ecolor = (0,1,0,0.5), yerr = [lower_deltas, upper_deltas], label = "Threshold alpha = " + ", ".join(str(temp_threshold)for temp_threshold in threshold_alphas))# + " " + labels[num])
            #plt.fill_between([np.sqrt(x) for x in sorted_alphas_p], lower_limits, upper_limits, zorder = 12, alpha = 0.5, facecolor = "green")
            ###plt.fill_between([np.sqrt(x) for x in sorted_alphas_p], lower_limits_2, upper_limits_2, zorder = 12, alpha = 0.5, facecolor = "yellow")
        #if threshold_alpha:
        #    plt.axvline(x=np.sqrt(threshold_alpha), ymin=0, ymax=1, hold=None, linestyle='--', color='0.75', alpha = 0.7)
        if threshold_alphas and not pretty_version:
            for temp_threshold in threshold_alphas:
                if temp_threshold:
                    plt.axvline(x=np.sqrt(temp_threshold), ymin=0, ymax=1, hold=None, linestyle='--', color='k', alpha = 0.7, zorder = 9)
    for temp_percentage in threshold_percentages:
        #plt.axhline(y=temp_percentage, xmin=0, xmax=1, hold=None, linestyle='--', color='k', alpha = 0.7)
        plt.axhline(y=temp_percentage, xmin=0, xmax=1, hold=None, linestyle='--', color='k', zorder = 10)#, alpha = 0.5)
    #plt.yscale('log')
    #plt.xscale('log')
    if pretty_version:
        plt.rc('text', usetex = True)
        plt.rc('font', family = 'sarif')
        plt.rc('font', serif = 'Computer Modern')
    ax.set_xscale('log')
    ax.set_xlabel(r"Injected Strain ($h_0$)")#"Square root of scale factor alpha")
    if xLimits:
        ax.set_xlim(xLimits)
    #plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
    #plt.ylabel('Strain [Counts / sqrt(Hz)]')
    plt.ylabel("Efficiency")
    #ax.set_ylabel("Efficiency")
    #plt.title("Threshold alpha = " + str(threshold_alpha) + ", threshold percentile = " + str(threshold_percent))#str(min(highAlphas)))
    #plt.title("Threshold percentile = " + str(threshold_percent))#str(min(highAlphas)))
    ##plt.title("Threshold = " + ", ".join(str(temp_threshold) for temp_threshold in threshold_percentages))#str(min(highAlphas)))
    #plt.title(r"Sine-Gaussian recovery efficiency for circular polarization ($\iota = 0$)")
    ##legend = plt.legend(prop={'size':6},loc='best')#, framealpha=0.5)
    if not plot_mode == "plain" or show_legend:
        legend = plt.legend(prop={'size':8}, loc='best')#, framealpha=0.5)
    #ax.set_xticks([9e-23, 1e-22, 2e-22, 3e-22, 4e-22, 5e-22, 6e-22], ['a', 'b', 'c', 'd', 'e', 'f', 'g'])
    #plt.xticks([9e-23, 1e-22, 2e-22, 3e-22, 4e-22, 5e-22, 6e-22], [r'$9\!\times\!10^{23}$', r'$10^{22}$', r'$2\times10^{22}$', r'$3\times10^{22}$', r'$4\times10^{22}$', r'$5\times10^{22}$', r'$6\times10^{22}$'])
    #plt.xticks([9e-23, 1e-22, 2e-22, 3e-22, 4e-22, 5e-22, 6e-22], ['9e-23', '1e-22', '2e-22', '3e-22', '4e-22', '5e-22', '6e-22'])
    #plt.xticks([1e-22, 2e-22, 3e-22, 4e-22, 5e-22, 6e-22], [r'$10^{22}$', r'$2\times10^{22}$', r'$3\times10^{22}$', r'$4\times10^{22}$', r'$5\times10^{22}$', r'$6\times10^{22}$'])
    #######plt.xticks([9e-23, 1e-22, 2e-22, 3e-22, 4e-22, 5e-22, 6e-22], [r'$9\!\times\!10^{-23}$',r'$10^{-22}$', r'$2\!\times\!10^{-22}$', r'$3\!\times\!10^{-22}$', r'$4\!\times\!10^{-22}$', r'$5\!\times\!10^{-22}$', r'$6\!\times\!10^{-22}$'])
    ####ax.xaxis.set_minor_formatter(FormatStrFormatter("%.2f"))
    if plot_mode == "plain" and show_legend:
        legend.get_frame().set_alpha(0.5)
    if lockPlot:
        plt.ylim([0,1])
        #ax.set_ylim([0,1])
    #plt.show()
    print(glueFileLocation(outputPath, "detection_efficiency_estimate_" + name_tag))

    #    plt.ylabel("False Alarm Probability")
    #    plt.savefig(dir_name + "/SNRvsFAP_all_clusters_semilogy_average_2.pdf", bbox_inches = 'tight', format='pdf')
    #else:
    plt.savefig(glueFileLocation(outputPath, "detection_efficiency_estimate_" + name_tag), bbox_inches = 'tight')
    plt.savefig(glueFileLocation(outputPath, "detection_efficiency_estimate_" + name_tag) + '.pdf', bbox_inches = 'tight', format='pdf')
    plt.clf()

    with open(glueFileLocation(outputPath, "threshold_values.txt"), "w") as outfile:
        output_string = "\n".join("\n".join([x[0], "\n".join(" ".join(str(z) for z in y) for y in x[1])]) for x in threshold_list)
        outfile.write(output_string)

elif polarized_version:
    iotas = []
    SNRs = []
    SNRs_1 = []
    SNRs_2 = []
    min_iotas = []
    min_SNRs = []
    cos_iotas = []
    cos_iotas_1 = []
    cos_iotas_2 = []
    ##print(len(temp_data_sets))
    for set_num in range(len(temp_data_sets)):
    #for x in temp_data:
        temp_orderedData = {}
        #print(len(temp_data_sets[0][0]))
        #print(temp_data_sets[0][0].keys())
#        for x in temp_data_sets[set_num]["SNR data"]:
        temp_SNRs = []
        temp_SNRs_1 = []
        temp_SNRs_2 = []
        temp_iotas = []
        temp_iotas_1 = []
        temp_iotas_2 = []
        temp_min_SNRs = []
        temp_min_iotas = []
        #print(len(temp_data_sets))
        #print(len(temp_data_sets[set_num]))
        ##print(len(temp_data_sets[set_num]))
        ##print(type(temp_data_sets[set_num]))
        ##print(type(temp_data_sets[set_num][0]))
        ##print(len(temp_data_sets[set_num][0]))
        for x in temp_data_sets[set_num]:
            #print('test')
            #temp_SNR = x[0]
            #temp_alpha = x[1]
            #temp_iota = x[2]
            #iotas+=[temp_iota]
            #SNRs+=[temp_SNR]
            temp_temp_SNRs = [x[y][0] for y in x]
            temp_temp_iotas = [x[y][2] for y in x]
            temp_SNRs += temp_temp_SNRs
            temp_iotas += temp_temp_iotas

            temp_temp_SNRs_1 = [x[y][0] for y in x if 'job_1' in y]
            temp_temp_iotas_1 = [x[y][2] for y in x if 'job_1' in y]
            temp_temp_SNRs_2 = [x[y][0] for y in x if 'job_2' in y]
            temp_temp_iotas_2 = [x[y][2] for y in x if 'job_2' in y]

            temp_SNRs_1 += temp_temp_SNRs_1
            temp_iotas_1 += temp_temp_iotas_1
            temp_SNRs_2 += temp_temp_SNRs_2
            temp_iotas_2 += temp_temp_iotas_2

            print("Minimum finding option currently only works for 2 individual job-pairs currently.")
            temp_min_SNR_1 = min(temp_temp_SNRs_1)
            temp_min_SNR_2 = min(temp_temp_SNRs_2)
            print("Maximum finding option currently only works for 2 individual job-pairs currently.")
            print(max(temp_temp_SNRs_1))
            print(max(temp_temp_SNRs_2))
            if trigger_number == 2475:
                target_SNR_value = 27.910364328766665
                find_surrounding_values(target_SNR_value, temp_temp_iotas_1, temp_temp_SNRs_1)
                find_surrounding_values(target_SNR_value, temp_temp_iotas_2, temp_temp_SNRs_2)
            #print(temp_min_SNR)
            for temp_num in range(len(temp_temp_iotas_1)):
                if temp_temp_SNRs_1[temp_num] == temp_min_SNR_1:
                    temp_min_iotas += [temp_temp_iotas_1[temp_num]]
                    temp_min_SNRs += [temp_temp_SNRs_1[temp_num]]
            for temp_num in range(len(temp_temp_iotas_2)):
                if temp_temp_SNRs_2[temp_num] == temp_min_SNR_2:
                    temp_min_iotas += [temp_temp_iotas_2[temp_num]]
                    temp_min_SNRs += [temp_temp_SNRs_2[temp_num]]
        temp_cos_iotas = [np.cos(np.deg2rad(x)) for x in temp_iotas]
        temp_cos_iotas_1 = [np.cos(np.deg2rad(x)) for x in temp_iotas_1]
        temp_cos_iotas_2 = [np.cos(np.deg2rad(x)) for x in temp_iotas_2]
        iotas+= [temp_iotas]
        SNRs+= [temp_SNRs]
        SNRs_1+= [temp_SNRs_1]
        SNRs_2+= [temp_SNRs_2]
        cos_iotas += [temp_cos_iotas]
        cos_iotas_1 += [temp_cos_iotas_1]
        cos_iotas_2 += [temp_cos_iotas_2]

        min_iotas+= [temp_min_iotas]
        min_SNRs+= [temp_min_SNRs]
    #cos_iotas = [np.cos(np.deg2rad(x)) for x in iotas]
    #sorted_indices = np.argsort(cos_iotas)
    #cos_iotas = [cos_iotas[x] for x in sorted_indices]
    #SNRs = [SNRs[x] for x in sorted_indices]
    #plt.grid(b=True, which='minor',color='0.85',linestyle='--')
    #plt.grid(b=True, which='major',color='0.75',linestyle='-')

    print(min_iotas)
    print(min_SNRs)
    required_margins = 1.25
    page_width = 8.5
    plot_width = page_width - 2*required_margins
    fig = plt.figure(figsize=(plot_width, plot_width*3/4))
    ax = fig.add_subplot(111)
    ax.grid(b=True, which='minor',linestyle=':', alpha = 1-0.85)
    ax.grid(b=True, which='major',linestyle='-', alpha = 1-0.75)
#    plt.grid(b=True, which='minor',linestyle='--', linewidth = 0.125)
#    plt.grid(b=True, which='major',linestyle='-', linewidth = 0.125)
    for x in range(len(SNRs)):
        if polarized_separate:
            plt.plot(cos_iotas_1[x], SNRs_1[x], 'x', label = labels[x])
            plt.plot(cos_iotas_2[x], SNRs_2[x], 'x', label = labels[x])
        elif abs_version:
            plt.plot(cos_iotas[x], [abs(y) for y in SNRs[x]], 'x', label = labels[x], markersize=4)#, color = colours[x])
        else:
            plt.plot(cos_iotas[x], SNRs[x], 'x', label = labels[x], markersize=4)#, color = colours[x])
    if polarized_test:
        plt.plot([np.cos(np.radians(69.049882206987093)), np.cos(np.radians(69.852525329854856))], [27.910364328766665, 27.910364328766665], 'x')
        plt.plot([np.cos(np.radians(68.556710444058893)), np.cos(np.radians(69.690743750961829))], [27.910364328766665, 27.910364328766665], 'x')
    #plt.plot(cos_iotas, SNRs, 'x')
    #plt.yscale('log')
    #plt.xscale('log')
    plt.xlabel(r"$\cos{\iota}$")
    #plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
    #plt.ylabel('Strain [Counts / sqrt(Hz)]')
    plt.ylabel("SNR")
    #plt.title("Threshold alpha = " + str(threshold_alpha) + ", threshold percentile = " + str(threshold_percent))#str(min(highAlphas)))
    #legend = plt.legend(prop={'size':6}, loc='best')#, framealpha=0.5)
    ####legend = plt.legend(loc='best')#, framealpha=0.5)
    #legend.get_frame().set_alpha(0.5)
    #plt.show()

    if pretty_version:
        plt.rc('text', usetex = True)
        plt.rc('font', family = 'sarif')
        plt.rc('font', serif = 'Computer Modern')
    plt.savefig(glueFileLocation(outputPath, "SNR_vs_cos_iota_" + name_tag), bbox_inches = 'tight')
    plt.savefig(glueFileLocation(outputPath, "SNR_vs_cos_iota_" + name_tag + '.pdf'), bbox_inches = 'tight', format='pdf')
    plt.clf()
