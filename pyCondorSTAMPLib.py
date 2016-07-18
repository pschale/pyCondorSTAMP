from __future__ import division, print_function
#from __future__ import print_function
from sys import hexversion
import datetime, os, subprocess
import numpy as np

# Helper function to create name for new copy of input parameter file
# stop gap measure to make the dags to be written depend upon the new file location
# it may be better to create the directories first instead so that this name doesn't have to be created twice.
# honestly not sure. Review and decide later.
# ugh. may be less work just to move the directory building up and force manual deletion if the program fails.
def new_input_file_name(filePath, outputDirectory):
    if "/" in filePath:
        reversePath = filePath[::-1]
        reverseName = reversePath[:reversePath.index("/")]
        fileName = reverseName[::-1]
    else:
        fileName = filePath
    if outputDirectory[-1] == "/":
        outputPath = outputDirectory + fileName
    else:
        outputPath = outputDirectory + "/" + fileName
    return outputPath

# Helper function to copy input parameter files
def copy_input_file(filePath, outputDirectory):

    outputPath = new_input_file_name(filePath, outputDirectory)
    #print(filePath)# debug
    with open(filePath, "r") as infile:
        text = [line for line in infile]
    with open(outputPath,"w") as outfile:
        outfile.write("".join(line for line in text))
    return outputPath

# Helper function to read in data from a file
# Possibly add a check here for whitespace characters that aren't spaces.  Think
# about how robust I want this to be and whether I want to check for this
# elsewhere instead.
def read_text_file(file_name, delimeter, strip_trailing = True):

    # is the empty variable needed?
    data = None
    with open(file_name, "r") as infile:
        if strip_trailing:
            data = [filter(None,line.strip().split(delimeter)) for line in infile if not line.isspace()]#(line.isspace or not line)]
        else:
            data = [line.strip().split(delimeter) for line in infile if not line.isspace()]#(line.isspace or not line)]
    return data

# Helper function to take take input properly in python 2 or 3
def version_input(input_string):
    output = ""
    if hexversion >= 0x3000000:
        output = input(input_string)
    else:
        output = raw_input(input_string)
    return output

# Helper function to ask a yes or no question
def ask_yes_no(question):
    answered = False
    while not answered:
        answer = version_input(question)
        if answer.lower() == 'y' or answer.lower() == 'n':
            answered = True
        else:
            print("\nSorry, '" + answer + "' is not a valid answer.  Please \
answer either 'y' or 'n'.\n")
    return answer.lower()

# Helper function to ask a yes or no question given as bool
def ask_yes_no_bool(question):
    answered = False
    while not answered:
        answer = version_input(question)
        if answer.lower() == 'y' or answer.lower() == 'n':
            answered = True
        else:
            print("\nSorry, '" + answer + "' is not a valid answer.  Please \
answer either 'y' or 'n'.\n")
    if answer.lower() == 'y':
        return True
    else:
        return False

# Helper function to make new directory
def create_dir(name, iterate_name = True):

    # set default directory name
    newDir = name
    # If directory doesn't exist, create
    if not os.path.exists(name):
        os.makedirs(name)

    # Otherwise, if iterate_name is set to true, iterate version number
    # to create new directory
    elif iterate_name:
        # Set initial version number
        version = 2
        # set base name to add version number to
        base_name = name + "_v"
        # while directory exists, iterate version number
        while os.path.exists(base_name + str(version)):
            version += 1
        # overwrite directory name
        newDir = base_name + str(version)
        # make new directory
        os.makedirs(newDir)

    return newDir

# Helper function to create dated directory
def dated_dir(name, date = None, iterate_name = True):

    # If date empty, get time and date
    if not date:
        date = datetime.datetime.now()
    # create dated name
    dated_name = name + "-" + str(date.year) + "_" + str(date.month) + \
                 "_" + str(date.day)
    # create directory
    newDir = create_dir(dated_name, iterate_name)

    return newDir

# Helper function to parse job settings and enter values in subdictionaries as needed based
# on '.' in strings
def nested_dict_entry(dictionary, entry, value, delimeter = "."):
    """Helper function to parse job settings and enter values in subdictionaries as needed based on '.' in strings"""
    if delimeter in entry:
        index = entry.index(delimeter)
        base_entry = entry[:index]
        new_entry = entry[index+1:]
 #       print(base_entry)
        if base_entry not in dictionary or not isinstance(dictionary[base_entry], dict):
            dictionary[base_entry] = {}
        dictionary[base_entry] = nested_dict_entry(dictionary[base_entry], new_entry, value, delimeter)
        return dictionary
    else:
        if entry == 'trackInputFiles':
            value_list = value.split(',')
            value_len = len(value_list)
            string_array = np.zeros(value_len, dtype=np.object)
            for num in range(value_len):
                string_array[num] = value_list[num]
            dictionary[entry] = string_array
        else:
            dictionary[entry] = value
 #       print(entry)
#        print(value)
        return dictionary

# Helper function to find frames of specified type during specified time
def create_frame_file_list(frame_type, start_time, end_time, observatory):

    # search for file location for a given frame type during specified times
    data_find = ['gw_data_find','-s', start_time, '-e', end_time, '-o',
                 observatory, '--url-type', 'file', '--lal-cache', '--type',
                 frame_type]

    frame_locations_raw = subprocess.Popen(data_find, stdout = subprocess.PIPE, stderr=subprocess.PIPE).communicate()#[0]
    if frame_locations_raw[1]:
        print(frame_locations_raw[1])
        print("The following shell command caused the above message:")
        raise pyCondorSTAMPanteprocError(str(frame_locations_raw[1]) + "\nCaused by the following shell command:\n" + " ".join(data_find))
    #frame_locations = frame_locations_raw.split("\n")
    #print(frame_locations_raw)
    frame_locations = [x[x.find("localhost") + len("localhost"):] for x in frame_locations_raw[0].split("\n") if x]

    # create frame list
    return frame_locations

# Helper function to grab time data from frame name
def frame_start_time(frame_path):
    if "/" in frame_path:
        frame_name = frame_path[::-1]
        frame_name = frame_name[:frame_name.index("/")]
        frame_name = frame_name[::-1]
        #frame_name = frame_path[::-1][:frame_path[::-1].index("/")][::-1] #?
    else:
        frame_name = frame_path
    #print(frame_name)
    #print(len(frame_name))
    frame_time = frame_name[frame_name.index("-") + 1:]
    frame_time = frame_time[frame_time.index("-") + 1:]
    frame_time = frame_time[:frame_time.index("-")]
    #print("Check if number: " + frame_time)
    return frame_time

# Helper function to create a file from the list of frame file locations
def create_cache_and_time_file(frame_list,observatory,jobNumber,jobCacheDir, archived_frames_okay = False):

    # make list of times
    time_list = [frame_start_time(x) for x in frame_list if x]
    time_string = "\n".join(x for x in time_list)
    # create string to write to file

    output_string = "\n".join(x for x in frame_list)
    # create list to hold list of files in archive directory

    archived = [x for x in frame_list if "archive" in x]

    # check data for possibly archived data
    if archived:
        if archived_frames_okay:
            for line in archived:
                print(line)
        else:
            display_files = ask_yes_no("Some frame files during the time \
specified may have to be loaded from tape. Display frame files in 'archive' \
directory? ('y' or 'n'): ")

            if display_files == 'y':
                for line in archived:
                    print(line)

            continue_program = ask_yes_no("Continue program? ('y' or 'n'): ")

            if continue_program == 'n':
                pyCondorSTAMPanteprocError("Program execution ended")

    # create file
    modifier = observatory + "." + str(jobNumber) + ".txt"
    with open(jobCacheDir + "/frameFiles" + modifier, "w") as outfile:
        outfile.write(output_string)
    with open(jobCacheDir + "/gpsTimes" + modifier, "w") as outfile:
        outfile.write(time_string)

def checkEssentialParameter(dictionary, parameter):
    output = None
    try:
        output = dictionary[parameter]
    except KeyError, e:
        print("KeyError: no default value for parameter " + str(e) + ".")
    return output

# Helper function to create a file from the list of frame file locations
def create_fake_cache_and_time_file(start_time, end_time, observatory, jobNumber, jobCacheDir):

    # calculate job duration
    tempJobDur = str(int(float(end_time) - float(start_time)))
    # create fake frame name and string to write to channel
    output_string = "/FAKEDATA/" + observatory + "-FAKE-" + str(int(start_time)) + "-" + tempJobDur + ".gwf\n"
    time_string = str(int(start_time)) + "\n"

    # create file
    modifier = observatory + "." + str(jobNumber) + ".txt"
    with open(jobCacheDir + "/frameFiles" + modifier, "w") as outfile:
        outfile.write(output_string)
    with open(jobCacheDir + "/gpsTimes" + modifier, "w") as outfile:
        outfile.write(time_string)

