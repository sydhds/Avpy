#!/usr/bin/env python

'''
WIP video player (pygame + alsa)
Warning: unsynced + memory leak
python videoPlayer.py -m file.avi -f
'''

import sys
from copy import copy
import ctypes
import threading
import Queue

from pyav import Media

import alsaaudio
import pygame

class videoThread(threading.Thread):

    def __init__(self, sharedData):
        super(videoThread, self).__init__()
        self._stopEvent = threading.Event()
        self.d = sharedData

    def stop(self):
        self._stopEvent.set()
   
    def run(self):

        while not self._stopEvent.isSet():
            try:
                #p = self.d.videoQueue.get(timeout=0.1)
                p = self.d.videoQueue.get_nowait()
            except Queue.Empty:
                pass
            else:
                p.decode()
                
                if p.decoded:
                    buf = p.swsFrame.contents.data[0]
                    bufLen = self.d.size[0]*self.d.size[1]*3
                    videoSurface = pygame.image.fromstring(ctypes.string_at(buf, bufLen), self.d.size, 'RGB')
                    self.d.window.blit(videoSurface, (0,0))
                    
                    #pygame.display.update()
                    pygame.display.flip()


class audioThread(threading.Thread):

    def __init__(self, sharedData):
        super(audioThread, self).__init__()
        self._stopEvent = threading.Event()
        self.d = sharedData

    def stop(self):
        self._stopEvent.set()

    def run(self):

        while not self._stopEvent.isSet():
            try:
                #p = self.d.audioQueue.get(timeout=0.1)
                p = self.d.audioQueue.get_nowait()
            except Queue.Empty:
                pass
            else:
                p.decode()
                if p.decoded:
                    buf = p.frame.contents.data[0]
                    bufLen = p.dataSize
                    self.d.out.write(ctypes.string_at(buf, bufLen))


class playerSharedData(object):

    def __init__(self):

        self.audioStreamIndex = -1
        self.videoStreamIndex = -1
        self.size = None
        self.out = None 
        self.window = None
        self.videoQueue = Queue.Queue(15)
        self.audioQueue = Queue.Queue(15)

class playerThread(threading.Thread):
    
    def __init__(self, filename, fullscreen):
        super(playerThread, self).__init__()
        self.setDaemon(True)
        self._stopEvent = threading.Event()
    
        self.d = playerSharedData()
        
        self.fullscreen = fullscreen
        self.m =  Media(options.media)
        # dump info
        self.mediaInfo = self.m.info()
        
        # first video and audio stream
        self.firstStreams()
        # sound setup
        self.soundSetup()
        # video setup
        self.videoSetup()

    def stop(self):
        self._stopEvent.set()
    
    def run(self):

        # audio thread
        if self.d.audioStreamIndex != -1:
            self.at = audioThread(self.d)
            self.at.setDaemon(True)
            self.at.start()

        # video thread
        if self.d.videoStreamIndex != -1:
            self.vt = videoThread(self.d)
            self.vt.setDaemon(True)
            self.vt.start()
        
        while not self._stopEvent.isSet():
            try:
                p = self.m.next()
            except StopIteration:
                self._stopEvent.set()

            if self.d.audioQueue.full() or self.d.videoQueue.full():
                # approx 1 frame - 33ms
                self._stopEvent.wait(0.033)
                #pass

            if p.streamIndex() == self.d.audioStreamIndex:
                self.d.audioQueue.put(copy(p))
            elif p.streamIndex() == self.d.videoStreamIndex:
                self.d.videoQueue.put(copy(p))
            else:
                # XXX free Packet?
                pass

        self.at.stop()
        self.vt.stop()
        self.at.join()
        self.vt.join()
    
    def videoSetup(self):
        
        vsInfo = self.mediaInfo['stream'][self.d.videoStreamIndex]
        size = vsInfo['width'], vsInfo['height']
        self.d.size = size
        self.m.addScaler2(self.d.videoStreamIndex, *size)
        
        # pygame
        pygame.init()
        
        if self.fullscreen:
            self.d.window = pygame.display.set_mode(size, pygame.DOUBLEBUF|pygame.HWSURFACE|pygame.FULLSCREEN)
            pygame.mouse.set_visible(False)
        else:
            self.d.window = pygame.display.set_mode(size)

    def soundSetup(self):

        # alsa setup
        si = self.mediaInfo['stream'][self.d.audioStreamIndex]
        aformat=getattr(alsaaudio, 'PCM_FORMAT_%s_%s' % (si['sample_fmt'].upper(), 'LE' if sys.byteorder == 'little' else 'BE'))
        self.d.out = alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL, card='default')

        self.d.out.setchannels(si['channels'])
        self.d.out.setrate(si['sample_rate'])
        self.d.out.setformat(aformat)    

    def firstStreams(self):

        # select first audio stream
        astreams = [i for i, s in enumerate(self.mediaInfo['stream']) if s['type'] == 'audio']
        if astreams:
            self.d.audioStreamIndex = astreams[0]
        else:
            raise RuntimeError('no audio stream...')

        # select first video stream
        vstreams = [i for i, s in enumerate(self.mediaInfo['stream']) if s['type'] == 'video']
        if vstreams:
            self.d.videoStreamIndex = vstreams[0]
        else:
            raise RuntimeError('no video stream...')

def main(options):

    pt = playerThread(options.media, options.fullscreen) 
    pt.start()
   
    print 'Playing "%s" ...' % options.media

    mainLoop = True 
    
    while mainLoop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                mainLoop = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    mainLoop = False
    
    pt.stop()
    pt.join()
    print 'Bye!'

if __name__ == '__main__':

    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-m', '--media', help='media input')
    parser.add_option('-f', '--fullscreen', 
            action='store_true',
            help='turn on full screen mode')

    (options, args) = parser.parse_args()

    if not options.media:
        print 'Please provide a media to play with -m option'
        sys.exit(1)

    main(options)

