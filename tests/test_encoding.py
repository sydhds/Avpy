import array
import ctypes

from avpy import avMedia

def ptrAdd(ptr, offset):

    ''' C pointer add
    '''

    address = ctypes.addressof(ptr.contents) + offset
    return ctypes.pointer(type(ptr.contents).from_address(address))

class TestEncoding(object):

    def compareData(self, frame, w, h):

        ''' Compare frame content
        '''

        # TODO
        # optim -> use memcmp?

        # 1 linesize
        _a = array.array('B', [109, 219, 1]*(w))
        a = array.array('B', [0]*(w*3))
        
        for i in range(h):
            ptr = ptrAdd(frame.contents.data[0], i*frame.contents.linesize[0])
            ctypes.memmove(a.buffer_info()[0], ptr, w*3)
            if _a != a:
                return False

        return True

    def fillRgb(self, frame, width, height):

        linesize = frame.contents.linesize[0]
        for i in xrange(0, height):
            for j in xrange(0, width):
                frame.contents.data[0][i*linesize+j*3] = 109 
                frame.contents.data[0][i*linesize+j*3+1] = 219
                frame.contents.data[0][i*linesize+j*3+2] = 1

    def testImage(self):

        # write image then read it and test data

        # TODO: temp dir --> from TOX or gen a new one?
        mediaName = '/tmp/blah.tiff'
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
                    assert self.compareData(frame, w, h)
                    break

