====
Avpy
====

Avpy is a Python binding for ffmpeg and libav (see www.ffmpeg.org or www.libav.org).

Typical usage often looks like this:

>>> from avpy import formats, codecInfo, Media
>>> print formats()
>>> print codecInfo('mp3', decode=True)
>>> m = Media('test.avi')
>>> print m.info()

More examples can be found in the examples folder. Documentation is available 
online: https://avpy.readthedocs.org/ 

This software is licensed under the LGPL v.2.1+. Examples (and tools)
are licensed under the Apache License 2.0.

The binding uses ctypes (https://docs.python.org/2/library/ctypes.html) to wrap ffmpeg or libav 
and is compatible with all major version of ffmpeg (v1.2 and from v2.5 to v2.8)
and libav (from v0.8 to v11). 
Note that python2 (v2.6 and v2.7), python3 (from v3.2 to v3.5) and pypy are supported.

Install
=======

Requirements
------------

libav

for ubuntu users, please run the following command:

sudo apt-get install ffmpeg

Install from source:
--------------------

- pip install Avpy

Install from source:
--------------------

Clone Avpy repo from bitbucket or github

- git clone https://bitbucket.org/sydh/avpy.git Avpy
- git clone https://github.com/sydhds/Avpy.git Avpy

Please read docs/DEV.txt (virtualenvs) or docs/Windows.txt for additional information.

Contact
=======

sydhds __at__ gmail __dot__ com

