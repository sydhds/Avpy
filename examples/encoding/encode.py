#!/usr/bin/env python

import math

from pyav import Media

class signalGen(object):

    def __init__(self, sampleRate):

        self.t = 0.0
        self.tincr = (2 * math.pi * 110.0) / sampleRate
        self.tincr2 = ((2 * math.pi * 110.0) / sampleRate)/ sampleRate

    def audioFrame(self, samples, frameSize, nbChannels):

        i = 0
        for j in xrange(frameSize):
            v = int(math.sin(self.t)*10000)
            for c in xrange(nbChannels):
                samples[i] = v 
                i += 1

            self.t += self.tincr
            self.tincr += self.tincr2

def fillYuvImage(picture, frameIndex, width, height):

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
        
        elif options.mediaType == 'audio':

            streamInfoAudio = {
                    'bitRate': 64000,
                    'sampleRate': 44100,
                    'channels': 2,
                    'codec': 'auto',
                    }
            streamIndex = m.addStream('audio',
                    streamInfo=streamInfoAudio)

            sg = signalGen(streamInfoAudio['sampleRate'])

        elif options.mediaType == 'both':

            raise NotImplementedError()

        else:
            raise RuntimeError()

        m.writeHeader()
        pkt = m.videoPacket(*resolution)

        i = 0
        while True:

            if options.mediaType == 'video':

                print 'generating video frame %d...' % i
                fillYuvImage(pkt.frame, i, *resolution) 
                print 'done.' 
                m.write(pkt, i+1, options.mediaType)
            
            i+= 1
            if i > 125:
                break

        m.writeTrailer()
        print('done writing %s' % options.media)

