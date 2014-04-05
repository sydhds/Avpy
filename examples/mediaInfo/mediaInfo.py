#!/usr/bin/env python

from pyav import Media

def printSep(ch='='):
    print(ch*25)

if __name__ == '__main__':

    # cmdline
    from optparse import OptionParser

    usage = "usage: %prog -m foo.avi"
    parser = OptionParser(usage=usage)
    parser.add_option('-m', '--media', 
            help='play media')
    parser.add_option('-i', '--info', 
            action='store_true',
            help='print codec info')
    (options, args) = parser.parse_args() 

    formats = Media.formats()
    codecs = Media.codecs() 

    # open
    if options.media:
        
        m = Media(options.media)
        infoDict = m.info()

        print('%s info:' % options.media)
        print(' metadata: %s' % infoDict['metadata'])
        print(' duration: %f' % infoDict['duration'])

        printSep() 
        print('stream(s):')
        for stream in infoDict['stream']:
            print('- %s' % stream)

            if options.info:
                print('  %s info: %s' % stream['codec'])
                for k, v in Media.codecInfo(stream['codec']).iteritems():
                    print('    %s: %s' % (k, v))
                printSep()
    else:
        print('please provide a movie or sound file')


