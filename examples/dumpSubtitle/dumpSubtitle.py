#!/usr/bin/env python

'''
print subtitle (text based subtitles only)
'''

import sys
import copy

from pyav import Media

if __name__ == '__main__':
    
    # cmdline
    from optparse import OptionParser

    usage = "usage: %prog -m foo.avi"
    parser = OptionParser(usage=usage)
    parser.add_option('-m', '--media', 
            help='play media')
    parser.add_option('-c', '--count', 
            type='int',
            default=5,
            help='limit of packet to process (default: %default)')
    parser.add_option('--copyPacket', 
            action='store_true',
            help='copy packet (debug only)')

    (options, args) = parser.parse_args()

    m = Media(options.media)
    # dump info
    mediaInfo = m.info()

    # select first subtitle stream
    stStreams = [i for i, s in enumerate(mediaInfo['stream']) if s['type'] == 'subtitle']
    if stStreams:
        stStream = stStreams[0]
    else:
        print('No subtitle stream in %s' % mediaInfo['name'])
        sys.exit(2)

    print(mediaInfo['stream'][stStream]['subtitle_header'])

    count = 0
    for p in m:
        if p.streamIndex() == stStream:
            
            if options.copyPacket:
                p2 = copy.copy(p) 
            else:
                p2 = p

            p2.decode()
            if p2.decoded:

                for i in xrange(p2.subtitle.num_rects):
                    
                    if p2.subtitleTypes[i] == 'text':
                        print(p2.subtitle.rects[i].contents.text)
                    elif p2.subtitleTypes[i] == 'ass':
                        print(p2.subtitle.rects[i].contents.ass)

                count += 1
                if count != -1 and count > options.count:
                    break

