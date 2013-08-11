#!/usr/bin/env python

'''
dumb video player (pygame)
python outputPygame2.py -m file.avi
'''

import sys
import ctypes
import copy

import pygame

from pyav import Media

if __name__ == '__main__':
    
    # cmdline
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-m', '--media', 
            help='play media')
    
    (options, args) = parser.parse_args()

    try:
        m = Media(options.media)
    except IOError, e:
        print 'Unable to open %s: %s' % (options.media, e)
        sys.exit(1)

    # dump info
    mediaInfo = m.info()

    # select first video stream
    vstreams = [ i for i, s in enumerate(mediaInfo['stream']) if s['type'] == 'video' ]
    if vstreams:
        vstream = vstreams[0]
    else:
        print 'No video stream in %s' % mediaInfo['name'] 
        sys.exit(2)

    streamInfo = mediaInfo['stream'][vstream]
    size = streamInfo['width'], streamInfo['height']

    print 'video stream index: %d' % vstream
    print 'video stream resolution: %dx%d' % (size[0], size[1])

    # XXX
    # /2 size
    size = [ i/2 for i in size ]

    m.addScaler2(vstream, *size)

    pygame.init()
 
    screen = pygame.display.set_mode(size)
    surfaces = []

    decodedCount = 0
    mainLoop = True

    while mainLoop:
        
        try:
            p = m.next()
        except StopIteration:
            mainLoop = False
            continue

        if p.streamIndex() == vstream:
            
            p2 = copy.copy(p)
            p2.decode()
            if p2.decoded:
                decodedCount += 1

                buf = p2.swsFrame.contents.data[0]
                bufLen = size[0]*size[1]*3
                surfaceStr = ctypes.string_at(buf, bufLen)
                cSurface = pygame.image.fromstring(surfaceStr, size, 'RGB')

                pygame.display.set_caption('Press Esc to quit...')
                screen.blit(cSurface, (0, 0))
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        mainLoop = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            mainLoop = False
    
                pygame.display.update()
