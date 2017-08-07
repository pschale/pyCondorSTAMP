#makes a job file for a given trigger time and number of offsource times
#requires GWPY to get segment list
#to activate gwpy virtual environment, run:
#. ~detchar/opt/gwpysoft/bin/activate
#(the dot is part of the command)

import argparse
from gwpy.segments import DataQualityFlag, SegmentList, Segment
from pylal.xlal.datatypes.ligotimegps import LIGOTimeGPS
import os

parser = argparse.ArgumentParser(description='Makes a job file for STAMP')
parser.add_argument('-t', dest='triggerTime', type=int, help='Trigger time')
parser.add_argument('-n', dest='numJobs', type=int, 
                        help='Number of jobs desired')
parser.add_argument('-d', dest='duration', type=int, default=1640,
                        help='OPTIONAL - duration of jobs (default 1640)')
parser.add_argument('-b', dest='onsourceBuffer', type=int, default=2,
                        help='OPTIONAL - seconds before trigger \
                        onsource starts (default 2)')
parser.add_argument('-N', dest='name', type=str, help='Name of Trigger')
parser.add_argument('-f', dest='frameType', type=str, help='Type of frame, \
                        default is C01', default='C01')
parser.add_argument('-l', dest='location', type=str, help='location to save files')
parser.add_argument('--start-background', dest='start_background', type=int,
                        help='OPTIONAL - start of background, default is n*d seconds before trigger')
parser.add_argument('--end-background', dest='end_background', type=int,
                        help='OPTIONAL - end of background, default is n*d seconds after trigger')


options = parser.parse_args()

onsource_job_file = options.name + '_onsource_job.txt'
offsource_job_file = options.name + '_offsource_jobs.txt'

if (options.start_background is not None) & (options.end_background is not None):
    startTime = options.start_background
    endTime = options.end_background
elif (options.start_background is not None) or (options.end_background is not None):
    raise ValueError('need to set both start_background and end_background')
else:
    startTime = options.triggerTime - options.duration*options.numJobs
    endTime = options.triggerTime + options.duration*options.numJobs

if options.frameType == 'C00':
    segName = 'DMT-ANALYSIS_READY'
elif options.frameType == 'C01':
    segName = 'DCS-ANALYSIS_READY_C01'
else:
    raise ValueError('Can only accept C00 or C01 for frametype')

H1flag = DataQualityFlag.query('H1:' + segName, startTime, endTime).active
L1flag = DataQualityFlag.query('L1:' + segName, startTime, endTime).active

#print H1flag
#print L1flag
bothActive = H1flag & L1flag

#verify that intersection was done correctly
for seg in bothActive:

    pass_H_test = Segment(seg) in H1flag
    pass_L_test = Segment(seg) in L1flag

    if not (pass_H_test and pass_L_test):
        print(seg)
        print('H in observing:', pass_H_test)
        print('L in observing:', pass_L_test)
        raise ValueError('Some segments not in observing time')



#remove onsource from active time, make onsource job
# 18 seconds before trigger is for PSD estimation:
# job output will be [-20, 1620] (this is fed into anteproc)
# job after processing by STAMP script will be [-2, 1600] (this is fed into grand_stochtrack)
onsource = [options.triggerTime - options.onsourceBuffer - 18, options.triggerTime + options.duration - options.onsourceBuffer - 18]


#check if onsource has flag active
if Segment(onsource) not in bothActive:
    print(bothActive)
    raise ValueError("Analysis Ready flag not active during onsource")

bothActive = bothActive - SegmentList([Segment(onsource)])

bothActive = SegmentList([Segment(ele) for ele in bothActive])

bothActive = SegmentList([Segment([int(bothActive[i][j])#.seconds 
                                for j in range(len(bothActive[i]))]) 
                                for i in range(len(bothActive))])
numJobsinSeg = [(bothActive[i].end-bothActive[i].start)//options.duration for i in range(len(bothActive)) ]

#remove all segments with 0 jobs
for i in range(len(numJobsinSeg))[::-1]:
    if numJobsinSeg[i] < 1:
        del numJobsinSeg[i]
        del bothActive[i]

offsource = []
for i in range(len(bothActive)):
    startOfJob = bothActive[i].start
    for j in range(numJobsinSeg[i]):
        offsource.append([startOfJob, startOfJob + options.duration])
        startOfJob += options.duration

#validation of offsource
for job in offsource:
    pass_H_test = Segment(job) in H1flag
    pass_L_test = Segment(job) in L1flag

    if not (pass_H_test and pass_L_test):
        print(job)
        print('H in observing:', pass_H_test)
        print('L in observing:', pass_L_test)
        raise ValueError('Some segments not in observing time')

    if SegmentList([Segment(job)]).intersects_segment(Segment(onsource)):
        raise ValueError('Offsource Segment overlaps with onsource')

print(len(offsource))
# Reduce number of jobs to numJobs; end up with same number before and after - or as close as possible
numBeforeTrigger = len([ele for ele in offsource if ele[0] < options.triggerTime])
print(numBeforeTrigger)
if numBeforeTrigger < options.numJobs/2:
    offsource = offsource[:options.numJobs]
    print('Unable to make equal split of background jobs.')
    print('Most jobs occur after trigger')
elif len(offsource) - numBeforeTrigger < options.numJobs/2:
    offsource = offsource[-options.numJobs:]
    print('Unable to make equal split of background jobs.')
    print('Most background jobs occur before trigger')
else:
    offsource = offsource[numBeforeTrigger-options.numJobs/2:]
    offsource = offsource[:options.numJobs]

#check that enough offsource jobs were made
if len(offsource) < options.numJobs:
    raise ValueError('Not enough background jobs were generated, {} asked for, only {} generated'.format(options.numJobs, len(offsource)))


#make things strings and output them

onsource_str = [str(ele) for ele in onsource]
onsource_str = ['1'] + onsource_str +  [str(options.duration)]
onsource_str = " ".join(onsource_str)

with open(os.path.join(options.location, onsource_job_file), "w") as h:
    h.write(onsource_str)

offsource_str = [[str(ele) for ele in line] for line in offsource]
offsource_str = [[str(i+1)] + line + [str(options.duration)] for i, line in enumerate(offsource_str)]
offsource_str = "\n".join([" ".join(line) for line in offsource_str])

with open(os.path.join(options.location, offsource_job_file), "w") as h:
    h.write(offsource_str)



