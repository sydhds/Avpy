#!/usr/bin/env python

'''
Decode 20 seconds of the first audio stream
and output it into a wav file
'''

import sys
import struct
import wave

from avpy import Media

# wav data (see audioDump)
waveData = []

def audioDump2(buf, bufLen):

    ''' Store audio data
    '''

    # TODO: unused, remove?

    global waveData	
    for i in range(bufLen):
        waveData.append(struct.pack('B', buf[i]))

def audioDump(buf, bufLen):

    ''' Store audio data 

    .. note:: faster than audioDump2
    '''

    import ctypes
    global waveData	
    waveData.append(ctypes.string_at(buf, bufLen))

def writeWav(wp):

    ''' Write wav file
    '''

    global waveData
   
    sep = ''.encode('ascii')

    # write data to wav object
    wp.writeframes(sep.join(waveData))
    wp.close()

if __name__ == '__main__':
    
    # cmdline
    from optparse import OptionParser

    usage = "usage: %prog -m foo.avi"
    parser = OptionParser(usage=usage)
    parser.add_option('-m', '--media', 
            help='play media')
    parser.add_option('-l', '--length', 
            help='decode at max seconds of audio',
            type='int',
            default=20)
    
    (options, args) = parser.parse_args()

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
    
    # setup output wav file
    outputName = 'out.wav'
    wp = wave.open(outputName, 'w')
    
    astreamInfo = mediaInfo['stream'][astream]
    
    try:
        # nchannels, sampwidth, framerate, nframes, comptype, compname 
        wp.setparams( (astreamInfo['channels'], 
           astreamInfo['bytesPerSample'], 
           astreamInfo['sampleRate'], 
           0, 
           'NONE', 
           'not compressed') )
    except wave.Error as e:
        print('Wrong parameters for wav file: %s' % e)
        sys.exit(1)

    # Size in bytes required for 1 second of audio
    secondSize = astreamInfo['channels'] * astreamInfo['bytesPerSample'] * astreamInfo['sampleRate']
    decodedSize = 0

    # iterate over media and decode audio packet
    for pkt in media:

        if pkt.streamIndex() == astream:
            pkt.decode()
            if pkt.decoded:
                print('writing %s bytes...' % pkt.dataSize)
                audioDump(pkt.frame.contents.data[0], pkt.dataSize)
                
                decodedSize += pkt.dataSize
                # stop after ~ 90s (default)
                # exact time will vary depending on dataSize
                if decodedSize >= options.length*secondSize:
                    break

    # all audio data have been decoded - write file
    writeWav(wp)
    print('writing %s done!' % outputName) 

