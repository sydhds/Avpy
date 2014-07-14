#!/usr/bin/env python

'''
dumb video player (PySDL2)
python outputSDL2.py -m file.avi
'''

import sys
import ctypes
import copy

import sdl2

from pyav import Media

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
    #parser.add_option('-o', '--overlay',
        #action='store_true', 
        #help='EXPERIMENTAL: use yuv')
    parser.add_option('-f', '--fullscreen', 
            action='store_true',
            help='turn on full screen mode')

    (options, args) = parser.parse_args()
    
    try:
        m = Media(options.media)
    except IOError as e:
        print('Unable to open %s: %s' % (options.media, e))
        sys.exit(1)

    # dump info
    mediaInfo = m.info()

    # select first video stream
    vstreams = [i for i, s in enumerate(mediaInfo['stream']) if s['type'] == 'video']
    if vstreams:
        vstream = vstreams[0]
    else:
        print('No video stream in %s' % mediaInfo['name'])
        sys.exit(2)

    streamInfo = mediaInfo['stream'][vstream]
    size = streamInfo['width'], streamInfo['height']

    print('video stream index: %d' % vstream)
    print('video stream resolution: %dx%d' % (size[0], size[1]))

    size = ( int(round(size[0]*options.scaleWidth)), 
            int(round(size[1]*options.scaleHeight)) )

    print('output resolution: %dx%d' % (size)) 

    # sdl2
    sdl2Version = sdl2.version_info
    print('Using sdl2 version: %d.%d.%d' % 
            (sdl2Version[0], sdl2Version[1], sdl2Version[2]))
    
    if sdl2.SDL_Init(sdl2.SDL_INIT_VIDEO) != 0:
        print(sdl2.SDL_GetError())
        sys.exit(3)
    event = sdl2.SDL_Event()
    
    window = sdl2.SDL_CreateWindow(b'Hello World',
                                   sdl2.SDL_WINDOWPOS_CENTERED,
                                   sdl2.SDL_WINDOWPOS_CENTERED,
                                   size[0], size[1], 
                                   sdl2.SDL_WINDOW_SHOWN)    
    if not window:
        print(sdl2.SDL_GetError())
        sys.exit(4)

    windowsurface = sdl2.SDL_GetWindowSurface(window)
   
    if sdl2.SDL_BYTEORDER == sdl2.SDL_LIL_ENDIAN:
        rmask = 0x000000ff
        gmask = 0x0000ff00
        bmask = 0x00ff0000
        amask = 0xff000000
    else:
        rmask = 0xff000000
        gmask = 0x00ff0000
        bmask = 0x0000ff00
        amask = 0x000000ff

    # end sdl2
    
    m.addScaler2(vstream, *size)

    decodedCount = 0
    mainLoop = True

    print('Press Esc to quit...')
    
    running = True
    event = sdl2.SDL_Event()
    while running:
        while sdl2.SDL_PollEvent(ctypes.byref(event)) != 0:
            keySim =  event.key.keysym.sym
            if (event.type == sdl2.SDL_KEYDOWN and keySim == sdl2.SDLK_ESCAPE) or\
                    event.type == sdl2.SDL_QUIT:
                running = False
                break

        p = m.next()

        if p.streamIndex() == vstream:
            p.decode()
            if p.decoded:
                decodedCount += 1
            
                buf = p.swsFrame.contents.data[0]
                    
                surface = sdl2.SDL_CreateRGBSurfaceFrom(buf, 
                        size[0], size[1], 24, 
                        size[0] * 3,
                        rmask, gmask,
                        bmask, amask)

                sdl2.SDL_BlitSurface(surface, None, windowsurface, None)
                sdl2.SDL_UpdateWindowSurface(window)
                sdl2.SDL_FreeSurface(surface)

        sdl2.SDL_Delay(10)

    sdl2.SDL_DestroyWindow(window)
    sdl2.SDL_Quit()

