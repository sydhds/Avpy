===========
Pyav
===========

Pyav is a ctypes binding for libav (and ffmpeg). Typical usage often 
looks like this:

    #!/usr/bin/env python
    from pyav import Media
    print Media.formats()
    print Media.codecInfo('mp3')
    m = Media('test.avi')
    print m.info()

More examples can be found in the examples folder.

FeatureMatrix:
- libav: 
    - version < 0.8: to be discussed
    - version 0.8: done
    - version 0.9: planned
- ffmpeg: to be discussed
- OS: 
    - Linux - BSD: done
    - MacOS: please report!
    - Windows: please report!
- pyav:
    - media info: done
    - basic video decoding: wip
    - basic audio decoding: wip
    - sync video player: wip 
    - subtitle support: wip
    - encoding: planned

Install
========

Requirements
-------------

libav

for ubuntu users, please run the following command:

sudo apt-get install ffmpeg

Install from source:
-------------

- Clone this repository
- python setup.py sdist
- pip install dist/Pyav-*.tar.gz

Contact
========

sydhds __at__ gmail __dot__ com

