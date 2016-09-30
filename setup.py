import os
from shutil import copyfile

home_folder = os.path.expanduser("~")
default_config_directory = os.path.join(home_folder, ".pycondorstamp")
default_config_file_path = os.path.join(default_config_directory, "config.txt")
source_cofig_file_path = "default_config.txt"
pycondorstamp_dir = os.getcwd()

if not os.path.exists(default_config_directory):
    os.mkdir(default_config_directory)

if not os.path.exists(default_config_file_path):
    copyfile(source_cofig_file_path, default_config_file_path)

with open(default_config_file_path, "a") as outfile:
    outfile.write("pycondorstamp_dir = " + pycondorstamp_dir)
