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
from scipy import stats

parser = OptionParser()
parser.add_option("-d", "--dummy_onsource", dest = "dummy_onsource")
parser.add_option("-b", "--background", dest = "background")
(options, args) = parser.parse_args()

background_dir = options.background
dummy_dir = options.dummy_onsource

if dummy_dir[0] == ".":
    dummy_dir = os.getcwd() + dummy_dir[1:]
elif dummy_dir[0] == "~":
    dummy_dir = os.path.expanduser('~') + dummy_dir[1:]
if background_dir[0] == ".":
    background_dir = os.getcwd() + background_dir[1:]
elif background_dir[0] == "~":
    background_dir = os.path.expanduser('~') + background_dir[1:]

background = pd.read_csv(os.path.join(background_dir, 'STAMP_output_dataframe.csv'))
dummy = pd.read_csv(os.path.join(dummy_dir, 'STAMP_output_dataframe.csv'))

background_data = background['SNR'].as_matrix()
dummy_data = dummy['SNR'].as_matrix()

ksstat, pvalue = stats.ks_2samp(background_data, dummy['SNR'].as_matrix())

[hist, bin_edges] = np.histogram(background_data, bins=20, range=(5.5, 9))

hist = np.cumsum(hist)
hist = hist[-1] - hist
hist = hist/hist[0]

xvals = (bin_edges[1:] + bin_edges[0:-1])/2
plt.semilogy(xvals, hist)

dummy_xvals = np.interp(dummy_data, xvals, hist)
plt.scatter(dummy_data, dummy_xvals, color='r')

plt.text(7, 0.4, "KS stat: {:f}".format(ksstat))
plt.text(7, 0.3, "p value: {:f}".format(pvalue))

plt.xlabel("SNR of loudest Trigger")
plt.ylabel("Number")
plt.xlim([5.5, max(8, max(dummy_data))])
plt.ylim([1e-3, 1])
plt.title('Background Dist and Dummy Onsource jobs')

plt.savefig(os.path.join(dummy_dir, 'hist_vs_background.png'))

plt.clf()

plt.hist(dummy_xvals)
plt.xlabel('\% of background triggers louder than')
plt.ylabel('Number of dummy onsource jobs')
plt.savefig(os.path.join(dummy_dir, 'hist_pvals.png'))

plt.clf()

#[dhist, dbins] = np.histogram(dummy_data, bins=np.sort(dummy_data))
#[bhist, bbins] = np.histogram(background_data, bins=np.sort(background_data))

[dhist, dbins] = np.histogram(dummy_data, bins=10000)
[bhist, bbins] = np.histogram(background_data, bins=10000)

dcumhist = np.cumsum(dhist)/len(dummy_data)
bcumhist = np.cumsum(bhist)/len(background_data)

plt.plot(dbins[:-1], dcumhist, label='Dummy onsource')
plt.plot(bbins[:-1], bcumhist, label='Background')

plt.legend(loc='best')

plt.xlabel('SNR')
plt.title('Cumulative Histogram of Background vs Dummy onsource')
plt.savefig(os.path.join(dummy_dir, 'compare_cumhists.png'))

plt.clf()
#Also plot this as log hist


plt.semilogy(dbins[:-1], 1 - dcumhist, label='Dummy onsource')
plt.semilogy(bbins[:-1], 1 - bcumhist, label='Background')
plt.legend()
plt.xlabel('SNR')
plt.ylabel('FAR')
plt.title('FAR of Background and Dummy Onsource')
plt.ylim([8e-3, 1])
plt.xlim([5.5, 7.5])
plt.savefig(os.path.join(dummy_dir, 'log_compare_cumhsits.png'))


