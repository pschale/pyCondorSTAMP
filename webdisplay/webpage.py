import os
from shutil import copy2
from optparse import OptionParser

home_folder = os.path.expanduser("~")
default_config_filepath = os.path.join(home_folder, ".pycondorstamp", 
                                        "config.txt")
webfile_subdir = "webdisplay"
webfiles = ["plot_results.html", "simple_ajax.js", "table_builder.js", 
                    "table_interact.js"]

def copy_webfiles(target_directory, pycondorstamp_dir):
    for filename in webfiles:
        filepath = os.path.join(pycondorstamp_dir, webfile_subdir, filename)
        copy2(filepath, target_directory)

def read_config_file(config_filepath):
    with open(config_filepath, "r") as infile:
        temp_list = [[x.strip() for x in line.split("=")] for line in infile]
        config = {line[0]: line[1] for line in temp_list}
    return config
    
def load_pycondorstamp_dir():

    return read_config_file(default_config_filepath)["pycondorstamp_dir"]

    
def load_conf_cp_webfiles(target_dir):
    pycondorstamp_dir = load_pycondorstamp_dir()
    copy_webfiles(target_dir, pycondorstamp_dir)

def main():
    parser = OptionParser()

    parser.add_option("-d", "--dir", dest = "targetDirectory",
           help = "Path to directory to create webpage to display results.",
           metavar = "DIRECTORY")

    (options, args) = parser.parse_args()

    displaydir = options.targetDirectory

    load_conf_cp_webfiles(displaydir)

if __name__ == "__main__":
    main()
