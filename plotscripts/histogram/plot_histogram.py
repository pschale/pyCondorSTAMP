from __future__ import division
import scipy.io as sio
import matplotlib as mpl
mpl.use("Agg")
mpl.rc('text', usetex=True)
import matplotlib.pyplot as plt
import os
import pandas as pd
from optparse import OptionParser
import numpy as np

parser = OptionParser()
parser.add_option("-d", "--directory", dest = "directory",)
(options, args) = parser.parse_args()

baseDir = options.directory

if baseDir[0] == ".":
    baseDir = os.getcwd() + baseDir[1:]
elif baseDir[0] == "~":
    baseDir = os.path.expanduser('~') + baseDir[1:]

data = pd.read_csv(os.path.join(baseDir, 'STAMP_output_dataframe.csv'))

groupnums = set(data['Group'].as_matrix())

datagroups = [data['SNR'][data['Group']==i].as_matrix() for i in groupnums]
varycols = [ele for ele in ['phi', 'iota', 'psi', 'InjAmp'] if ele in data.columns]

if len(varycols) > 0:
    varies = [not all(data[ele][1:] == data[ele][:-1]) for ele in varycols]

    if np.count_nonzero(varies)>1:
        print(varies)
        raise ValueError("Error: more than 1 parameter varies, code not ready for that")
    varyparam = varycols[varies.index(True)]
    varyparams_by_group = [data[varyparam][data['Group']==i].as_matrix() for i in groupnums]

    #check to make sure all values are the same
    checks = [all(ele[1:] == ele[:-1]) for ele in varyparams_by_group]
    if not all(checks):
        raise ValueError("varyingparam not the same for every job in group")

    val_by_group = [ele[0] for ele in varyparams_by_group]
    plt.hist(datagroups, label=[varyparam + ": " + str(ele) for ele in val_by_group], stacked=True)
    plt.legend()
else:
    plt.hist(datagroups, label=['Group ' + str(ele) for ele in groupnums], bins=20, range=(5.5, 9.5))
plt.xlabel("SNR of loudest Trigger")
plt.ylabel("Number")
plt.savefig(os.path.join(baseDir, 'new_histogram.png'))

plt.clf()
if len(varycols) == 0:
    h = plt.hist(datagroups, cumulative=-1, normed=True, range=(3, 9.5), bins=5000)
    plt.clf()
    xvals = [(h[1][i] + h[1][i+1])/2. for i in range(len(h[1])-1)]
    plt.semilogy(xvals, h[0])
    plt.xlabel("SNR")
    plt.ylabel("Fraction of jobs at least that loud")
    plt.ylim([1e-3, 1])
    plt.xlim([5.5, 9.5])
    plt.savefig(os.path.join(baseDir, 'new_cum_histogram.png'))




