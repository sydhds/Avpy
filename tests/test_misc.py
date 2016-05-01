import os
from avpy import avMedia 

class TestMediaInfo(object):

    # test avMedia.Media.info call

    def test(self):

        mediaName = os.environ['BBB_MOVIE']
        media = avMedia.Media(mediaName, quiet=False)
        infoDict = media.info() 
        #print(infoDict)
        assert infoDict['name'] == mediaName
        assert 'mov' in infoDict['format']
        assert infoDict['stream'][0]['type'] == 'video'
        assert infoDict['stream'][0]['width'] == 320
        assert infoDict['stream'][0]['height'] == 180
        assert infoDict['stream'][1]['type'] == 'audio'
        assert infoDict['stream'][1]['channels'] == 2
        # FIXME
        #assert infoDict['stream'][1]['channelLayout'] == 'stereo'

class TestVersion(object):

    # test avMedia.versions call

    def test(self):
        
        #import os
        #print os.environ['AVPY_AVCODEC']
        #print os.environ['LD_LIBRARY_PATH']
        v = avMedia.versions() 
        assert v['libavcodec']['path'] != ''

class TestFormats(object):

    # test avMedia.formats call

    def test(self):

        f = avMedia.formats()

        assert f['muxing']['avi']
        #print(f['muxing']['avi'])
        assert f['muxing']['avi'] in ['AVI format', 'AVI (Audio Video Interleaved)']
        assert f['demuxing']['avi']
        #print(f['demuxing']['avi'])
        assert f['demuxing']['avi'] in ['AVI format', 'AVI (Audio Video Interleaved)']

class TestCodecInfo(object):

    # test codecInfo call 

    def test_video(self):

        ci = avMedia.codecInfo('mpeg2video')
        assert ci['name'] == 'mpeg2video'
        assert ci['longName'] == 'MPEG-2 video'
        assert ci['type'] == 'video'

    def test_audio(self):

        ci = avMedia.codecInfo('mp3')
        assert ci['name'] == 'mp3'
        assert ci['longName'] == 'MP3 (MPEG audio layer 3)'
        assert ci['type'] == 'audio'

class TestCodecs(object):

    def test(self):

        c = avMedia.codecs()
        from pprint import pprint
        # pprint(c['video']['encoding'])
        # TODO: add more tests
        assert 'mpeg1video' in c['video']['decoding']
        assert 'mpeg2video' in c['video']['encoding']

        # pprint(c['audio'])
        # pprint(c['subtitle'])

        assert 'mp1' in c['audio']['decoding']
        assert 'mp2' in c['audio']['encoding']

        assert 'srt' in c['subtitle']['decoding']

