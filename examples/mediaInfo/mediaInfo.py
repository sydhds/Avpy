#!/usr/bin/env python

import sys
from pyav import Media

if __name__ == '__main__':

    # print a dict with available formats to encode and decode
    print 'available formats:'
    print Media.formats()

    # print mp3 codec information
    print 'codec information:'
    print Media.codecInfo('mp3')
    
    # open
    if len(sys.argv) > 1:
        m = Media(sys.argv[1])
        print 'file info:'
        print m.info()
    else:
        print 'please provide a movie or sound file'
