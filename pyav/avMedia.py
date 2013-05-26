'''
High-level libav python API
'''

import ctypes
import av

class Media():

    def __init__(self, mediaName):

        # TODO: init lib in a singleton?
        av.lib.av_register_all()
        self.pFormatCtx = ctypes.POINTER(av.lib.AVFormatContext)()

        if av.lib.avformat_open_input(self.pFormatCtx, mediaName, None, None):
            raise IOError('Unable to open %s' % mediaName)

        # need this call in order to retrieve duration
        if av.lib.avformat_find_stream_info(self.pFormatCtx, None) < 0:
        #if av.lib.av_find_stream_info(self.pFormatCtx) < 0:
            raise IOError('Unable to retrieve stream info')

    def info(self):

        '''
        return a dict with media information

        duration: media duration in seconds
        name: media filename
        stream: list of stream info (dict)
        '''

        infoDict = {}
        infoDict['name'] = self.pFormatCtx.contents.filename
        infoDict['metadata'] = self.metadata()
        infoDict['stream'] = [] 
        infoDict['duration'] = self.pFormatCtx.contents.duration / av.lib.AV_TIME_BASE

        for i in range(self.pFormatCtx.contents.nb_streams):
            cStream = self.pFormatCtx.contents.streams[i]
            cStreamInfo = self._streamInfo(cStream)
            infoDict['stream'].append(cStreamInfo)

        return infoDict

    def _streamInfo(self, stream):
        
        streamDict = {}
        
        cCodec = stream.contents.codec

        streamDict['type'] = 'video' if cCodec.contents.codec_type == av.lib.AVMEDIA_TYPE_VIDEO else 'audio'

        if streamDict['type'] == 'video':
                streamDict['width'] = cCodec.contents.width
                streamDict['height'] = cCodec.contents.width

        return streamDict

    def metadata(self):

        '''
        get metadata

        @return : a dict with key, value = metadata key, metadata value
        '''

        done = False
        metaDict = {}
        tag = ctypes.POINTER(av.lib.AVDictionaryEntry)()

        while not done:
            tag = av.lib.av_dict_get(self.pFormatCtx.contents.metadata, "", tag, av.lib.AV_DICT_IGNORE_SUFFIX)
            if tag:
                metaDict[tag.contents.key] = tag.contents.value
            else:
                done = True

        return metaDict

    @staticmethod
    def formats():

        '''
        return a dict with 2 keys: encoding & decoding

        each key value is a dict: key=format name, value: format long name
        '''

        # port of show_formats function (cf cmdutils.c)

        f = {'encoding': {}, 'decoding': {}}

        av.lib.av_register_all()
        ifmt  = None
        ofmt = None

        while 1:
            ofmt = av.lib.av_oformat_next(ofmt)
            if ofmt:
                f['encoding'][ofmt.contents.name] = ofmt.contents.long_name
            else:
                break

        while 1:
            ifmt = av.lib.av_iformat_next(ifmt)
            if ifmt:
                f['decoding'][ifmt.contents.name] = ifmt.contents.long_name
            else:
                break

        return f

    @staticmethod
    def codecInfo(name, decode=True):

        '''
        set decode to False to get codec encoder info
        '''

        ci = {}

        av.lib.av_register_all()
        if decode:
            c = av.lib.avcodec_find_decoder_by_name(name)
        else:
            c = av.lib.avcodec_find_encoder_by_name(name)

        if c:
            ci['decoder'] = None
            ci['name'] = c.contents.name
            ci['longName'] = c.contents.long_name
            ci['threads'] = None

            ci['framerates'] = []
            fps = c.contents.supported_framerates
            if fps:
                i=0
                f = fps[i]
                while f.num:
                    ci['framerates'].append('%d/%d' % (f.num, f.den))

            ci['pix_fmt'] = []
            pixFmts = c.contents.pix_fmts 
            if pixFmts:
                i = 0
                p = pixFmts[i]
                while p != av.lib.PIX_FMT_NONE:
                    ci['pix_fmt'].append(av.lib.avcodec_get_pix_fmt_name(p))
                    i += 1
                    p = pixFmts[i]
        else:
            raise ValueError('Unable to find codec %s' % name)
        
        # TODO --> http://new.libav.org/doxygen/master/cmdutils_8c_source.html#l00598

        return ci

