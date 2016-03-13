#!/usr/bin/env python

'''
Encode image, video or sound from auto generated data

This example can only generate yuv data and s16 audio data; for other
formats the ouput will be a black image or a silent sound

video:
* python -u examples/encoding/encode.py -m foo.avi -t video -c 15

image:
* python -u examples/encoding/encode.py -m foo.tiff -t image

audio:
* python -u examples/encoding/encode.py -m foo.mp2 -t audio -c 15

This is a complex example, see encodeImage.py for simpler code.
'''

import sys
import math
import ctypes

from avpy import Media

# Python3 compat stuff...
def progress(msg):

    ''' Print progress message
    '''

    if sys.version_info >= (3, 0):

        # python3 only - break python2 compat
        #print('\r%s' % msg, end='')
        print('\r%s' % msg),
    else:
        print('\r%s' % msg),

if sys.version_info >= (3, 0):
    xrange = range


class SignalGen(object):

    ''' Single tone sound generator
    '''

    def __init__(self, sampleRate):
        self.t = 0
        self.tincr = 2 * math.pi * 440.0 / sampleRate

    def audioFrame(self, pkt, frameSize, nbChannels):

        samples = ctypes.cast(pkt.frame.contents.data[0],
                ctypes.POINTER(ctypes.c_uint16))

        for j in xrange(frameSize/nbChannels):
            samples[j] = int(math.sin(self.t)*10000)
            
            for k in xrange(1, nbChannels):
                samples[j+k] = samples[2*j]

            self.t += self.tincr


def fillYuvImage(picture, frameIndex, width, height):

    ''' Yuv image generator
    '''

    i = frameIndex

    # Y
    for y in xrange(0, height):
        for x in xrange(0, width):
            picture.contents.data[0][y*picture.contents.linesize[0] + x] = x + y + i*3

    # Cb and Cr
    for y in xrange(0, int(height/2)):
        for x in xrange(0, int(width/2)):
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

    parser.add_option('-c', '--frameCount',
            help='number of frame to encode',
            type='int',
            default=125)
    
    # test only
    parser.add_option('--forceCodec',
            help='force to use codec, audio only')
    parser.add_option('--forceSampleFormat',
            help='force to use sample format, audio only')
    parser.add_option('--forceFmt',
            help='force to use pixel format, image only')

    (options, args) = parser.parse_args() 

    # open
    if options.media:
        
        # setup media encoder
        media = Media(options.media, 'w', quiet=False)
        
        # setup stream info
        if options.mediaType == 'image':

            resolution = (320, 240)

            streamInfoVideo = {
                'width': resolution[0],
                'height': resolution[1],
                }

            # codec auto. guess
            streamInfoVideo['codec'] = 'auto'

            if options.forceFmt:
                streamInfoVideo['pixelFormat'] = options.forceFmt
            else:
                streamInfoVideo['pixelFormat'] = 'rgb24'

            streamIndex = media.addStream('video', streamInfoVideo)
        
            pkt = media.videoPacket()

            # single image -> set frameCount to 1
            options.frameCount = 1

        elif options.mediaType == 'video':
        
            resolution = (320, 240)

            streamInfoVideo = {
                'bitRate': 400000,
                'width': resolution[0],
                'height': resolution[1],
                # 25 fps
                'timeBase': (1, 25),
                'pixelFormat': 'yuv420p',
                }

            streamIndex = media.addStream('video', streamInfoVideo)
        
            pkt = media.videoPacket()

        elif options.mediaType == 'audio':

            streamInfoAudio = {
                    'bitRate': 64000,
                    'sampleRate': 44100,
                    'channels': 2,
                    'codec': 'auto',
                    }

            if options.forceSampleFormat:
                streamInfoAudio['sampleFmt'] = options.forceSampleFormat
            if options.forceCodec:
                streamInfoAudio['codec'] = options.forceCodec
            
            # No generator available if sample format is not signed 16 bit
            # patch welcome!
            if options.forceSampleFormat and options.forceSampleFormat != 's16':
                print('Warning: will generate a silent sound!') 

            streamIndex = media.addStream('audio',
                    streamInfo=streamInfoAudio)

            info = media.info()
            frameSize = info['stream'][0]['frameSize']

            soundGen = SignalGen(streamInfoAudio['sampleRate'])
            pkt = media.audioPacket()

        elif options.mediaType == 'both':

            raise NotImplementedError()

        else:
            raise RuntimeError()

        # see http://multimedia.cx/eggs/supplying-ffmpeg-with-metadata/
        # for available metadata per container
        metadata = {'artist': 'me'}
        media.writeHeader(metadata)
        
        # Presentation TimeStamp (pts)
        pts = 0
        maxFrame = options.frameCount

        while True:

            if options.mediaType == 'image':

                progress('Generating image frame...    ')
                # TODO: need a fillRgbImage
                # patch welcome!
                #fillYuvImage(pkt.frame, i, *resolution) 
                media.write(pkt, pts+1, 'video')
            
            elif options.mediaType == 'video':

                progress('Generating video frame %d/%d...    ' % (pts, maxFrame))
                fillYuvImage(pkt.frame, pts, *resolution) 
                media.write(pkt, pts+1, options.mediaType)

            elif options.mediaType == 'audio':

                progress('Generating audio frame %d/%d...    ' % (pts, maxFrame))
                
                if 'sampleFmt' not in streamInfoAudio or streamInfoAudio['sampleFmt'] == 's16': 
                    soundGen.audioFrame(pkt, frameSize, streamInfoAudio['channels'])

                media.write(pkt, pts+1, options.mediaType) 

            elif options.mediaType == 'both':

                raise NotImplementedError()

            else:
                raise RuntimeError()
           
            pts+=1
            if pts >= maxFrame:
                break

        media.writeTrailer()
        print('done writing %s' % options.media)

