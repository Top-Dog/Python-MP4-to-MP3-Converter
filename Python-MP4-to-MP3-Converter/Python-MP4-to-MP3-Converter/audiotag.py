# Download Chromaprint dymaic libriary or command line tool (fpcac): https://acoustid.org/chromaprint
# If using fpcalc command line tool, add the Chromaprint fcalc.exe location to the path, or change FPCALC_ENVVAR to the install location (C:\python\lib\site-packages)
# Download and install pyacoustid Python Bindings: pip install pyacoustid
# An audio decoder is needed, such as FFmeg, GStreamer with PyGObject, MAD with pymad

import acoustid

apikey = "8GXrGT5g"

metatags = ["recordings", "recordingids", "releases", "releaseids", "releasegroups", "releasegroupids", "tracks", "compress", "usermeta", "sources"]

path = r"C:\Users\Sean O'Connor\Downloads\MP4 test\MP3s\Rootbeer - Under Control - Copy.mp3"

for meta in metatags:
    print(acoustid.match(apikey, path, meta=meta, parse=False))