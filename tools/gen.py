#!/usr/bin/env python

'''
Easily generate python binding for libav/ffmpeg

require: h2xml & xml2py utilities (see docs/Dev.txt)

howto:
'''

import sys
import os
import subprocess
import re


def stripLibPath(src, dst, folder):

    ''' Replace full lib path with relative path
    '''

    with open(src, 'r') as fs:
        with open(dst, 'w') as fd:
            for line in fs:
                fd.write(re.sub(folder, '', line))


def run(cmd):

    ''' print and run shell command
    '''
    
    print(cmd)

    retCode = subprocess.call(cmd, shell=True)	
    if retCode != 0:
        raise RuntimeError('cmd %s failed!' % cmd)


def main(options):

    buildDir = os.path.abspath(os.path.join(options.buildDir, '%s_%s' % (options.lib, options.version)))

    if not os.path.isdir(buildDir):
        print('Could not find %s build @ %s' % (options.lib, buildDir))
        sys.exit(1)

    pyLibVersion = ''.join(options.version.split('.')[:2])
    pyLibVersion = pyLibVersion.zfill(3)
    pyLibPrefix = 'ff' if options.lib == 'ffmpeg' else 'av'
    xmlFile = '%s%s.xml' % (pyLibPrefix, pyLibVersion)
    pyFileTmp = '%s%s_tmp.py' % (pyLibPrefix, pyLibVersion)
    pyFile = '%s%s.py' % (pyLibPrefix, pyLibVersion)
    
    # include file if exists 
    _addInclude = [
            'libavutil/channel_layout.h', # libav >= 9
            'libavresample/avresample.h', # libav >= 9
            'libswresample/swresample.h', # ffmpeg >= 1.2
            'libavutil/frame.h', # libav >= 10
            ]
    addInclude = []

    for i in _addInclude:
        if os.path.isfile(os.path.join(buildDir, 'include', i)):
            addInclude.append(i)
        else:
            print('skipping %s' % i)
    addInclude = ' '.join(addInclude)

    print('generating xml...')
    xmlCmd = 'h2xml -I {0}/include -c libavcodec/avcodec.h'\
            ' libavdevice/avdevice.h libavformat/avformat.h libavutil/avutil.h'\
            ' libavutil/mathematics.h libavutil/rational.h libswscale/swscale.h'\
            ' libavutil/pixdesc.h libavutil/opt.h'\
            ' {2} -o {1}'\
            ' -D__STDC_CONSTANT_MACROS'.format(buildDir, xmlFile, addInclude)
    run(xmlCmd)
   
    # preload libavutil & resample lib (libavresample or swresample)
    # libav has libavresample
    # ffmpeg has libswresample
    preloads = ' --preload ' + os.path.join(buildDir, 'lib', 'libavutil.so')
    libResample = os.path.join(buildDir, 'lib', 'libavresample.so')
    if os.path.isfile(libResample):
        preloads += (' --preload ' + libResample)

    libSwResample = os.path.join(buildDir, 'lib', 'libswresample.so')
    if os.path.isfile(libSwResample):
        preloads += (' --preload ' + libSwResample)

    print('generating python module')

    if options.lib == 'ffmpeg':
        xml2pyCmd = 'xml2py {0} -o {1} -l {2}/lib/libavutil.so -l {2}/lib/libavcodec.so'\
                ' -l {2}/lib/libswresample.so'\
                ' -l {2}/lib/libavformat.so -l {2}/lib/libswscale.so'\
                ' -l {2}/lib/libavfilter.so'\
                ' -l {2}/lib/libavdevice.so'.format(xmlFile, pyFileTmp, buildDir) 
    else:
        xml2pyCmd = 'xml2py {0} -o {1} -l {2}/lib/libavutil.so -l {2}/lib/libavcodec.so'\
                ' -l {2}/lib/libavformat.so -l {2}/lib/libavdevice.so'\
                ' -l {2}/lib/libswscale.so'.format(xmlFile, pyFileTmp, buildDir) 
   
    
    # append resample lib
    libResample = os.path.join(buildDir, 'lib', 'libavresample.so')
    if os.path.isfile(libResample):
        xml2pyCmd += ' -l %s' % libResample
        
    #libSwResample = os.path.join(buildDir, 'lib', 'libswresample.so')
    #if os.path.isfile(libSwResample):
        #xml2pyCmd += ' -l %s' % libSwResample
    
    xml2pyCmd += preloads
    run(xml2pyCmd)

    print(buildDir + 'lib%s' % os.sep)
    stripLibPath(pyFileTmp, pyFile, os.path.join(buildDir, 'lib%s' % os.sep))

    print('generation done!')
    print('python module: %s' % pyFile)


if __name__ == '__main__':

    from optparse import OptionParser
    
    usage = '%prog -l libav -v 0.8.1'
    parser = OptionParser(usage=usage)
    parser.add_option('-l', '--lib', 
            help='gen python binding for lib: ffmpeg or libav (default: %default)',
            default='libav')
    parser.add_option('-v', '--version',
            help='gen python binding for libav version (ex: 0.8.1)')

    parser.add_option('-b', '--buildDir',
            default='./build',
            help='where to find libav or ffmpeg build')
   
    (options, args) = parser.parse_args()

    main(options)

