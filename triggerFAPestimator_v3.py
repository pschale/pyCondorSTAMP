from __future__ import division
from optparse import OptionParser
import json
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['legend.numpoints'] = 1

# command line options
parser = OptionParser()
parser.set_defaults(verbose = True)
parser.add_option("-d", "--dataFile", dest = "dataFile",
                  help = "Path to JSON containing backgrounds SNRs and FAPs",
                  metavar = "DIRECTORY")
parser.add_option("-s", "--snr", dest = "snr",
                  help = "SNR of trigger to calculate FAP for using background data",
                  metavar = "NUMBER")
parser.add_option("-r", "--realsnr", dest = "realDataSNR",
                  help = "SNR of trigger to calculate FAP for using background data",
                  metavar = "NUMBER")
parser.add_option("-o", "--output", dest = "outputDir",
                  help = "Directory for output plot summarizing results (will create in current directory unless full path specified. will overwrite any existing files)",
                  metavar = "DIRECTORY")
#parser.add_option("-v", action="store_true", dest="verbose")

(options, args) = parser.parse_args()

with open(options.dataFile, "r") as jsonFile:
    data = json.load(jsonFile)

rankedSNRs = data["rankedSNRs"]
ranks = [x*100 for x in data["ranks"]]

print("I am getting the FAP of the loudest background cluster that the trigger is louder than. So I'm returning the SNR of the background event that is just under the SNR of the trigger. This should give a slightly conservative measure for the FAP (a larger FAP).")

def findSNRIndex(SNR_list, snr):
    vals = [index for index, x in enumerate(SNR_list) if float(snr) > x]
    if rankedSNRs[vals[0]] > rankedSNRs[vals[-1]]:
        snrIndex = vals[0]
    else:
        snrIndex = vals[-1]
    return snrIndex

snrs = options.snr.split(",")
realSNRs = options.realDataSNR.split(",")

targetIndices = [findSNRIndex(rankedSNRs, x) for x in snrs]
targetFAPs = [ranks[x] for x in targetIndices]
backgroundSNRs = [rankedSNRs[x] for x in targetIndices]

realTargetIndices = [findSNRIndex(rankedSNRs, x) for x in realSNRs]
realTargetFAPs = [ranks[x] for x in realTargetIndices]
realBackgroundSNRs = [rankedSNRs[x] for x in realTargetIndices]

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.plot(rankedSNRs, ranks,'b-')#, label = "SNR distribution")
for x in range(len(snrs)):
    plt.plot(snrs[x], targetFAPs[x], 'o', label = "Estimated minimum FAP = " + str(targetFAPs[x]) + "%\nTrigger SNR = " + str(snrs[x]) + "\n(Background SNR = " + str(backgroundSNRs[x]) + ")")
for x in range(len(realSNRs)):
    plt.plot(realSNRs[x], realTargetFAPs[x], '^', label = "Estimated minimum FAP = " + str(realTargetFAPs[x]) + "%\nReal Data Trigger SNR = " + str(realSNRs[x]) + "\n(Background SNR = " + str(realBackgroundSNRs[x]) + ")")
#plt.yscale('log')
#plt.xscale('log')
plt.xlabel("SNR")
#plt.ylabel(r'$Strain \left(\frac{Counts}{\sqrt{Hz}}\right)$')
#plt.ylabel('Strain [Counts / sqrt(Hz)]')
plt.ylabel("False Alarm Probability [%]")
plt.ylim([0,100])
#plt.title("")
legend = plt.legend(prop={'size':6})#, framealpha=0.5)
legend.get_frame().set_alpha(0.5)
#plt.show()
plt.savefig(options.outputDir + "/SNRvsFAPforTriggersRealData", bbox_inches = 'tight')
plt.clf()