#!/usr/bin/env python

'''
Decode audio packets in media and output them using alsa audio API

python alsaPlay.py -m file.avi
'''

import sys
import ctypes
from copy import copy

import alsaaudio

from pyav import Media

if __name__ == '__main__':
    
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-m', '--media', help='play media')

    (options, args) = parser.parse_args()

    if not options.media:
        print 'Please provide a media to play with -m or --media option'
        sys.exit(1)

    # open media
    m = Media(options.media)
    # dump info
    mediaInfo = m.info()

    # select first audio stream
    astreams = [ i for i, s in enumerate(mediaInfo['stream']) if s['type'] == 'audio' ]
    if astreams:
        astream = astreams[0]
    else:
        print 'No audio stream in %s' % mediaInfo['name']
        sys.exit(2)
    
    # setup alsa output
    si = mediaInfo['stream'][astream]
    channels = si['channels']
    fe = si['sample_rate']
    
    aformat=getattr(alsaaudio, 'PCM_FORMAT_%s_%s' % (si['sample_fmt'].upper(), 'LE' if sys.byteorder == 'little' else 'BE'))

    out = alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL, card='default')
    out.setchannels(channels)
    out.setrate(fe)
    out.setformat(aformat)

    # let's play!
    for i, p2 in enumerate(m):
        
        # TODO: add --copyPacket option (debug only)
        p = copy(p2)

        if p.streamIndex() == astream:
            p.decode()
            if p.decoded:
                buf = p.frame.contents.data[0]
                bufLen = p.dataSize
                out.write(ctypes.string_at(buf, bufLen))
                
                # TODO: stop after a given number of seconds            
                if i > 5000:
                    break
