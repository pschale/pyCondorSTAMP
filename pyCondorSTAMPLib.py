from __future__ import division, print_function
#from __future__ import print_function
from sys import hexversion
import datetime, os

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
    """if "/" in filePath:
        reversePath = filePath[::-1]
        reverseName = reversePath[:reversePath.index("/")]
        fileName = reverseName[::-1]
    else:
        fileName = filePath
    if outputDirectory[-1] == "/":
        outputPath = outputDirectory + fileName
    else:
        outputPath = outputDirectory + "/" + fileName"""
    outputPath = new_input_file_name(filePath, outputDirectory)
    with open(filePath, "r") as infile:
        text = [line for line in infile]
    with open(outputPath,"w") as outfile:
        outfile.write("".join(line for line in text))

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
        dictionary[entry] = value
 #       print(entry)
#        print(value)
        return dictionary
