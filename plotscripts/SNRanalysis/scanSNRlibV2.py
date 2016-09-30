# Written by Ryan Quitzow-James

from __future__ import division
import scipy.io as sio
import os#, subprocess

# Helper function to make new directory
def create_dir(name, iterate_name = True):

    # Set default directory name
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

def getSNR(inputFile):
    if inputFile:
        data = sio.loadmat(inputFile)
        #SNR = data['stoch_out'][0,0].max_SNR[0,0]
        SNR = data['stoch_out']['max_SNR'][0,0][0,0]
    else:
        SNR = None
    return SNR

def getSNRother(inputFile):
    if inputFile:
        data = sio.loadmat(inputFile)
        SNR = data['output'][0,0]
    else:
        SNR = None
    return SNR

def getAlpha(inputFile):
    alpha = None
    with open(inputFile, "r") as infile:
        readData = [x for x in infile if len(x.split()) > 0]
        alphaLine = [x.split()[1] for x in readData if x.split()[0] == "stamp.alpha"]
        alpha = alphaLine[0]
    return alpha

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

def getPartialPath(path):
    if path[-1] == "/":
        path = path[:-1]
    reversedPath = path[::-1]
    shortened = reversedPath[reversedPath.index("/")+1:]
    #shortenedSecond = shortened[shortened.index("/")+1:]
    frontPath = shortened[::-1]
    #frontPath = shortenedSecond[::-1]
    shortPath = path[len(frontPath) + 1:]
    return shortPath

def getPartialPathOld(path):
    if path[-1] == "/":
        path = path[:-1]
    reversedPath = path[::-1]
    shortened = reversedPath[reversedPath.index("/")+1:]
    shortenedSecond = shortened[shortened.index("/")+1:]
    frontPath = shortenedSecond[::-1]
    shortPath = path[len(frontPath) + 1:]
    return shortPath

def returnMatrixFilePath(directory, nameBase = "bknd_"):
    files = [x for x in os.listdir(directory) if nameBase in x]
    if len(files) != 1:
        print("WARNING: Number of files in " + directory + " with name base " + nameBase + " is not equal to one. Number of files is " + str(len(files)) + ". Selecting first occurance for rest of script.")
    if len(files) == 0:
        filePath = None
    else:
        filePath = directory + "/" + files[0]
    return filePath

class job_info(object):

    def __init__(self, path = None):
        self.matrix_sub_dir = "grandstochtrackOutput"
        self.preproc_file_short_path = "preprocInput/preprocParams.txt"
        self.matrix_path = None
        self.preproc_path = None
        self.set_path(path)
        self.SNR = None
        self.alpha = None
        if path:
            self.load_info()

    def set_path(self, path = None):
        self.path = path.strip()
        self.short_name = None
        if path:
            self.short_name = getPartialPath(path)
            #print(self.short_name)
            self.matrix_path = returnMatrixFilePath(glueFileLocation(self.path, self.matrix_sub_dir))
            self.preproc_path = glueFileLocation(self.path, self.preproc_file_short_path)

    def load_info(self):
        self.SNR = getSNR(self.matrix_path)
        self.alpha = getAlpha(self.preproc_path)

    def get_snr(self):
        return self.SNR

    def get_alpha(self):
        return self.alpha

    def get_job(self):
        return self.short_name

    def get_job_path(self):
        return self.path

class job_group(object):

    def __init__(self, group_path = None):
        self.set_path(group_path)
        self.jobs = []
        if group_path:
            self.load_jobs()

    def set_path(self, group_path = None):
        self.group_path = group_path.strip()
        self.group_short_name = None
        if group_path:
            self.group_short_name = getPartialPath(group_path)

    def load_jobs(self):
        job_dirs = [glueFileLocation(self.group_path, x) for x in os.listdir(self.group_path) if "job" in x]
        self.jobs = [job_info(x) for x in job_dirs]

    #def load_info():
    def get_snrs(self):
        temp_SNRs = [x.get_snr() for x in self.jobs]
        return temp_SNRs

    def get_alphas(self):
        temp_alphas = [x.get_alpha() for x in self.jobs]
        return temp_alphas

    def get_jobs(self, run_name = None, group_name = True):
        temp_jobs = [x.get_job() for x in self.jobs]
        if group_name:
            temp_jobs = [glueFileLocation(self.group_short_name, x) for x in temp_jobs]
            #temp_jobs = [x for x in temp_jobs]
        if run_name:
            temp_jobs = [glueFileLocation(run_name, x) for x in temp_jobs]
        return temp_jobs

    def get_job_paths(self):
        temp_jobs = [x.get_job_path() for x in self.jobs]
        return temp_jobs

    def get_loudest_SNR(self):
        temp_snrs = self.get_snrs()
        temp_max_snr = max(temp_snrs)
        temp_jobs = [x for x in self.jobs if x.get_snr() == temp_max_snr]
        temp_job_text = " and ".join(glueFileLocation(self.group_short_name, x.get_job()) for x in temp_jobs)
        temp_job_paths = [x.get_job_path() for x in temp_jobs]
        max_SNR_data = [temp_job_text, temp_max_snr, temp_job_paths]
        return max_SNR_data

    def get_data(self, run_name = None):
        data = [self.get_jobs(run_name), self.get_job_paths(), self.get_snrs(), self.get_alphas()]
        return data

class search_run_info(object):

    def __init__(self, run_path = None):
        self.set_path(run_path)
        self.job_groups = []
        if run_path:
            self.load_job_groups()

    def set_path(self, run_path = None):
        self.run_path = run_path.strip()
        self.run_short_name = None
        self.jobs_base_dir = None
        if run_path:
            self.run_short_name = getPartialPath(run_path)
            self.jobs_base_dir = glueFileLocation(run_path, "jobs")

    def load_job_groups(self):
        job_group_dirs = [glueFileLocation(self.jobs_base_dir, x) for x in os.listdir(self.jobs_base_dir) if "group" in x]
        self.job_groups = [job_group(x) for x in job_group_dirs]
        """temp_extra_jobs = [glueFileLocation(self.jobs_base_dir, x) for x in os.listdir(self.jobs_base_dir) if "job" in x]
        extra_jobs = [x for x in temp_extra_jobs if x not in job_group_dirs]
        if extra_jobs:
            extra_group = job_group()
            extra_group.group_short_name = "groupless """

    def get_snrs(self):
        temp_snrs = [x for group in self.job_groups for x in group.get_snrs()]
        return temp_snrs

    def get_alphas(self):
        temp_alphas = [x for group in self.job_groups for x in group.get_alphas()]
        return temp_alphas

    # Todo to get paths to plots
    #def get_relative_paths(self):
    #    temp_paths = [glueFileLocation("jobs", )

    def get_high_snrs(self):
        high_snrs = [x.get_loudest_SNR() for x in self.job_groups]
        return high_snrs

    def get_data(self, include_run_name = True):
        if include_run_name:
            temp_path = glueFileLocation(self.run_short_name, "jobs")
            data = [x.get_data(temp_path) for x in self.job_groups]
        else:
            data = [x.get_data() for x in self.job_groups]
        return data


class job_info_no_alpha(object):

    def __init__(self, path = None):
        self.matrix_sub_dir = "grandstochtrackOutput"
        #self.preproc_file_short_path = "preprocInput/preprocParams.txt"
        self.matrix_path = None
        #self.preproc_path = None
        self.set_path(path)
        self.SNR = None
        #self.alpha = None
        if path:
            self.load_info()

    def set_path(self, path = None):
        self.path = path.strip()
        self.short_name = None
        if path:
            self.short_name = getPartialPath(path)
            #print(self.short_name)
            self.matrix_path = returnMatrixFilePath(glueFileLocation(self.path, self.matrix_sub_dir))
            #self.preproc_path = glueFileLocation(self.path, self.preproc_file_short_path)

    def load_info(self):
        self.SNR = getSNR(self.matrix_path)
        #self.alpha = getAlpha(self.preproc_path)

    def get_snr(self):
        return self.SNR

    #def get_alpha(self):
     #   return self.alpha

    def get_job(self):
        return self.short_name

    def get_job_path(self):
        return self.path

class job_group_no_alphas(object):

    def __init__(self, group_path = None):
        self.set_path(group_path)
        self.jobs = []
        if group_path:
            self.load_jobs()

    def set_path(self, group_path = None):
        self.group_path = group_path.strip()
        self.group_short_name = None
        if group_path:
            self.group_short_name = getPartialPath(group_path)

    def load_jobs(self):
        job_dirs = [glueFileLocation(self.group_path, x) for x in os.listdir(self.group_path) if "job" in x]
        self.jobs = [job_info_no_alpha(x) for x in job_dirs]

    #def load_info():
    def get_snrs(self):
        temp_SNRs = [x.get_snr() for x in self.jobs]
        return temp_SNRs

    #def get_alphas(self):
      #  temp_alphas = [x.get_alpha() for x in self.jobs]
     #   return temp_alphas

    def get_jobs(self, run_name = None, group_name = True):
        temp_jobs = [x.get_job() for x in self.jobs]
        if group_name:
            temp_jobs = [glueFileLocation(self.group_short_name, x) for x in temp_jobs]
            #temp_jobs = [x for x in temp_jobs]
        if run_name:
            temp_jobs = [glueFileLocation(run_name, x) for x in temp_jobs]
        return temp_jobs

    def get_job_paths(self):
        temp_jobs = [x.get_job_path() for x in self.jobs]
        return temp_jobs

    def get_loudest_SNR(self):
        temp_snrs = self.get_snrs()
        temp_max_snr = max(temp_snrs)
        temp_jobs = [x for x in self.jobs if x.get_snr() == temp_max_snr]
        temp_job_text = " and ".join(glueFileLocation(self.group_short_name, x.get_job()) for x in temp_jobs)
        temp_job_paths = [x.get_job_path() for x in temp_jobs]
        max_SNR_data = [temp_job_text, temp_max_snr, temp_job_paths]
        return max_SNR_data

    def get_data(self, run_name = None):
        data = [self.get_jobs(run_name), self.get_job_paths(), self.get_snrs()]#, self.get_alphas()]
        return data

class search_run_info_no_alphas(object):

    def __init__(self, run_path = None):
        print("Initializing run object")
        self.set_path(run_path)
        self.job_groups = []
        if run_path:
            self.load_job_groups()

    def set_path(self, run_path = None):
        print("Setting path")
        self.run_path = run_path.strip()
        self.run_short_name = None
        self.jobs_base_dir = None
        if run_path:
            self.run_short_name = getPartialPath(run_path)
            self.jobs_base_dir = glueFileLocation(run_path, "jobs")

    def load_job_groups(self):
        print("Loading job groups")
        job_group_dirs = [glueFileLocation(self.jobs_base_dir, x) for x in os.listdir(self.jobs_base_dir) if "group" in x]
        self.job_groups = [job_group_no_alphas(x) for x in job_group_dirs]

    def get_snrs(self):
        print("Getting SNRs")
        temp_snrs = [x for group in self.job_groups for x in group.get_snrs()]
        return temp_snrs

   # def get_alphas(self):
    #    temp_alphas = [x for group in self.job_groups for x in group.get_alphas()]
     #   return temp_alphas

    # Todo to get paths to plots
    #def get_relative_paths(self):
    #    temp_paths = [glueFileLocation("jobs", )

    def get_high_snrs(self):
        print("Getting loudest group SNRs")
        high_snrs = [x.get_loudest_SNR() for x in self.job_groups]
        return high_snrs

    def get_data(self, include_run_name = True):
        print("Getting data")
        if include_run_name:
            temp_path = glueFileLocation(self.run_short_name, "jobs")
            data = [x.get_data(temp_path) for x in self.job_groups]
        else:
            data = [x.get_data() for x in self.job_groups]
        return data

    def get_snrs_by_group(self):
        print("Creating SNR dictionary")
        temp_dict = dict((group.group_short_name, group.get_snrs()) for group in self.job_groups)
        return temp_dict

class search_run_info_no_alphas_v2(object):

    def __init__(self, run_path = None):
        print("Initializing run object")
        self.set_path(run_path)
        self.job_groups = []
        if run_path:
            self.load_job_groups()

    def set_path(self, run_path = None):
        print("Setting path")
        self.run_path = run_path.strip()
        self.run_short_name = None
        self.jobs_base_dir = None
        if run_path:
            self.run_short_name = getPartialPath(run_path)
            self.jobs_base_dir = glueFileLocation(run_path, "jobs")

    def load_job_groups(self):
        print("Loading job groups")
        job_group_dirs = [glueFileLocation(self.jobs_base_dir, x) for x in os.listdir(self.jobs_base_dir) if "group" in x]
        self.job_groups = [job_group_no_alphas_v2(x) for x in job_group_dirs]

    def get_snrs(self):
        print("Getting SNRs")
        temp_snrs = [x for group in self.job_groups for x in group.get_snrs()]
        return temp_snrs

    def get_high_snrs(self):
        print("Getting loudest group SNRs")
        high_snrs = [x.get_loudest_SNR() for x in self.job_groups]
        return high_snrs

    def get_data(self, include_run_name = True):
        print("Getting data")
        print(self.jobs_base_dir)
        if include_run_name:
            temp_path = glueFileLocation(self.run_short_name, "jobs")
            data = [x.get_data(temp_path) for x in self.job_groups]
        else:
            data = [x.get_data() for x in self.job_groups]
        return data

    def get_snrs_by_group(self):
        print("Creating SNR dictionary")
        temp_dict = dict((group.group_short_name, group.get_snrs()) for group in self.job_groups)
        return temp_dict

class job_group_no_alphas_v2(object):

    def __init__(self, group_path = None):
        self.set_path(group_path)
        self.jobs = []
        if group_path:
            self.load_jobs()

    def set_path(self, group_path = None):
        self.group_path = group_path.strip()
        self.group_short_name = None
        if group_path:
            self.group_short_name = getPartialPath(group_path)

    def load_jobs(self):
        matrix_paths = [returnMatrixFilePath(glueFileLocation(glueFileLocation(self.group_path, x),"grandstochtrackOutput")) for x in os.listdir(self.group_path) if "job" in x]
        #self.jobs = [job_info_no_alpha(x) for x in job_dirs]
        self.jobs = dict((x, getSNR(x)) for x in matrix_paths)

    #def load_info():
    def get_snrs(self):
        temp_SNRs = [self.jobs[x] for x in self.jobs]
        return temp_SNRs

    #def get_alphas(self):
      #  temp_alphas = [x.get_alpha() for x in self.jobs]
     #   return temp_alphas

    def get_jobs(self, run_name = None, group_name = True):
        temp_jobs = [x[x.rfind("/")+1:] for x in self.jobs]
        if group_name:
            temp_jobs = [glueFileLocation(self.group_short_name, x) for x in temp_jobs]
            #temp_jobs = [x for x in temp_jobs]
        if run_name:
            temp_jobs = [glueFileLocation(run_name, x) for x in temp_jobs]
        return temp_jobs

    def get_job_paths(self):
        temp_jobs = [x for x in self.jobs]
        return temp_jobs

    def get_loudest_SNR(self):
        temp_snrs = self.get_snrs()
        temp_max_snr = max(temp_snrs)
        temp_jobs = [x for x in self.jobs if self.jobs[x] == temp_max_snr]
        temp_job_text = " and ".join(glueFileLocation(self.group_short_name, self.jobs[x]) for x in temp_jobs)
        temp_job_paths = [x for x in temp_jobs]
        max_SNR_data = [temp_job_text, temp_max_snr, temp_job_paths]
        return max_SNR_data

    def get_data(self, run_name = None):
        data = [self.get_jobs(run_name), self.get_job_paths(), self.get_snrs()]#, self.get_alphas()]
        return data
