import os
import copy
import array
import ctypes

from avpy import avMedia 

def ptrAdd(ptr, offset):

    ''' C pointer add
    '''

    address = ctypes.addressof(ptr.contents) + offset
    return ctypes.pointer(type(ptr.contents).from_address(address))

class TestOutput(object):

    def compareData(self, frame, w, h):

        ''' Compare frame content
        '''

        # TODO
        # optim -> use memcmp?

        # 1 linesize
        _a = array.array('B', [146, 219, 109]*(w))
        a = array.array('B', [0]*(w*3))
        
        for i in range(h):
            ptr = ptrAdd(frame.contents.data[0], i*frame.contents.linesize[0])
            ctypes.memmove(a.buffer_info()[0], ptr, w*3)
            if _a != a:
                return False

        return True

    def compareAudioData(self, frame, dataSize):

        # 16 bits data
        _a = array.array('B', [1, 0, 2, 0]*int(dataSize/4))
        a = array.array('B', [0]*(dataSize))
       
        ptr = frame.contents.data[0]
        ctypes.memmove(a.buffer_info()[0], ptr, dataSize)
        if _a != a:
            return False

        return True

    def testImage(self):

        mediaName = os.environ['TIFF_IMAGE']
        media = avMedia.Media(mediaName)
        mediaInfo = media.info()

        # retrieve video width and height
        vstream = 0 # video stream index
        streamInfo = mediaInfo['stream'][vstream]
        w, h = streamInfo['width'], streamInfo['height']

        # output rgb24 (24 bits)
        media.addScaler(vstream, w, h)

        for pkt in media:
            if pkt.streamIndex() == vstream:
                pkt.decode()
                if pkt.decoded:

                    frame = pkt.swsFrame
                    assert self.compareData(frame, w, h) 

                    # only 1 frame here
                    break

    def testAudio(self):

        mediaName = os.environ['CONSTANT_WAV']
        media = avMedia.Media(mediaName)
        mediaInfo = media.info()

        astream = 0 # audio stream index
        streamInfo = mediaInfo['stream'][astream]

        for pkt in media:
            if pkt.streamIndex() == astream:
                pkt.decode()
                if pkt.decoded:

                    frame = pkt.frame
                    assert self.compareAudioData(frame, pkt.dataSize) 
    
    def testCopyPacket(self):

        mediaName = os.environ['CONSTANT_WAV']
        media = avMedia.Media(mediaName)
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

