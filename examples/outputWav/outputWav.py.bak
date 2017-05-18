#!/usr/bin/env python

'''
Decode 20 seconds of the first audio stream
and output it into a wav file
'''

import sys
import struct
import wave

from avpy import avMedia, Media

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
   
    astreamInfo = mediaInfo['stream'][astream]

    # forge output audio format
    # write a standard stereo 16 bits 44.1 kHz wav file

    # only force sample rate resampling if supported 
    # libav 0.8 does not support audio resampling
    # outSampleRate = astreamInfo['sampleRate']
    outSampleRate = 44100 if avMedia.AVPY_RESAMPLE_SUPPORT else astreamInfo['sampleRate']
    outAudio = {
            'layout': 'stereo', # XXX: channelLayout?
            'channels': 2,
            'sampleRate': outSampleRate,
            'sampleFmt': 's16',
            'bytesPerSample': 2,
            }

    if outAudio['layout'] != astreamInfo['channelLayout'] or\
        outAudio['channels'] != astreamInfo['channels'] or\
        outAudio['sampleFmt'] != astreamInfo['sampleFmt'] or\
        outAudio['sampleRate'] != astreamInfo['sampleRate']:

        inAudio = astreamInfo
        resampler = True

        try:
            media.addResampler(astream, inAudio, outAudio)
        except RuntimeError as e:
            
            print('Could not add an audio resampler: %s' % e)
            sys.exit(3)

    else:
        resampler = False
    
    # setup output wav file
    outputName = 'out.wav'
    wp = wave.open(outputName, 'w') 
    try:
        # nchannels, sampwidth, framerate, nframes, comptype, compname 
        wp.setparams( (outAudio['channels'], 
           outAudio['bytesPerSample'], 
           outAudio['sampleRate'], 
           0, 
           'NONE', 
           'not compressed') )
    except wave.Error as e:
        print('Wrong parameters for wav file: %s' % e)
        sys.exit(1)

    # Size in bytes required for 1 second of audio
    # secondSize = astreamInfo['channels'] * astreamInfo['bytesPerSample'] * astreamInfo['sampleRate']
    secondSize = outAudio['channels'] * outAudio['bytesPerSample'] * outAudio['sampleRate']
    decodedSize = 0

    # iterate over media and decode audio packet
    for pkt in media:

        if pkt.streamIndex() == astream:
            pkt.decode()
            if pkt.decoded:
                print('writing %s bytes...' % pkt.dataSize)
                
                if resampler:
                    audioDump(pkt.resampledFrame.contents.data[0], 
                            pkt.rDataSize)
                    decodedSize += pkt.rDataSize
                else:
                    audioDump(pkt.frame.contents.data[0],
                            pkt.dataSize)
                    decodedSize += pkt.dataSize

                # stop after ~ 20s (default)
                # exact time will vary depending on dataSize
                if decodedSize >= options.length*secondSize:
                    break

    # all audio data have been decoded - write file
    writeWav(wp)
    print('writing %s done!' % outputName) 

