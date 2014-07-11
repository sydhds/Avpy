#!/usr/bin/env python

'''
pyav tools/build.py

Easily build libav/ffmpeg from git
'''

import os
import errno
import sys
import subprocess
import shutil

def run(cmd):

    print(cmd)

    retCode = subprocess.call(cmd, shell=True)	
    if retCode != 0:
        raise RuntimeError('cmd %s failed!' % cmd)

def buildGit(options):

    buildDir = os.path.abspath(os.path.join('build', '%s_%s' % (options.lib, options.version)))

    if options.suffix:
        buildDir += '_%s' % options.suffix

    try:
        os.makedirs(buildDir)
    except OSError as e:
        if e.errno == errno.EEXIST:
            pass
        else:
            raise

    try:
        os.chdir('build/%s_git' % options.lib)
    except OSError:
        print('Could not find libav repo: ./build/%s_git' % options.lib)
        sys.exit(1)

    run('git checkout v%s' % options.version)
    run('git describe --tags')

    run('./configure --prefix={0} {1} --logfile={0}/config.log'.format(buildDir, ' '.join(c for c in options.configure_options)))

    # in case we rebuild
    run('make clean')
    print('now building...')
    run('make -j {1} -k > {0}/make.log 2>&1'.format(buildDir, options.jobs))
    run('make install > {0}/make_install.log 2>&1'.format(buildDir))

    print('build done!')
    print('configure log: %s' % os.path.join(buildDir, 'config.log'))
    print('make log: %s' % os.path.join(buildDir, 'make.log'))

    if options.doc:
        basedir = ''
        basefile = 'Doxyfile'
        if not os.path.isfile(os.path.join(basedir, basefile)): 
            basedir = 'doc'
            if not os.path.isfile(os.path.join(basedir, basefile)):
                print('Could not find doxygen configuration file: %s' % basefile)
                sys.exit(2)        

        doxyf = os.path.join(basedir, basefile)
        doxyDst = os.path.join(basedir, 'doxy', 'html')
        try:
            # clean
            print('removing %s...' % doxyDst)
            shutil.rmtree(doxyDst)
            print('done.')
        except OSError as e:
            if e.errno == errno.ENOENT:
                pass
            else:
                raise

        # gen
        run('doxygen %s > %s 2>&1' % (doxyf, os.path.join(buildDir, 'doxygen.log')))
        # pseudo install
        run('cp -r {0} {1}'.format(doxyDst, buildDir))


def main(options):

    try:
        os.mkdir('build')
    except OSError as e:
        if e.errno == errno.EEXIST:
            buildGit(options)
        else:
            print('Could not create folder: build')
            sys.exit(1)

if __name__ == '__main__':

    from optparse import OptionParser

    usage = 'build.py -l libav -v 0.8.1'
    parser = OptionParser(usage=usage)
    parser.add_option('-l', '--lib', 
            help='lib to build: ffmpeg or libav (default: %default)',
            default='libav')
    parser.add_option('-v', '--version',
            help='libav version to build (ex: 0.8.1)')
    parser.add_option('-d', '--doc',
            action='store_true',
            default=False,
            help='generate documentation (require doxygen)')
    parser.add_option('-c', '--configure_options',
            action='append',
            default=['--enable-shared', '--enable-swscale'],
            help='configure options (default: %default)'
            )
    parser.add_option('-s', '--suffix',
            default='',
            help='install folder suffix, ex: libav_0.8.1_SUFFIX'
            )
    parser.add_option('-j', '--jobs', 
            default=2,
            type='int',
            help='allow N jobs at once (default: %default)'
            )

    (options, args) = parser.parse_args()

    if not options.version:
        print('Please provide a version using -v flag')
    else:
        main(options)

