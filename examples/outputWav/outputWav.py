#!/usr/bin/env python

'''
Decode 5000 packets of the first audio stream
and output it into a wav file
'''

import sys
import struct
import wave

from pyav import Media

waveData = []
def audioDump2(buf, bufLen):

    global waveData	
    for i in range(bufLen):
        waveData.append(struct.pack('B', buf[i]))

# faster than audioDump2
def audioDump(buf, bufLen):
    
    import ctypes
    global waveData	
    waveData.append(ctypes.string_at(buf, bufLen))

def writeWav(wp):

    global waveData
    # write data to wav object
    wp.writeframes(''.join(waveData))
    wp.close()

if __name__ == '__main__':
    
    # cmdline
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option('-m', '--media', 
            help='play media')
    
    (options, args) = parser.parse_args()

    m = Media(options.media)
    # dump info
    mediaInfo = m.info()

    # prepare wav file
    wp = wave.open('out.wav', 'w')
    # FIXME: hardcoded value
    wp.setparams( (2, 2, 48000, 0, 'NONE', 'not compressed') )

    # select first audio stream
    astreams = [ i for i, s in enumerate(mediaInfo['stream']) if s['type'] == 'audio' ]
    if astreams:
        astream = astreams[0]
    else:
        print 'No audio stream in %s' % mediaInfo['name']
        sys.exit(1)

    for i, p in enumerate(m):

        if p.streamIndex() == astream:
            p.decode()
            if p.decoded:
                # find a way to retrieve data after decoding
                print 'writing %s bytes...' % p.dataSize
                audioDump(p.frame.contents.data[0], p.dataSize)
                if i > 5000:
                    break

    writeWav(wp)
