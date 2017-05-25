#makes a job file for a given trigger time and number of offsource times
#requires GWPY to get segment list
import argparse
from gwpy.segments import DataQualityFlag, SegmentList, Segment
from pylal.xlal.datatypes.ligotimegps import LIGOTimeGPS


parser = argparse.ArgumentParser(description='Makes a job file for STAMP')
parser.add_argument('-t', dest='triggerTime', type=int, help='Trigger time')
parser.add_argument('-n', dest='numJobs', type=int, 
                        help='Number of jobs desired')
parser.add_argument('-d', dest='duration', type=int, default=1540,
                        help='OPTIONAL - duration of jobs (default 1540)')
parser.add_argument('-b', dest='onsourceBuffer', type=int, default=2,
                        help='OPTIONAL - seconds before trigger \
                        onsource starts (default 2)')
parser.add_argument('-N', dest='name', type=str, help='Name of Trigger')
parser.add_argument('-f', dest='frameType', type=str, help='Type of frame, \
                        default is C01', default='C01')

options = parser.parse_args()

onsource_job_file = options.name + '_onsource_job.txt'
offsource_job_file = options.name + '_offsource_jobs.txt'

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


bothActive = H1flag and L1flag

#check if onsource has flag active
if Segment(options.triggerTime - 100, options.triggerTime + 1700) not in bothActive:
    print(bothActive)
    raise ValueError("Analysis Ready flag not active during onsource")

#remove onsource from active time, make onsource job
onsource = [options.triggerTime - options.onsourceBuffer, options.triggerTime + options.duration - options.onsourceBuffer]
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

# Reduce number of jobs to numJobs; end up with same number before and after - or as close as possible
numBeforeTrigger = len([ele for ele in offsource if ele[0] < options.triggerTime])

if numBeforeTrigger < options.numJobs/2:
    offsource = offsource[:options.numJobs]
else:
    offsource = offsource[numBeforeTrigger-options.numJobs/2:]
    offsource = offsource[:options.numJobs]

#make things strings and output them

onsource_str = [str(ele) for ele in onsource]
onsource_str = ['1'] + onsource_str +  [str(options.duration)]
onsource_str = " ".join(onsource_str)

with open(onsource_job_file, "w") as h:
    h.write(onsource_str)

offsource_str = [[str(ele) for ele in line] for line in offsource]
offsource_str = [[str(i+1)] + line + [str(options.duration)] for i, line in enumerate(offsource_str)]
offsource_str = "\n".join([" ".join(line) for line in offsource_str])

with open(offsource_job_file, "w") as h:
    h.write(offsource_str)



