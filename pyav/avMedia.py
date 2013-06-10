'''
High-level libav python API
'''

import os
import ctypes
import av

class Media():

    def __init__(self, mediaName):

        av.lib.av_log_set_level(av.lib.AV_LOG_QUIET)

        # TODO: init lib in a singleton?
        av.lib.av_register_all()
        self.pFormatCtx = ctypes.POINTER(av.lib.AVFormatContext)()
 
        # open media
        res = av.lib.avformat_open_input(self.pFormatCtx, mediaName, None, None)
        if res: 
            raise IOError(avError(res))
        
        # get stream info
        # need this call in order to retrieve duration
        res = av.lib.avformat_find_stream_info(self.pFormatCtx, None)
        if res < 0:
            raise IOError(avError(res))

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
        
        streamInfo = {}
        cCodecCtx = stream.contents.codec
        
        # cCodecCtx.contents.codec is NULL so retrieve codec using id  
        c = av.lib.avcodec_find_decoder(cCodecCtx.contents.codec_id)
        streamInfo['codec'] = c.contents.name

        streamInfo['type'] = 'video' if cCodecCtx.contents.codec_type == av.lib.AVMEDIA_TYPE_VIDEO else 'audio'

        if streamInfo['type'] == 'video':
            streamInfo['width'] = cCodecCtx.contents.width
            streamInfo['height'] = cCodecCtx.contents.height

        return streamInfo

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

        # from http://new.libav.org/doxygen/master/cmdutils_8c_source.html#l00598
        # examples
        # framerates -> Media.codecInfo('mpeg1video', decode=False)
        # samplerates -> Media.codecInfo('mp2', decode=False)
        # pix_fmt -> Media.codecInfo('ffv1', decode=False)
        # profiles -> Media.codecInfo('mpeg4', decode=True)
        # image -> Media.codecInfo('png', decode=True) - Media.codecInfo('gif', decode=True)
        # subtitle -> Media.codecInfo('ass', decode=True)
        
        ci = {}
        
        # init lib
        av.lib.av_register_all()

        if decode:
            c = av.lib.avcodec_find_decoder_by_name(name)
        else:
            c = av.lib.avcodec_find_encoder_by_name(name)

        if c:
            ci['name'] = c.contents.name
            ci['longName'] = c.contents.long_name
            codecType = c.contents.type
            if codecType == av.lib.AVMEDIA_TYPE_VIDEO:
                ci['type'] = 'video'
            elif codecType == av.lib.AVMEDIA_TYPE_AUDIO:
                ci['type'] = 'audio'
            elif codecType == av.lib.AVMEDIA_TYPE_SUBTITLE:
                ci['type'] = 'subtitle'
            else:
                ci['type'] = 'unknown'
            
            # thread caps
            ci['thread'] = None

            ci['framerates'] = []
            ci['samplerates'] = [] 
            ci['pix_fmt'] = []
            ci['profiles'] = []
            
            # thread caps
            caps = c.contents.capabilities & (av.lib.CODEC_CAP_FRAME_THREADS|av.lib.CODEC_CAP_SLICE_THREADS)
            if caps == (av.lib.CODEC_CAP_FRAME_THREADS|av.lib.CODEC_CAP_SLICE_THREADS):
                ci['thread'] = 'frame and slice'
            elif caps == av.lib.CODEC_CAP_FRAME_THREADS:
                ci['thread'] = 'frame'
            elif caps == av.lib.CODEC_CAP_SLICE_THREADS:
                ci['thread'] = 'slice'

            # support auto thread
            ci['auto_thread'] = False
            caps = c.contents.capabilities & (av.lib.CODEC_CAP_AUTO_THREADS)
            if caps == av.lib.CODEC_CAP_AUTO_THREADS:
                ci['auto_thread'] = True

            # supported frame rates
            fps = c.contents.supported_framerates
            if fps:
                for f in fps:
                    if not f.num and not f.den:
                        break
                    ci['framerates'].append((f.num, f.den))
                
            # supported sample rates
            srates = c.contents.supported_samplerates
            if srates:
                for r in srates:
                    if r==0:
                        break
                    ci['samplerates'].append(r)
            
            # supported pixel formats
            pixFmts = c.contents.pix_fmts 
            if pixFmts:
                for p in pixFmts:
                    if p == av.lib.PIX_FMT_NONE:
                        break
                    ci['pix_fmt'].append(av.lib.avcodec_get_pix_fmt_name(p))

            # profiles
            pf = c.contents.profiles
            if pf:
                for p in pf:
                    if not p.name:
                        break
                    ci['profiles'].append(p.name)

        else:
            raise ValueError('Unable to find codec %s' % name)
        

        return ci


def avError(res):

    '''
    Return an error message according to AVERROR code 
    '''

    # cmdutils.c - print_error

    # setup error buffer
    bufSize = 128
    buf = ctypes.create_string_buffer(bufSize) 
    errRes = av.lib.av_strerror(res, buf, bufSize)
    if errRes < 0:
        try:
            msg = os.strerror(res)
        except ValueError:
            msg = 'Unknown error code %d' % res
        
        return msg
    else:
        return buf.value



