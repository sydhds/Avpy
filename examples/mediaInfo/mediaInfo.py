#!/usr/bin/env python

from pyav import Media

def printSep(ch='='):
    print ch*25

if __name__ == '__main__':

    # cmdline
    from optparse import OptionParser

    usage = "usage: %prog -m foo.avi"
    parser = OptionParser(usage=usage)
    parser.add_option('-m', '--media', 
            help='play media')
    (options, args) = parser.parse_args() 

    # print a dict with available formats to encode and decode
    print 'available formats:'
    formats = Media.formats()
    print formats

    # print mp3 codec information
    codecName = 'mp3'
    printSep()
    print '%s (%s) information:' % (codecName, formats['decoding'].get(codecName, ''))
    print Media.codecInfo('mp3')
    
    # open
    if options.media:
        m = Media(options.media)
        printSep()
        print '%s info:' % options.media
        infoDict = m.info()

        print 'stream(s):'
        for stream in infoDict['stream']:
            print stream

    else:
        print 'please provide a movie or sound file'


