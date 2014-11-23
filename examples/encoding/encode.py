#!/usr/bin/env python

import sys
import math
import ctypes

from pyav import Media

class signalGen(object):

    ''' Single tone sound generator
    '''

    def __init__(self, sampleRate):
        self.t = 0
        self.tincr = 2 * math.pi * 440.0 / sampleRate

    def audioFrame(self, pkt, frameSize, nbChannels):

        samples = ctypes.cast(pkt.frame.contents.data[0],
                ctypes.POINTER(ctypes.c_uint16))

        for j in xrange(frameSize):
            samples[2*j] = int(math.sin(self.t)*10000)
            
            for k in xrange(1, nbChannels):
                samples[2*j+k] = samples[2*j]

            self.t += self.tincr

def fillYuvImage(picture, frameIndex, width, height):

    ''' quad image generator
    '''

    i = frameIndex;

    # Y
    for y in range(0, height):
        for x in range(0, width):
            picture.contents.data[0][y*picture.contents.linesize[0] + x] = x + y + i*3

    # Cb and Cr
    for y in range(0, height/2):
        for x in range(0, width/2):
            picture.contents.data[1][y * picture.contents.linesize[1] + x] = 128 + y + i * 2
            picture.contents.data[2][y * picture.contents.linesize[2] + x] = 64 + x + i * 5

if __name__ == '__main__':

    # cmdline
    from optparse import OptionParser

    usage = "usage: %prog -m foo.avi"
    parser = OptionParser(usage=usage)
    parser.add_option('-m', '--media', 
            help='play media')
    parser.add_option('-t', '--mediaType',
            help='media type: video, audio, both')

    (options, args) = parser.parse_args() 

    # open
    if options.media:
        
        m = Media(options.media, 'w')
        
        if options.mediaType == 'video':
        
            resolution = (320, 240)

            streamInfoVideo = {
                'bitRate': 400000,
                'width': resolution[0],
                'height': resolution[1],
                'timeBase': (1, 25),
                'pixelFormat': 'yuv420p',
                }

            streamIndex = m.addStream('video', streamInfoVideo)
        
            pkt = m.videoPacket(*resolution)

        elif options.mediaType == 'audio':

            streamInfoAudio = {
                    'bitRate': 64000,
                    'sampleRate': 44100,
                    'channels': 2,
                    'codec': 'auto',
                    }
            streamIndex = m.addStream('audio',
                    streamInfo=streamInfoAudio)

            info = m.info()
            frameSize = info['stream'][0]['frame_size']

            sg = signalGen(streamInfoAudio['sampleRate'])
            pkt = m.audioPacket(streamInfoAudio['channels'])

        elif options.mediaType == 'both':

            raise NotImplementedError()

        else:
            raise RuntimeError()

        m.writeHeader()

        i = 0
        maxFrame = 125

        while True:

            if options.mediaType == 'video':

                print('\rgenerating video frame %d (/%d)...    ' % (i, maxFrame)),
                fillYuvImage(pkt.frame, i, *resolution) 
                m.write(pkt, i+1, options.mediaType)

            elif options.mediaType == 'audio':

                # FIXME frame size
                print('\rgenerating audio frame %d (/%d)...    ' % (i, maxFrame)),
                sg.audioFrame(pkt, frameSize, streamInfoAudio['channels'])

                m.write(pkt, i+1, options.mediaType) 

            elif options.mediaType == 'both':

                raise NotImplementedError()

            else:
                raise RuntimeError()
           
            i+= 1
            if i > maxFrame:
                break

        m.writeTrailer()
        print('done writing %s' % options.media)

