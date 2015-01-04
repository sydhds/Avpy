Frequently Asked Questions
==========================

.. contents::

Libav and FFmpeg version support?
---------------------------------

- Libav 0.8, 9, 10 and 11 (all patch version supported)
- FFmpeg 1.2 (all patch version supported)

Note that support for FFmpeg 2.2, 2.4 and 2.5 will be added later.

Does Avpy support Python 3?
---------------------------

Yes for Python 3.2+ (pypy is supported as well). 
Please report if something is broken for Python3.

Is the hight level API stable?
------------------------------

Short answer: Almost but not yet.

Long answer:

As the api provides support for decoding and encoding, it should remain almost stable. Some additional code will be provided to abstract as much as possible any 'ctypes code' and to support new features (filtering, audio resampling, seeking ...).    

Does Avpy only provide a hight level API?
-----------------------------------------

Short answer: Yes but not recommended.

Long answer:

A low level API is available as ctypes functions that directly map
the underlying C functions. 

Note that this API varies from library (ffmpeg or libav) and from version (libav0.8 and libav 9). So while the high level API take cares of theses differences, the low API does not. 

Available functions are declared in avpy/version/av{VERSION}.py. Please report if some functions are missing.

