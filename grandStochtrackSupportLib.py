from __future__ import division
import json
import collections
#import scipy.io as sio

# Helper function to convert unicode strings in dictionary to strings
# WARNING: Not currently set up to traverse lists or tuples or other structures
def convert_unicode_to_strings(data):
    if isinstance(data, basestring):
        return(str(data))
    elif isinstance(data, dict):
        return dict((convert_unicode_to_strings(key), convert_unicode_to_strings(value)) for key, value in data.iteritems())
    else:
        return data

# Helper function
def load_dict_from_json(filename):
    with open(filename, "r") as infile:
        rawDictionary = json.load(infile)
        dictionary = convert_unicode_to_strings(rawDictionary)
    return dictionary

# Helper function to copy default dictionary.
# WARNING: Not currently set up to traverse and copy lists or tuples or other structures
def dict_copy(data):
    if isinstance(data, dict):
        return dict((key, dict_copy(value)) for key, value in data.iteritems())
    # add case to handle lists
    elif isinstance(data, list):
        return data[:]
    else:
        return data

# Helper function to copy default dictionary into specific dictionary.
def load_default_dict(specificDictionary, defaultDictionary):
    dictionary = dict_copy(defaultDictionary)
    for key in specificDictionary:
        if key in dictionary and isinstance(dictionary[key], collections.Mapping):
            dictionary[key] = load_default_dict(specificDictionary[key], dictionary[key])
        else:
            dictionary[key] = specificDictionary[key]
    #dictionary.update(specificDictionary)
    # or this one just to be extra careful, but I don't think you'll want a copy without the defaults if you're loading the defaults, but this is here anyway just in case, just uncomment it and comment out the above line.
    #dictionary.update(dict_copy(specificDictionary))
    return dictionary

# Helper function to save dictionary as Matlab matrix object
# Not needed as a function really, but here for now as a reminder
#def save_as_Matlab_matrix(filename, dictionary):
 #   sio.savemat(filename, dictionary)

# Helper function to determine if a string is a number
def number_check(num):
    try:
        temp = float(num)
        #if temp == float('NaN') or temp == float('inf'):
         #   return False
        #else:
         #   return True
        return True
    except ValueError:
        return False

# Helper function to load a number as int or float as appropriate
def load_number(number):
    if int(float(number)) == float(number):
        return int(number)
    else:
        return float(number)

# Helper function to load a value as a number if possible and as itself otherwise
# TODO: better name needed!
def load_if_number(data):
    if number_check(data):
        return float(data)#load_number(data)
    else:
        return data
