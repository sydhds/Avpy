'''
High-level libav python API
'''

import os
import ctypes
import av

class Media(object):

    def __init__(self, mediaName, mode='r'):
        
        av.lib.av_log_set_level(av.lib.AV_LOG_QUIET)

        av.lib.av_register_all()
        self.pFormatCtx = ctypes.POINTER(av.lib.AVFormatContext)()

        if mode == 'r':
            
            # prevent coredump
            if mediaName is None:
                mediaName = ''
            
            # open media for reading
            res = av.lib.avformat_open_input(self.pFormatCtx, mediaName, None, None)
            if res: 
                raise IOError(avError(res))
            
            # get stream info
            # need this call in order to retrieve duration
            res = av.lib.avformat_find_stream_info(self.pFormatCtx, None)
            if res < 0:
                raise IOError(avError(res))
       
        elif mode == 'w':
            raise NotImplementedError('no write support') 

        self.pkt = None

    def __del__(self):

        for i in range(self.pFormatCtx.contents.nb_streams):
            cStream = self.pFormatCtx.contents.streams[i]
            av.lib.avcodec_close(cStream.contents.codec)

        av.lib.avformat_close_input(self.pFormatCtx)

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
            if cStreamInfo:
                infoDict['stream'].append(cStreamInfo)

        return infoDict

    def _streamInfo(self, stream):
        
        streamInfo = {}
        cCodecCtx = stream.contents.codec
        
        # cCodecCtx.contents.codec is NULL so retrieve codec using id  
        # avcodec_find_decoder can return a null value: AV_CODEC_ID_FIRST_UNKNOWN 
        c = av.lib.avcodec_find_decoder(cCodecCtx.contents.codec_id)
        
        if c:
            streamInfo['codec'] = c.contents.name

        codecType = cCodecCtx.contents.codec_type
        if codecType == av.lib.AVMEDIA_TYPE_VIDEO:
            streamInfo['type'] = 'video'
            streamInfo['width'] = cCodecCtx.contents.width
            streamInfo['height'] = cCodecCtx.contents.height
            streamInfo['fps'] = (cCodecCtx.contents.time_base.num, 
                    cCodecCtx.contents.time_base.den, 
                    cCodecCtx.contents.ticks_per_frame) 
        elif codecType == av.lib.AVMEDIA_TYPE_AUDIO:
            streamInfo['type'] = 'audio'
            streamInfo['sample_rate'] = cCodecCtx.contents.sample_rate
            streamInfo['channels'] = cCodecCtx.contents.channels
            streamInfo['sample_fmt'] = av.lib.av_get_sample_fmt_name(cCodecCtx.contents.sample_fmt)
            streamInfo['bytes_per_sample'] = av.lib.av_get_bytes_per_sample(cCodecCtx.contents.sample_fmt)
        elif codecType == av.lib.AVMEDIA_TYPE_SUBTITLE:
            streamInfo['type'] = 'subtitle'
            streamInfo['subtitle_header'] = ctypes.string_at(cCodecCtx.contents.subtitle_header,
                    cCodecCtx.contents.subtitle_header_size)
        else:
            pass
        
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
    def codecs():

        codecs = {
                'audio': {'decoding': [], 'encoding': []},
                'video': {'decoding': [], 'encoding': []},
                'subtitle': {'decoding': [], 'encoding': []},
            } 
        
        av.lib.av_register_all()
        c  = None
        
        while 1:
            c = av.lib.av_codec_next(c)
            if c :

                codecName = c.contents.name

                key1 = ''
                if c.contents.type == av.lib.AVMEDIA_TYPE_VIDEO:
                    key1 = 'video'                  
                elif c.contents.type == av.lib.AVMEDIA_TYPE_AUDIO:
                    key1 = 'audio'
                elif c.contents.type == av.lib.AVMEDIA_TYPE_SUBTITLE:
                    key1 = 'subtitle'

                if key1:
                    if c.contents.decode:
                        codecs[key1]['decoding'].append(codecName)
                    elif c.contents.encode:
                        codecs[key1]['encoding'].append(codecName)

            else:
                break

        return codecs

    @staticmethod
    def formats():

        '''
        return a dict with 2 keys: muxing & demuxing

        each key value is a dict: key=format name, value: format long name
        '''

        # port of show_formats function (cf cmdutils.c)

        f = {'muxing': {}, 'demuxing': {}}

        av.lib.av_register_all()
        ifmt  = None
        ofmt = None

        while 1:
            ofmt = av.lib.av_oformat_next(ofmt)
            if ofmt:
                f['muxing'][ofmt.contents.name] = ofmt.contents.long_name
            else:
                break

        while 1:
            ifmt = av.lib.av_iformat_next(ifmt)
            if ifmt:
                f['demuxing'][ifmt.contents.name] = ifmt.contents.long_name
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
   
    # read
    def __iter__(self):
        return self

    def next(self):
        
        '''
        iter over packet in media, return a Packet object
        '''
        
        if self.pkt is None:
            self.pkt = Packet(self.pFormatCtx) 
        
        while av.lib.av_read_frame(self.pFormatCtx, self.pkt.pktRef) >= 0:
            return self.pkt

        # end of generator
        raise StopIteration

    # TODO: rename to addScaler
    def addScaler2(self, streamIndex, width, height):

        '''
        add a scaler for given stream
        '''
        
        if self.pkt is None:
            self.pkt = Packet(self.pFormatCtx)
      
        scaler = (streamIndex, width, height)

        self.pkt.scaler[streamIndex] = scaler         
        self.pkt.addScaler(*scaler)

    def seek(self, time, direction='forward', streamIndex=-1):

        '''
        seek to given time in direction
        :time (float): in seconds
        '''

        flags = 0
        if direction == 'backward':
            flags = av.lib.AVSEEK_FLAG_BACKWARD
        
        if streamIndex >= 0:
            # FIXME: should be stream time base... 
            timestamp = time * av.lib.AV_TIME_BASE
        else:
            timestamp = time * av.lib.AV_TIME_BASE
        timestamp = int(round(time * av.lib.AV_TIME_BASE)) 
        
        return av.lib.av_seek_frame(self.pFormatCtx, -1, timestamp, flags)

class Packet(object):

    def __init__(self, formatCtx):

        # alloc packet and keep a ref (for Media.__next__)
        self.pkt = av.lib.AVPacket()
        self.pktRef = ctypes.byref(self.pkt)
        # alloc frame 
        self.frame = av.lib.avcodec_alloc_frame()
        self.decoded = ctypes.c_int(-1)
        self.decodedRef = ctypes.byref(self.decoded)
        # subtitle
        self.subtitle = av.lib.AVSubtitle()

        # frame after conversion by scaler
        self.swsFrame = None
        
        # after decode
        self.dataSize = -1
        
        # retrieve a list of codec context for each stream in file
        self.codecCtx = []
        self.swsCtx = []
        self.scaler = []

        self.f = formatCtx
        formatCtxCt = formatCtx.contents
        streamCount = formatCtxCt.nb_streams
        for i in xrange(streamCount):
            
            cStream = formatCtxCt.streams[i]
            cCodecCtx = cStream.contents.codec
            cCodec = av.lib.avcodec_find_decoder(cCodecCtx.contents.codec_id)
            
            if not cCodec:
                self.codecCtx.append(None)
            else:
                av.lib.avcodec_open(cCodecCtx, cCodec)
                self.codecCtx.append(cCodecCtx)
            
            self.swsCtx.append(None)
            self.scaler.append(None)

    def addScaler(self, streamIndex, width=None, height=None):

        '''
        '''

        scalerTuple = (width, height)
        if self.scaler[streamIndex] != scalerTuple:

            self.scaler[streamIndex] = scalerTuple
            
            codecCtx = self.codecCtx[streamIndex]
           
            if width:
                newWidth = width
            else:
                newWidth = codecCtx.contents.width
            
            if height:
                newHeight = height
            else:
                newHeight = codecCtx.contents.height

            self.swsCtx[streamIndex] = av.lib.sws_getContext(
                codecCtx.contents.width,
                codecCtx.contents.height,
                codecCtx.contents.pix_fmt,
                newWidth,
                newHeight,
                av.lib.PIX_FMT_RGB24,
                av.lib.SWS_BILINEAR,
                None,
                None,
                None)
            
            self.swsFrame = av.lib.avcodec_alloc_frame()
            if not self.swsFrame:
                raise RuntimeError('Could not alloc frame')

            # FIXME perf - let the user alloc a buffer?
            av.lib.avpicture_alloc(
                    ctypes.cast(self.swsFrame, ctypes.POINTER(av.lib.AVPicture)), 
                    av.lib.PIX_FMT_RGB24,
                    newWidth, 
                    newHeight)

    def __copy__(self):

        p = Packet(self.f)
        
        #ctypes.memmove(p.pktRef, self.pktRef, ctypes.sizeof(av.lib.AVPacket))

        pkt = p.pkt
        srcPkt = self.pkt

        pkt.pts = srcPkt.pts
        pkt.dts = srcPkt.dts
        pkt.size = srcPkt.size
        pkt.stream_index = srcPkt.stream_index
        pkt.flags = srcPkt.flags
        pkt.side_data_elems = srcPkt.side_data_elems
        pkt.duration = srcPkt.duration
        pkt.destruct = srcPkt.destruct
        pkt.pos = srcPkt.pos
        pkt.convergence_duration = srcPkt.convergence_duration

        # data copy
        data_size = pkt.size * ctypes.sizeof(av.lib.uint8_t)
        pkt.data = ctypes.cast( av.lib.av_malloc(data_size), ctypes.POINTER(av.lib.uint8_t))
        # XXX: use memcpy from libavcodec?
        ctypes.memmove(pkt.data, srcPkt.data, data_size)
                
        # side data copy
        side_data_size = pkt.side_data_elems * ctypes.sizeof(av.lib.N8AVPacket4DOT_30E)
        p.side_data = ctypes.cast(av.lib.av_malloc(side_data_size), ctypes.POINTER(av.lib.N8AVPacket4DOT_30E))
        # XXX: use memcpy from libavcodec?
        ctypes.memmove(pkt.side_data, srcPkt.side_data, side_data_size)
        
        # scaler copy
        for streamIndex, scaler in enumerate(self.scaler):
            if scaler:
                p.scaler.append(scaler)
                p.addScaler(streamIndex, scaler[0], scaler[1])

        return p

    def __del__(self):

        av.lib.avsubtitle_free(ctypes.byref(self.subtitle))
        for ctx in self.swsCtx:
            av.lib.sws_freeContext(ctx)

        av.lib.avpicture_free(ctypes.cast(self.swsFrame, ctypes.POINTER(av.lib.AVPicture)))
        av.lib.av_free(self.frame)

        av.lib.av_free_packet(ctypes.byref(self.pkt))

    def streamIndex(self):
        return self.pkt.stream_index

    def decode(self):
        
        codecCtx = self.codecCtx[self.pkt.stream_index]
        #print 'c ctx', codecCtx
        if codecCtx is not None:
           
            codecType = codecCtx.contents.codec_type
            #print 'c type', codecType, av.lib.AVMEDIA_TYPE_AUDIO

            if codecType == av.lib.AVMEDIA_TYPE_AUDIO:
                result = av.lib.avcodec_decode_audio4(codecCtx, self.frame, 
                        self.decodedRef, self.pktRef)
                if result > 0 and self.decoded:
                    self.dataSize = av.lib.av_samples_get_buffer_size(None, 
                            codecCtx.contents.channels, self.frame.contents.nb_samples, 
                            codecCtx.contents.sample_fmt, 1)
                else:
                    # FIXME: raise?
                    print 'failed decode...'

            elif codecType == av.lib.AVMEDIA_TYPE_VIDEO:
                # FIXME: avcodec_decode_video2 return result?
                av.lib.avcodec_decode_video2(codecCtx, self.frame, 
                        self.decodedRef, self.pktRef)

                if self.decoded:
                    swsCtx = self.swsCtx[self.pkt.stream_index]

                    if swsCtx:
                        av.lib.sws_scale(swsCtx,
                                self.frame.contents.data,
                                self.frame.contents.linesize,
                                0,
                                codecCtx.contents.height,
                                self.swsFrame.contents.data,
                                self.swsFrame.contents.linesize)
            elif codecType == av.lib.AVMEDIA_TYPE_SUBTITLE:
                av.lib.avcodec_decode_subtitle2(codecCtx, self.subtitle, 
                        self.decodedRef, self.pktRef)
                
                if self.decoded:
                    self.subtitleCount = self.subtitle.num_rects 
                    self.subtitleTypes = []

                    for i in xrange(self.subtitleCount):

                        cType = self.subtitle.rects[i].contents.type
                        cTypeName = ''
                        # FIXME: AVSubtitleType is an enum 
                        if cType == av.lib.SUBTITLE_BITMAP:
                            cTypeName = 'bitmap'
                        elif cType == av.lib.SUBTITLE_TEXT:
                            cTypeName = 'text'
                        elif cType == av.lib.SUBTITLE_ASS:
                            cTypeName = 'ass'
                        self.subtitleTypes.append(cTypeName)

            else:
                # unsupported codec type - subtitle?
                pass
    
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

