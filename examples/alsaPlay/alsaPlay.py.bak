#!/usr/bin/env python

'''
Decode audio packets in media and output them using alsa audio API

python alsaPlay.py -m file.avi
'''

import sys
import ctypes

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
   
    # forge output audio format
    si = mediaInfo['stream'][astream]
    outAudio = {
            'layout': 'stereo',
            'channels': 2,
            'sampleRate': si['sampleRate'], # keep original sample rate
            'sampleFmt': 's16',
            'bytesPerSample': 2,
            }

    if outAudio['layout'] != si['channelLayout'] or\
        outAudio['channels'] != si['channels'] or\
        outAudio['sampleFmt'] != si['sampleFmt'] or\
        outAudio['sampleRate'] != si['sampleRate']:

        resampler = True

        try:
            media.addResampler(astream, si, outAudio)
        except RuntimeError as e:
            
            print('Could not add an audio resampler: %s' % e)
            sys.exit(3)

    else:
        resampler = False

    sampleFmt = outAudio['sampleFmt'].upper()
    alsaFmt = 'PCM_FORMAT_%s_%s' % (sampleFmt, 'LE' if sys.byteorder == 'little' else 'BE')
    aformat=getattr(alsaaudio, alsaFmt)

    out = alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL, card='default')
    out.setchannels(outAudio['channels'])
    out.setrate(outAudio['sampleRate'])
    out.setformat(aformat)

    # Size in bytes required for 1 second of audio
    secondSize = outAudio['channels'] * outAudio['bytesPerSample'] * outAudio['sampleRate']
    decodedSize = 0

    print('playing sound of %s (%s seconds)...' % (options.media, options.length))

    # let's play!
    for i, pkt in enumerate(media):
        
        if pkt.streamIndex() == astream:
            pkt.decode()
            if pkt.decoded:
                buf = pkt.resampledFrame.contents.data[0]
                bufLen = pkt.rDataSize
                out.write(ctypes.string_at(buf, bufLen))
               
                decodedSize += bufLen
                # stop after ~ 20s (default)
                # exact time will vary depending on rDataSize
                if decodedSize >= options.length*secondSize:
                    break

