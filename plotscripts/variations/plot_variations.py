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


parser = OptionParser()
parser.add_option("-d", "--directory", dest="directory")
parser.add_option("-t", "--title", dest="title", default=False)
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

varyingParam = configs.get('variations', 'paramName')
varyingDist = configs.get('variations', 'distribution')

data = pd.read_csv(os.path.join(baseDir, 'STAMP_output_dataframe.csv'))
cols = data.columns

desired_col = [ele for ele in cols if ele in varyingParam]
if len(desired_col) > 1:
    raise ValueError("Error: more than 1 parameter matched to varyingParam. This is a problem with the (shortened) names of columns")
desired_col=desired_col[0]

rec_SNRs = list(data['SNR'][data['recov']].as_matrix())
rec_xvals = list(data[desired_col][data['recov']].as_matrix())
unrec_SNRs = list(data['SNR'][data['recov']==False].as_matrix())
unrec_xvals = list(data[desired_col][data['recov']==False].as_matrix())

#axes = plt.subplot(111)
fig1, axes = plt.subplots()

axes.scatter(rec_xvals, rec_SNRs, color='g', label="Recovered Injection")
axes.scatter(unrec_xvals, unrec_SNRs, color='r', label="Recovered Noise")
axes.set_xlabel(varyingParam)
axes.set_ylabel("SNR")
axes.set_xlim([min(rec_xvals + unrec_xvals)*0.9, max(rec_xvals + unrec_xvals)*1.1])
axes.plot([min(rec_xvals + unrec_xvals)*0.9, max(rec_xvals + unrec_xvals)*1.1], [7.5, 7.5], label="Loudest Background (est)")
axes.legend(loc='upper left')
axes.get_xaxis().set_major_formatter(ScalarFormatter())
axes.get_xaxis().get_major_formatter().labelOnlyBase = False

if 'log' in varyingDist:
    plt.xscale('log')

if options.title:
    plt.title(options.title)

plt.savefig(os.path.join(baseDir, "scatterplot_new.png"))



