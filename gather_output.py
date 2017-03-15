from __future__ import division
import scipy.io as sio
import pandas as pd
import os
from optparse import OptionParser
import ConfigParser
import numpy as np

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

variations = configs.getboolean('variations', 'doVariations')
injection = configs.getboolean('injection', 'doInjections')

outdata = {}

if variations:
    numJobGroups = configs.getint('variations', 'numJobGroups')
    varyingParam = configs.get('variations', 'paramName')
    varyingDist = configs.get('variations', 'distribution')
    if varyingParam not in ['stamp.alpha', 'stamp.phi', 'stamp.iota', 'stamp.psi']:
        outdata[varyingParam] = []
else:
    numJobGroups = 1

if injection:
    outdata["recov"] = []
    outdata['alpha'] = []
    outdata['phi'] = []
    outdata['iota'] = []
    outdata['psi'] = []
    outdata['injfreq'] = []

def get_param_from_anteproc(baseDir, IFO, jg, jn):
    f = os.path.join(baseDir, 'anteproc_data', IFO + "-anteproc_params_group_" + str(jg) + "_" + str(int(jn)) + ".txt")
    outdict = {}
    for line in open(f):
        text = line.split(" ")
        outdict[text[0]] = text[1]
    return outdict

def Round_To_n(x, n):
    return round(x, -int(np.floor(np.sign(x) * np.log10(abs(x)))) + n)

outdata['SNRs'] = []
outdata['tmin'] = []
outdata['tmax'] = []
outdata['fmin'] = []
outdata['fmax'] = []
outdata['length'] = []
outdata['jobNumH'] = []
outdata['jobNumL'] = []
outdata['Group'] = []
outdata['Job'] = []
for i in range(numJobGroups):
    jgdir = os.path.join(baseDir, 'jobs', 'job_group_' + str(i+1))
    jobcounter = 0
    for jobdir in [os.path.join(jgdir, ele) for ele in os.listdir(jgdir)]:
        jobcounter+=1
        try:
            datapoint = pd.DataFrame
            files = os.listdir(os.path.join(jobdir, 'grandStochtrackOutput'))
            matfile = [ele for ele in files if 'mat' in ele][0]
            mat = sio.loadmat(os.path.join(jobdir, 'grandStochtrackOutput', matfile))
            outdata['SNRs'].append(mat['stoch_out']['max_SNR'][0,0][0,0])
            outdata['fmin'].append(mat['stoch_out'][0,0]['fmin'][0,0])
            outdata['fmax'].append(mat['stoch_out'][0,0]['fmax'][0,0])
            outdata['tmin'].append(mat['stoch_out'][0,0]['tmin'][0,0])
            outdata['tmax'].append(mat['stoch_out'][0,0]['tmax'][0,0])
            outdata['length'].append(outdata['tmax'][-1] - outdata['tmin'][-1])
            outdata['Group'].append(i+1)
            outdata['Job'].append(jobcounter)
            inmat = sio.loadmat(os.path.join(jobdir, 'grandStochtrackInput', 'params.mat'))
            
            H1num = int(inmat['params']['anteproc'][0][0]['jobNum1'][0][0][0][0])
            L1num = int(inmat['params']['anteproc'][0][0]['jobNum2'][0][0][0][0])

            outdata['jobNumH'].append(H1num)
            outdata['jobNumL'].append(L1num)

            H1anteproc = get_param_from_anteproc(baseDir, 'H1', i+1, H1num)
            L1anteproc = get_param_from_anteproc(baseDir, 'L1', i+1, L1num)


            if variations:
                hval = H1anteproc[varyingParam]
                lval = L1anteproc[varyingParam]

                if varyingParam not in ['stamp.alpha', 'stamp.phi', 'stamp.iota', 'stamp.psi', 'stamp.f0']:
                    outdata[varyingParam].append(hval)

                if not hval == lval:
                    raise ValueError("Error: Values for parameter {} do not match between H and L; " + \
                                     "job group {}, H job {}, L job {}".format(varyingParam, i+1, 
                                                    H1num, L1num))

            if injection:
                for key in ['stamp.alpha', 'stamp.phi0', 'stamp.iota', 'stamp.psi']:
                    if not H1anteproc[key] == L1anteproc[key]:
                        raise ValueError("Error: Values for parameter {} do not match between H and L; " + \
                                     "job group {}, H job {}, L job {}".format(key, i+1, 
                                                    H1num, L1num))
                injfreq = float(H1anteproc['stamp.f0'])
                outdata['recov'].append( (float(outdata['fmin'][-1]) - injfreq) * (float(outdata['fmax'][-1]) - injfreq) < 0 )
                outdata['alpha'].append(Round_To_n(float(H1anteproc['stamp.alpha']), 3))
                outdata['phi'].append(float(H1anteproc['stamp.phi0']))
                outdata['iota'].append(float(H1anteproc['stamp.iota']))
                outdata['psi'].append(float(H1anteproc['stamp.psi']))
                outdata['injfreq'] = injfreq
            

        except IndexError:
            print("job " + str(i) + "has not finished yet")

allkeys = outdata.keys()

ordered_keys = ['Group', 'Job', 'SNRs', 'fmin', 'fmax', 'length', 'tmin', 'tmax', 'jobNumH', 'jobNumL', 'injfreq', 'phi', 'iota', 'psi', 'alpha', 'recov']
ordered_keys = [ele for ele in ordered_keys if ele in allkeys]

if variations and varyingParam not in ['stamp.alpha', 'stamp.phi', 'stamp.iota', 'stamp.psi', 'stamp.f0']:
    ordered_keys.append(varyingParam)

output_frame = pd.DataFrame(outdata, index=range(1, len(outdata['SNRs'])+1))
output_frame = output_frame.round({'SNRs': 2})
output_frame = output_frame[ordered_keys]
output_frame.to_csv(os.path.join(baseDir, 'STAMP_output_dataframe.csv'))
output_frame.to_html(buf=open(os.path.join(baseDir, 'STAMP_output_data.html'), 'w'))


