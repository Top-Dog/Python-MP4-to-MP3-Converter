# Script to convert MP4 files to MP3 files, and clean-up metadata
# Run this script from the same directory as the target MP4 files
# A new folder called "MP3s" will be created with the output files
# Requires ffmeg for the conversion and python audio tools for the metadata

# References:
# http://zulko.github.io/blog/2013/10/04/read-and-write-audio-files-in-python-using-ffmpeg/
# https://gist.github.com/thinkski/3976945
# https://acoustid.org/server
# http://www.randombytes.org/audio_comparison.html

import os, threading, time, sys
from subprocess import Popen, PIPE, call

FFMPEG_BIN = "ffmpeg.exe" # The exectuable, make sure to add the bin directory to the path (if using Linux remove the '.exe')


def check_file_exists(directory, filename, extension):
    '''Check a particular exsists, returns true if it does'''
    abspath = directory + "/" + filename + extension
    return os.path.isfile(abspath)

def check_folder_exsists(directory):
    '''Check that the output dir exsists and is writable'''
    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.access(directory, os.W_OK):
        exit("Error: directory \'" + directory + "\' is not writeable.")
    print("Folder structure OK")

def get_all(filetype=".mp4", ignoredir="MP3s"):
    '''Reccsively get all the files from the dir
    The first loop prints all the subdirs in the current folder
    The second loop prints all the files in current dir
    The outside loop moves into each subdir, and the sub-subdirs..
    when it's done returns to the root dir and moves onto the next subdir'''
    # Proudly lifted from: http://stackoverflow.com/questions/120656/directory-listing-in-python

    for dirname, dirnames, filenames in os.walk('.'):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            print(os.path.join(dirname, subdirname))

        # print path to all filenames.
        for filename in filenames:
            print(os.path.join(dirname, filename))

        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if ignoredir in dirnames:
            # don't go into the output directory
            dirnames.remove(ignoredir)

def get_file_list(directory, outdir):
    '''Create a list of mp4 files for conversion, excluding ones already in the output dir'''
    # Get the list of MP4s in the current dir
    mp4setwithext = {file for file in os.listdir(directory) if file.endswith(".mp4")}
    mp4setwithext = {file for file in os.listdir(directory) if file.endswith(".mp4")}
    (root, ext) = os.path.splitext(fileurl)
    #mp4dic = dict.fromkeys(range(len(os.listdir(directory))), filelist)

    # Get a list of MP3s in the output dir
    mp3set = {file for file in os.listdir(directory + outdir) if file.endswith(".mp3")}
    #mp3dic = dict.fromkeys(range(len(os.listdir(directory + outdir))), filelist)

    # Set diffrence = tracks still to convert
    return (mp4set - mp3set)


def mp4_to_mp3(directory, fileName):
    '''A worker thread'''
    # -ab means the mp3 is encoded at 192Kbps
    # -vn means no video
    # -f means an mp3 container
    # -b:a 192K, -q:a (variable bit rate)
    # The - at the end tells FFMPEG that it is being used with a pipe by another program
    #command = "ffmpeg -i %s.mp4 -f mp3 -ab 192000 -vn %s.mp3" % (fileName, fileName)
    command = [FFMPEG_BIN,
               "-i", directory + "\\" + fileName + ".mp4",
               "-f", "mp3",
               "-ab", "192000",
               '-ar', '44100', # ouput will have 44100 Hz
               '-ac', '2', # stereo (set to '1' for mono)
               "-vn", directory + "\\MP3s\\" + fileName + ".mp3"]   

    # Do the conversion from mp4 to mp3
    # call(command)
    pipe = Popen(command, stdout=PIPE, bufsize=10**8)
    pipe.stdout.close()
    print(pipe.wait())

    # Print the files information
    print("Converting: %s" % (fileName))
    sys.stdout.flush()

# Create a thread lock, for access to stdout - not used atm
tLock = threading.Lock()

def main():
    # Create an array of threads
    threads = []

    directory = r"C:\Users\Sean O'Connor\Downloads\MP4 test"
    testfileName = r"Rootbeer - Under Control"
    check_folder_exsists(directory + "\\MP3s")
    #mp4_to_mp3(directory, testfileName)
    filelist = [testfileName]

    for filename in filelist:
        thread = threading.Thread(target=mp4_to_mp3, args=(directory, filename))
        threads += [thread]
        thread.start()

    for xthread in threads:
        xthread.join()
    
    print("Main Completed!")

if __name__ == "__main__":
    main()
