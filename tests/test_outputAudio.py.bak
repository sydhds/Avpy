import os
import copy
import array
import ctypes
import wave

from avpy import avMedia 

class TestAudio(object):

    def compareAudioData(self, frame, dataSize):

        # 16 bits data
        _a = array.array('B', [1, 0, 2, 0]*int(dataSize/4))
        a = array.array('B', [0]*(dataSize))
       
        ptr = frame.contents.data[0]
        ctypes.memmove(a.buffer_info()[0], ptr, dataSize)
        if _a != a:
            return False

        return True

    def testAudio(self):

        mediaName = os.environ['CONSTANT_WAV']
        media = avMedia.Media(mediaName, quiet=False)
        mediaInfo = media.info()

        astream = 0 # audio stream index
        streamInfo = mediaInfo['stream'][astream]

        wp = wave.open(mediaName) 
        
        # check ffmpeg info against wave info
        frames = wp.getnframes()
        rate = wp.getframerate()
        assert wp.getnchannels() == streamInfo['channels']
        assert rate == streamInfo['sampleRate']
        assert wp.getsampwidth() == streamInfo['bytesPerSample']
        duration = frames / float(rate)
        assert duration == mediaInfo['duration']

        # size in bytes for 1 second of audio
        secondSize = streamInfo['channels'] * streamInfo['bytesPerSample'] * streamInfo['sampleRate']

        decodedSize = 0
        for pkt in media:
            if pkt.streamIndex() == astream:
                pkt.decode()
                if pkt.decoded:

                    frame = pkt.frame
                    decodedSize += pkt.dataSize
                    assert self.compareAudioData(frame, pkt.dataSize) 

        # check total decoded size
        # TODO: check with wav of len 2.1s
        assert secondSize * duration == decodedSize 

    def testAudioResampling(self):

        mediaName = os.environ['CONSTANT_WAV']
        media = avMedia.Media(mediaName, quiet=False)
        mediaInfo = media.info()

        astream = 0 # audio stream index
        streamInfo = mediaInfo['stream'][astream]
        
        if not avMedia.AVPY_RESAMPLE_SUPPORT:

            print('No resampling support, test disabled.')
            return

        wp = wave.open(mediaName) 
        
        # check ffmpeg info against wave info
        frames = wp.getnframes()
        rate = wp.getframerate()
        assert wp.getnchannels() == streamInfo['channels']
        assert rate == streamInfo['sampleRate']
        assert wp.getsampwidth() == streamInfo['bytesPerSample']
        duration = frames / float(rate)
        assert duration == mediaInfo['duration']
        
        # inital sample rate / 2
        outSampleRate = 22050 
        outAudio = {
            'layout': 'stereo', # XXX: channelLayout?
            'channels': 2,
            'sampleRate': outSampleRate,
            'sampleFmt': 's16',
            'bytesPerSample': 2,
            }
        
        hasResampler = media.addResampler(astream, streamInfo, outAudio)

        assert hasResampler

        # size in bytes for 1 second of audio
        secondSize = outAudio['channels'] * outAudio['bytesPerSample'] * outAudio['sampleRate']
        
        decodedSize = 0
        for pkt in media:
            if pkt.streamIndex() == astream:
                
                pkt.decode()
                if pkt.decoded:

                    frame = pkt.resampledFrame
                    decodedSize += pkt.rDataSize
                    assert self.compareAudioData(frame, pkt.rDataSize) 
        
        expectedSize = duration*secondSize
        print('decodedSize', decodedSize)
        print('expectedSize', expectedSize)
        print('frame size', streamInfo['frameSize'])
        secondsDiff = float(expectedSize-decodedSize)/secondSize
        print('diff (in seconds)', secondsDiff) 
        # XXX: accept a small margin error for now
        # wondering if this is normal or not...
        assert secondsDiff < 0.01

    def testCopyPacket(self):

        mediaName = os.environ['CONSTANT_WAV']
        media = avMedia.Media(mediaName, quiet=False)
        mediaInfo = media.info()

        astream = 0 # audio stream index
        streamInfo = mediaInfo['stream'][astream]

        for pkt in media:
            if pkt.streamIndex() == astream:
                
                pkt2 = copy.copy(pkt)
                
                pkt2.decode()
                if pkt2.decoded:

                    frame = pkt2.frame
                    assert self.compareAudioData(frame, pkt2.dataSize) 

