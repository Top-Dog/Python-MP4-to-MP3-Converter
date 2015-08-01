# Script to convert MP4 files to MP3 files, and clean-up metadata
# Run this script from the same directory as the target MP4 files
# A new folder called "MP3s" will be created with the output files
# Requires ffmeg for the conversion and python audio tools for the metadata

import os
from subprocess import Popen, PIPE

def check_file_exists(directory, filename, extension):
    abspath = directory + "/" + filename + extension
    return os.path.isfile(abspath)

def main():
    pass

if __name__ == "__main__":
    main()