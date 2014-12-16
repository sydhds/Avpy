#!/usr/bin/env python

'''
Decode the 5th first frame of the first video stream 
and write tiff images

python encodeImage.py -m file.avi -> save frame 1 to 5
python encodeImage.py -m file.avi -o 140 -> save frame 140 to 145
'''

import sys
import copy
from pyav import Media

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

    m.addScaler2(vstream, w, h)

    decodedCount = 0
    for _p in m:
        
        if _p.streamIndex() == vstream:
            
            p = copy.copy(_p)
            p.decode()

            if p.decoded:

                decodedCount += 1
                print('decoded frame %d' % decodedCount)

                if decodedCount >= options.offset:
                    print('saving frame...')
                    fn = 'frame.%d.tiff' % decodedCount
                    m2 = Media(fn, 'w', quiet=False)
                    streamInfoImage = {
                            'width': w,
                            'height': h,
                            'pixelFormat': 'rgb24',
                            'codec': 'tiff',
                            }
                    m2.addStream('video', streamInfoImage)
                    m2.writeHeader()
                    m2.write(p, 1, 'video') 
                    m2.writeTrailer()

                    del(m2)

                if decodedCount >= options.offset+options.frameCount:
                    break 
