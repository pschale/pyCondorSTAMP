import os

#condensed by Paul Schale
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
    accounting_tag = "accounting_group = ligo.dev.s6.burst.sgr_qpo.stamp"
    queue = "queue 1"
    string_list = [universe, executable_line, log, error, output, arguments,
                   notifications, accounting_tag, queue]
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
    if retry:
        retry_line = "RETRY " + jobNum + " " + str(int(retry)) + "\n"
    else:
        retry_line = ""
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
def preproc_dag_job(job_number, jobKey, jobDictionary, condor_sub_loc, output_string, preproc_category = None, preprocInputDir = None, no_job_retry = False):#output_dir, output_string)#, test_interval = None):
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
        if no_job_retry:
            job_number, output_string = create_dag_job(job_number, condor_sub_loc, vars_entries, argList, output_string, restrictCat = preproc_category, retry = None)
        else:
            job_number, output_string = create_dag_job(job_number, condor_sub_loc, vars_entries, argList, output_string, restrictCat = preproc_category)

    return job_number, output_string

# Helper function to write list of preproc job entries
def write_preproc_jobs(job_number, jobDictionary, job_tracker, condor_sub_loc, output_string, preproc_category = None, job_order = None, job_group_preproc = None, no_job_retry = False):
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
                job_ID = str(job_tracker[jobKey][0]) + " " + str(job_tracker[jobKey][1])
                if job_ID not in created_jobs:#job_tracker[jobKey][1] not in created_jobs:
                    temp_job_group = job_tracker[jobKey][0]
                    temp_preproc_job = job_tracker[jobKey][1]
                    #print(job_group_preproc)
                    #print(job_group_preproc[temp_job_group][temp_preproc_job])
                    #print(temp_job_group)
                    #print(temp_preproc_job)
                    preprocInputDir = job_group_preproc[temp_job_group][temp_preproc_job]["preprocInputDir"]
                    job_number, output_string = preproc_dag_job(job_number, jobKey, jobDictionary, condor_sub_loc, output_string, preproc_category, preprocInputDir, no_job_retry = no_job_retry)
                    #created_jobs[job_tracker[jobKey][1]] = range(start_job, job_number)
                    created_jobs[job_ID] = range(start_job, job_number)
                job_relationship[jobKey] = created_jobs[job_ID]
            else:
                job_number, output_string = preproc_dag_job(job_number, jobKey, jobDictionary, condor_sub_loc, output_string, preproc_category)
                job_relationship[jobKey] = range(start_job, job_number)
    # record range of job numbers just written
    return job_relationship, job_number, output_string

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
    #print(job_relation_pair_lists) # debug
    for pair_list in job_relation_pair_lists:
        parent = "PARENT "
        child = "CHILD "
        parent += " ".join(str(x) for x in pair_list[0])
        child += " ".join(str(x) for x in pair_list[1])
        output_string += parent + " " + child + "\n\n"
        #list_of_orderings.append(order_string)
    #output_string = "\n\n".join(string for string in list_of_orderings)
    return output_string

# Helper function to enter job hierarchy in dagfile
def job_heirarchy_from_listing(pre_listing, post_listing, output_string):
    # [[pre1,pre2...],[post1,post2...],[pre1_2,pre2_2...],[post1_2,post2_2]]
    #list_of_orderings = []
    output_string += "\n\n"
    output_string += "PARENT " + " ".join(str(x) for x in pre_listing)
    output_string += " CHILD " + " ".join(str(x) for x in post_listing)
    output_string += "\n\n"
    return output_string

# create grandstochtrack jobs
def create_matlab_mat_file_extraction_jobs(job_number, job_dictionary, matlab_matrix_extraction_executable, dag_dir, output_string, job_order = None, matrix_extraction_category = None, no_job_retry = False):
    # create grand_stochtrack executable submit file
    #memory = "1000"
    additional_inputs = ["request_gpus = 1"]
    extraction_sub_filename = write_sub_file("matlab_matrix_extraction", matlab_matrix_extraction_executable, dag_dir, "$(inputFileName) $(outputDir)", additional_requirements_list = additional_inputs)#, memory)
    dag_string = ""
    #job_number = 0
    job_relationship = {}
    # create grand_stochtrack jobs
    for jobKey in job_order:
        if jobKey != "constants":
            argList = ["inputFileName", "outputDir"]
            jobNum = str(job_dictionary[jobKey]["jobNum"])
            outputDir = job_dictionary[jobKey]["grandstochtrackOutputDir"]
            inputFileName = outputDir + "/" + "bknd_" + jobNum + ".mat"
            vars_entries = [inputFileName, outputDir]

            job_relationship[jobKey] = [job_number]
            # create job entry
            if no_job_retry:
                job_number, dag_string = create_dag_job(job_number, extraction_sub_filename, vars_entries,
                                        argList, dag_string, restrictCat = matrix_extraction_category, retry = None)
            else:
                job_number, dag_string = create_dag_job(job_number, extraction_sub_filename, vars_entries,
                                        argList, dag_string, restrictCat = matrix_extraction_category)

    output_string += dag_string
    return job_relationship, job_number, output_string

# create preproc dag submission files
def write_grandstochtrack_bash_script(file_name, executable, STAMP_export_script, memory_limit = 14000000):
    output_string = """#!/bin/bash

source """ + STAMP_export_script + """

ulimit -v """ + str(memory_limit) + """

""" + executable + """ $1 $2"""
    with open(file_name, "w") as outfile:
        outfile.write(output_string)

def write_anteproc_bash_script(file_name, executable, STAMP_export_script, memory_limit = 14000000):
    output_string = """#!/bin/bash

source """ + STAMP_export_script + """

ulimit -v """ + str(memory_limit) + """

""" + executable + """ $1 $2 $3"""
    with open(file_name, "w") as outfile:
        outfile.write(output_string)


# create grandstochtrack jobs
def create_anteproc_jobs_v4(job_number, condor_sub_loc, post_processing_job_file, H1_job_numbers, L1_job_numbers, anteproc_filename_dictionary, dag_dir, output_string, anteproc_category = None, no_job_retry = False):
    # create grand_stochtrack executable submit file
    dag_string = ""
    #job_number = 0
    job_listings = []
    # create jobs for H1
    for job in set(H1_job_numbers):
        for anteproc_H_filename in anteproc_filename_dictionary["H1"][job]:
            job_listings += [job_number]
            vars_entries = [anteproc_H_filename, post_processing_job_file, str(job)]
            argList = ["paramFile", "jobFile", "jobNum"]
            if no_job_retry:
                job_number, dag_string = create_dag_job(job_number, condor_sub_loc, vars_entries,
                                                        argList, dag_string, restrictCat = anteproc_category, retry = None)
            else:
                job_number, dag_string = create_dag_job(job_number, condor_sub_loc, vars_entries,
                                                        argList, dag_string, restrictCat = anteproc_category)
    # create jobs for L1
    for job in set(L1_job_numbers):
        for anteproc_L_filename in anteproc_filename_dictionary["L1"][job]:
            job_listings += [job_number]
            vars_entries = [anteproc_L_filename, post_processing_job_file, str(job)]
            argList = ["paramFile", "jobFile", "jobNum"]
            if no_job_retry:
                job_number, dag_string = create_dag_job(job_number, condor_sub_loc, vars_entries,
                                                        argList, dag_string, restrictCat = anteproc_category, retry = None)
            else:
                job_number, dag_string = create_dag_job(job_number, condor_sub_loc, vars_entries,
                                                        argList, dag_string, restrictCat = anteproc_category)

    output_string += dag_string
    return job_listings, job_number, output_string

# create grandstochtrack jobs
def create_grand_stochtrack_jobs_v2(job_number, job_dictionary, grand_stochtrack_executable, dag_dir, output_string, use_gpu = False, restrict_cpus = False, job_order = None, gs_category = None, no_job_retry = False, single_cpu = False):
    # create grand_stochtrack executable submit file
    if type(use_gpu) == str:
        if use_gpu.lower() == "true":
            print("Using GPUs for clustermap.")
            use_gpu = True
        else:
            print("doGPU set to '" + use_gpu + "'. Using CPUs for clustermap.")
            use_gpu = False
    if single_cpu:
        additional_inputs = None
        memory = "4000"
    elif use_gpu:
        additional_inputs = ["request_gpus = 1"]
        memory = "4000"
    elif restrict_cpus:
        print("Restricted cpu option selected. Using 4 cpus.")
        additional_inputs = ["request_cpus = 4"]
        memory = "8000"
    else:
        additional_inputs = ["request_cpus = 8"]
        memory = "8000"
    grand_stochtrack_sub_filename = write_sub_file("grand_stochtrack", grand_stochtrack_executable, dag_dir, "$(paramPath) $(jobNum)", memory, additional_inputs)
    dag_string = ""
    #job_number = 0
    job_relationship = {}
    # create grand_stochtrack jobs
    for jobKey in job_order:
        if jobKey != "constants":
            argList = ["paramPath", "jobNum"]
            jobNum = str(job_dictionary[jobKey]["jobNum"])
            num_variations = len(job_dictionary[jobKey]["stochtrackInputDir"])
            job_relationship[jobKey] = []
            for temp_index in range(num_variations):
                paramPath = job_dictionary[jobKey]["stochtrackInputDir"][temp_index] + "/" + "params.mat"
                vars_entries = [paramPath, jobNum]

                job_relationship[jobKey] += [job_number]
                # create job entry
                if no_job_retry:
                    job_number, dag_string = create_dag_job(job_number, grand_stochtrack_sub_filename, vars_entries,
                                            argList, dag_string, restrictCat = gs_category, retry = None)
                else:
                    job_number, dag_string = create_dag_job(job_number, grand_stochtrack_sub_filename, vars_entries,
                                            argList, dag_string, restrictCat = gs_category)

    output_string += dag_string
    return job_relationship, job_number, output_string

# create preproc dag submission files
def create_anteproc_dag_v6(job_dictionary, grand_stochtrack_executable, matlab_matrix_extraction_executable, anteproc_executable, dag_dir, post_processing_job_file, H1_job_numbers, L1_job_numbers, anteproc_filename_dictionary, multiple_job_group_version, use_gpu = False, restrict_cpus = False, max_anteproc_jobs = 20, max_gs_jobs = 100, max_extract_jobs = 100, job_order = None, no_job_retry = False, extract_from_gpu = False, single_cpu = False):
    anteproc_category = "ANTEPROC"
    gs_category = "GRANDSTOCKTRACK"
    matrix_extraction_category = "GPUARRAY_TO_ARRAY"
    dag_string = ""
    job_number = 0
    job_tracker = []
    
    
    # order jobs alphanumerically (this will also help with parent child relationships later)
    if not job_order:
        job_order = job_dictionary.keys()
        job_order.sort()
    # create anteroc submit file and jobs
    anteproc_sub_filename = write_sub_file("anteproc", anteproc_executable, dag_dir, "$(paramFile) $(jobFile) $(jobNum)", 2048)
    anteproc_job_listing, job_number, dag_string = create_anteproc_jobs_v4(job_number, anteproc_sub_filename, post_processing_job_file, H1_job_numbers, L1_job_numbers, anteproc_filename_dictionary, dag_dir, dag_string, anteproc_category = anteproc_category, no_job_retry = no_job_retry)

    # create grand stochtrack jobs
    job_relationship_gs, job_number, dag_string = create_grand_stochtrack_jobs_v2(job_number, job_dictionary, grand_stochtrack_executable, dag_dir, dag_string, use_gpu = use_gpu, restrict_cpus = restrict_cpus, job_order = job_order, gs_category = gs_category, no_job_retry = no_job_retry, single_cpu = single_cpu)
    gs_job_listing = [x for key in job_relationship_gs for x in job_relationship_gs[key]]
    gs_job_listing.sort()
    # create matrix extraction jobs
    if extract_from_gpu:
        job_relationship_extraction, job_number, dag_string = create_matlab_mat_file_extraction_jobs(job_number, job_dictionary, matlab_matrix_extraction_executable, dag_dir, dag_string, job_order = job_order, matrix_extraction_category = matrix_extraction_category, no_job_retry = no_job_retry)

    # to add!
    print("add test job(s) to check if frame type exists")
    # create test jobs if searching frames
        # create job hierarchy

    job_orderings = []
    if extract_from_gpu:
        job_orderings += [[job_relationship_gs[job],job_relationship_extraction[job]] for job in job_order if job != "constants"]

    dag_string =  job_heirarchy_from_listing(anteproc_job_listing, gs_job_listing, dag_string)
    dag_string = job_heirarchy_v2(job_orderings, dag_string)

    # write preproc job category restriction
    dag_string += "\nMAXJOBS " + anteproc_category + " " + str(max_anteproc_jobs)
    dag_string += "\nMAXJOBS " + gs_category + " " + str(max_gs_jobs)
    if extract_from_gpu:
        dag_string += "\nMAXJOBS " + matrix_extraction_category + " " + str(max_extract_jobs)
        
    filename = dag_dir + "/stampAnalysis.dag"
    
    with open(filename, "w") as outfile:
        outfile.write(dag_string)
    return filename
    
def write_anteproc_sub_file(memory, anteprocSH, dagDir, accountingGroup):

    contents = "universe = vanilla\ngetenv = True\nrequest_memory = " + str(memory) + "\n"
    contents += "executable = " + anteprocSH + "\n"
    contents += "log = " + dagDir + "/dagLogs/anteproc$(jobNumber).log\n"
    contents += "error = " + dagDir + "/dagLogs/logs/anteproc$(jobNumber).err\n"
    contents += "output = " + dagDir + "/dagLogs/logs/anteproc$(jobNumber).out\n"
    contents += '''arguments = " $(paramFile) $(jobFile) $(jobNum) "\n'''
    contents += "notification = error\n"
    contents += "accounting_group = " + accountingGroup + "\n"
    contents += "queue 1"
    
    with open(dagDir + "/anteproc.sub", "w") as h:
        print >> h, contents
        
    return dagDir + "/anteproc.sub"
        
def write_stochtrack_sub_file(memory, grandStochtrackSH, dagDir, accountingGroup, doGPU, numCPU):

    if doGPU:
        memory = 4000
    contents = "universe = vanilla\ngetenv = True\nrequest_memory = " + str(memory) + "\n"
    if doGPU:
        contents += "request_gpus = 1"
    elif numCPU > 1:
        contents += "request_cpus = " + str(numCPU)
    contents += "executable = " + grandStochtrackSH + "\n"
    contents += "log = " + dagDir + "/dagLogs/grand_stochtrack$(jobNumber).log\n"
    contents += "error = " + dagDir + "/dagLogs/logs/grand_stochtrack$(jobNumber).err\n"
    contents += "output = " + dagDir + "/dagLogs/logs/grand_stochtrack$(jobNumber).out\n"
    contents += '''arguments = " $(paramPath) $(jobNum) "\n'''
    contents += "notification = error\n"
    contents += "accounting_group = " + accountingGroup + "\n"
    contents += "queue 1"
    
    with open(dagDir + "/grand_stochtrack.sub", "w") as h:
        print >> h, contents
    
    return dagDir + "/grand_stochtrack.sub"
    
def write_dag(dagDir, anteprocDir, jobFile, H1AnteprocJobNums, L1AnteprocJobNums, anteprocSub, stochtrackParamsList, stochtrackSub, maxJobsAnteproc, maxJobsGrandStochtrack):

    output = ""
    jobCounter = 0
    for jobNum in H1AnteprocJobNums:
        
        output += "JOB " + str(jobCounter) + " " + anteprocSub + "\nRETRY " + str(jobCounter) + " 2\n"
        output += "VARS " + str(jobCounter) + "jobNumber=\"" + str(jobCounter) + "\" \"paramFile=" + anteprocDir + "/H1-anteproc_params_" + str(jobNum) + ".txt\"\n"
        output += "jobFile=\"" + jobFile + "\" jobNum=\"" + str(jobNum) + "\"\n"
        output += "CATEGORY " + str(jobCounter) + " ANTEPROC\n\n"
        jobCounter += 1
        
    for jobNum in L1AnteprocJobNums:
        
        output += "JOB " + str(jobCounter) + " " + anteprocExecutable + "\nRETRY " + str(jobCounter) + " 2\n"
        output += "VARS " + str(jobCounter) + "jobNumber=\"" + str(jobCounter) + "\" \"paramFile=" + anteprocDir + "/H1-anteproc_params_" + str(jobNum) + ".txt\"\n"
        output += "jobFile=\"" + jobFile + "\" jobNum=\"" + str(jobNum) + "\"\n"
        output += "CATEGORY " + str(jobCounter) + " ANTEPROC\n\n"
        jobCounter += 1
    
    cutoff = jobCounter
        
    for jobDict in stochtrackParamsList:
    
        output += "JOB " + str(jobCounter) + " " + stochtrackSub + "\nRETRY " + str(jobCounter) + " 2\n"
        output += "VARS " + str(jobCounter) + "jobNumber=\"" + str(jobCounter) + "\" \"paramPath=" + jobDict["stochtrackInputDir"] + "/params_new.mat"
        output += "jobNum=\"" + str(jobDict['grandStochtrackParams']['params']['jobNumber']) + "\"\n"
        output += "CATEGORY " + str(jobCounter) + " GRANDSTOCHTRACK\n\n"
        jobCounter += 1
        
    output += "\n\n"
    
    output += "PARENT " + " ".join([str(i) for i in range(0, cutoff)])
    output += " CHILD " + " ".join([str(i) for i in range(cutoff, jobCounter)])
    
    output += "\n\n\n\n\n\n"
    
    output += "MAXJOBS ANTEPROC " + str(maxJobsAnteproc) + "\n"
    output += "MAXJOBS GRANDSTOCHTRACK " + str(maxJobsGrandStochtrack)
    
    with open(dagDir + "/stampAnalysis.dag", "w") as h:
        print >> h, output        
    
 
  
