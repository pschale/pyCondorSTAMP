import os

#
print("Make sure to finish updating the universe and local variables part.")

# Helper function to write condor sub file
def write_sub_file(filenameBase, executable, baseDir, args, requestMemory = None, additional_requirements_list = None, getEnv = True):
    condor_sub_filename = baseDir + "/" + filenameBase + ".sub"
    # Separate strings
    universe = "universe = vanilla"
    if getEnv:
        universe += "\ngetenv = True"
    if requestMemory:
        universe += "\nrequest_memory = " + str(requestMemory)
    if additional_requirements_list:
        universe += "\n" + "\n".join(x for x in additional_requirements_list)
    executable_line = "executable = " + executable
    log = "log = " + baseDir + "/dagLogs/" + filenameBase + "$(jobNumber).log"
    error = "error = " + baseDir + "/dagLogs/logs/" + filenameBase + "$(jobNumber).err"
    output = "output = " + baseDir + "/dagLogs/logs/" + filenameBase + "$(jobNumber).out"
    arguments = ""
    if args:
        arguments = 'arguments = " ' + args + ' "'
    notifications = "notification = error"
    queue = "queue 1"
    string_list = [universe, executable_line, log, error, output, arguments,
                   notifications, queue]
    output_string = "\n".join(line for line in string_list)
    with open(condor_sub_filename, "w") as infile:
        infile.write(output_string)
    return condor_sub_filename

# create job
def create_dag_job(job_number, condor_sub_loc, vars_entries, arg_list, output_string, retry = 2, restrictCat = None):
    # create job entry strings
    jobNum = str(job_number)
    varEntries = [jobNum] + vars_entries
    argList = ["jobNumber"] + arg_list
    job_line = "JOB " + jobNum + " " + condor_sub_loc + "\n"
    retry_line = "RETRY " + jobNum + " " + str(int(retry)) + "\n"
    vars_line = "VARS " + jobNum
    for num in range(len(varEntries)):
        vars_line += ' ' + argList[num] + '="' + varEntries[num] + '"'
    if restrictCat:
        restrict_line = "\nCATEGORY " + str(job_number) + " " + restrictCat
        vars_line += restrict_line
    vars_line += '\n\n'

    # enter string in dag file
    job_string = job_line + retry_line + vars_line
    output_string += job_string
    # iterate job number
    job_number +=1

    return job_number, output_string

# create external dag job
def create_external_dag_job(job_number, dag_name, dag_location, output_string, retry = 2):
    # create job entry strings
    jobNum = str(job_number)
    dag_line = "SUBDAG EXTERNAL " + jobNum + " " + dag_name + " DIR " + dag_location + "\n"
    retry_line = "RETRY " + jobNum + " " + str(int(retry)) + "\n\n"

    # enter string in dag file
    job_string = dag_line + retry_line
    output_string += job_string
    # iterate job number
    job_number +=1

    return job_number, output_string

# Helper function to write preproc dag job entry
#def blrms_dag_job(job_number, condor_sub_loc, frame_list_dict, frame_list,
#                  conf_path, output_dir, file, test_interval = None):
def preproc_dag_job(job_number, jobKey, jobDictionary, condor_sub_loc, output_string, preproc_category = None, preprocInputDir = None):#output_dir, output_string)#, test_interval = None):
    # possible arguments
    argList = ["paramFile", "jobFile", "jobNum"]
    jobPath = jobDictionary[jobKey]["grandStochtrackParams"]["params"]["jobsFile"]
    if preprocInputDir:
        confPath = preprocInputDir + "/preprocParams.txt"
    else:
        confPath = jobDictionary[jobKey]["preprocInputDir"] + "/preprocParams.txt"
    for job_num in jobDictionary[jobKey]["preprocJobs"].split(","):
        jobNum = str(job_num)
        vars_entries = [confPath, jobPath, jobNum]

        # create job entry
        job_number, output_string = create_dag_job(job_number, condor_sub_loc, vars_entries, argList, output_string, restrictCat = preproc_category)

    return job_number, output_string

"""def preproc_dag_job_backup(job_number, jobKey, jobDictionary, condor_sub_loc, output_string, preproc_category = None):#output_dir, output_string)#, test_interval = None):
    # possible arguments
    argList = ["paramFile", "jobFile", "jobNum"]
    jobPath = jobDictionary[jobKey]["grandStochtrackParams"]["params"]["jobsFile"]
    confPath = jobDictionary[jobKey]["preprocInputDir"] + "/preprocParams.txt"
    jobNum = str(jobDictionary[jobKey]["preprocJobs"])
    vars_entries = [confPath, jobPath, jobNum]

    # create job entry
    job_number, output_string = create_dag_job(job_number, condor_sub_loc, vars_entries,
                                argList, output_string, restrictCat = preproc_category)

    return job_number, output_string"""

# Helper function to write list of preproc job entries
def write_preproc_jobs(job_number, jobDictionary, job_tracker, condor_sub_loc, output_string, preproc_category = None, job_order = None, job_group_preproc = None):
    # record jobs to job numbers translation
    job_relationship = {}
    if not job_order:
        job_order = jobDictionary.keys()
    created_jobs = {}
    if job_group_preproc:
        job_tracker = job_group_preproc["job_tracker"]
    for jobKey in job_order:
        if jobKey != "constants":
            start_job = job_number
            if job_group_preproc:
                if job_tracker[jobKey][1] not in created_jobs:
                    temp_job_group = job_tracker[jobKey][0]
                    temp_preproc_job = job_tracker[jobKey][1]
                    preprocInputDir = job_group_preproc[temp_job_group][temp_preproc_job]["preprocInputDir"]
                    job_number, output_string = preproc_dag_job(job_number, jobKey, jobDictionary, condor_sub_loc, output_string, preproc_category, preprocInputDir)
                    created_jobs[job_tracker[jobKey][1]] = range(start_job, job_number)
                job_relationship[jobKey] = created_jobs[job_tracker[jobKey][1]]
            else:
                job_number, output_string = preproc_dag_job(job_number, jobKey, jobDictionary, condor_sub_loc, output_string, preproc_category)
                job_relationship[jobKey] = range(start_job, job_number)
    # record range of job numbers just written
    return job_relationship, job_number, output_string

"""def write_preproc_jobs_backup(job_number, jobDictionary, job_tracker, condor_sub_loc,
                     output_string, preproc_category = None, job_order = None):
    start_job = job_number
    # record jobs to job numbers translation
    job_relationship = {}
    if not job_order:
        job_order = jobDictionary.keys()
    for jobKey in job_order:
        if jobKey != "constants":
            job_relationship[jobKey] = job_number
            job_number, output_string = preproc_dag_job(job_number, jobKey, jobDictionary, condor_sub_loc, output_string, preproc_category)

    end_job = job_number - 1
    # record range of job numbers just written
    #job_tracker += [[start_job, end_job]]
    return job_relationship, job_number, output_string"""

# Helper function to enter job hierarchy in dagfile
def job_heirarchy(job_tracker, output_string):
    #list_of_orderings = []
    output_string += "\n\n"
    for num in range(len(job_tracker) - 1):
        pair_1 = job_tracker[num]
        pair_2 = job_tracker[num+1]
        parent = "PARENT "
        child = "CHILD"
        for num in range(pair_1[0], pair_1[1]+1):
            parent += str(num) + " "
        for num in range(pair_2[0], pair_2[1]+1):
            child += " " + str(num)
        #order_string = parent + child
        output_string += parent + child + "\n\n"
        #list_of_orderings.append(order_string)
    #output_string = "\n\n".join(string for string in list_of_orderings)
    return output_string

# Helper function to enter job hierarchy in dagfile
def job_heirarchy_v2(job_relation_pair_lists, output_string):
    # [[pre1,pre2...],[post1,post2...],[pre1_2,pre2_2...],[post1_2,post2_2]]
    #list_of_orderings = []
    output_string += "\n\n"
    print(job_relation_pair_lists)
    for pair_list in job_relation_pair_lists:
        parent = "PARENT "
        child = "CHILD "
        parent += " ".join(str(x) for x in pair_list[0])
        child += " ".join(str(x) for x in pair_list[1])
        output_string += parent + " " + child + "\n\n"
        #list_of_orderings.append(order_string)
    #output_string = "\n\n".join(string for string in list_of_orderings)
    return output_string

# create grandstochtrack dag submission files
def create_grand_stochtrack_dag(job_dictionary, grand_stochtrack_executable, dag_dir, quit_program, use_gpu = False, max_gs_jobs = 100, job_order = None):
    if not quit_program:
        gs_category = "GRANDSTOCKTRACK"
        # create grand_stochtrack executable submit file
        if use_gpu:
            additional_inputs = ["Requirements = TARGET.WantGPU =?= True","+WantGPU = True"]
            memory = "4000"
        else:
            additional_inputs = ["request_cpus = 8"]
            memory = "8000"
        grand_stochtrack_sub_filename = write_sub_file("grand_stochtrack", grand_stochtrack_executable, dag_dir, "$(paramPath) $(jobNum)", memory, additional_inputs)
        # create dag file
        filename = dag_dir + "/grand_stochtrack.dag"
        dag_string = ""
        job_number = 0
        # create grand_stochtrack jobs
        for jobKey in job_order:
            if jobKey != "constants":
                argList = ["paramPath", "jobNum"]
                jobNum = str(job_dictionary[jobKey]["grandStochtrackParams"]["job"])
                paramPath = job_dictionary[jobKey]["stochtrackInputDir"] + "/" + "params.mat"
                vars_entries = [paramPath, jobNum]

                # create job entry
                job_number, dag_string = create_dag_job(job_number, grand_stochtrack_sub_filename, vars_entries,
                                            argList, dag_string, restrictCat = gs_category)
        # write grandStochtrack category job restriction
        dag_string += "\nMAXJOBS " + gs_category + " " + str(max_gs_jobs)

        with open(filename, "w") as outfile:
            outfile.write(dag_string)
        return filename

# create grandstochtrack jobs
def create_grand_stochtrack_jobs(job_number, job_dictionary, grand_stochtrack_executable, dag_dir, output_string, quit_program, use_gpu = False, job_order = None, gs_category = None):
    if not quit_program:
        # create grand_stochtrack executable submit file
        if type(use_gpu) == str:
            if use_gpu.lower() == "true":
                print("Using GPUs for clustermap.")
                use_gpu = True
            else:
                print("doGPU set to '" + use_gpu + "'. Using CPUs for clustermap.")
                use_gpu = False
        if use_gpu:
            additional_inputs = ["Requirements = TARGET.WantGPU =?= True","+WantGPU = True"]
            memory = "4000"
        else:
            additional_inputs = ["request_cpus = 8"]
            memory = "8000"
        grand_stochtrack_sub_filename = write_sub_file("grand_stochtrack", grand_stochtrack_executable, dag_dir, "$(paramPath) $(jobNum)", memory, additional_inputs)
        # create dag file
        #filename = dag_dir + "/grand_stochtrack.dag"
        dag_string = ""
        #job_number = 0
        job_relationship = {}
        # create grand_stochtrack jobs
        for jobKey in job_order:
            if jobKey != "constants":
                argList = ["paramPath", "jobNum"]
                jobNum = str(job_dictionary[jobKey]["jobNum"])
                paramPath = job_dictionary[jobKey]["stochtrackInputDir"] + "/" + "params.mat"
                vars_entries = [paramPath, jobNum]

                job_relationship[jobKey] = job_number
                # create job entry
                job_number, dag_string = create_dag_job(job_number, grand_stochtrack_sub_filename, vars_entries,
                                            argList, dag_string, restrictCat = gs_category)
        # write grandStochtrack category job restriction

        output_string += dag_string

        #with open(filename, "w") as outfile:
        #    outfile.write(dag_string)
        #return filename
        return job_relationship, job_number, output_string

# create preproc dag submission files
def create_preproc_dag(job_dictionary, preproc_executable, grand_stochtrack_executable, dag_dir, shell_path, quit_program, use_gpu = False, max_preproc_jobs = 20, max_gs_jobs = 100, job_order = None, job_group_preproc = None):
    if not quit_program:
        preproc_category = "PREPROC"
        gs_category = "GRANDSTOCKTRACK"
        # order jobs alphanumerically (this will also help with parent child relationships later)
        if not job_order:
            job_order = job_dictionary.keys()
            job_order.sort()
        # create preproc executable submit file
        preproc_sub_filename = write_sub_file("preproc", preproc_executable, dag_dir, "$(paramFile) $(jobFile) $(jobNum)", 2048)
        filename = dag_dir + "/preproc.dag"
        dag_string = ""
        job_number = 0
        job_tracker = []
        # create preproc jobs
        job_relationship_preproc, job_number, dag_string = write_preproc_jobs(job_number, job_dictionary,
                                                                 job_tracker, preproc_sub_filename, dag_string, preproc_category, job_order, job_group_preproc)
        # create grand stochtrack jobs
        job_relationship_gs, job_number, dag_string = create_grand_stochtrack_jobs(job_number, job_dictionary, grand_stochtrack_executable, dag_dir, dag_string, quit_program, use_gpu = use_gpu, job_order = job_order, gs_category = gs_category)

        # create grand stochtrack submission job
        #gs_dag_name_split_index = len(gs_dag_path) - gs_dag_path[::-1].find("/") - 1
        #gs_dag_name = gs_dag_path[gs_dag_name_split_index+1:]
        #gs_dag_directory = gs_dag_path[:gs_dag_name_split_index]
        #job_number, dag_string = create_external_dag_job(job_number, gs_dag_name, gs_dag_directory, dag_string)
        #end_job = job_number - 1
        #job_tracker += [[end_job, end_job]]
        # to add!
        print("add test job(s) to check if frame type exists")
        # create test jobs if searching frames
            # create job hierarchy
        print(dag_string)
        print(job_order)
        print(job_relationship_preproc)
        job_orderings = [[job_relationship_preproc[job],[job_relationship_gs[job]]] for job in job_order if job != "constants"]
        #job_orderings = [[[job_relationship_preproc[job]],[job_relationship_gs[job]]] for job in job_order if job != "constants"]
        dag_string = job_heirarchy_v2(job_orderings, dag_string)

        # write preproc job category restriction
        dag_string += "\nMAXJOBS " + preproc_category + " " + str(max_preproc_jobs)
        dag_string += "\nMAXJOBS " + gs_category + " " + str(max_gs_jobs)

        #dagfile.close()
        with open(filename, "w") as outfile:
            outfile.write(dag_string)
        return filename
