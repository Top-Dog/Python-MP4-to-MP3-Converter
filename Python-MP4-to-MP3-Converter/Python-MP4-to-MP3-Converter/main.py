# Script to convert MP4 files to MP3 files, and clean-up metadata
# Run this script from the same directory as the target MP4 files
# A new folder called "MP3s" will be created with the output files
# Requires ffmeg for the conversion and python audio tools for the metadata

import os
from subprocess import Popen, PIPE, call

FFMPEG_BIN = "C:\Apps\ffmpeg-win64-static\bin\ffmpeg.exe" # Absoulate path to the exectuable

def check_file_exists(directory, filename, extension):
    abspath = directory + "/" + filename + extension
    return os.path.isfile(abspath)

def check_folder_exsists(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def mp4_to_mp3(directory, fileName):
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
    #pipe = Popen(command, stdout=PIPE, bufsize=10**8)
    #pipe.stdout.close()
    #print pipe.wait()
    #call(["ffmpeg", "-i", "Rootbeer - Under Control.mp4", "-f", "mp3", "-ab", "192000", "-vn", "out.mp3"])
    call(["ffmpeg"])

def main():
    directory = "C:\Users\Sean O'Connor\Downloads\MP4 test"
    fileName = "Rootbeer - Under Control"
    check_folder_exsists(directory + "\MP3s")
    mp4_to_mp3(directory, fileName)

if __name__ == "__main__":
    main()