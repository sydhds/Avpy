#!/usr/bin/env python

'''
Decode the 5th first frame of the first video stream and write pgm file

python outputPgm.py -m file.avi -> save frame 1 to 5
python outputPgm.py -m file.avi -o 140 -c 8 -> save frame 140 to 148
'''

import sys
import itertools
import array
import ctypes
from pyav import Media

def ptr_add(ptr, offset):
    address = ctypes.addressof(ptr.contents) + offset
    return ctypes.pointer(type(ptr.contents).from_address(address))

def saveFrame(frame, w, h, i):

    #a = array.array('B', [0]*(w*3))
    a = array.array('B', itertools.repeat(0, (w*3)))

    header = 'P6\n%d %d\n255\n' % (w, h)

    if sys.version_info >= (3, 0):
        header = bytes(header, 'ascii')

    with open('frame.%d.ppm' % i, 'wb') as f:
        #header
        f.write(header)
        for i in range(h):
            ptr = ptr_add(frame.contents.data[0], i*frame.contents.linesize[0])
            ctypes.memmove(a.buffer_info()[0], ptr, w*3)	
            a.tofile(f)

if __name__ == '__main__':
    
    # cmdline
    from optparse import OptionParser

    usage = "usage: %prog -m foo.avi -o 140"
    parser = OptionParser(usage=usage)
    parser.add_option('-m', '--media', 
            help='play media')
    parser.add_option('-o', '--offset', 
            type='int',
            help='frame offset', default=0)
    parser.add_option('-c', '--frameCount', 
            type='int',
            default=5,
            help='number of image to save (default: %default)')

    (options, args) = parser.parse_args()

    if not options.media:
        print('Please provide a media to play with -m or --media option')
        sys.exit(1)

    try:
        m = Media(options.media)
    except IOError as e:
        print('Unable to open %s: %s' % (options.media, e))
        sys.exit(1)

    # dump info
    mediaInfo = m.info()

    # select first video stream
    vstreams = [ i for i, s in enumerate(mediaInfo['stream']) if s['type'] == 'video' ]
    if vstreams:
        vstream = vstreams[0]
    else:
        print('No video stream in %s' % mediaInfo['name'])
        sys.exit(2)

    streamInfo = mediaInfo['stream'][vstream]
    w, h = streamInfo['width'], streamInfo['height']

    print('video stream resolution: %dx%d' % (w, h))

    m.addScaler(vstream, w, h)

    decodedCount = 0
    for p in m:
        
        if p.streamIndex() == vstream:
            p.decode()
            if p.decoded:

                decodedCount += 1
                print('decoded frame %d' % decodedCount)

                if decodedCount >= options.offset:
                    print('saving frame...')
                    saveFrame(p.swsFrame, w, h, decodedCount)

                if decodedCount >= options.offset+options.frameCount:
                    break 

