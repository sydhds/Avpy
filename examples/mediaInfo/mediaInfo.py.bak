#!/usr/bin/env python

'''
Print media information such as:
- format or container (avi, mkv...)
- metadata
- duration
- stream(s) info:
    - codec info
'''

from avpy import Media, formats, codecs, codecInfo

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
        
        media = Media(options.media)
        # retrieve media infos
        infoDict = media.info()
        
        # general info
        print('%s info:' % options.media)
        print(' format: %s' % infoDict['format'])
        print(' metadata: %s' % infoDict['metadata'])
        print(' duration: %f' % infoDict['duration'])

        # stream(s) info
        printSep() 
        print('stream(s):')
        for stream in infoDict['stream']:
            print('- %s' % stream)
            
            # codec info
            if options.info:
                print('  %s info:' % stream['codec'])
                info = codecInfo(stream['codec'])
                for k in info:
                    print('    %s: %s' % (k, info[k]))
                printSep()
    else:
        print('please provide a movie or sound file')


