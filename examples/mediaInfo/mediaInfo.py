#!/usr/bin/env python

from pyav import Media, formats, codecs, codecInfo

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

    formats = formats()
    codecs = codecs() 

    # open
    if options.media:
        
        m = Media(options.media)
        infoDict = m.info()

        print('%s info:' % options.media)
        print(' format: %s' % infoDict['format'])
        print(' metadata: %s' % infoDict['metadata'])
        print(' duration: %f' % infoDict['duration'])

        printSep() 
        print('stream(s):')
        for stream in infoDict['stream']:
            print('- %s' % stream)

            if options.info:
                print('  %s info:' % stream['codec'])
                info = codecInfo(stream['codec'])
                for k in info:
                    print('    %s: %s' % (k, info[k]))
                printSep()
    else:
        print('please provide a movie or sound file')


