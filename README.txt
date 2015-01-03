====
Avpy
====

Avpy is a ctypes binding for libav and ffmpeg (see www.libav.org or www.ffmpeg.org). 

Typical usage often looks like this:

>>> from avpy import formats, codecInfo, Media
>>> print formats()
>>> print codecInfo('mp3', decode=True)
>>> m = Media('test.avi')
>>> print m.info()

More examples can be found in the examples folder.

FeatureMatrix:

- libav: 
    - version 0.8: done
    - version 9: done
    - version 10: done
    - version 11: done
- OS: 
    - Linux - BSD: done
    - MacOS: please report!
    - Windows: please report!
- avpy:
    - media info: done
    - basic video decoding: done
    - basic audio decoding: done
    - basic encoding: done
    - subtitle support: done
- doc:
    - sphinx doc: done
- examples:
    - dump image/wav/subtitle: done
    - alsaaudio: done
    - Pygame: done
    - PIL, pillow: done
    - PySDL2 video: done
    - encoding: done
- misc:
    - Python2.6, 2.7: done
    - Python3: done
    - PyPy: done

Missing features:

- ffmpeg:
    - version ?: todo
- avpy:
    - filter: todo (see old filter branch)
    - audio resampling: todo
    - seeking: todo
- examples:
    - PySDL2 audio: todo
    - PySDL2 video player: todo

Install
=======

Requirements
------------

libav

for ubuntu users, please run the following command:

sudo apt-get install ffmpeg

Install from source:
--------------------

- Clone this repository
- python setup.py sdist
- pip install dist/Avpy-*.tar.gz

Please read doc/DEV.txt (virtualenvs) or doc/Windows.txt for additional information.

Contact
=======

sydhds __at__ gmail __dot__ com

