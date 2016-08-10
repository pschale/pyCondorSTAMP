from __future__ import division
from scanSNRlibV2 import *
import os
import pickle
from numpy import argsort, sqrt#, linspace
#from scipy.interpolate import spline
#import webpageGenerateLib as webGen
#from plotClustersLib import returnMatrixFilePath, plotClusterInfo_v2, getPixelInfo, getFrequencyInfo
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['legend.numpoints'] = 1

pdf_latex_mode = True #False#True
verbose = True
includePseudoEvents = False
dots = False
maxLim = None
minLim = None
reload_data = False
eventSNR = False

triggerNumber = 2475

#libertine = True


def color_conversion(R, G, B):
    return (R/256, G/256, B/256)


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


print("NOTE: script ignores all files and directories starting with '.'")

print("WARNING: Script is currently not set up to handle directories with multiple files with the name base.")

def verbosePrint(string, switch = verbose):
    if switch:
        print(string)

data_base_path = "/Users/Quitzow/Documents/Git_Branches/Thesis/Figures/Chapter_5/Open_Box_Results/2475"
closed_box_data_path = glueFileLocation(data_base_path, "runDataActual_2475.txt")
output_path = "/Users/Quitzow/Documents/Git_Branches/Thesis/Figures/Chapter_5/Open_Box_Results/2475/"
simulation_files = ["runDataSimulated_0_2475.txt",
                    "runDataSimulated_1_2475.txt",
                    "runDataSimulated_2_2475.txt",
                    "runDataSimulated_3_2475.txt",
                    "runDataSimulated_4_2475.txt",
                    "runDataSimulated_5_2475.txt",
                    "runDataSimulated_6_2475.txt",
                    "runDataSimulated_7_2475.txt",
                    "runDataSimulated_8_2475.txt",
                    "runDataSimulated_9_2475.txt"]

simulation_paths = [glueFileLocation(data_base_path, x) for x in simulation_files]

with open(closed_box_data_path, "r") as infile:
    SNRs = [float(x.split(", ")[0]) for x in infile]
SNRs.sort(reverse = True)

simulated_SNRs = []
for sim_file in simulation_paths:
    with open(sim_file, "r") as infile:
        temp_SNR = [float(x.split(", ")[0]) for x in infile]
    temp_SNR.sort(reverse = True)
    simulated_SNRs += [temp_SNR]

N = len(SNRs)
proportions = [x/N + 1/N for x in range(N)]


numSimulations = len(simulated_SNRs)
numJobs = len(simulated_SNRs[0])
meanSimulatedSNR = [sum([simulated_SNRs[simIndex][jobIndex] for simIndex in range(numSimulations)])/numSimulations for jobIndex in range(numJobs)]
stDevSimulatedSNR = [sqrt(sum([(simulated_SNRs[simIndex][jobIndex] - meanSimulatedSNR[jobIndex])**2 for simIndex in range(numSimulations)])/numSimulations) for jobIndex in range(numJobs)]
sigmaOneSimSNRLow = [meanSimulatedSNR[jobIndex] - stDevSimulatedSNR[jobIndex] for jobIndex in range(numJobs)]
sigmaOneSimSNRHigh = [meanSimulatedSNR[jobIndex] + stDevSimulatedSNR[jobIndex] for jobIndex in range(numJobs)]
sigmaTwoSimSNRLow = [meanSimulatedSNR[jobIndex] - stDevSimulatedSNR[jobIndex]*2 for jobIndex in range(numJobs)]
sigmaTwoSimSNRHigh = [meanSimulatedSNR[jobIndex] + stDevSimulatedSNR[jobIndex]*2 for jobIndex in range(numJobs)]
sigmaThreeSimSNRLow = [meanSimulatedSNR[jobIndex] - stDevSimulatedSNR[jobIndex]*3 for jobIndex in range(numJobs)]
sigmaThreeSimSNRHigh = [meanSimulatedSNR[jobIndex] + stDevSimulatedSNR[jobIndex]*3 for jobIndex in range(numJobs)]


required_margins = 1.25
page_width = 8.5
plot_width = page_width - 2*required_margins

"""plt.grid(b=True, which='minor',linestyle='--', linewidth = 0.125)
plt.grid(b=True, which='major',linestyle='-', linewidth = 0.125)
if dots:
    plt.plot(sortedAllSNRs, all_percentage,'b.-', label = "Background SNR Distribution", linewidth = 2)
    plt.plot(meanSimulatedSNR, all_percentage,'k.--', label = "Mean of Simulations")
    plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'g.-', label = "Monte Carlo Simulations", alpha = 0.3)
    if len(sortedAllSimulatedSNRs) > 1:
        for num in range(1,len(sortedAllSimulatedSNRs)):
            plt.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'g.-', alpha = 0.3)
    plt.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g.--', label = "Monte Carlo Simulations")
    plt.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g.--')
else:
    plt.fill_betweenx(proportions, sigmaOneSimSNRLow, sigmaOneSimSNRHigh, color=str(1 - 0.5*0.7), linewidth = 0.0)#'grey', alpha='0.7', linewidth = 0.0)#, zorder = 3)
    plt.fill_betweenx(proportions, sigmaTwoSimSNRLow, sigmaOneSimSNRLow, color=str(1 - 0.5*0.5), linewidth = 0.0)#'grey', alpha='0.3')#'0.5', linewidth = 0.0)#, zorder = 3)
    plt.fill_betweenx(proportions, sigmaTwoSimSNRHigh, sigmaOneSimSNRHigh, color=str(1 - 0.5*0.5), linewidth = 0.0)#color='grey')#, alpha='0.5', linewidth = 0.0)#, zorder = 3)
    plt.fill_betweenx(proportions, sigmaTwoSimSNRLow, sigmaThreeSimSNRLow, color=str(1 - 0.5*0.3), linewidth = 0.0)#'grey', alpha='0.3', linewidth = 0.0)#, zorder = 3)
    plt.fill_betweenx(proportions, sigmaTwoSimSNRHigh, sigmaThreeSimSNRHigh, color=str(1 - 0.5*0.3), linewidth = 0.0)#, alpha='0.3')#, linewidth = None)#0.0)#, zorder = 3)

    #plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'r-', label = "Monte Carlo Simulations", alpha = 0.5)#, zorder = 4)
    #plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'y-', label = "Monte Carlo Simulations")#, alpha = 0.5)#, zorder = 4)
    #plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'y-', label = "Gaussian Simulations", color = colours[1])#, alpha = 0.5)#, zorder = 4)
    #x#simulationLine, = plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'-', label = "Gaussian Simulations", color = colours[1])#, alpha = 0.5)#, zorder = 4)

    ##simulationLine, = plt.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'-', label = "Gaussian Simulations", color = colours[4])#, alpha = 0.5)#, zorder = 4)
    ##if len(sortedAllSimulatedSNRs) > 1:
    ##    for num in range(1,len(sortedAllSimulatedSNRs)):
            #plt.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'r-', alpha = 0.5)#, zorder = 4)
            ##plt.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'-', color = colours[1])#, alpha = 0.5)#, zorder = 4)
    ##        plt.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'-', color = colours[4])#, alpha = 0.5)#, zorder = 4)
    #plt.plot(meanSimulatedSNR, all_percentage,'k--', label = "Mean of Simulations")#, zorder = 6)
    #plt.plot(meanSimulatedSNR, all_percentage,'k--', label = "Simulation Mean")#, zorder = 6)
    meanLine, = plt.plot(meanSimulatedSNR, proportions,'k--', label = "Simulation Mean")#, zorder = 6)
    #plt.plot(sortedAllSNRs, all_percentage,'b-', label = "Background SNR Distribution", linewidth = 1.5)#, zorder = 5)
    #plt.plot(sortedAllSNRs, all_percentage,'b-', label = "Background", linewidth = 1.5, color = colours[0])#, zorder = 5)
    ##backgroundLine, = plt.plot(sortedAllSNRs, all_percentage,'-', label = "Background", linewidth = 1.5, color = colours[0])#, zorder = 5)
    backgroundLine, = plt.plot(SNRs, proportions,'-', label = "Background", linewidth = 1.5, color = colours[0])#, zorder = 5)
##if pseudoEventSNRs:
    #plt.plot(pseudoEventSNRs, pseudoEventPercentages,'b^', label = "Zero-lag pseudo event\n(SNR = " + ", ".join(str(x) for x in pseudoEventSNRs) + " FAP = " + ", ".join(str(x) for x in pseudoEventPercentages) + ")")
##    plt.plot(pseudoEventSNRs, pseudoEventPercentages,'b^', label = "Dummy On-Source")
##if eventSNRs:
    #plt.plot(eventSNRs, eventPercentages,'r*', zorder = 6, markersize = 8, label = "On-source event\n(SNR = " + ", ".join(str(x) for x in eventSNRs) + " FAP = " + ", ".join(str(x) for x in eventPercentages) + ")")
    #plt.plot(eventSNRs, eventPercentages,'r*', zorder = 6, markersize = 8, label = "On-Source Event")
    #eventLine, = plt.plot(eventSNRs, eventPercentages,'ro', zorder = 6, markersize = 8, label = "On-Source Event", markeredgecolor = "r")#, color = colours[5])
##    eventLine, = plt.plot(eventSNRs, eventPercentages,'ro', zorder = 6, label = "On-Source Event", markeredgecolor = "r")#, color = colours[5])
    ##eventLine, = plt.plot(eventSNRs, eventPercentages,'co', zorder = 6, label = "On-Source Event", markeredgecolor = "c")#, color = colours[5])
plt.xlabel("SNR")
ymin = min(proportions)
plt.ylim([ymin,1])
plt.yscale('log')
#legend = plt.legend(prop={'size':12})
##legend = plt.legend([backgroundLine, simulationLine, meanLine, eventLine], ["Background", "Gaussian Simulations", "Simulation Mean", "On-Source Event"], prop={'size':12})
legend = plt.legend([backgroundLine], ["Background"], prop={'size':12})
#legend.get_frame().set_alpha(0.5)
if pdf_latex_mode:
    plt.rc('text', usetex = True)
    #plt.rc('text.latex', preamble = '\usepackage[T1]{fontenc}, \usepackage[notextcomp]{kpfonts}')
    #plt.rc('text.latex', preamble = '\usepackage[T1]{fontenc}, \usepackage{fbb}, \usepackage[libertine]{newtxmath}, \usepackage[italic]{mathastext}, \MTsetmathskips{f}{5mu}{1mu}')
    #plt.rc('text.latex', preamble = '\usepackage{kpfonts}')
    plt.rc('text.latex', preamble = '\usepackage[T1]{fontenc}')
    plt.rc('font', family = 'sarif')
    #plt.rc('font', serif = 'Palatino')
    plt.rc('font', serif = 'Libertine')
    plt.ylabel("False Alarm Probability")
    plt.savefig(glueFileLocation(output_path, "SNRvsFAP_all_clusters_semilogy_average_2.pdf"), bbox_inches = 'tight', format='pdf')
else:
    plt.ylabel("False Alarm Probability")
    plt.savefig(glueFileLocation(output_path, "SNRvsFAP_all_clusters_semilogy_average_2"), bbox_inches = 'tight')
plt.clf()#"""


#plt.grid(b=True, which='minor',color='0.85',linestyle='--')
#plt.grid(b=True, which='major',color='0.75',linestyle='-')
plot_size = 5
#fig = plt.figure(figsize=(8,6))
#fig = plt.figure(figsize=(plot_size*1.61803398875,plot_size))
#fig = plt.figure(figsize=(plot_width, plot_width/1.61803398875))
fig = plt.figure(figsize=(plot_width, plot_width*3/4))
ax1 = fig.add_subplot(111)
ax1.grid(b=True, which='minor',linestyle='--', alpha = 1-0.85)
ax1.grid(b=True, which='major',linestyle='-', alpha = 1-0.75)
if dots:
    ax1.plot(sortedAllSNRs, all_percentage,'b.-', label = "Background SNR Distribution", linewidth = 2)
    ax1.plot(meanSimulatedSNR, all_percentage,'k.--', label = "Mean of Simulations")
    ax1.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'g.-', label = "Monte Carlo Simulations", alpha = 0.3)
    if len(sortedAllSimulatedSNRs) > 1:
        for num in range(1,len(sortedAllSimulatedSNRs)):
            ax1.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'g.-', alpha = 0.3)
    ax1.plot(sortedAllSimulatedSNRs, allSimulated_percentage,'g.--', label = "Monte Carlo Simulations")
    ax1.plot(sortedAllSimulatedSNRs2, allSimulated_percentage2,'g.--')
else:
    ax1.fill_betweenx(proportions, sigmaOneSimSNRLow, sigmaOneSimSNRHigh, color='grey', alpha='0.7', linewidth = 0.0)#, zorder = 3)
    ax1.fill_betweenx(proportions, sigmaTwoSimSNRLow, sigmaOneSimSNRLow, color='grey', alpha='0.5', linewidth = 0.0)#, zorder = 3)
    ax1.fill_betweenx(proportions, sigmaTwoSimSNRHigh, sigmaOneSimSNRHigh, color='grey', alpha='0.5', linewidth = 0.0)#, zorder = 3)
    ax1.fill_betweenx(proportions, sigmaTwoSimSNRLow, sigmaThreeSimSNRLow, color='grey', alpha='0.3', linewidth = 0.0)#, zorder = 3)
    ax1.fill_betweenx(proportions, sigmaTwoSimSNRHigh, sigmaThreeSimSNRHigh, color='grey', alpha='0.3', linewidth = 0.0)#, zorder = 3)
    ##simulationLine, = ax1.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'-', label = "Gaussian Simulations", color = colours[1])#, alpha = 0.5)#, zorder = 4)
    ##simulationLine, = ax1.plot(sortedAllSimulatedSNRs[0], allSimulated_percentage[0],'-', label = "Gaussian Simulations", color = colours[4])#, alpha = 0.5)#, zorder = 4)
    simulationLine, = ax1.plot(simulated_SNRs[0], proportions,'-', label = "Gaussian Simulations", color = colours[4])#, alpha = 0.5)#, zorder = 4)
    if len(simulated_SNRs) > 1:
        for num in range(1,len(simulated_SNRs)):
            ##ax1.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'-', color = colours[1])#, alpha = 0.5)#, zorder = 4)
            ##ax1.plot(sortedAllSimulatedSNRs[num], allSimulated_percentage[num],'-', color = colours[4])#, alpha = 0.5)#, zorder = 4)
            ax1.plot(simulated_SNRs[num], proportions,'-', color = colours[4])#, alpha = 0.5)#, zorder = 4)
    meanLine, = ax1.plot(meanSimulatedSNR, proportions,'--', label = "Simulation Mean", color = 'blue')#)#, zorder = 6)
    #backgroundLine, = ax1.plot(sortedAllSNRs, proportions,'-', label = "Background", linewidth = 1.5, color = colours[0])#, zorder = 5)
    backgroundLine, = ax1.plot(SNRs, proportions,'-k', label = "Background", linewidth = 1)#, color = colours[1])#, zorder = 5)
#if pseudoEventSNRs:
#    ax1.plot(pseudoEventSNRs, pseudoEventPercentages,'b^', label = "Dummy On-Source")
##if eventSNRs:
##    eventLine, = ax1.plot(eventSNRs, eventPercentages,'o', zorder = 6, label = "On-Source Event", markeredgecolor = None, markersize = 5, color = colours[1])#, color = colours[5])
    ##eventLine, = ax1.plot(eventSNRs, eventPercentages,'co', zorder = 6, label = "On-Source Event", markeredgecolor = "c")#, color = colours[5])
#plt.xlabel("SNR")
ax1.set_xlabel("SNR")
ymin = min(proportions)
#plt.ylim([ymin,1])
ax1.set_ylim([ymin,1])
#plt.yscale('log')
ax1.set_yscale('log')
#legend = ax1.legend(prop={'size':12})
#legend = ax1.legend([backgroundLine, simulationLine, meanLine, eventLine], ["Background", "Gaussian Simulations", "Simulation Mean", "On-Source Event"], prop={'size':10})
legend = ax1.legend([backgroundLine, simulationLine, meanLine], ["Background", "Gaussian Simulations", "Simulation Mean"], prop={'size':10})
#legend.get_frame().set_alpha(0.5)
if pdf_latex_mode:
    plt.rc('text', usetex = True)
    plt.rc('text.latex', preamble = '\usepackage[T1]{fontenc}')
    #if libertine:
    #    plt.rc('text.latex', preamble = '\usepackage[T1]{fontenc}, \usepackage{fbb}, \usepackage[libertine]{newtxmath}, \usepackage[italic]{mathastext}, \MTsetmathskips{f}{5mu}{1mu}')
    #else:
    #    plt.rc('text.latex', preamble = '\usepackage[T1]{fontenc}, \usepackage[notextcomp]{kpfonts}')
    plt.rc('font', family = 'sarif')
    #plt.rc('font', weight = 'bold')
    #if libertine:
    #    plt.rc('font', serif = 'Libertine')
    #else:
    #    plt.rc('font', serif = 'Palatino')
    #plt.rc('font', serif = 'Palatino')
    plt.rc('font', serif = 'Libertine')
    #plt.rc('font', size = 11)#default 12
    #plt.ylabel("False Alarm Probability")
    ax1.set_ylabel("False Alarm Probability")
    plt.savefig(glueFileLocation(output_path, "SNRvsFAP_all_clusters_semilogy_average_2.pdf"), bbox_inches = 'tight', format='pdf')
else:
    plt.ylabel("False Alarm Probability")
    plt.savefig(glueFileLocation(output_path, "SNRvsFAP_all_clusters_semilogy_average_2"), bbox_inches = 'tight')
fig.clf()#"""
