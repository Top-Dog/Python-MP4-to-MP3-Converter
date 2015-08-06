# Script to convert MP4 files to MP3 files, and clean-up metadata
# Run this script from the same directory as the target MP4 files
# A new folder called "MP3s" will be created with the output files
# Requires ffmeg for the conversion and python audio tools for the metadata

# References:
# http://zulko.github.io/blog/2013/10/04/read-and-write-audio-files-in-python-using-ffmpeg/
# https://gist.github.com/thinkski/3976945
# https://acoustid.org/server
# http://www.randombytes.org/audio_comparison.html
# http://stackoverflow.com/questions/120656/directory-listing-in-python

import os, threading, time, sys, queue
from subprocess import Popen, PIPE, call

FFMPEG_BIN = "ffmpeg.exe" # The exectuable, make sure to add the bin directory to the path (if using Linux remove the '.exe')

MAX_NUM_OF_WORKER_THREADS = 2
q_mp4s_to_convert = queue.Queue(maxsize=0) # All the names of exsiting mp4 files in the root dir that need to be converted
q_created_mp3s = queue.Queue(maxsize=0) # All the names of created mp3 files (for printing)


def check_file_exists(directory, filename, extension):
    '''Check a particular exsists, returns true if it does'''
    abspath = directory + "/" + filename + extension
    return os.path.isfile(abspath)

def check_create_folder_exsists(directory):
    '''Check that the output dir exists and is writable'''
    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        userinput = ""
        #while bool(userinput != "y") != bool(userinput != "n"):
        userinput = input("Directory \'" + directory + "\' already exists, overwrite it? (y/n) ")
        if userinput == "n":
            sys.exit()
    if not os.access(directory, os.W_OK):
        print("Error: directory \'" + directory + "\' is not writeable.")
        time.sleep(5)
        sys.exit()
    
def remove_dir(directory):
    '''Removes a dir, only if it is empty'''
    try:
        os.rmdir(directory)
    except:
        print("Error: please remove " + directory + " manually")
        time.sleep(5)
        sys.exit()

def convert_queue(myqueue):
    '''Convert a queue to a set'''
    outset = set()
    for i in range(myqueue.qsize()):
        outset.add(myqueue.get())
    return outset

def add_to_queue(myqueue, filename, filetypes):
    '''Populate a list with all the files with extensions in the filetypes array (empty=all)'''
    (fname, fext) = os.path.splitext(filename)
    for filetype in filetypes:
        if fext == filetype:
            myqueue.put(fname) #append to a global list of known MP3s
    # Return all the files if no filetype is defined
    if len(filetypes) == 0:
        myqueue.put(fname)

def add_to_set(myset, filename, filetypes):
    (fname, fext) = os.path.splitext(filename)
    for filetype in filetypes:
        if fext == filetype:
            myset.add(fname) #append to a global list of known MP3s
    # Return all the files if no filetype is defined
    if len(filetypes) == 0:
        myset.add(fname)
    
def worker(rootdir):
    '''Function to run the mp4 to mp3 task'''
    timeout = 8 # seconds
    while True:
        try:
            mp4name = q_mp4s_to_convert.get(True, timeout) # blocks if there is nothing to get
        except:
            print("Worker timedout")
            return
        q_created_mp3s.put(mp4_to_mp3(rootdir, mp4name)) 
        q_mp4s_to_convert.task_done() # signal that a queued task is completed (oppisite to q.get())
        time.sleep(0.01)
        

def traverse_files(funchandle, myset, searchdir='.', filetypes=[".mp4"], ignoredirs=["MP3s"]):
    '''Reccsively get all the files from the root dir of a particular type (empty =all)
    The first loop prints all the subdirs in the current folder
    The second loop prints all the files in current dir
    The outside loop moves into each subdir, and the sub-subdirs..
    when it's done returns to the root dir and moves onto the next subdir'''
    for dirname, dirnames, filenames in os.walk(searchdir):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            #print(os.path.join(dirname, subdirname))
            pass

        # print path to all filenames.
        for filename in filenames:
            #print(os.path.join(dirname, filename))
            # Call the helper function to do something with the filename
            funchandle(myset, filename, filetypes)

        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        for ignoredir in ignoredirs:
            if ignoredir in dirnames:
                # don't go into the output directory
                dirnames.remove(ignoredir)

def get_file_list(directory, outdir):
    '''Create a list of mp4 files for conversion, excluding ones already in the output dir (outdir)'''
    # doesn't look like this function is needed anymore, surpassed by handels in "get_all_files"
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
    '''A worker thread for converting a mp4 file to mp3 
    actually do work in this thread'''
    # -ab means the mp3 is encoded at 192Kbps
    # -vn means no video
    # -f means an mp3 container
    # -b:a 192K, -q:a (variable bit rate)
    # The - at the end tells FFMPEG that it is being used with a pipe by another program
    #command = "ffmpeg -i %s.mp4 -f mp3 -ab 192000 -vn %s.mp3" % (fileName, fileName)
    command = [FFMPEG_BIN,
               "-loglevel", "0", # lower ffmeg's verbosity
               "-i", directory + "\\" + fileName + ".mp4",
               "-f", "mp3",
               "-ab", "192000",
               '-ar', '44100', # output will have 44100 Hz
               '-ac', '2', # stereo (set to '1' for mono)
               "-vn", directory + "\\MP3s\\" + fileName + ".mp3"]
    
    # Block stdout from showing debug and progress info
    #sys.stdout = open(os.devnull, "w")
    
    # Do the conversion from mp4 to mp3
    call(command)
    #pipe = Popen(command, stdout=PIPE, bufsize=10**8)
    #pipe.stdout.close()
    #print(pipe.wait())

    # Renable stout
    ##sys.stdout.flush()
    #sys.stdout = sys.__stdout__
    
    return "Successfully converted '%s' to mp3!" % (fileName)

# Create a thread lock, for access to stdout - not used atm
tLock = threading.Lock()

def printer():
    print("Printer started")
    timeout = 8 # seconds
    while True:
        try:
            print(q_created_mp3s.get(True, timeout))
        except:
            print("Printer timedout")
            return
        q_created_mp3s.task_done() # Let the queue know the file has been dealt with
        time.sleep(0.1)

def main():
    unsortedoutputdir = r"\Unsorted"
    sortedoutputdir = r"\MP3s"
    rootdir = r"C:\Users\Sean O'Connor\Downloads\MP4 test"

    testfileName = r"Rootbeer - Under Control"

    existing_mp3_files = set()
    existing_mp4_files = set()
    
    # Set up the folder structure
    check_create_folder_exsists(rootdir + sortedoutputdir)
    check_create_folder_exsists(rootdir + unsortedoutputdir)
    
    # Populate a set of all the existing converted mp3 tracks
    traverse_files(add_to_set, existing_mp3_files, searchdir=rootdir+sortedoutputdir, filetypes=[".mp3"], ignoredirs=[])

    # Populate a set of all the mp4s files 
    traverse_files(add_to_set, existing_mp4_files, searchdir=rootdir, filetypes=[".mp4"], ignoredirs=["MP3s", "Unsorted"])

    # Only convert mp4 files that do not have an mp3 with the same name already existing, and put them in the queue
    existing_mp4_files.difference_update(existing_mp3_files)
    for filename in existing_mp4_files:
        q_mp4s_to_convert.put(filename) # This queue is accessed by the worker threads

    # TODO: remove time.sleep(), could cause P(race conditions) to increase

    # For performance benchmarking
    starttime = time.time()

    # Condition variable to allow threads to join when stuck in a while loop
    cond = threading.Condition(threading.Lock())
    cond.acquire()
    workingthreadcount = MAX_NUM_OF_WORKER_THREADS
    threads = []

    # Spawn a worker task if the mp4 file name cannot be found in the list of known mp3s
    for i in range(MAX_NUM_OF_WORKER_THREADS):
        thread = threading.Thread(target=worker, args=(rootdir,))
        thread.daemon = True # The threads created here will shutdown when hte program exits
        threads.append(thread)
        thread.start()

    # Spawn a printer thread to update stdout
    thread = threading.Thread(target=printer)
    thread.daemon = True # The threads created here will shutdown when hte program exits
    threads.append(thread)
    thread.start()

    q_mp4s_to_convert.join()
    q_created_mp3s.join()

    endworktime = time.time()

    for x in threads:
        x.join()
    
    print("\nMain Completed! Threadtime (before timeouts): %f sec. Total duration: %f sec" % (time.time()-endworktime, time.time()-starttime))

if __name__ == "__main__":
    main()