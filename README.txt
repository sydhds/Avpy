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
    - version 0.8: done
    - version 9: done
    - version 10: done
    - version 11: done
- ffmpeg:
    - version 1.2: todo
    - version 2.1: todo
    - version 2.2: todo
- OS: 
    - Linux - BSD: done
    - MacOS: please report!
    - Windows: please report!
- pyav:
    - media info: done
    - basic video decoding: done
    - basic audio decoding: done
    - sync video player: wip 
    - subtitle support: wip
    - encoding: todo
    - filter: todo
    - accurate seeking: todo
- doc:
    - sphinx doc: done
- examples:
    - dump image/wav/subtitle: done
    - alsaaudio: done
    - Pygame: wip
    - PIL, pillow: done
    - PySDL2: wip
    - PyAL: todo
- misc:
    - Python2.6, 2.7: done
    - Python3: done

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
- pip install dist/Pyav-*.tar.gz

Please read doc/DEV.txt (virtualenvs) or doc/Windows.txt for additional information.

Contact
=======

sydhds __at__ gmail __dot__ com

