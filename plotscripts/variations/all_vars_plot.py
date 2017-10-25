from __future__ import division
import scipy.io as sio
import matplotlib as mpl
mpl.use("Agg")
mpl.rc('text', usetex=True)
import matplotlib.pyplot as plt
import os
from optparse import OptionParser
import ConfigParser
import pandas as pd
from matplotlib.ticker import ScalarFormatter
from matplotlib.ticker import FormatStrFormatter
import numpy as np

parser = OptionParser()
parser.add_option("-d", "--directory", dest="directory")
parser.add_option("-t", "--title", dest="title", default=False)
parser.add_option("-s", "--snr-threshold", dest="snrthreshold", default=7.5, type=float,
                                            help="Only used if singletrack active")
(options, args) = parser.parse_args()

baseDir = options.directory

if baseDir[0] == ".":
    baseDir = os.getcwd() + baseDir[1:]
elif baseDir[0] == "~":
    baseDir = os.path.expanduser('~') + baseDir[1:]
elif not baseDir[0] == "/":
    baseDir = os.getcwd() + "/" + baseDir[0:]

configfile = [ele for ele in os.listdir(os.path.join(baseDir, 'input_files')) if ele[-4:] == '.ini'][0]
configs = ConfigParser.ConfigParser()
configs.read(os.path.join(baseDir, 'input_files', configfile))


if not configs.getboolean('variations', 'doVariations'):
    raise ValueError("Specified Directory does not have variations enabled")

if configs.has_option('injection', 'waveform_name') and configs.get('injection', 'waveform_name') == 'ringdown':
    inj_type = 'ringdown'
else:
    inj_type = 'hsg'

if not configs.get('variations', 'paramName') == 'stamp.alpha':
    raise ValueError('amplitude not varied')

if configs.has_option('singletrack', 'singletrackBool') and configs.getboolean('singletrack', 'singletrackBool'):
    search_type = 'Singletrack'
else:
    search_type = 'Stochtrack'


varyingParam = configs.get('variations', 'paramName')
varyingDist = configs.get('variations', 'distribution')

data = pd.read_csv(os.path.join(baseDir, 'STAMP_output_dataframe.csv'))

tau = 400 if configs.getboolean('injection', 'longTau') else 150

if inj_type == 'ringdown':
    f = lambda x: np.sqrt(x['alpha']*tau/2)*x['h0'] * (1 - np.exp(-6))
else:
    f = lambda x: np.sqrt(np.pi*x['alpha']*tau/(2*np.sqrt(2)) * (1 - 2e-8))
data['hrss'] = data.apply(f, 1)

desired_col = 'hrss'

rec_SNRs = list(data['SNR'][data['recov']].as_matrix())
rec_xvals = list(data[desired_col][data['recov']].as_matrix())
unrec_SNRs = list(data['SNR'][data['recov']==False].as_matrix())
unrec_xvals = list(data[desired_col][data['recov']==False].as_matrix())

axes = plt.subplot(111)
#fig1, axes = plt.subplots()


axes.scatter(rec_xvals, rec_SNRs, color='g', label="Recovered Injection")
axes.scatter(unrec_xvals, unrec_SNRs, color='r', label="Recovered Noise")
axes.set_xlabel('hrss')
axes.set_ylabel("SNR")
axes.set_xlim([min(rec_xvals + unrec_xvals)*0.9, max(rec_xvals + unrec_xvals)*1.1])
axes.semilogx([min(rec_xvals + unrec_xvals)*0.9, max(rec_xvals + unrec_xvals)*1.1], [7.5, 7.5], label="Loudest Background (est)")
axes.legend(loc='upper left')
axes.xaxis.set_minor_formatter(FormatStrFormatter("%.0e"))


title = " ".join([configs.get('trigger', 'triggerNumber'), 
                  configs.get('injection', 'waveFrequency') + 'Hz', 
                  "$\\tau=" + str(tau) + "$ sec", 
                  search_type, 
                  inj_type])
plt.title(title)
plt.savefig(os.path.join(baseDir, "scatterplot_hrss.png"))

if 'recov' not in data.columns:
    raise ValueError("Recovery boolean not found in data frame")

groupNums = list(set(data['Group'].as_matrix()))
groupNums.sort()


eff = []

for num in groupNums:
    if configs.getboolean('singletrack', 'singletrackBool'):
        group_rec = data['SNR'][data['Group']==num].as_matrix() >= options.snrthreshold
    else:
        group_rec = data['recov'][data['Group']==num].as_matrix()
    eff.append(np.count_nonzero(group_rec)/group_rec.size)
else:
    if configs.getboolean('singletrack', 'singletrackBool'):
        print("Singletrack was active, using threshold {}".format(options.snrthreshold))


xvals = [data[desired_col][data['Group']==ele].as_matrix()[0] for ele in groupNums]
#print(xvals, eff)

axes.clear()

axes = plt.subplot(111)

axes.semilogx(xvals, eff, 'bo-')

axes.set_xlabel('hrss')
axes.set_ylabel('Recovery Efficiency, threshold SNR = ' + str(options.snrthreshold))
axes.set_xlim([min(xvals)*0.9, max(xvals)*1.1])
axes.set_ylim([0, 1])
#axes.get_xaxis().set_major_formatter(ScalarFormatter())
#axes.get_xaxis().get_major_formatter().labelOnlyBase = False
axes.xaxis.set_minor_formatter(FormatStrFormatter("%.0e"))

#title = " ".join([configs.get('trigger', 'triggerNumber'), 
#                  configs.get('injection', 'waveFrequency') + 'Hz', 
#                  "$\\tau=" + str(tau) + "$ sec", 
#                  search_type, 
#                  inj_type])
plt.title(title)
#if options.title:
#    plt.title(options.title)

plt.savefig(os.path.join(baseDir, "hrss_efficiency_plot.png"))




