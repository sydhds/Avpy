'''
High-level libav python API
'''

import os
import sys
import ctypes
from . import av

FRAME_SIZE_DEFAULT = 1152

class Media(object):

    def __init__(self, mediaName, mode='r'):
        
        '''Command constructor

	:param mediaName: media to open for reading or writing
        :type label: str
        :param mode: 'r' or 'w' 
	:type mode: str

	'''
 
        av.lib.av_log_set_level(av.lib.AV_LOG_QUIET)

        av.lib.av_register_all()
        self.pFormatCtx = ctypes.POINTER(av.lib.AVFormatContext)()

        if mode == 'r':
            
            # prevent coredump
            if mediaName is None:
                mediaName = ''
           
            # open media for reading
            
            # XXX: ok for python3 and python2 with special characters
            # not sure this is a right/elegant solution 
            if sys.version_info >= (3, 0):
                _mediaName = mediaName.encode('utf-8')
            else:
                _mediaName = mediaName
            
            res = av.lib.avformat_open_input(self.pFormatCtx, _mediaName, None, None)
            if res: 
                raise IOError(avError(res))
            
            # get stream info
            # need this call in order to retrieve duration
            res = av.lib.avformat_find_stream_info(self.pFormatCtx, None)
            if res < 0:
                raise IOError(avError(res))
       
        elif mode == 'w':
            
            # FIXME: code dup...

            # XXX: ok for python3 and python2 with special characters
            # not sure this is a right/elegant solution 
            if sys.version_info >= (3, 0):
                _mediaName = mediaName.encode('utf-8')
                defaultCodec = ctypes.c_char_p(b'mpeg')
            else:
                _mediaName = mediaName
                defaultCodec = ctypes.c_char_p('mpeg')

            # Autodetect the output format from the name, default to MPEG
            fmt = av.lib.av_guess_format(None, _mediaName, None)
            if not fmt:
                #print('Could not deduce output format from file extension: using MPEG.')
                fmt = av.lib.av_guess_format(defaultCodec, None ,None)

            if not fmt:
                raise RuntimeError('Could not find a valid output format')

            # Allocate the output media context.
            self.pFormatCtx = av.lib.avformat_alloc_context()
            if not self.pFormatCtx:
                raise IOError(avError(res))

            self.pFormatCtx.contents.oformat = fmt
            self.pFormatCtx.contents.filename = _mediaName

        self.pkt = None
        self.mode = mode

    def __del__(self):

        if self.pFormatCtx:
            for i in range(self.pFormatCtx.contents.nb_streams):
                cStream = self.pFormatCtx.contents.streams[i]
                av.lib.avcodec_close(cStream.contents.codec)

            if self.mode == 'r':
                av.lib.avformat_close_input(self.pFormatCtx)

    def info(self):

        ''' get media information

        :return: dict with the following fields: name, metadata, stream, duration
        :rtype: dict

        * duration: media duration in seconds
        * name: media filename
        * stream: list of stream info (dict)
        '''
        
        infoDict = {}
        infoDict['name'] = self.pFormatCtx.contents.filename

        if self.mode == 'r':
            avFormat = self.pFormatCtx.contents.iformat
        else:
            avFormat = self.pFormatCtx.contents.oformat

        infoDict['format'] = avFormat.contents.name
        infoDict['metadata'] = self.metadata()
        infoDict['stream'] = []
        infoDict['duration'] = float(self.pFormatCtx.contents.duration)/av.lib.AV_TIME_BASE

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
            
            try:
                pixFmtName = av.lib.avcodec_get_pix_fmt_name
            except AttributeError:
                pixFmtName = av.lib.av_get_pix_fmt_name
            
            streamInfo['pixelFormat'] = pixFmtName(cCodecCtx.contents.pix_fmt)
        elif codecType == av.lib.AVMEDIA_TYPE_AUDIO:
            streamInfo['type'] = 'audio'
            streamInfo['sample_rate'] = cCodecCtx.contents.sample_rate
            streamInfo['channels'] = cCodecCtx.contents.channels
            streamInfo['sample_fmt'] = av.lib.av_get_sample_fmt_name(cCodecCtx.contents.sample_fmt)
            streamInfo['sample_fmt_id'] = cCodecCtx.contents.sample_fmt
            streamInfo['frame_size'] = cCodecCtx.contents.frame_size

            if streamInfo['frame_size'] == 0:
                streamInfo['frame_size'] = FRAME_SIZE_DEFAULT

            streamInfo['bytes_per_sample'] = av.lib.av_get_bytes_per_sample(cCodecCtx.contents.sample_fmt)
        elif codecType == av.lib.AVMEDIA_TYPE_SUBTITLE:
            streamInfo['type'] = 'subtitle'
            streamInfo['subtitle_header'] = ctypes.string_at(cCodecCtx.contents.subtitle_header,
                    cCodecCtx.contents.subtitle_header_size)
        else:
            pass
        
        return streamInfo

    def metadata(self):

        ''' get media metadata

        :return: a dict with key, value = metadata key, metadata value

        .. note:: method is used to fullfill the metadata entry in :meth:`info`
        '''

        done = False
        metaDict = {}
        tag = ctypes.POINTER(av.lib.AVDictionaryEntry)()

        while not done:
            tag = av.lib.av_dict_get(self.pFormatCtx.contents.metadata, ''.encode('ascii'), tag, av.lib.AV_DICT_IGNORE_SUFFIX)
            if tag:
                metaDict[tag.contents.key] = tag.contents.value
            else:
                done = True
        
        return metaDict

    @staticmethod
    def codecs():

        ''' get all supported codecs

        :return: a dict with 3 keys (audio, video and subtitle). For each key, the value is a dict with 2 keys (encoding and decoding).
        :rtype: dict
        '''

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
                    
                    # libav8 has encode attribute but libav9 has encode2
                    encodeAttr = None
                    if hasattr(c.contents, 'encode'):
                        encodeAttr = 'encode'
                    elif hasattr(c.contents, 'encode2'):
                        encodeAttr = 'encode2'
                    
                    if c.contents.decode:
                        codecs[key1]['decoding'].append(codecName)
                    elif getattr(c.contents, encodeAttr):
                        codecs[key1]['encoding'].append(codecName)

            else:
                break

        return codecs

    @staticmethod
    def formats():

        ''' return a dict with 2 keys: muxing & demuxing

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

        ''' retrieve specific codec information
        
        :param name: codec name
	:type name: str
        :param decode: codec decoder info. Set decode to False to get codec encoder info.
	:type name: bool
        :return: codec information as a dict with the following keys -> name, longname, type
        :rtype: dict

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
            ci['sample_fmts'] = []
            
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
                    if r.num == 0 and r.den == 0:
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

            # sample_fmts
            sfmts = c.contents.sample_fmts
            if sfmts:
                for s in sfmts:
                    if s == -1:
                        break
                    ci['sample_fmts'].append(av.lib.av_get_sample_fmt_name(s))

        else:
            raise ValueError('Unable to find codec %s' % name)
        

        return ci

    # read
    def __iter__(self):
        return self
    
    def __next__(self):
        # python3 require __next__, python2 next
        return self.next()

    def next(self):
        
        ''' iter over packet in media
        
        :rtype: :class:`Packet`
        '''
        
        if self.pkt is None:
            self.pkt = Packet(self.pFormatCtx) 
        
        while av.lib.av_read_frame(self.pFormatCtx, self.pkt.pktRef) >= 0:
            return self.pkt

        # end of generator
        raise StopIteration

    # TODO: rename to addScaler
    def addScaler2(self, streamIndex, width, height):

        ''' add a scaler for given stream

        :param streamIndex: stream index
	:type streamIndex: int
	:param with: new stream width
	:type width: int
	:param height: new stream height
	:type height: int
        '''
        
        if self.pkt is None:
            self.pkt = Packet(self.pFormatCtx)
      
        scaler = (streamIndex, width, height)

        self.pkt.scaler[streamIndex] = scaler         
        self.pkt.addScaler(*scaler)

    def seek(self, time, direction='forward', streamIndex=-1):

        # seek to given time in direction
        # :time (float): in seconds

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

    def addStream(self, streamType, streamInfo):

        ''' Add a stream
        '''

        if streamType == 'video':
            
            codecId = self.pFormatCtx.contents.oformat.contents.video_codec 

            # find the video encoder
            codec = av.lib.avcodec_find_encoder(codecId)
            if not codec:
                raise RuntimeError('Codec not found')
            
            stream = av.lib.avformat_new_stream(self.pFormatCtx, codec)
            if not stream:
                raise RuntimeError('Could not alloc stream')

            c = stream.contents.codec

            c.contents.bit_rate = streamInfo['bitRate']
            c.contents.width = streamInfo['width']
            c.contents.height = streamInfo['height']
            c.contents.time_base.den = streamInfo['timeBase'][1]
            c.contents.time_base.num = streamInfo['timeBase'][0]

            # TODO: from info
            c.contents.gop_size = 12

            # TODO: from info
            c.contents.pix_fmt = av.lib.PIX_FMT_YUV420P 

            if hasattr(av.lib, 'CODEC_ID_MPEG2VIDEO'):
                mpg2CodecId = av.lib.CODEC_ID_MPEG2VIDEO
            else:
                mpg2CodecId = av.lib.AV_CODEC_ID_MPEG2VIDEO

            if c.contents.codec_id == mpg2CodecId:
                c.contents.max_b_frames = 2

            if hasattr(av.lib, 'CODEC_ID_MPEG1VIDEO'):
                mpg1CodecId = av.lib.CODEC_ID_MPEG1VIDEO
            else:
                mpg1CodecId = av.lib.AV_CODEC_ID_MPEG1VIDEO
            
            if c.contents.codec_id == mpg1CodecId:
                c.contents.mb_decision = 2;

            if self.pFormatCtx.contents.oformat.contents.flags & av.lib.AVFMT_GLOBALHEADER:
                c.contents.flags |= av.lib.CODEC_FLAG_GLOBAL_HEADER 
        
            # open codec
            res = av.lib.avcodec_open2(c, None, None) 
            if res < 0:
                raise RuntimeError(avError(res))

            self.videoOutBufferSize = av.lib.avpicture_get_size(av.lib.PIX_FMT_YUV420P, streamInfo['width'], streamInfo['height'])
            self.videoOutBuffer = ctypes.cast(av.lib.av_malloc(self.videoOutBufferSize), 
                    ctypes.POINTER(ctypes.c_ubyte))
            self.outStream = stream

        elif streamType == 'audio':

            if 'codec' in streamInfo and streamInfo['codec'] == 'auto':
                codecId = self.pFormatCtx.contents.oformat.contents.audio_codec
                _codec = av.lib.avcodec_find_encoder(codecId)
            else:
                # TODO: result
                _codec = av.lib.avcodec_find_encoder_by_name(streamInfo['codec'])
                codecId = _codec.contents.id

            # find the audio encoder
            if not _codec:

                if 'codec' in streamInfo and streamInfo['codec'] == 'auto':
                    exceptMsg = 'Codec for format %s not found' % self.pFormatCtx.contents.oformat.contents.name
                else:
                    exceptMsg = 'Codec %s not found' % _codec.contents.name

                raise RuntimeError(exceptMsg)
            
            # XXX: use COMPLIANCE_NORMAL or COMPLIANCE_STRICT?
            res = av.lib.avformat_query_codec(self.pFormatCtx.contents.oformat, codecId, av.lib.FF_COMPLIANCE_STRICT)

            # Note:
            # 1 -> codec supported by output format
            # 0 -> unsupported
            # < 0 -> not available
            # for safety reason, raise for <= 0 
            # ex: codec mp2 in ogg report < 0 but can crash encoder
            errorTpl = (_codec.contents.name, self.pFormatCtx.contents.oformat.contents.name)
            if res == 0:
                raise RuntimeError('Codec %s not supported in %s muxer' % errorTpl )
            elif res < 0:
                print('Warning: could not determine if codec %s is supported by %s muxer' % errorTpl)            

            stream = av.lib.avformat_new_stream(self.pFormatCtx, _codec)
            if not stream:
                raise RuntimeError('Could not alloc stream')

            c = stream.contents.codec

            # sample parameters 
            c.contents.sample_fmt = av.lib.AV_SAMPLE_FMT_S16;
            c.contents.bit_rate = streamInfo['bitRate']
            c.contents.sample_rate = streamInfo['sampleRate']
            c.contents.channels = streamInfo['channels']

            if self.pFormatCtx.contents.oformat.contents.flags & av.lib.AVFMT_GLOBALHEADER:
                c.contents.flags |= av.lib.CODEC_FLAG_GLOBAL_HEADER 
            
            # open codec
            res = av.lib.avcodec_open2(c, None, None) 
            if res < 0:
                raise RuntimeError(avError(res))

            # FIXME: multiple stream
            self.outStream = stream
            
        else:
            raise RuntimeError('Unknown stream type (not video or audio)')
    
    def writeHeader(self):
        
        ''' Start writing process (header) 
        '''
        
        fmt = self.pFormatCtx.contents.oformat
        fn = self.pFormatCtx.contents.filename
        if not (fmt.contents.flags & av.lib.AVFMT_NOFILE):
            res = av.lib.avio_open(ctypes.byref(self.pFormatCtx.contents.pb), 
                    fn, av.lib.AVIO_FLAG_WRITE)
            if res < 0:
                raise IOError(avError(res))

        # write the stream header, if any
        # libav8 -> av_write_header, libav9 -> avformat...
        if hasattr(av.lib, 'av_write_header'):
            av.lib.av_write_header(self.pFormatCtx)
        else:
            av.lib.avformat_write_header(self.pFormatCtx, None)

    def writeTrailer(self):

        ''' End writing process (trailer)
        '''
        
        av.lib.av_write_trailer(self.pFormatCtx)
   
    def videoPacket(self, width, height):

        ''' Get a packet ready for encoding purpose  
        '''

        self.pkt = Packet(self.pFormatCtx)
        
        # TODO: from codec
        pix_fmt = av.lib.PIX_FMT_YUV420P
        
        av.lib.avpicture_alloc(
                ctypes.cast(self.pkt.frame, ctypes.POINTER(av.lib.AVPicture)), 
                pix_fmt,
                width, 
                height)

        return self.pkt

    def audioPacket(self, channels):

        c = self.outStream.contents.codec
        
        if c.contents.frame_size == 0:
            # frame size is set to 0 for pcm codec
            bufSize = FRAME_SIZE_DEFAULT * c.contents.channels * av.lib.av_get_bytes_per_sample(c.contents.sample_fmt) 
        else:
            bufSize = av.lib.av_samples_get_buffer_size(None, c.contents.channels, c.contents.frame_size,
                    c.contents.sample_fmt, 0)

        buf = ctypes.cast(av.lib.av_malloc(bufSize), ctypes.POINTER(ctypes.c_uint16))
        #ctypes.memset(buf, 0, bufSize) 
        
        self.pkt = Packet(self.pFormatCtx)

        av.lib.avcodec_get_frame_defaults(self.pkt.frame) 

        self.pkt.frame.contents.nb_samples = int(bufSize / (channels * av.lib.av_get_bytes_per_sample(av.lib.AV_SAMPLE_FMT_S16)))
        
        res = av.lib.avcodec_fill_audio_frame(self.pkt.frame, 
                c.contents.channels, c.contents.sample_fmt,
                ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte)), bufSize, 0)

        if res < 0:
            raise RuntimeError('fill audio frame failed')

        return self.pkt
    
    def write(self, packet, pts, mediaType='video'):
        
        c = self.outStream.contents.codec
        st = self.outStream

        if mediaType == 'video':

            if hasattr(av.lib, 'avcodec_encode_video'):
               
                encSize = av.lib.avcodec_encode_video(c, 
                        self.videoOutBuffer, self.videoOutBufferSize, packet.frame)
     
                if encSize > 0:

                    pkt = av.lib.AVPacket()
                    pktRef = ctypes.byref(pkt)

                    av.lib.av_init_packet(pktRef)

                    if c.contents.coded_frame.contents.pts != av.lib.AV_NOPTS_VALUE:
                    
                        pkt.pts = pts

                        if c.contents.coded_frame.contents.key_frame:
                            pkt.flags |= av.lib.AV_PKT_FLAG_KEY

                        pkt.stream_index = st.contents.index

                        pkt.data = self.videoOutBuffer
                        pkt.size = encSize

                        ret = av.lib.av_interleaved_write_frame(self.pFormatCtx, pktRef)
            else:
                     
                outPkt = av.lib.AVPacket()
                outPktRef = ctypes.byref(outPkt)
                outPkt.data = None

                self.decoded = ctypes.c_int(-1)
                self.decodedRef = ctypes.byref(self.decoded)

                av.lib.av_init_packet(outPktRef)
                
                encSize = av.lib.avcodec_encode_video2(c, outPktRef, packet.frame, self.decodedRef) 
                
                if outPkt.size > 0:
                    pktRef = ctypes.byref(outPkt)
                    ret = av.lib.av_interleaved_write_frame(self.pFormatCtx, pktRef)

        elif mediaType == 'audio':

            outPkt = av.lib.AVPacket()
            outPktRef = ctypes.byref(outPkt)
            outPkt.data = None

            self.decoded = ctypes.c_int(-1)
            self.decodedRef = ctypes.byref(self.decoded)

            av.lib.av_init_packet(outPktRef)
            
            encSize = av.lib.avcodec_encode_audio2(c, outPktRef, packet.frame, self.decodedRef) 
            
            if outPkt.size > 0:
                pktRef = ctypes.byref(outPkt)
                ret = av.lib.av_interleaved_write_frame(self.pFormatCtx, pktRef)

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
        for i in range(streamCount):
            
            cStream = formatCtxCt.streams[i]
            cCodecCtx = cStream.contents.codec
            cCodec = av.lib.avcodec_find_decoder(cCodecCtx.contents.codec_id)
            
            if not cCodec:
                self.codecCtx.append(None)
            else:
                av.lib.avcodec_open2(cCodecCtx, cCodec, None)
                self.codecCtx.append(cCodecCtx)
            
            self.swsCtx.append(None)
            self.scaler.append(None)

    def addScaler(self, streamIndex, width=None, height=None):

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
        
        if self.swsFrame:
            av.lib.avpicture_free(ctypes.cast(self.swsFrame, ctypes.POINTER(av.lib.AVPicture)))
       
        av.lib.av_free(self.frame)
        av.lib.av_free_packet(ctypes.byref(self.pkt))
        
    def streamIndex(self):
        return self.pkt.stream_index

    def decode(self):
       
        ''' decode data
        '''

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
                    print('failed decode...')

            elif codecType == av.lib.AVMEDIA_TYPE_VIDEO:
                # FIXME: avcodec_decode_video2 return result?
                av.lib.avcodec_decode_video2(codecCtx, self.frame, 
                        self.decodedRef, self.pktRef)

                if self.decoded:
                        
                    swsCtx = self.swsCtx[self.pkt.stream_index]
                    if swsCtx:
                        
                        srcFrame = self.frame
                        
                        av.lib.sws_scale(swsCtx,
                                srcFrame.contents.data,
                                srcFrame.contents.linesize,
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
                # unsupported codec type...
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


