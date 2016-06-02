The files in this folder can be used to create a config file that is then used in pyCondorSTAMPanteproc_v4.
In order to use this, first update the file paths (this section starts at line 86).  A job file is required for all searches,
and should be found within a folder named for the search type (eg "offsource") - which is itself in a folder named on line 86 - 
and named "sgr_trigger_" + number + "_" + search type + "_jobs.txt". 

Next, the specific search needs to be configured.  Currently the code is set up to do an offsource search, but can easily be set to
onsource (as long as an onsource job file is given), pseudo onsource, or upper limits with injections, though additional tinkering may be required.

Additionally, the default config file currently attempts to use GPUs. This can be changed by editing that one line; nothing else is required.

Paul Schale
pschale@uoregon.edu 
