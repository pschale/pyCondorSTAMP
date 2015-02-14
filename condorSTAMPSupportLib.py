import os

#
print("Make sure to finish updating the universe and local variables part.")

# Helper function to write condor sub file
def write_sub_file(filenameBase, executable, baseDir, args, requestMemory = None, getEnv = True):
    condor_sub_filename = baseDir + "/" + filenameBase + ".sub"
    #condor_sub_file = open(condor_sub_filename, "w")
    # Separate strings
    universe = "universe = vanilla"
    if getEnv:
        universe += "\ngetenv = True"
    if requestMemory:
        universe += "\nrequest_memory = " + str(requestMemory)
    executable_line = "executable = " + executable
    log = "log = " + baseDir + "/dagLogs/" + filenameBase + ".log"
    error = "error = " + baseDir + "/dagLogs/logs/" + filenameBase + ".err"
    output = "output = " + baseDir + "/dagLogs/logs/" + filenameBase + ".out"
    arguments = 'arguments ='
    if args:
        arguments += ' " ' + args + ' "'
    #if args:
    #    arguments = 'arguments = " ' + args + ' "'
    notifications = "notification = error"
    queue = "queue 1"
    string_list = [universe, executable_line, log, error, output, arguments,
                   notifications, queue]
    output_string = "\n".join(line for line in string_list)
    with open(condor_sub_filename, "w") as infile:
        infile.write(output_string)
    #condor_sub_file.write(output_string)
    #condor_sub_file.close()
    return condor_sub_filename

# create job
def create_dag_job(job_number, condor_sub_loc, vars_entries, arg_list, output_string, retry = 2):
    # create job entry strings
    jobNum = str(job_number)
    varEntries = [jobNum] + vars_entries
    argList = ["jobNumber"] + arg_list
    job_line = "JOB " + jobNum + " " + condor_sub_loc + "\n"
    retry_line = "RETRY " + jobNum + " " + str(int(retry)) + "\n"
    vars_line = "VARS " + jobNum
    for num in range(len(varEntries)):
        vars_line += ' ' + argList[num] + '="' + varEntries[num] + '"'
    vars_line += '\n\n'

    # enter string in dag file
    job_string = job_line + retry_line + vars_line
    output_string += job_string
    #output_string += "\n" + job_string
    # iterate job number
    job_number +=1

    return job_number, output_string

# Helper function to write preproc dag job entry
#def blrms_dag_job(job_number, condor_sub_loc, frame_list_dict, frame_list,
#                  conf_path, output_dir, file, test_interval = None):
def preproc_dag_job(job_number, jobKey, jobDictionary, condor_sub_loc, output_string):#output_dir, output_string)#, test_interval = None):
    # possible arguments
#    argList = ["confFile", "startTime", "endTime", "inlistFile", "outputDir"]
    argList = ["paramFile", "jobFile", "jobNum"]
    # create variable entry list
#    start = frame_list_dict[frame_list][0]
#    if not test_interval:
#        end = frame_list_dict[frame_list][1]
#    else:
#        end = str(int(start) + test_interval)
#    list_file_name = frame_list
    print(jobDictionary[jobKey].keys())
    jobPath = jobDictionary[jobKey]["grandStochtrackParams"]["params"]["jobsFile"]
    print(jobKey)
    print(jobDictionary[jobKey].keys())
    confPath = jobDictionary[jobKey]["preprocInputDir"] + "/preprocParams.txt"
    jobNum = str(jobDictionary[jobKey]["grandStochtrackParams"]["job"])
    vars_entries = [confPath, jobPath, jobNum]

    # create job entry
    job_number, output_string = create_dag_job(job_number, condor_sub_loc, vars_entries,
                                argList, output_string)

    return job_number, output_string

# Helper function to write list of preproc job entries
def write_preproc_jobs(job_number, jobDictionary, job_tracker, condor_sub_loc,
                     output_string):#, output_dir = None):
#    if output_dir:
#        test_job = True
#    else:
#        test_job = False
    start_job = job_number
    for jobKey in jobDictionary:
        #conf_path = conf_file_dict[base_conf_name]["config file path"]
        # create handle to handle frame files
        #frame_list_dict = conf_file_dict[base_conf_name]["frame file lists"]
        # determine if test jobs
        #if not test_job:
            # get output directory
            #output_dir = conf_file_dict[base_conf_name]["frame directory"]
            # run through frame lists
            #for frame_list in frame_list_dict:
#                job_number, output_string = preproc_dag_job(job_number, condor_sub_loc,
 #                                          frame_list_dict, frame_list,
  #                                         conf_path, output_dir, output_string)
        if jobKey != "constants":
            job_number, output_string = preproc_dag_job(job_number, jobKey, jobDictionary, condor_sub_loc, output_string)
#                                    preproc_dag_job(job_number, condor_sub_loc,
 #                                          frame_list_dict, frame_list,
  #                                         conf_path, output_dir, output_string)
#        else:
            # grab any entry for test job
 #           frame_list = list(frame_list_dict.keys())[0]
            # determine test job length
  #          test_interval = 60
            # write test job
   #         job_number = blrms_dag_job(job_number, condor_sub_loc,
    #                                   frame_list_dict, frame_list, conf_path,
     #                                  output_dir, file, test_interval)
    end_job = job_number - 1
    # record range of job numbers just written
    job_tracker += [[start_job, end_job]]
    return job_tracker, job_number, output_string

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

# Create shell script to allow dag to execute python analysis code
def create_dag_shell_script(dag_dir, shell_path, new_dag, quit_program, max_jobs = 100):
    if not quit_program:
        filename = dag_dir + "/grand_stochtrackDagSubmit.sh"
        max_jobs = str(max_jobs)
        with open(filename, 'w') as outfile:
            # find bash path - can automate this later, maybe manual for now
            outfile.write(shell_path + "\n\n")
            outfile.write("condor_submit_dag -maxjobs " + max_jobs + " " + new_dag)
        os.chmod(filename, 0764)
        return filename

# create dag submission files
# create dag submission files
def create_grand_stochtrack_dag(job_dictionary, grand_stochtrack_executable, dag_dir, quit_program):
    if not quit_program:
        # create grand_stochtrack executable submit file
        grand_stochtrack_sub_filename = write_sub_file("grand_stochtrack", grand_stochtrack_executable, dag_dir, "$(paramPath) $(jobNum)")
        # create dag file
        filename = dag_dir + "/grand_stochtrack.dag"
        dag_string = ""
        job_number = 0
        # create grand_stochtrack jobs
        for jobKey in job_dictionary:
            if jobKey != "constants":
                argList = ["paramPath", "jobNum"]
                jobNum = str(job_dictionary[jobKey]["grandStochtrackParams"]["job"])
                paramPath = job_dictionary[jobKey]["stochtrackInputDir"] + "/" + "params.mat"
                vars_entries = [paramPath, jobNum]

                # create job entry
                job_number, dag_string = create_dag_job(job_number, grand_stochtrack_sub_filename, vars_entries,
                                            argList, dag_string)

        with open(filename, "w") as outfile:
            outfile.write(dag_string)
        return filename

def create_preproc_dag(job_dictionary, preproc_executable, grand_stochtrack_executable, dag_dir, shell_path, quit_program):
    if not quit_program:
        # create preproc executable submit file
        preproc_sub_filename = write_sub_file("preproc", preproc_executable, dag_dir, "$(paramFile) $(jobFile) $(jobNum)", 2048)
#        args = "-conf $(confFile) -start $(startTime) -end $(endTime) -inlist \
#$(inlistFile) -dir $(outputDir)"
#        blrms_sub_filename = write_sub_file("blrmsExc", blrmsExc,
#                                            support_dir, args)
        # create condor shell script that executes python plot analysis submit file
        #shell_arg = "-file $(pickledFile) -dir $(outputDir)"
        # create shell executable to execute grand_stochtrack dag
        gs_dag_path = create_grand_stochtrack_dag(job_dictionary, grand_stochtrack_executable, dag_dir, quit_program)
        dag_shell_script = create_dag_shell_script(dag_dir, shell_path, gs_dag_path, quit_program)
        shell_arg = None
        shell_sub_name = write_sub_file("grand_stochtrack_dag_shell", dag_shell_script,
                                             dag_dir, shell_arg)
        # create dag file
        filename = dag_dir + "/preproc.dag"
        #dagfile = open(filename, "w")
        dag_string = ""
        job_number = 0
        job_tracker = []
        # create preproc jobs
        job_tracker, job_number, dag_string = write_preproc_jobs(job_number, job_dictionary,
                                                                 job_tracker, preproc_sub_filename, dag_string)
        # create grand stochtrack submission job
        job_number, dag_string = create_dag_job(job_number, shell_sub_name, [], [], dag_string)
        end_job = job_number - 1
        job_tracker += [[end_job, end_job]]
            # create test blrms jobs
#        job_tracker, job_number, dag_string = write_preproc_jobs(job_number, config_file_dict,
 #                                      job_tracker, blrms_sub_filename, dagfile,
  #                                     support_dir)
            # create rest of jobs
   #     job_tracker, job_number = write_blrms_jobs(job_number, config_file_dict,
    #                                   job_tracker, blrms_sub_filename, dagfile)
            # create shell executable with pickled object input

 #       job_tracker, job_number = write_analysis_dag_job(job_number,
  #                                                       job_tracker,
   #                                                      python_sub_filename,
    #                                                     dagfile)

#        job_tracker, job_number = write_analysis_dag_job(job_number,
#                                                         pickled_conf_name,
#                                                         job_tracker,
#                                                         python_sub_filename,
#                                                         dagfile, plot_dir)
            # create job hierarchy
        print(dag_string)
        dag_string = job_heirarchy(job_tracker, dag_string)

        #dagfile.close()
        with open(filename, "w") as outfile:
            outfile.write(dag_string)
        return filename
