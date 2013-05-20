===========
Pyav
===========

Pyav is a ctypes binding for libav (and ffmpeg). Typical usage often 
looks like this:

    #!/usr/bin/env python
    from pyav import av
    print Media.formats()
    print Media.codecInfo('mp3')
    m = Media.info()

Install
========

Requirements
-------------

libav

for ubuntu users, please run the following command:

sudo apt-get install ffmpeg

Install from source:
-------------

- Clone repository
- python setup.py sdist
- pip install dist/Pyav-*.tar.gz

