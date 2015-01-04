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

def version():
    
    '''
    Return libavcodec version as a tuple: major, minor, patch version
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

        libavcodec = os.environ['AVPY_AVCODEC']
    else:
        libavutil = util.find_library('avutil')
        libavresample = util.find_library('avresample')
        libavcodec = util.find_library('avcodec')
        
    CDLL(libavutil, RTLD_GLOBAL)
    # libav11
    if os.path.exists(libavresample):
        CDLL(libavresample, RTLD_GLOBAL)
    version = CDLL(libavcodec, mode=RTLD_GLOBAL).avcodec_version() 
    
    return version >> 16 & 0xFF, version >> 8 & 0xFF, version & 0xFF


def findModuleName():
   
    '''
    find libav python binding to import

    on error, raise an ImportError exception
    '''

    versionDict = { 
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

    major, minor, micro = version()	

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

_moduleName = findModuleName() 
# import module
_temp = __import__('avpy.version', globals(), locals(), [_moduleName])
# import as lib
lib = getattr(_temp, _moduleName)

