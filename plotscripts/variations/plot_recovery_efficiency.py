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

varyingParam = configs.get('variations', 'paramName')
varyingDist = configs.get('variations', 'distribution')

data = pd.read_csv(os.path.join(baseDir, 'STAMP_output_dataframe.csv'))

cols = data.columns

desired_col = [ele for ele in cols if ele in varyingParam]
if len(desired_col) > 1:
    raise ValueError("Error: more than 1 parameter matched to varyingParam. This is a problem with the (shortened) names of columns")
desired_col=desired_col[0]

if 'recov' not in cols:
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
plt.plot(xvals, eff, 'bo-')
plt.xlim([min(xvals)*0.9, max(xvals)*1.1])
#plt.ylim([-.01, 1.1])
plt.ylim([0, 1])
plt.ylabel("Recovery Efficiency")
plt.xlabel(varyingParam)
if 'log' in varyingDist:
    plt.xscale('log')

if options.title:
    plt.title(options.title)

plt.savefig(os.path.join(baseDir, "efficiency_plot.png"))



