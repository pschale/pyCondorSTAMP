# Written Ryan Quitzow-James

from __future__ import division
from math import ceil

#opens a file, outputs a 2-d array (1st dimension - line, 2nd dimension - word)
def readFile(file_name, delimeter = None):
    with open(file_name, "r") as infile:
        content = [x.split(delimeter) for x in infile]
    return content

def loadLines(filename):
    with open(filename, "r") as infile:
        data = [[y.strip("_") for y in x.split()] for x in infile]
    return data

def saveText(file_name, output_text):
    with open(file_name, "w") as outfile:
        outfile.write(output_text)

#takes diretory+filename, outputs full path (takes care of "/"s)
def glueFileLocation(directory, filename):
    output = None
    if directory[-1] == "/":
        if filename[0] == "/":
            output = directory + filename[1:]
        else:
            output = directory + filename
    else:
        if filename[0] == "/":
            output = directory + filename
        else:
            output = directory + "/" + filename
    return output

def lineCut1Hz(line_info, delta_F):
    band = line_info[0].split("-")
    if len(band) > 0:
        #band_low = band[0]#min(line_center_int(band[0]))
        #band_high = band[1]#max(line_center_int(band[-1]))
        band_low = int(ceil(float(band[0])))
        band_high = int(float(band[-1]))
        notch_lines = [x for x in range(band_low, band_high + 1)]
    else:
        notch_lines = None
    return notch_lines

def findOverlappingTimes(timeList1, timeList2):
    index_2 = 0
    dual_segments = []
    for seg_1 in timeList1:
        start_1 = int(seg_1[0])
        end_1 = int(seg_1[1])
        if index_2 < len(timeList2):
            while int(timeList2[index_2][1]) <= start_1:
                index_2 += 1
            break_loop = False
            if index_2 >= len(timeList2):
                break_loop = True
            while not break_loop:
                start_2 = int(timeList2[index_2][0])
                end_2 = int(timeList2[index_2][1])
                if start_2 >= end_1:
                    break_loop = True
                else:
                    if start_1 > start_2:
                        seg_start = start_1
                    else:
                        seg_start = start_2
                    if end_1 > end_2:
                        index_2 += 1
                        seg_end = end_2
                    else:
                        break_loop = True
                        seg_end = end_1
                    dual_segments += [[seg_start, seg_end]]
                    """seg_start = max(start_1, start_2)
                        seg_end = min(end_1, end_2)
                        dual_segments += [[seg_start, seg_end]]
                        if end_1 > end_2:
                            index_2 += 1
                        else:
                            break_loop = True"""
                    if index_2 >= len(timeList2):
                        break_loop = True
    return dual_segments

def calculateSegmentBuffer(NSPI, pixel_duration, buffer_seconds):
    buffer_time = (NSPI - 1) * pixel_duration / 2 + buffer_seconds
    return buffer_time

def getShortSegTimes(segment, long_buffer, short_buffer, long_pre_trigger, short_pre_trigger, short_preproc_job_duration):
    job_start = segment[0]
    trigger_time = job_start + long_buffer + long_pre_trigger
    job_short_start = trigger_time - short_pre_trigger - short_buffer
    job_short_end = job_short_start + short_preproc_job_duration
    return [job_short_start, job_short_end]

#def calculateWindows(time_list, job_buffer):
#    return None

class backgroundJobSet(object):
    def __init__(self, NSPI = 9, long_pixel_duration = 4, short_pixel_duration = 1, job_buffer = 1, time_shift = 1, buffer_seconds = 2, short_job_post_trigger = 400, short_job_pre_trigger = 10, possible_interval_list = None, post_veto_times = None, bad_times = None, essential_jobs = None, essential_short_jobs = None, long_job_duration_override = None, short_job_duration_override = None):
        self.NSPI = NSPI
        self.longPixelDuration = long_pixel_duration
        self.shortPixelDuration = short_pixel_duration
        self.jobBuffer = job_buffer
        self.timeShift = time_shift
        self.bufferSeconds = buffer_seconds
        self.calculateSegmentBuffers()
        self.shortJobPreTrigger = short_job_pre_trigger
        self.shortJobPostTrigger = short_job_post_trigger
        self.possibleIntervalList = possible_interval_list
        self.essential_jobs = essential_jobs
        self.essential_short_jobs = essential_short_jobs
        self.long_job_duration_override = long_job_duration_override
        self.short_job_duration_override = short_job_duration_override
        if self.possibleIntervalList:
            self.calculateJobs()
        if post_veto_times:
            self.findPostVetoJobs(post_veto_times, bad_times)

    def calculateSegmentBuffers(self):
        self.longSegmentBuffer = calculateSegmentBuffer(self.NSPI, self.longPixelDuration, self.bufferSeconds)
        self.shortSegmentBuffer = calculateSegmentBuffer(self.NSPI, self.shortPixelDuration, self.bufferSeconds)

    def getShortSegTime(self, segment):
        job_start = segment[0]
        trigger_time = job_start + self.longSegmentBuffer + self.longJobPreTrigger
        job_short_start = trigger_time - self.shortJobPreTrigger - self.shortSegmentBuffer
        job_short_end = job_short_start + self.shortPreprocJobDuration
        return [job_short_start, job_short_end]

    def calculateJobs(self):
        #print(self.possibleIntervalList)
        print("Preparing job list from possibleIntervalList")
        self.longJobPostTrigger = self.shortJobPostTrigger * self.longPixelDuration / self.shortPixelDuration
        self.longJobPreTrigger = self.shortJobPreTrigger * self.longPixelDuration / self.shortPixelDuration
        self.longJobDuration = self.longJobPreTrigger + self.longJobPostTrigger
        if self.long_job_duration_override:
            self.longPreprocJobDuration = self.long_job_duration_override
        else:
            self.longPreprocJobDuration = self.longJobDuration + 2*self.longSegmentBuffer + int(ceil(self.longPixelDuration/2))
        self.longJobStartSeparation = self.longPreprocJobDuration + self.jobBuffer

        self.shortJobDuration = self.shortJobPreTrigger + self.shortJobPostTrigger
        if self.short_job_duration_override:
            self.shortPreprocJobDuration = self.short_job_duration_override
        else:
            self.shortPreprocJobDuration = self.shortJobDuration + 2*self.shortSegmentBuffer + int(ceil(self.shortPixelDuration/2))

        # create list of long duration jobs
        job_start_dif = self.longJobStartSeparation
        effective_job_length = self.longPreprocJobDuration
        #temp_job_list = [[[x[0] + y*(job_start_dif), x[0] + y*(job_start_dif) + effective_job_length]
        #                  for y in range(int((x[1] - x[0])//(job_start_dif)))] for x in self.possibleIntervalList]
        temp_job_list = [create_jobs_from_interval(x, job_start_dif, effective_job_length) for x in self.possibleIntervalList]
        if not temp_job_list[0]:
            print("Temporary version of interval checker that checks first interval only. This function should be updated to include the last possible interval even if there is no buffer after it since it would be the last one. This probably entails making the first section per interval separately, then the rest based on haveing the buffer between jobs in front.")
            if self.possibleIntervalList[0][1] - self.possibleIntervalList[0][0] >= effective_job_length:
                temp_job_list = [[[self.possibleIntervalList[0][0],self.possibleIntervalList[0][0] + effective_job_length]]]
        #print(temp_job_list)
        #print(job_start_dif)
        #print(int((x[1] - x[0])//(job_start_dif)))
        # flatten job list into just a list of lists, instead of a list of lists of lists
        print("Finding long jobs")
        self.longJobs = [y for x in temp_job_list for y in x]
        if self.essential_jobs:
            self.longJobs += self.essential_jobs
        self.longJobList = self.longJobs[:]
        print("Finding short jobs")
        self.shortJobs = [self.getShortSegTime(x) for x in self.longJobs]
        if self.essential_short_jobs:
            self.shortJobs += essential_short_jobs
        print("Creating full list of jobs")
        temp_full_list = [[self.longJobs[num], self.shortJobs[num]] for num in range(len(self.longJobs))]
        print("flattening list of jobs")
        flat_temp_full_list = [y for x in temp_full_list for y in x]
        print("Creating job list")
        self.jobList = [[num + 1] + flat_temp_full_list[num] + [flat_temp_full_list[num][1] - flat_temp_full_list[num][0]] for num in range(len(flat_temp_full_list))]
        print("Creating preprocJobList")
        self.preprocJobList = [[num + 1] + flat_temp_full_list[num] + [flat_temp_full_list[num][1] - flat_temp_full_list[num][0]] for num in range(len(flat_temp_full_list))]
        print("Creating burstegardPreprocJobList")
        self.burstegardPreprocJobList = [[num + 1] + self.longJobs[num] + [self.longJobs[num][1] - self.longJobs[num][0]] for num in range(len(self.longJobs))]
        #print(self.shortJobs)
        print("Creating jobMap")
        self.jobMap = dict((job+1, job+1) for job in range(len(self.preprocJobList)))
        self.longJobMap = dict((job+1, job+1) for job in range(len(self.longJobList)))
        print("Creating burstegardJobMap")
        self.burstegardJobMap = dict((job+1, job+1) for job in range(len(self.burstegardPreprocJobList)))
        print("Done creating possible jobs")
        #print("In object")
        #print(self.jobList)

    def alignIntervals(self, time_segments, pixel_duration):
        #print("test")
        #print(time_segments)
        end_buffer = (self.NSPI - 1)*pixel_duration/2 + self.bufferSeconds
        front_time = time_segments[0][0]
        #print(front_time)
        #print(time_segments[0])
        temp_intervals = [x if (x[0] - front_time) % (pixel_duration/2) == 0 else [x[0] + ((x[0] - front_time) % (pixel_duration/2)), x[1]] for x in time_segments]
        #print(temp_intervals)
        temp_intervals = [x if (x[1] - x[0] - 2*self.bufferSeconds) % (pixel_duration/2) == 0 else [x[0], x[1] - ((x[1] - x[0] - 2*self.bufferSeconds) % (pixel_duration/2))] for x in temp_intervals]
        #print(temp_intervals)
        return temp_intervals

    def cutBadTimes(self, interval, bad_times):
        tempBadTimes = [x for x in bad_times if interval[0] <= x < interval[1]]
        if len(tempBadTimes) > 0:
            timeList = []
            if tempBadTimes[0] > interval[0]:
                timeList += [[interval[0], tempBadTimes[0]]]
            if len(tempBadTimes) > 1:
                timeList += [[tempBadTimes[num] + 1, tempBadTimes[num+1]] for num in range(len(tempBadTimes)-1)]
            if tempBadTimes[-1] + 1 < interval[1]:
                timeList += [[tempBadTimes[-1] + 1, interval[1]]]
        else:
            timeList = [interval]
        return timeList

    def findJobTimeNotDuringVeto(self, interval, post_veto_times, bad_times, pixel_duration):
        post_times_of_interest = [x for x in post_veto_times if x[0] < interval[1] and x[1] > interval[0]]
        num_times = len(post_times_of_interest)
        if num_times > 1:
            times = [[max([interval[0], post_times_of_interest[0][0]]), post_times_of_interest[0][1]]]
            if num_times > 2:
                times += post_times_of_interest[1:-1]
            times += [[post_times_of_interest[-1][0], min([interval[1], post_times_of_interest[-1][1]])]]
        elif num_times == 1:
            times = [[max([interval[0], post_times_of_interest[0][0]]), min([interval[1], post_times_of_interest[0][1]])]]
        else:
            times = []
        if len(times) > 0:
            #print(times)
            if bad_times:
                times = [self.cutBadTimes(x, bad_times) for x in times]
                #print(times)
                times = [x for y in times for x in y]
            #print(times)
            times = self.alignIntervals(times, pixel_duration)
            #print(times)
            times = [x for x in times if x[1] - x[0] >= self.NSPI * pixel_duration + self.bufferSeconds*2]
        return times

    def findPostVetoJobs(self, post_veto_times, bad_times):
        print("Creating post veto jobs")
        temp_interval_list_long = [self.findJobTimeNotDuringVeto(x, post_veto_times, bad_times, self.longPixelDuration) for x in self.longJobs]
        temp_interval_list_short = [self.findJobTimeNotDuringVeto(x, post_veto_times, bad_times, self.shortPixelDuration) for x in self.shortJobs]
        temp_burstegard_interval_list = [self.findJobTimeNotDuringVeto(x, post_veto_times, bad_times, self.shortPixelDuration) for x in self.longJobs]
        temp_full_list = [[temp_interval_list_long[num], temp_interval_list_short[num]] for num in range(len(temp_interval_list_long))]
        flat_temp_full_list = [y for x in temp_full_list for y in x]
        temp_job_counter = 0
        self.jobMap = {}
        # map jobs
        for num in range(len(flat_temp_full_list)):
            old_job_num = num + 1
            num_new_jobs = len(flat_temp_full_list[num])
            temp_list = [temp_job_counter + x + 1 for x in range(num_new_jobs)]
            if temp_list:
                self.jobMap[old_job_num] = [temp_job_counter + x + 1 for x in range(num_new_jobs)]
            temp_job_counter += num_new_jobs
        self.burstegardJobMap = {}
        # map jobs
        temp_job_counter = 0
        for num in range(len(temp_burstegard_interval_list)):
            old_job_num = num + 1
            num_new_jobs = len(temp_burstegard_interval_list[num])
            temp_list = [temp_job_counter + x + 1 for x in range(num_new_jobs)]
            if temp_list:
                self.burstegardJobMap[old_job_num] = [temp_job_counter + x + 1 for x in range(num_new_jobs)]
            temp_job_counter += num_new_jobs
        self.longJobMap = {}
        # map jobs
        temp_job_counter = 0
        for num in range(len(temp_interval_list_long)):
            old_job_num = num + 1
            num_new_jobs = len(temp_interval_list_long[num])
            temp_list = [temp_job_counter + x + 1 for x in range(num_new_jobs)]
            if temp_list:
                self.longJobMap[old_job_num] = [temp_job_counter + x + 1 for x in range(num_new_jobs)]
                #print(old_job_num)
                #print(temp_job_counter)
            temp_job_counter += num_new_jobs
        #print(temp_interval_list_long)
        #print(self.longJobMap)
        flat_interval_list = [y for x in flat_temp_full_list for y in x]
        flat_long_interval_list = [y for x in temp_interval_list_long for y in x]
        flat_long_burstegard_list = [y for x in temp_burstegard_interval_list for y in x]
        self.preprocJobList = [[num + 1] + flat_interval_list[num] + [flat_interval_list[num][1] - flat_interval_list[num][0]] for num in range(len(flat_interval_list))]
        self.longJobList = [[num + 1] + flat_long_interval_list[num] + [flat_long_interval_list[num][1] - flat_long_interval_list[num][0]] for num in range(len(flat_long_interval_list))]
        self.burstegardPreprocJobList = [[num + 1] + flat_long_burstegard_list[num] + [flat_long_burstegard_list[num][1] - flat_long_burstegard_list[num][0]] for num in range(len(flat_long_burstegard_list))]
        print("Complete")

        """
    def findPostVetoJobs(self, post_veto_times, bad_times):
        print("Creating post veto jobs")
        temp_interval_list_long = [self.findJobTimeNotDuringVeto(x, post_veto_times, bad_times, self.longPixelDuration) for x in self.longJobs]
        temp_interval_list_short = [self.findJobTimeNotDuringVeto(x, post_veto_times, bad_times, self.shortPixelDuration) for x in self.shortJobs]
        temp_full_list = [[temp_interval_list_long[num], temp_interval_list_short[num]] for num in range(len(temp_interval_list_long))]
        flat_temp_full_list = [y for x in temp_full_list for y in x]
        temp_job_counter = 0
        self.jobMap = {}
        # map jobs
        for num in range(len(flat_temp_full_list)):
            old_job_num = num + 1
            num_new_jobs = len(flat_temp_full_list[num])
            temp_list = [temp_job_counter + x + 1 for x in range(num_new_jobs)]
            if temp_list:
                self.jobMap[old_job_num] = [temp_job_counter + x + 1 for x in range(num_new_jobs)]
            temp_job_counter += num_new_jobs
        self.burstegardJobMap = {}
        # map jobs
        temp_job_counter = 0
        for num in range(len(temp_interval_list_long)):
            old_job_num = num + 1
            num_new_jobs = len(temp_interval_list_long[num])
            temp_list = [temp_job_counter + x + 1 for x in range(num_new_jobs)]
            if temp_list:
                self.burstegardJobMap[old_job_num] = [temp_job_counter + x + 1 for x in range(num_new_jobs)]
            temp_job_counter += num_new_jobs
        flat_interval_list = [y for x in flat_temp_full_list for y in x]
        flat_long_interval_list = [y for x in temp_interval_list_long for y in x]
        self.preprocJobList = [[num + 1] + flat_interval_list[num] + [flat_interval_list[num][1] - flat_interval_list[num][0]] for num in range(len(flat_interval_list))]
        self.burstegardPreprocJobList = [[num + 1] + flat_long_interval_list[num] + [flat_long_interval_list[num][1] - flat_long_interval_list[num][0]] for num in range(len(flat_long_interval_list))]
        print("Complete")"""

    def saveJobs(self, job_file_name):
        output_text = "\n".join(" ".join(str(int(x)) for x in line) for line in self.preprocJobList)
        saveText(job_file_name, output_text)

    def saveBurstegardJobs(self, job_file_name):
        output_text = "\n".join(" ".join(str(int(x)) for x in line) for line in self.burstegardPreprocJobList)
        saveText(job_file_name, output_text)

    def saveLongJobs(self, job_file_name):
        output_text = "\n".join(" ".join(str(int(x)) for x in line) for line in self.longJobList)
        saveText(job_file_name, output_text)

def create_jobs_from_interval(interval, job_start_difference, temp_effective_job_length):
    #print("Calculating jobs for interval " + str(interval))
    #print(temp_effective_job_length)
    number_jobs = int((interval[1] - interval[0])//(job_start_difference))
    temp_jobs = [[interval[0] + y*(job_start_difference), interval[0] + y*(job_start_difference) + temp_effective_job_length]
                          for y in range(number_jobs)]
    if not temp_jobs:
        if interval[1] - interval[0] >= temp_effective_job_length:
            temp_jobs = [[interval[0], interval[0] + temp_effective_job_length]]
    elif interval[1] - temp_jobs[-1][1] >= job_start_difference:
        print("extra job")
        print("temp_effective_job_length")
        print(temp_effective_job_length)
        print([interval[1] - temp_effective_job_length, interval[1]])
        print("\n\n\n")
        temp_jobs += [[interval[1] - temp_effective_job_length, interval[1]]]
    #print(str(number_jobs) + " jobs created")
    return temp_jobs
