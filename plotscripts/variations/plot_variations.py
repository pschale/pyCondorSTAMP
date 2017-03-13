from __future__ import division
import scipy.io as sio
import matplotlib as mpl
mpl.use("Agg")
mpl.rc('text', usetex=True)
import matplotlib.pyplot as plt
import os
from optparse import OptionParser
import ConfigParser

parser = OptionParser()
parser.add_option("-d", "--directory", dest = "directory",)
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

numJobGroups = configs.getint('variations', 'numJobGroups')
varyingParam = configs.get('variations', 'paramName')
varyingDist = configs.get('variations', 'distribution')
injfreq = configs.getfloat('injection', 'waveFrequency')

def get_param_from_anteproc(baseDir, IFO, jg, jn, param):
    f = os.path.join(baseDir, 'anteproc_data', IFO + "-anteproc_params_group_" + str(jg) + "_" + str(int(jn)) + ".txt")
    for line in open(f):
        text = line.split(" ")
        if text[0] == param:
            return float(text[1])
    else:
        raise ValueError("parameter not found in anteproc config file")

rec_xvals = []
rec_SNRs = []
unrec_xvals = []
unrec_SNRs = []

for i in range(numJobGroups):
    jgdir = os.path.join(baseDir, 'jobs', 'job_group_' + str(i+1))
    for jobdir in [os.path.join(jgdir, ele) for ele in os.listdir(jgdir)]:
        try:
            files = os.listdir(os.path.join(jobdir, 'grandStochtrackOutput'))
            matfile = [ele for ele in files if 'mat' in ele][0]
            mat = sio.loadmat(os.path.join(jobdir, 'grandStochtrackOutput', matfile))
            snr = mat['stoch_out']['max_SNR'][0,0][0,0]
            fmin = mat['stoch_out'][0,0]['fmin'][0,0]
            fmax = mat['stoch_out'][0,0]['fmax'][0,0]

            inmat = sio.loadmat(os.path.join(jobdir, 'grandStochtrackInput', 'params.mat'))
            anteproc_job_nums = [inmat['params']['anteproc'][0][0]['jobNum1'][0][0][0][0], inmat['params']['anteproc'][0][0]['jobNum2'][0][0][0][0]]

            hval = get_param_from_anteproc(baseDir, 'H1', i+1, anteproc_job_nums[0], varyingParam)
            lval = get_param_from_anteproc(baseDir, 'L1', i+1, anteproc_job_nums[1], varyingParam)

            if not hval == lval:
                raise ValueError("Error: Values for parameter {} do not match between H and L; " + \
                                 "job group {}, H job {}, L job {}".format(varyingParam, i, 
                                                anteproc_job_nums[0], anteproc_job_nums[1]))

            if (float(fmin) - injfreq) * (float(fmax) - injfreq) < 0:
                rec_xvals.append(hval)
                rec_SNRs.append(snr)
            else:
                unrec_xvals.append(hval)
                unrec_SNRs.append(snr)

        except IndexError:
            print("job " + str(i) + "has not finished yet")

plt.scatter(rec_xvals, rec_SNRs, color='g', label="Recovered Injection")
plt.scatter(unrec_xvals, unrec_SNRs, color='r', label="Recovered Noise")
plt.xlabel(varyingParam)
plt.ylabel("SNR")
plt.xlim([min(rec_xvals + unrec_xvals)*0.9, max(rec_xvals + unrec_xvals)*1.1])
plt.plot([min(rec_xvals + unrec_xvals)*0.9, max(rec_xvals + unrec_xvals)*1.1], [7.5, 7.5], label="Loudest Background (est)")
plt.legend(loc='upper left')

if 'log' in varyingDist:
    plt.xscale('log')

plt.savefig(os.path.join(baseDir, "scatterplot.png"))



