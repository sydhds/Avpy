#!/usr/bin/env python

'''
demo video player (PySDL2)
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
    
    window = sdl2.SDL_CreateWindow(b'Demo player',
                                   sdl2.SDL_WINDOWPOS_CENTERED,
                                   sdl2.SDL_WINDOWPOS_CENTERED,
                                   size[0], size[1], 
                                   sdl2.SDL_WINDOW_SHOWN)    
    if not window:
        print(sdl2.SDL_GetError())
        sys.exit(4)
 
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
    
    renderer = sdl2.SDL_CreateRenderer(window, -1, sdl2.SDL_RENDERER_ACCELERATED)
   
    useTexture = False
    rendererYuv = False
    rendererRgb = True # force to True (see below) 
    
    # query renderer caps
    # a more valid example would check for renderer supported resolution
    
    if not renderer:
        print('Could not create renderer: %s' % sdl2.SDL_GetError())
        useTexture = False
    else:
        useTexture = True
        rendererInfo = sdl2.SDL_RendererInfo() 
        res = sdl2.SDL_GetRendererInfo(renderer, rendererInfo)

        if res == 0:
            formats = rendererInfo.texture_formats
            
            print('renderer %s - fmts:' % rendererInfo.name)
            for fmt in formats:
                print(sdl2.SDL_GetPixelFormatName(fmt))
            
            if sdl2.SDL_PIXELFORMAT_YV12 in formats:
                rendererYuv = True
            else:
                print('Warning: render (%s) does not support yv12 format' 
                        % rendererInfo.name)
            
            # XXX: opengl renderer does not report supporting RGB24
            # but only ARGB888 - bug? 

            if sdl2.SDL_PIXELFORMAT_RGB24 in formats or\
                    sdl2.SDL_PIXELFORMAT_ARGB8888 in formats:
                rendererRgb = True
            else:
                # wtf?
                print('Warning: renderer (%s) does not support rgb24 or argb8888 format' 
                        % rendererInfo.name)
        else:
            print('Unable to query render info: %s' % sdl2.SDL_GetError())
        
    useYuv =  False
    
    # 3 rendering modes:
    # mode 1: useYuv + useTexture == True
    # -> upload yuv data to graphic card + hardware scaling
    # mode 2: useTexture == True, useYuv == False
    # -> yuv to rgb in software, upload rgb to graphic card + hardware scaling
    # mode 3: useTexture + useYuv == False
    # -> uyv to rgb + scaling in software 
    # Note: in this example, we don't perform scaling

    if useTexture == True:         
        
        # select clear color
        sdl2.SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255)
        # clear screen
        sdl2.SDL_RenderClear(renderer) 
        sdl2.SDL_RenderPresent(renderer)

        # mode 1
        if rendererYuv == True and streamInfo['pixelFormat'] == 'yuv420p':
            
            print('mode 1: fast yuv rendering...')

            useYuv = True

            # texture will change frequently so use streaming access
            yuvTexture = sdl2.SDL_CreateTexture(renderer, sdl2.SDL_PIXELFORMAT_YV12, 
                    sdl2.SDL_TEXTUREACCESS_STREAMING, size[0], size[1])
        else:
            
            print('mode 2: basic rgb rendering (slow)...')

            # mode 2
            m.addScaler2(vstream, *size)
        
    else:
        
        print('mode 3: software rendering (very slow)...')
        
        # mode 3
        m.addScaler2(vstream, *size)
        
        sdl2.SDL_DestroyRenderer(renderer)
        windowSurface = sdl2.SDL_GetWindowSurface(window)

    print('Press Esc to quit...')
    
    running = True
    event = sdl2.SDL_Event()
    while running:
       
        # process events...
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
             
                if useYuv:
                   
                    fc = p.frame.contents
                
                    sdl2.SDL_UpdateYUVTexture(yuvTexture, None,
                            fc.data[0], fc.linesize[0], 
                            fc.data[1], fc.linesize[1], 
                            fc.data[2], fc.linesize[2] )

                    res = sdl2.SDL_RenderCopy(renderer, yuvTexture, None, None);
                    if res < 0:
                        raise RuntimeError(sdl2.SDL_GetError())
                    sdl2.SDL_RenderPresent(renderer)

                else:
                    
                    buf = p.swsFrame.contents.data[0]
                    surface = sdl2.SDL_CreateRGBSurfaceFrom(buf, 
                            size[0], size[1], 24, 
                            size[0] * 3,
                            rmask, gmask,
                            bmask, amask)

                    #print sdl2.SDL_GetPixelFormatName(surface.contents.format.contents.format)

                    if useTexture:

                        texture = sdl2.SDL_CreateTextureFromSurface(renderer, surface)

                        res = sdl2.SDL_RenderCopy(renderer, texture, None, None)
                        if res < 0:
                            raise RuntimeError(sdl2.SDL_GetError())
                        sdl2.SDL_RenderPresent(renderer)

                    else:
                        sdl2.SDL_BlitSurface(surface, None, windowSurface, None)
                        sdl2.SDL_UpdateWindowSurface(window)
                        sdl2.SDL_FreeSurface(surface)

        sdl2.SDL_Delay(10)

    sdl2.SDL_DestroyWindow(window)
    sdl2.SDL_Quit()

