#!/usr/bin/env python

'''
Decode audio packets in media and output them using alsa audio API

python alsaPlay.py -m file.avi
'''

import sys
import ctypes
from copy import copy

import alsaaudio

from avpy import Media

if __name__ == '__main__':
   
    # cmdline
    from optparse import OptionParser

    usage = "usage: %prog -m foo.avi"
    parser = OptionParser(usage=usage)
    parser.add_option('-m', '--media', 
            help='play media')
    parser.add_option('--length', 
            help='decode at max seconds of audio',
            type='int',
            default=20)    
    parser.add_option('--copyPacket', 
            action='store_true',
            help='copy packet (debug only)')

    (options, args) = parser.parse_args()

    if not options.media:
        print('Please provide a media to play with -m or --media option')
        sys.exit(1)

    # open media
    media = Media(options.media)
    # dump info
    mediaInfo = media.info()

    # select first audio stream
    astreams = [ i for i, s in enumerate(mediaInfo['stream']) if s['type'] == 'audio' ]
    if astreams:
        astream = astreams[0]
    else:
        print('No audio stream in %s' % mediaInfo['name'])
        sys.exit(2)
    
    # setup alsa output
    # stream index, channel count, sampleRate
    si = mediaInfo['stream'][astream]
    channels = si['channels']
    fe = si['sampleRate']
  
    # S16P -> S16
    sampleFmt = si['sampleFmt'].upper()
    sampleFmt = sampleFmt[:-1] if sampleFmt.endswith('P') else sampleFmt
    aformat=getattr(alsaaudio, 'PCM_FORMAT_%s_%s' % (sampleFmt, 'LE' if sys.byteorder == 'little' else 'BE'))

    out = alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL, card='default')
    out.setchannels(channels)
    out.setrate(fe)
    out.setformat(aformat)

    # Size in bytes required for 1 second of audio
    secondSize = si['channels'] * si['bytesPerSample'] * si['sampleRate']
    decodedSize = 0

    print('playing sound of %s (%s seconds)...' % (options.media, options.length))

    # let's play!
    for i, pkt2 in enumerate(media):
        
        # test only
        if options.copyPacket:
            pkt = copy(pkt2)
        else:
            pkt = pkt2

        if pkt.streamIndex() == astream:
            pkt.decode()
            if pkt.decoded:
                buf = pkt.frame.contents.data[0]
                bufLen = pkt.dataSize
                out.write(ctypes.string_at(buf, bufLen))
               
                decodedSize += bufLen
                # stop after ~ 20s (default)
                # exact time will vary depending on dataSize
                if decodedSize >= options.length*secondSize:
                    break

