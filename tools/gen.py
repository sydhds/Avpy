'''
pyav tools/build.py

Easily generate python binding for libav/ffmpeg
'''

import os
import subprocess
import re

def stripLibPath(src, dst, folder):

    with open(src, 'r') as fs:
        with open(dst, 'w') as fd:
            for line in fs:
                fd.write(re.sub(folder, '', line))

def run(cmd):

    print cmd

    retCode = subprocess.call(cmd, shell=True)	
    if retCode != 0:
        raise RuntimeError('cmd %s failed!' % cmd)

def main(options):

    buildDir = os.path.abspath('build/%s_%s' % (options.lib, options.version))

    pyLibVersion = ''.join(options.version.split('.')[:2])
    xmlFile = 'av%s.xml' % (pyLibVersion)
    pyFileTmp = 'av%s_tmp.py' % (pyLibVersion)
    pyFile = 'av%s.py' % (pyLibVersion)

    print 'generating xml...'
    xmlCmd = 'h2xml -I {0}/include -c libavcodec/avcodec.h'\
            ' libavdevice/avdevice.h libavformat/avformat.h libavutil/avutil.h'\
            ' libavutil/mathematics.h libavutil/rational.h libswscale/swscale.h -o {1}'\
            ' -D__STDC_CONSTANT_MACROS'.format(buildDir, xmlFile)
    run(xmlCmd)

    print 'generating python module'
    xml2pyCmd = 'xml2py {0} -o {1} -l {2}/lib/libavcodec.so'\
            ' -l {2}/lib/libavformat.so -l {2}/lib/libavdevice.so'\
            ' -l {2}/lib/libavutil.so -l {2}/lib/libswscale.so'\
            ' --preload {2}/lib/libavutil.so'.format(xmlFile, pyFileTmp, buildDir) 
    run(xml2pyCmd)

    print buildDir + 'lib%s' % os.sep
    stripLibPath(pyFileTmp, pyFile, os.path.join(buildDir, 'lib%s' % os.sep))

    print 'generation done!'
    print 'python module: %s' % pyFile

if __name__ == '__main__':

    from optparse import OptionParser
    
    usage = '%prog -l libav -v 0.8.1'
    parser = OptionParser(usage=usage)
    parser.add_option('-l', '--lib', 
            help='gen python binding for lib: ffmpeg or libav (default: %default)',
            default='libav')
    parser.add_option('-v', '--version',
            help='gen python binding for libav version (ex: 0.8.1)')

    (options, args) = parser.parse_args()

    main(options)
