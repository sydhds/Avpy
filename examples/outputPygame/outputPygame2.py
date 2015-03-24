#!/usr/bin/env python

'''
demo video player (pygame)
python outputPygame2.py -m file.avi

.. note: 
    * use yuv hardware acceleration if available
    * no sound
    * no video sync
'''

import sys
import ctypes
import copy

import pygame

from avpy import Media

if __name__ == '__main__':
    
    # cmdline
    from optparse import OptionParser
    
    usage = "usage: %prog -m foo.avi"
    parser = OptionParser(usage=usage)
    parser.add_option('-m', '--media', 
            help='play media')
    parser.add_option('--copyPacket', 
            action='store_true',
            help='copy packet (debug only)')
    parser.add_option('--scaleWidth', 
        type='float', default=1.0,
        help='width scale (default: %default)')
    parser.add_option('--scaleHeight',
        type='float', default=1.0,
        help='height scale (default: %default)')
    parser.add_option('-f', '--fullscreen', 
            action='store_true',
            help='turn on full screen mode')
    #parser.add_option('--scaling', 
            #default='bilinear',
            #help='scaling algorithm')

    (options, args) = parser.parse_args()
    
    try:
        media = Media(options.media)
    except IOError as e:
        print('Unable to open %s: %s' % (options.media, e))
        sys.exit(1)

    # dump info
    mediaInfo = media.info()

    # select first video stream
    vstreams = [i for i, s in enumerate(mediaInfo['stream']) if s['type'] == 'video']
    if vstreams:
        vstream = vstreams[0]
    else:
        print('No video stream in %s' % mediaInfo['name'])
        sys.exit(2)

    # retrieve video width and height
    streamInfo = mediaInfo['stream'][vstream]
    size = streamInfo['width'], streamInfo['height']

    print('video stream index: %d' % vstream)
    print('video stream resolution: %dx%d' % (size[0], size[1]))

    size = ( int(round(size[0]*options.scaleWidth)), 
            int(round(size[1]*options.scaleHeight)) )

    print('output resolution: %dx%d' % (size)) 

    # setup pygame
    pygame.init()
 
    if options.fullscreen:
        screen = pygame.display.set_mode(size, pygame.DOUBLEBUF|pygame.HWSURFACE|pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode(size)

    useYuv = False
    if streamInfo['pixelFormat'] == 'yuv420p':
        overlay = pygame.Overlay(pygame.YV12_OVERLAY, size)
        overlay.set_location(0, 0, size[0], size[1]) 
        
        useYuv = True
        if overlay.get_hardware():
            print('render: Hardware accelerated yuv overlay (fast)')
        else:
            print('render: Software yuv overlay (slow)')
    else:
        print('render: software rgb (very slow)')
        # add scaler to convert to rgb
        media.addScaler(vstream, *size)
        #media.addScaler(vstream, *size, scaling='gauss')

    decodedCount = 0
    mainLoop = True

    print('Press Esc to quit...')

    while mainLoop:
        
        try:
            pkt = media.next()
        except StopIteration:
            mainLoop = False
            continue

        if pkt.streamIndex() == vstream:
           
            if options.copyPacket:
                pkt2 = copy.copy(pkt)
            else:
                pkt2 = pkt

            pkt2.decode()
            if pkt2.decoded:
                decodedCount += 1

                if useYuv:
                   
                    # upload yuv data

                    size0 = pkt2.frame.contents.linesize[0] * pkt2.frame.contents.height
                    size1 = pkt2.frame.contents.linesize[1] * (pkt2.frame.contents.height/2)
                    size2 = pkt2.frame.contents.linesize[2] * (pkt2.frame.contents.height/2)

                    yuv = (ctypes.string_at(pkt2.frame.contents.data[0], size0),
                            ctypes.string_at(pkt2.frame.contents.data[1], size1),
                            ctypes.string_at(pkt2.frame.contents.data[2], size2))
                    
                    overlay.display(yuv)
                    
                    # add a small delay otherwise pygame will crash
                    pygame.time.wait(20)

                else:

                    # upload rgb data

                    buf = pkt2.swsFrame.contents.data[0]
                    bufLen = size[0]*size[1]*3
                    surfaceStr = ctypes.string_at(buf, bufLen)
                    cSurface = pygame.image.fromstring(surfaceStr, size, 'RGB')

                    pygame.display.set_caption('Press Esc to quit...')
                    screen.blit(cSurface, (0, 0))
               
                    pygame.display.flip()

                # event processing
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        mainLoop = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_ESCAPE:
                            mainLoop = False
    
