from __future__ import division
from optparse import OptionParser
import json
import sys

# command line options
parser = OptionParser()
parser.set_defaults(verbose = True)
parser.add_option("-j", "--jsonFile", dest = "jsonFile",
                  help = "Path to JSON containing time segments",
                  metavar = "FILE_PATH")
parser.add_option("-s", "--shift", dest = "timeShift",
                  help = "Seconds to time shift the data by",
                  metavar = "NUMBER")
parser.add_option("-o", "--output", dest = "outputDir",
                  help = "Directory for output list of background jobs",
                  metavar = "DIRECTORY")
parser.add_option("-n", "--numJobs", dest = "numberJobs",
                  help = "Number of jobs to attempt to build background",
                  metavar = "INTEGER")
parser.add_option("-i", "--nspi", dest = "NSPI",
                  help = "Number of segments per interval (odd numbers only)",
                  metavar = "INTEGER")
parser.add_option("-b", "--buffer", dest = "jobBuffer",
                  help = "Number of seconds to separate the data of each job by",
                  metavar = "INTEGER")
parser.add_option("-d", "--duration", dest = "duration",
                  help = "Duration of individual jobs in seconds",
                  metavar = "INTEGER")
parser.add_option("-t", "--name", dest = "fileNameBase",
                  help = "Base string to base the job files name on",
                  metavar = "STRING")
parser.add_option("-v", action="store_true", dest="verbose")

(options, args) = parser.parse_args()

with open(options.jsonFile, "r") as inJSON:
    data = json.load(inJSON)

timeSegments = data["section list"]

if int(options.NSPI) % 2 == 0:
    print("WARNING: NSPI entered is not odd. Buffers of job may not guard properly for desired NSPI.")
    sys.exit()

print("NSPI used: " + str(int(options.NSPI)))

endsBuffer = (int(options.NSPI) - 1) / 2 + 2

separation = endsBuffer * 2 + int(options.jobBuffer) + int(options.timeShift) + 1 # last one to account for the last half pixel and give an extra separation due to it.

quit_loop = False

def jobsFromSegment(segment, ends_buffer, job_separation, job_duration):
    segment_start = int(segment[0])
    segment_end = int(segment[1])
    segment_duration = segment_end - segment_start
    start_time = segment_start + ends_buffer
    num_jobs = segment_duration // job_duration
    jobs = [[start_time + (job_duration + job_separation) * x, start_time + job_separation * x + job_duration * (x + 1)] for x in range(num_jobs) if start_time + job_separation * x + job_duration * (x + 1) < segment_end]
    return jobs

possibleJobs = [jobsFromSegment(x, endsBuffer, separation, int(options.duration)) for x in timeSegments]

possibleJobsFlat = [x for jobs in possibleJobs for x in jobs]

if len(possibleJobsFlat) < int(options.numberJobs):
    backgroundJobs = possibleJobsFlat
else:
    backgroundJobs = possibleJobsFlat[:int(options.numberJobs)]

stringOne = "\n".join(" ".join(str(int(x)) for x in [index+1, job[0] - endsBuffer, job[1] + endsBuffer + 1, job[1] - job[0] + 2 * endsBuffer + 1]) for index, job in enumerate(backgroundJobs))
stringTwo = "\n\n".join("\n".join(x for x in ["job " + str(index+1), "grandStochtrack job " + str(index+1), "grandStochtrack hstart " + str(int(job[0])), "grandStochtrack hstop " + str(int(job[1]))]) for index, job in enumerate(backgroundJobs))

with open(options.outputDir + "/" + options.fileNameBase + "Jobs.txt","w") as outfile:
    outfile.write(stringOne)

with open(options.outputDir + "/" + options.fileNameBase + "Configuration.txt","w") as outfile:
    outfile.write(stringTwo)
