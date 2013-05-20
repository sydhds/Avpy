'''
pyav tools/build.py

Easily build libav/ffmpeg from git
'''

import os
import errno
import sys
import subprocess

def run(cmd):

    print cmd

    retCode = subprocess.call(cmd, shell=True)	
    if retCode != 0:
        raise RuntimeError('cmd %s failed!' % cmd)

def buildGit(options):

    buildDir = os.path.abspath(os.path.join('build', '%s_%s' % (options.lib, options.version)))

    print buildDir
    try:
        os.makedirs(buildDir)
    except OSError, e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

    try:
        os.chdir('build/%s_git' % options.lib)
    except OSError:
        print 'Could not find libav repo: %s_git' % options.lib
        sys.exit(1)

    run('git checkout v%s' % options.version)
    run('git describe --tags')

    run('./configure --prefix={0} --enable-shared --enable-swscale --logfile={0}/config.log'.format(buildDir))

    # in case we rebuild
    run('make clean')
    print 'now building...'
    run('make -j 2 -k > {0}/make.log 2>&1'.format(buildDir))
    run('make install > {0}/make_install.log 2>&1'.format(buildDir))

    print 'build done!'
    print 'configure log: %s' % os.path.join(buildDir, 'config.log')
    print 'make log: %s' % os.path.join(buildDir, 'make.log')

def main(options):

    try:
        os.mkdir('build')
    except OSError, e:
        if e.errno == errno.EEXIST:
            buildGit(options)
        else:
            print 'Could not create folder: build'
            sys.exit(1)

if __name__ == '__main__':

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-l', '--lib', 
            help='lib to build: ffmpeg or libav (default: %default)',
            default='libav')
    parser.add_option('-v', '--version',
            help='libav version to build (ex: 0.8.3)')

    (options, args) = parser.parse_args()

    if not options.version:
        print 'Please provide a version using -v flag'
    else:
        main(options)

