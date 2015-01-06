#!/usr/bin/env python

'''
Decode the 5th first frame of the first video stream 
and write tiff images

Note that this example, use avpy to decode and encode image (no dependencies)

python encodeImage.py -m file.avi -> save frame 1 to 5
python encodeImage.py -m file.avi -o 140 -c 3 -> save frame 140 to 143
'''

import sys
import copy
from avpy import Media

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
        media = Media(options.media, quiet=False)
    except IOError as e:
        print('Unable to open %s: %s' % (options.media, e))
        sys.exit(1)

    # dump info
    mediaInfo = media.info()

    # select first video stream
    vstreams = [ i for i, s in enumerate(mediaInfo['stream']) if s['type'] == 'video' ]
    if vstreams:
        vstream = vstreams[0]
    else:
        print('No video stream in %s' % mediaInfo['name'])
        sys.exit(2)

    # retrieve video width and height
    streamInfo = mediaInfo['stream'][vstream]
    w, h = streamInfo['width'], streamInfo['height']

    print('video stream resolution: %dx%d' % (w, h))
 
    # tiff format require rgb24 (24 bits)
    media.addScaler(vstream, w, h)

    # setup encoder (stream info)
    streamInfoImage = {
            'width': w,
            'height': h,
            'pixelFormat': 'rgb24',
            'codec': 'tiff',
            }

    decodedCount = 0
    # iterate over media
    for pkt in media:
        
        if pkt.streamIndex() == vstream:
            
            # copy packet - not mandatory
            # TODO: remove copy?
            pkt2 = copy.copy(pkt)
            pkt2.decode()

            if pkt2.decoded:

                decodedCount += 1
                print('decoded frame %d' % decodedCount)

                if decodedCount >= options.offset:
                    
                    img = 'frame.%d.tiff' % decodedCount
                    print('saving image %s...' % img)
                    
                    # setup output media
                    imgMedia = Media(img, 'w', quiet=False)
                    imgMedia.addStream('video', streamInfoImage)

                    # write data
                    imgMedia.writeHeader()
                    imgMedia.write(pkt2, 1, 'video') 
                    imgMedia.writeTrailer()

                    #del(imgMedia)

                if decodedCount >= options.offset+options.frameCount:
                    break 
