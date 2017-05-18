#!/usr/bin/env python

'''
Easily build libav/ffmpeg from git

howto:

- clone ffmpeg or libav in BUILD_FOLDER
- cd tools
- run: 
    - ./build.py -l ffmpeg -v 2.5 -r BUILD_FOLDER
    - ./build.py -l libav -v 0.8.1 -r BUILD_FOLDER
'''

import os
import errno
import sys
import subprocess
import shutil


def run(cmd):
        
    ''' print and run shell command
    '''

    print(cmd)

    retCode = subprocess.call(cmd, shell=True)	
    if retCode != 0:
        raise RuntimeError('cmd %s failed!' % cmd)


def buildGit(options):
        
    ''' build libav or ffmpeg git
    '''

    pathToGit = os.path.abspath(os.path.join(options.repo, '%s_git' % options.lib))
    installFolder = os.path.abspath(os.path.join(options.repo, '%s_%s' % (options.lib, options.version)))

    if os.path.isdir(installFolder):
        print('A build already exists @ %s' % installFolder)
        sys.exit(1)
    else:
        os.makedirs(installFolder)

    if not os.path.isdir(pathToGit):
        # TODO: auto clone repo
        print('Could not find folder %s, please clone %s before running build' % (pathToGit, options.lib)) 
        sys.exit(1)

    print('Building in %s' % pathToGit)
    print('Install in %s' % installFolder)
    
    os.chdir(pathToGit)

    if options.lib == 'ffmpeg':
        tagChar = 'n'
    else:
        tagChar = 'v'

    # compile is a std: ./configure && make && make install process

    run('git checkout %s%s' % (tagChar, options.version))
    run('git describe --tags')
    run('./configure --prefix={0} {1} --logfile={0}/config.log'.format(installFolder, ' '.join(c for c in options.configure_options)))

    # clean up before building
    run('make clean')
    print('now building...')
    run('make -j {1} -k > {0}/make.log 2>&1'.format(installFolder, options.jobs))
    run('make install > {0}/make_install.log 2>&1'.format(installFolder))

    print('build done!')
    print('configure log: %s' % os.path.join(installFolder, 'config.log'))
    print('make log: %s' % os.path.join(installFolder, 'make.log'))
    
    if options.doc:
        
        # libav has Doxyfile in git root folder
        # ffmpeg has Doxyfile in GIT_ROOT/doc
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
        run('doxygen %s > %s 2>&1' % (doxyf, os.path.join(installFolder, 'doxygen.log')))
        # pseudo install
        run('cp -r {0} {1}'.format(doxyDst, installFolder))


def main(options):

    buildGit(options)


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
    parser.add_option('-r', '--repo',
            default='./build',
            help='where to find libav_git or ffmpeg_git folder')

    (options, args) = parser.parse_args()

    if not options.version:
        print('Please provide a version using -v flag')
    else:
        main(options)

