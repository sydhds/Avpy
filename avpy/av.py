# Avpy
# Copyright (C) 2013-2015 Sylvain Delhomme
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

import os
import re
from ctypes import CDLL, RTLD_GLOBAL, util

def _version():
    
    '''
    Return libavcodec version as a tuple: lib (libav or ffmpeg), major, minor 
    and patch version
    '''

    # find_library does not support LD_LIBRARY_PATH for python < 3.4
    if 'AVPY_AVCODEC' in os.environ:
        fold, base = os.path.split(os.environ['AVPY_AVCODEC'])
        
        if 'AVPY_AVUTIL' in os.environ:
            libavutil = os.environ['AVPY_AVUTIL']
        else:
            libavutil = os.path.join(fold, re.sub('avcodec', 'avutil', base)) 

        if 'AVPY_AVRESAMPLE' in os.environ:
            libavresample = os.environ['AVPY_AVRESAMPLE']
        else:
            libavresample = os.path.join(fold, re.sub('avcodec', 'avresample', base))

        if 'AVPY_SWRESAMPLE' in os.environ:
            libswresample = os.environ['AVPY_SWRESAMPLE']
        else:
            libswresample = os.path.join(fold, re.sub('avcodec', 'swresample', base))

        libavcodec = os.environ['AVPY_AVCODEC']
    else:
        libavutil = util.find_library('avutil')
        libswresample = util.find_library('swresample')
        libavresample = util.find_library('avresample')
        libavcodec = util.find_library('avcodec')
    
    # RTD tests (debug only)
    #libavutil = None
    #libavcodec = None
    #libswresample = None
    #libavresample = None

    CDLL(libavutil, RTLD_GLOBAL)
    
    # ffmpeg have both libswresample and libavresample
    # libav only have libavresample
    if libswresample and os.path.exists(libswresample):
        lib = 'ffmpeg'
    else:
        lib = 'libav'

    # libav11
    if libavresample and os.path.exists(libavresample):
        CDLL(libavresample, RTLD_GLOBAL)
    
    version = CDLL(libavcodec, mode=RTLD_GLOBAL).avcodec_version() 

    return lib, version >> 16 & 0xFF, version >> 8 & 0xFF, version & 0xFF


def _findModuleName():
   
    '''
    find libav python binding to import

    on error, raise an ImportError exception
    '''

    libavVersion = { 
            53: {
                #(0, 10): 'av7',
                (30, 40): 'av8',
                },
            54: {
                (30, 40): 'av9',
                },
            55: {
                (30, 40): 'av10',
                },
            56: {
                (1, 40): 'av11',
                }
            }

    ffmpegVersion = {
            54: {
                (90, 93): 'ff12',
                },
            56: {
                (13, 20): 'ff25',
                (26, 30): 'ff26',
                (40, 50): 'ff27',
                (60, 65): 'ff28',
                },
            # 57: {
                # (24, 30): 'ff30',
                # }
            }

    lib, major, minor, micro = _version()	
    
    if lib == 'ffmpeg':
        versionDict = ffmpegVersion
    else:
        versionDict = libavVersion

    if major in versionDict:
        
        intv = versionDict[major]
        libName = None
        
        for k in intv.keys():
            if minor >= k[0] and minor < k[1]:
                libName = intv[k]
                break

        if libName is None:
            raise ImportError('ffmpeg/libav minor version not supported')
    else:
        raise ImportError('ffmpeg/libav major version not supported')

    return libName

_moduleName = _findModuleName() 
# import module
_temp = __import__('avpy.version', globals(), locals(), [_moduleName])
# import as lib
lib = getattr(_temp, _moduleName)

