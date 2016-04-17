import os
import array
import ctypes
import wave

from avpy import avMedia

from nose.tools import assert_less

def ptrAdd(ptr, offset):

    ''' C pointer add
    '''

    address = ctypes.addressof(ptr.contents) + offset
    return ctypes.pointer(type(ptr.contents).from_address(address))

class TestEncoding(object):

    def compareData(self, frame, w, h, colorTpl):

        ''' Compare frame content
        '''

        # TODO
        # optim -> use memcmp?

        # 1 linesize
        # _a = array.array('B', [109, 219, 1]*(w))
        _a = array.array('B', colorTpl*(w))
        a = array.array('B', [0]*(w*3))
        
        for i in range(h):
            ptr = ptrAdd(frame.contents.data[0], i*frame.contents.linesize[0])
            ctypes.memmove(a.buffer_info()[0], ptr, w*3)
            if _a != a:
                return False

        return True

    def fillRgb(self, frame, width, height):

        linesize = frame.contents.linesize[0]
        for i in range(0, height):
            for j in range(0, width):
                frame.contents.data[0][i*linesize+j*3] = 109 
                frame.contents.data[0][i*linesize+j*3+1] = 219
                frame.contents.data[0][i*linesize+j*3+2] = 1

    def testImage(self):

        # write image then read it and test data

        # TODO: temp dir --> from TOX or gen a new one?
        mediaName = '/tmp/foo.tiff'
        # FIXME: invalid argument with .tga?
        #mediaName = '/tmp/blah.tga'

        w = 160
        h = 120

        media = avMedia.Media(mediaName, 'w', quiet=False)
        
        resolution = (w, h)

        streamInfoVideo = {
            'width': resolution[0],
            'height': resolution[1],
            }

        # codec auto. guess
        streamInfoVideo['codec'] = 'auto'
        streamInfoVideo['pixelFormat'] = 'rgb24'

        streamIndex = media.addStream('video', streamInfoVideo)
    
        pkt = media.videoPacket()

        # see http://multimedia.cx/eggs/supplying-ffmpeg-with-metadata/
        # for available metadata per container
        metadata = {'artist': 'me'}
        media.writeHeader(metadata)
        
        # Presentation TimeStamp (pts)
        pts = 0
        #maxFrame = 1

        self.fillRgb(pkt.frame, *resolution)
        media.write(pkt, pts+1, 'video')

        media.writeTrailer()

        # writing done
        # now read image and check data

        assert(os.path.exists(mediaName))
        assert(os.path.getsize(mediaName) > 0)

        media2 = avMedia.Media(mediaName)
        mediaInfo = media2.info()
        vstream = 0
        streamInfo = mediaInfo['stream'][vstream]
        
        assert streamInfo['width'] == w
        assert streamInfo['height'] == h

        media2.addScaler(vstream, w, h)

        for pkt in media2:
            if pkt.streamIndex() == vstream:
                pkt.decode()
                if pkt.decoded:
                    frame = pkt.swsFrame
                    assert self.compareData(frame, w, h, (109, 219, 1))
                    break

    def testWav(self):

        # write wav then read it and test data

        mediaName = '/tmp/foo.wav'
        
        media = avMedia.Media(mediaName, 'w', quiet=False)

        streamInfoAudio = {
                'bitRate': 64000, # XXX: compute it, why 64000?
                'sampleRate': 44100,
                'channels': 2,
                'codec': 'auto',
                }

        streamIndex = media.addStream('audio', streamInfoAudio)
    
        pkt = media.audioPacket()
        
        info = media.info()
        si = info['stream'][0]
        frameSize = info['stream'][0]['frameSize']
    
        # size in bytes for 1 second of audio
        secondSize = si['channels'] * si['bytesPerSample'] * si['sampleRate']

        # write ~ 1s of audio
        nFrame = float(secondSize)/float(frameSize)
        nFrameInt = int(round(nFrame))

        # TODO: check with empty dict or None
        metadata = {'artist': 'me'}
        media.writeHeader(metadata)
        
        # Presentation TimeStamp (pts)
        pts = 0

        for i in range(nFrameInt):

            for i in range(int(frameSize/4)):
                # write 
                # 1 - 255 (left channel)
                # 250 - 253 (right channel)
                pkt.frame.contents.data[0][i*4] = 1
                pkt.frame.contents.data[0][i*4+1] = 255
                pkt.frame.contents.data[0][i*4+2] = 250
                pkt.frame.contents.data[0][i*4+3] = 254

            media.write(pkt, pts+1, 'audio')
            pts += 1

        media.writeTrailer()

        # read wav

        wp = wave.open(mediaName) 
        
        # check ffmpeg info against wave info
        frames = wp.getnframes()
        rate = wp.getframerate()
        
        assert wp.getnchannels() == si['channels']
        assert rate == si['sampleRate']
        assert wp.getsampwidth() == si['bytesPerSample']

        duration = frames / float(rate)
       
        assert(duration > 0)

        if nFrame != nFrameInt:
            # assert abs(1.0 - duration) < 0.01
            assert_less(abs(1.0 - duration), 0.01)
        else:
            assert duration == 1.0

        # note: for wave module, a frame is equivalent of
        # 1 sample of audio 
        # so here: 4 bytes (2 channels * 2 bytes per channel)
        wpFrame = wp.readframes(1)
        wpFrameCount = 0
        while wpFrame:
            # 01 - 255 - 250 - 254
            if avMedia.PY3:
                assert wpFrame == b'\x01\xff\xfa\xfe'
            else:
                assert wpFrame == '\x01\xff\xfa\xfe'
            wpFrameCount += 1
            wpFrame = wp.readframes(1)
        
        assert wpFrameCount / nFrameInt == frameSize / (si['channels'] * si['bytesPerSample'])

    def testImageArray(self):

        # write image then read it and test data

        mediaName = '/tmp/fooArray.tiff'

        w = 8
        h = 8

        resolution = (w, h)

        streamInfo = {
            'width': resolution[0],
            'height': resolution[1],
            'codec': 'auto',
            'pixelFormat': 'rgb24',
            'type': 'video',
            }

        # codec auto. guess

        a = array.array('B')
        colorTuple = [11, 128, 255]
        a.fromlist(colorTuple*w*h)
        
        with avMedia.Media.open(mediaName, 'w', streamsInfo=[streamInfo]) as m:
            m.write(a, 1, 'video')

        assert(os.path.exists(mediaName))
        assert(os.path.getsize(mediaName) > 0)

        media2 = avMedia.Media(mediaName)
        mediaInfo = media2.info()
        vstream = 0
        streamInfo = mediaInfo['stream'][vstream]
        
        assert streamInfo['width'] == w
        assert streamInfo['height'] == h

        media2.addScaler(vstream, w, h)

        for pkt in media2:
            if pkt.streamIndex() == vstream:
                pkt.decode()
                if pkt.decoded:
                    frame = pkt.swsFrame

                    assert self.compareData(frame, w, h, colorTuple)

                    break

