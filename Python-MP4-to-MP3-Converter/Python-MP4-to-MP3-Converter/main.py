# Script to convert MP4 files to MP3 files, and clean-up metadata
# Run this script from the same directory as the target MP4 files
# A new folder called "MP3s" will be created with the output files
# Requires ffmeg for the conversion and python audio tools for the metadata

# References:
# http://zulko.github.io/blog/2013/10/04/read-and-write-audio-files-in-python-using-ffmpeg/
# https://gist.github.com/thinkski/3976945
# https://acoustid.org/server
# http://www.randombytes.org/audio_comparison.html

import os, threading, time, sys, queue
from subprocess import Popen, PIPE, call

FFMPEG_BIN = "ffmpeg.exe" # The exectuable, make sure to add the bin directory to the path (if using Linux remove the '.exe')

max_num_worker_threads = 3
q_input_mp4s = queue.Queue(maxsize=0)
q_created_mp3s = queue.Queue(maxsize=0)
q_existing_mp3s = queue.Queue(maxsize=0)
q_threads = queue.Queue(maxsize=max_num_worker_threads)


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

def populate_file_list(rootdir, filename, filetypes):
    # depricated
    '''Populate a list with all the files with extensions in the filetypes array (empty=all)'''
    (fname, fext) = os.path.splitext(filename)
    for filetype in filetypes:
        if fext == filetype:
            q_existing_mp3s.put(fname) #append to a global list of known MP3s
    # Return all the files if no filetype is defined
    if len(filetypes) == 0:
        q_existing_mp3s.put(fname)

def add_to_queue(myqueue, filename, filetypes):
    '''Populate a list with all the files with extensions in the filetypes array (empty=all)'''
    (fname, fext) = os.path.splitext(filename)
    for filetype in filetypes:
        if fext == filetype:
            myqueue.put(fname) #append to a global list of known MP3s
    # Return all the files if no filetype is defined
    if len(filetypes) == 0:
        myqueue.put(fname)

        
def spawn_thread(rootdir, filename, filetypes):
    '''Spawn a new thread to convert a file using ffmpeg'''
    #---- depricated --- not needed -- replaced by "worker"
    thread = threading.Thread(target=mp4_to_mp3, args=(rootdir, filename))
    #threads += [thread]
    q_threads.put(thread)
    thread.start()
    
def worker(rootdir):
    while True:
        mp4name = q_input_mp4s.get() # blocks if there is nothing to get
        q_created_mp3s.put(mp4_to_mp3(rootdir, mp4name)) 
        q_input_mp4s.task_done() # signal that a queued task is completed (oppisite to q.get())
        time.sleep(0.5)
        

def traverse_files(funchandle, myqueue, searchdir='.', filetypes=[".mp4"], ignoredirs=["MP3s"]):
    '''Reccsively get all the files from the root dir of a particular type (empty =all)
    The first loop prints all the subdirs in the current folder
    The second loop prints all the files in current dir
    The outside loop moves into each subdir, and the sub-subdirs..
    when it's done returns to the root dir and moves onto the next subdir'''
    # Proudly lifted from: http://stackoverflow.com/questions/120656/directory-listing-in-python
    for dirname, dirnames, filenames in os.walk(searchdir):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            #print(os.path.join(dirname, subdirname))
            pass

        # print path to all filenames.
        for filename in filenames:
            #print(os.path.join(dirname, filename))
            # Call the helper function to do something with the filename
            funchandle(myqueue, filename, filetypes)

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
    sys.stdout = open(os.devnull, "w")
    
    # Do the conversion from mp4 to mp3
    # call(command)
    pipe = Popen(command, stdout=PIPE, bufsize=10**8)
    pipe.stdout.close()
    print(pipe.wait())

    # Renable stout
    sys.stdout.flush()
    sys.stdout = sys.__stdout__
    
    return "Successfully converted '%s' to mp3!" % (fileName)

# Create a thread lock, for access to stdout - not used atm
tLock = threading.Lock()

def printer():
    print("Printer started")
    while True:
        print(q_created_mp3s.get())
        q_created_mp3s.task_done() # Let the queue know the file has been dealt with
        time.sleep(0.1)

def main():
    
    # Create an array of threads
    #threads = []
    unsortedoutputdir = r"\Unsorted"
    sortedoutputdir = r"\MP3s"
    rootdir = r"C:\Users\Sean O'Connor\Downloads\MP4 test"

    testfileName = r"Rootbeer - Under Control"
    
    # Set up the folder structure
    check_create_folder_exsists(rootdir + sortedoutputdir)
    check_create_folder_exsists(rootdir + unsortedoutputdir)
    
    # Populate a queue of all the existing converted mp3 tracks
    traverse_files(add_to_queue, q_existing_mp3s, searchdir=rootdir+sortedoutputdir, filetypes=[".mp3"], ignoredirs=[])

    # Populate a queue of all the mp4s that still need to be converted 
    traverse_files(add_to_queue, q_input_mp4s, searchdir=rootdir, filetypes=[".mp4"], ignoredirs=["MP3s", "Unsorted"])
    

    #mp4_to_mp3(rootdir, testfileName)
    #filelist = [testfileName]

    starttime = time.time()
    # Spawn a worker task if the mp4 file name cannot be found in the list of known mp3s
    for i in range(max_num_worker_threads):
        thread = threading.Thread(target=worker, args=(rootdir,))
        thread.daemon = True # The threads created here will shutdown when hte program exits
        #q_threads.put(thread)
        thread.start()

    # Spawn a printer thread to update stdout
    thread = threading.Thread(target=printer)
    thread.daemon = True # The threads created here will shutdown when hte program exits
    #q_threads.put(thread)
    thread.start()

    #for filename in filelist:
    #    thread = threading.Thread(target=mp4_to_mp3, args=(rootdir, filename))
    #    threads += [thread]
    #    thread.start()

    #for xthread in q_threads:
    #    xthread.join()
    #q_threads.join()
    q_input_mp4s.join()
    q_created_mp3s.join()
    
    print("Main Completed! Duration: %f sec" % (time.time()-starttime))

if __name__ == "__main__":
    main()