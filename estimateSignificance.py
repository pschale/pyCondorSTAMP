from __future__ import division
from optparse import OptionParser
import math
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['legend.numpoints'] = 1

# command line options
parser = OptionParser()

parser.add_option("-d", "--dir", dest = "targetDirectory",
                  help = "Path to directory with data to approximate",
                  metavar = "DIRECTORY")
parser.add_option("-s", "--snr", dest = "snr",
                  help = "SNR to determine significance of",
                  metavar = "FLOAT")

(options, args) = parser.parse_args()

with open(options.targetDirectory + "/basic_snr_info/AllSnrs.txt", "r") as infile:
    snrDistribution = [float(x.strip()) for x in infile if x.strip()]

snrDistribution.sort()

mean = sum(snrDistribution)/len(snrDistribution)
variance = sum([(x-mean)**2 for x in snrDistribution])/len(snrDistribution)
print(mean)
print(variance)

gDistribution = [math.e**(-(x-mean)**2/(2*variance)) for x in snrDistribution]

plt.grid(b=True, which='minor',color='0.85',linestyle='--')
plt.grid(b=True, which='major',color='0.75',linestyle='-')
plt.hist(snrDistribution, normed = 1)
plt.plot(snrDistribution, gDistribution,'r-')#, label = "SNR distribution")
#plt.xlabel("SNR")
#plt.ylabel("False Alarm Probability")
#ymin = min(all_percentage)
#plt.ylim([ymin,1])
#plt.yscale('log')
plt.savefig(options.targetDirectory + "/basic_snr_info/test_distribution", bbox_inches = 'tight')
plt.clf()