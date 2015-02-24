# Avpy
# Copyright (C) 2013-2015 Sylvain Delhomme
# 
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
# 
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301
# USA

import os
import sys
import ctypes
from . import av

__version__ = '0.1.1.dev0'

FRAME_SIZE_DEFAULT = 1152
FPS_DEFAULT = (1, 24)

class Media(object):

    def __init__(self, mediaName, mode='r', quiet=True):
        
        ''' Initialize a media object for decoding or encoding

	:param mediaName: media to open
        :type label: str
        :param mode: 'r' (decoding) or 'w' (encoding) 
	:type mode: str
        :param quiet: turn on/off libav or ffmpeg warnings
        :type quiet: bool
	'''
 
        if quiet:
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
                defaultCodec = ctypes.c_char_p('mpeg'.encode('utf8'))
            else:
                _mediaName = mediaName
                defaultCodec = ctypes.c_char_p('mpeg')

            # Autodetect the output format from the name, default to MPEG
            fmt = av.lib.av_guess_format(None, _mediaName, None)
            if not fmt:
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
        self.videoOutBuffer = None
        self.mode = mode

    def __del__(self):

        if self.pFormatCtx:
            
            for i in range(self.pFormatCtx.contents.nb_streams):
                cStream = self.pFormatCtx.contents.streams[i]
                av.lib.avcodec_close(cStream.contents.codec)

            if self.mode == 'r':

                av.lib.avformat_close_input(self.pFormatCtx)
            
            elif self.mode == 'w':
               
                if self.videoOutBuffer:
                    av.lib.av_free(self.videoOutBuffer)

                pAvioCtx = self.pFormatCtx.contents.pb
                
                if pAvioCtx:
                    res = av.lib.avio_close(pAvioCtx) 
                    if res < 0:
                        raise IOError(avError(res))

                av.lib.avformat_free_context(self.pFormatCtx)

    def info(self):

        ''' Get media information

        :return: dict with the following fields: name, metadata, stream, duration
        :rtype: dict

        * duration: media duration in seconds
        * name: media filename
        * stream: list of stream info (dict)

        .. note:: 
            each stream info will contains the following fields:
            
            - all:
                - codec: codec short name
                - type: video, audio or subtitle
            - video:
                - widht, height: video size
                - fps: as a tuple of 3 values (num, den, ticks)
                - pixelFormat: pixel format name (ie. rgb24, yuv420p ...)
            - audio:
                - sampleRate: sample rate
                - channels: channel count
                - sampleFmt: sample format name (ie. s16 ...)
                - sampleFmtId: sample format id (internal use)
                - frameSize: frame size
                - bytesPerSample: bytes for sample format (ie. 2 for s16)
                - planarFmt: if True, each audio channel is in a separate buffer
                - channelLayout: mono, stereo...
            - subtitle:
                - subtitle header: header string

        .. seealso:: :meth:`writeHeader`
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
            streamInfo['sampleRate'] = cCodecCtx.contents.sample_rate
            streamInfo['channels'] = cCodecCtx.contents.channels
            streamInfo['sampleFmt'] = av.lib.av_get_sample_fmt_name(cCodecCtx.contents.sample_fmt)
            streamInfo['sampleFmtId'] = cCodecCtx.contents.sample_fmt
            streamInfo['frameSize'] = cCodecCtx.contents.frame_size
            
            # FIXME

                            
            bufSize = 128
            buf = ctypes.create_string_buffer(bufSize) 
            av.lib.av_get_channel_layout_string(
                    buf, bufSize, 
                    streamInfo['channels'], cCodecCtx.contents.channel_layout)

            streamInfo['channelLayoutDescription'] = buf.value
            streamInfo['channelLayoutId'] = cCodecCtx.contents.channel_layout
            
            if hasattr(av.lib, 'av_get_channel_name'):
                # av_get_channel_name return None if format is planar
                streamInfo['channelLayout'] = av.lib.av_get_channel_name(
                        cCodecCtx.contents.channel_layout) or ''
            else:
                # libav8 only
                # dirty workaround so user can easily guess if audio resampling is
                # is needed (by comparing channel layout strings)
                # see outputWav example 
                # a proper fix could be to add a function like needResampling(...)
                streamInfo['channelLayout'] = streamInfo['channelLayoutDescription']

            streamInfo['planarFmt'] = bool(av.lib.av_sample_fmt_is_planar(cCodecCtx.contents.sample_fmt))

            if streamInfo['frameSize'] == 0:
                streamInfo['frameSize'] = FRAME_SIZE_DEFAULT

            streamInfo['bytesPerSample'] = av.lib.av_get_bytes_per_sample(cCodecCtx.contents.sample_fmt)
        elif codecType == av.lib.AVMEDIA_TYPE_SUBTITLE:
            streamInfo['type'] = 'subtitle'
            streamInfo['subtitleHeader'] = ctypes.string_at(cCodecCtx.contents.subtitle_header,
                    cCodecCtx.contents.subtitle_header_size)
        else:
            pass
        
        return streamInfo

    def metadata(self):

        ''' Get media metadata

        :return: a dict with key, value = metadata key, metadata value

        .. note:: method is also called by :meth:`info`

        .. seealso:: :meth:`writeHeader`
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


    # read
    def __iter__(self):
        return self
    
    def __next__(self):
        # python3 require __next__, python2 next
        return self.next()

    def next(self):
        
        ''' Iterate over Media
        
        :rtype: :class:`Packet`
        '''
        
        if self.pkt is None:
            self.pkt = Packet(self.pFormatCtx) 
        
        while av.lib.av_read_frame(self.pFormatCtx, self.pkt.pktRef) >= 0:
            return self.pkt

        # end of generator
        raise StopIteration

    def addScaler(self, streamIndex, width, height):

        ''' Add a scaler

        A scaler is responsible for:
        
        - scaling a video
        - converting output data format (ie yuv420p to rgb24) 

        :param streamIndex: stream index
	:type streamIndex: int
	:param with: new stream width
	:type width: int
	:param height: new stream height
	:type height: int

        .. note:: 
            Selecting output data format is not yet available (rgb24 only)
        
        '''
        
        if self.pkt is None:
            self.pkt = Packet(self.pFormatCtx)
      
        scaler = (streamIndex, width, height)

        self.pkt.scaler[streamIndex] = scaler         
        self.pkt.addScaler(*scaler)

    def addResampler(self, streamIndex, inAudio, outAudio):

        ''' Add an audio resampler
        
        A resampler is responsible for:
        
        - resampling audio (frequency, layout)
        - converting output data format (ie s16p -> s16) 

        :param inAudio: audio input info
        :type inAudio: dict
        :param outAudio: audio output info
        :type outAudio: dict

        .. note:: 
            each audio info requires the following fields:
            
            - sampleRate: sample rate
            - sampleFmt: sample format name (ie s16)
            - layout (optional): channel layout (ie. mono, stereo...)
            - channels (optional): channel count

            if 'layout' is not specified, its value is guessed from the channel
            count

        '''

        if self.pkt is None:
            self.pkt = Packet(self.pFormatCtx)

        resampler = (inAudio, outAudio)
        self.pkt.resampler[streamIndex] = resampler
        self.pkt.addResampler(streamIndex)

    def addStream(self, streamType, streamInfo):

        ''' Add a stream

        After opening a media for encoding (writing), a stream of
        desired type (video or audio) have to be added.

        :param streamType: video or audio stream
        :type streamType: str
        :param streamInfo: stream parameters
        :type streamInfo: dict

        Supported stream parameters:
        
        - video:
            - width, height: video size
            - pixelFormat: pixel format name (ie. rgb24, yuv420p ...)
            - codec: video codec name (ie. mp4), auto is a valid value
            - timeBase: as a tuple (ie (1, 25) for 25 fps)
            - bitRate: average bit rate (ie 64000 for 64kbits/s)
        - audio:
            - sampleRate: sample frequency (ie. 44100 for 44.1 kHz)
            - bitRate: average bit rate (see video bit rate)
            - channels channel count (ie. usually 2)
            - codec: audio codec name, auto is a valid value
            - sampleFmt: sample format (ie flt for float)
        
        More parameters are documented here: :doc:`../api/encoding`
        
        .. note:: 
            
            - For an image, timeBase and bitRate parameters are ignored
            - More parameters will be supported in the near futur
            - Subtitle streams are not yet supported

        .. note:: use :func:`codecInfo` to query codec caps

        '''

        if streamType == 'video':
           
            _codecRequested = streamInfo.get('codec', 'auto')

            if sys.version_info >= (3, 0):
                codecRequested = ctypes.c_char_p(_codecRequested.encode('utf-8'))
            else:
                codecRequested = _codecRequested

            if _codecRequested == 'auto':
                oformat = self.pFormatCtx.contents.oformat
                codecId = av.lib.av_guess_codec(oformat,
                        None, self.pFormatCtx.contents.filename,
                        None, av.lib.AVMEDIA_TYPE_VIDEO)
                _codec = av.lib.avcodec_find_encoder(codecId)

            else:
                _codec = av.lib.avcodec_find_encoder_by_name(codecRequested)
                if _codec:
                    codecId = _codec.contents.id

            # find the audio encoder
            if not _codec:                

                if 'codec' not in streamInfo or streamInfo['codec'] == 'auto':
                    exceptMsg = 'Codec for format %s not found' % self.pFormatCtx.contents.oformat.contents.name
                else:
                    exceptMsg = 'Codec %s not found' % codecRequested

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

            av.lib.avcodec_get_context_defaults3(c, _codec)

            if 'bitRate' in streamInfo:
                c.contents.bit_rate = streamInfo['bitRate']
            
            c.contents.width = streamInfo['width']
            c.contents.height = streamInfo['height']
            
            if 'timeBase' in streamInfo:
                c.contents.time_base.den = streamInfo['timeBase'][1]
                c.contents.time_base.num = streamInfo['timeBase'][0]
            else:
                # note: even for writing an image, a time base is required
                c.contents.time_base.den = FPS_DEFAULT[1]
                c.contents.time_base.num = FPS_DEFAULT[0] 

            # more parameters
            if 'gopSize' in streamInfo:
                c.contents.gop_size = streamInfo['gopSize'] 

            if sys.version_info >= (3, 0):
                pixFmt = ctypes.c_char_p(streamInfo['pixelFormat'].encode('utf8'))
            else:
                pixFmt = streamInfo['pixelFormat']
            
            c.contents.pix_fmt = av.lib.av_get_pix_fmt(pixFmt)

            if self.pFormatCtx.contents.oformat.contents.flags & av.lib.AVFMT_GLOBALHEADER:
                c.contents.flags |= av.lib.CODEC_FLAG_GLOBAL_HEADER 
        
            # open codec
            res = av.lib.avcodec_open2(c, _codec, None) 
            if res < 0:
                raise RuntimeError(avError(res))
            
            # FIXME: only alloc for libav8?
            self.videoOutBufferSize = av.lib.avpicture_get_size(c.contents.pix_fmt, 
                    streamInfo['width'], streamInfo['height'])
            self.videoOutBuffer = ctypes.cast(av.lib.av_malloc(self.videoOutBufferSize), 
                    ctypes.POINTER(ctypes.c_ubyte))
            self.outStream = stream

        elif streamType == 'audio':

            _codecRequested = streamInfo.get('codec', 'auto')

            if sys.version_info >= (3, 0):
                codecRequested = ctypes.c_char_p(_codecRequested.encode('utf-8'))
            else:
                codecRequested = _codecRequested

            if _codecRequested == 'auto':

                oformat = self.pFormatCtx.contents.oformat
                codecId = av.lib.av_guess_codec(oformat,
                        None, self.pFormatCtx.contents.filename,
                        None, av.lib.AVMEDIA_TYPE_AUDIO)
                _codec = av.lib.avcodec_find_encoder(codecId)
                
            else:
                _codec = av.lib.avcodec_find_encoder_by_name(codecRequested)
                if _codec:
                    codecId = _codec.contents.id
            
            # find the audio encoder
            if not _codec:

                if 'codec' not in streamInfo or streamInfo['codec'] == 'auto':
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

            av.lib.avcodec_get_context_defaults3(c, _codec)
            
            # sample parameters 
            if 'sampleFmt' in streamInfo:

                _sfmt = streamInfo.get('sampleFmt', '')
                if sys.version_info >= (3, 0):
                    _sfmt = _sfmt.encode('utf-8')
                
                sampleFmt = av.lib.av_get_sample_fmt(_sfmt)
            else:
                # default to signed 16 bits sample format
                sampleFmt = av.lib.AV_SAMPLE_FMT_S16

            # check if sample format is supported by codec
            # TODO: facto. codec - see codecInfo 
            sfmtOk = False
            for sfmt in _codec.contents.sample_fmts:
                if sfmt == av.lib.AV_SAMPLE_FMT_NONE:
                    break
                else:
                    if sampleFmt == sfmt:
                        sfmtOk = True
                        break

            if not sfmtOk:
                raise RuntimeError('Sample format %s not supported' % av.lib.av_get_sample_fmt_name(sampleFmt))

            c.contents.sample_fmt = sampleFmt
            c.contents.bit_rate = streamInfo['bitRate']
            c.contents.sample_rate = streamInfo['sampleRate']

            nbChannels = streamInfo['channels']
            c.contents.channels = nbChannels

            if hasattr(av.lib, 'av_get_default_channel_layout'):
                f = av.lib.av_get_default_channel_layout
            else:
                f = _guessChannelLayout

            c.contents.channel_layout = f(nbChannels)

            if self.pFormatCtx.contents.oformat.contents.flags & av.lib.AVFMT_GLOBALHEADER:
                c.contents.flags |= av.lib.CODEC_FLAG_GLOBAL_HEADER 
            
            # open codec
            res = av.lib.avcodec_open2(c, _codec, None) 
            if res < 0:
                raise RuntimeError(avError(res))

            # FIXME: multiple stream
            self.outStream = stream
            
        else:
            raise RuntimeError('Unknown stream type (not video or audio)')
    
    def writeHeader(self, metaData=None):
        
        ''' Write media header 

        Write media header. This method have to be called before any
        call to :meth:`write` 

        :param metaData: media metaData (ie. artist, year ...)
        :type metaData: dict
    
        .. note:: 
            see http://multimedia.cx/eggs/supplying-ffmpeg-with-metadata/
            for available metadata per container
        '''
        
        fmt = self.pFormatCtx.contents.oformat
        fn = self.pFormatCtx.contents.filename
         
        res = av.lib.avio_open(ctypes.byref(self.pFormatCtx.contents.pb), 
                fn, av.lib.AVIO_FLAG_WRITE)
        if res < 0:
            raise IOError(avError(res))

        if metaData:
            for k in metaData:
                
                v = metaData[k] 
                if sys.version_info >= (3, 0):
                    k = ctypes.c_char_p(k.encode('utf-8'))
                    v = ctypes.c_char_p(v.encode('utf-8')) 

                metaDict = ctypes.POINTER(ctypes.POINTER(av.lib.AVDictionary))()
                metaDict.contents = self.pFormatCtx.contents.metadata

                av.lib.av_dict_set(metaDict,
                        k, v, 
                        av.lib.AV_DICT_IGNORE_SUFFIX)
    
        # write the stream header, if any
        # libav8 -> av_write_header, libav9 -> avformat...
        if hasattr(av.lib, 'av_write_header'):
            av.lib.av_write_header(self.pFormatCtx)
        else:
            av.lib.avformat_write_header(self.pFormatCtx, None)

    def writeTrailer(self):

        ''' Write media trailer 
            
        Write media trailer. Call this method just before closing 
        or deleting media.
        '''
        
        av.lib.av_write_trailer(self.pFormatCtx)
   
    def videoPacket(self):

        ''' Get a video packet ready for encoding purpose  

        Initialize and allocate data for a video packet. Data format will
        depend to the previously added stream.

        :return: video packet
        :rtype: :class:`Packet`
        '''

        self.pkt = Packet(self.pFormatCtx)
        
        c = self.outStream.contents.codec
        width = c.contents.width
        height = c.contents.height
        pixFmt = c.contents.pix_fmt
        
        av.lib.avpicture_alloc(
                ctypes.cast(self.pkt.frame, ctypes.POINTER(av.lib.AVPicture)), 
                pixFmt,
                width, 
                height)

        return self.pkt

    def audioPacket(self):
        
        ''' Get an audio packet ready for encoding purpose  

        Initialize and allocate data for an audio packet. Data format will
        depend to the previously added stream.

        :return: video packet
        :rtype: :class:`Packet`

        :raises: RuntimeError if data could not be allocated
        '''

        c = self.outStream.contents.codec
        
        if c.contents.frame_size == 0:
            # frame size is set to 0 for pcm codec
            bufSize = FRAME_SIZE_DEFAULT * c.contents.channels * av.lib.av_get_bytes_per_sample(c.contents.sample_fmt) 
        else:
            bufSize = av.lib.av_samples_get_buffer_size(None, c.contents.channels, c.contents.frame_size,
                    c.contents.sample_fmt, 0)
        
        # FIXME: free buffer (if not used by avcodec_fill_audio frame
        # TODO: cast buf here (to c_ubyte pointer)
        buf = av.lib.av_malloc(bufSize)
        
        self.pkt = Packet(self.pFormatCtx)

        av.lib.avcodec_get_frame_defaults(self.pkt.frame) 

        self.pkt.frame.contents.nb_samples = int(bufSize / 
                (c.contents.channels * av.lib.av_get_bytes_per_sample(c.contents.sample_fmt)))
        
        res = av.lib.avcodec_fill_audio_frame(self.pkt.frame, 
                c.contents.channels, c.contents.sample_fmt,
                ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte)), bufSize, 0)

        if res < 0:
            raise RuntimeError('fill audio frame failed')

        return self.pkt
    
    def write(self, packet, pts, mediaType='video'):
        
        ''' Write packet to media

        :param packet: packet to encode and add to media
        :type packet: :class:`Packet`
        '''

        c = self.outStream.contents.codec
        st = self.outStream

        if mediaType == 'video':

            # guess if we should use packet.frame or packet.swsFrame

            pktFrame = packet.frame

            swsCtx = packet.swsCtx[packet.streamIndex()]
            if swsCtx:
                pktFrame = packet.swsFrame
            
            # libav8: encode_video, libav 9 or > encode_video2
            if hasattr(av.lib, 'avcodec_encode_video'):
               
                encSize = av.lib.avcodec_encode_video(c, 
                        self.videoOutBuffer, self.videoOutBufferSize, pktFrame)
     
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
                
                encSize = av.lib.avcodec_encode_video2(c, outPktRef, pktFrame, self.decodedRef) 
                
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

        else:
            raise RuntimeError('Unknown media type %s' % mediaType)


class Packet(object):

    ''' Media data container

    When decoding a media, a packet object will be returned and
    might be decoded later.

    When encoding, a packet is retrieved then written.
    '''

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
        self.resampledFrame = None
        
        # after decode

        # retrieve a list of codec context for each stream in file
        self.codecCtx = []
        self.swsCtx = []
        self.scaler = []
        self.resampler = []
        self.resamplerCtx = []

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
            self.resampler.append(None)
            self.resamplerCtx.append(None)

    def addScaler(self, streamIndex, width=None, height=None):

        ''' Add a scaler

        .. note:: called by :meth:`Media.addScaler`
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

    def addResampler(self, streamIndex):

        ''' Add an audio resampler

        .. note:: called by :meth:`Media.addResampler`
        '''
        
        def queryAudioInfos(infos):
            
            infos['sampleFmtId'] = av.lib.av_get_sample_fmt(infos['sampleFmt'])

            if 'channelLayout' not in infos or not infos['channelLayout']:

                # guess channel layout from number of channels

                if hasattr(av.lib, 'av_get_default_channel_layout'):
                    
                    f = av.lib.av_get_default_channel_layout
                else:
                    f = _guessChannelLayout

                infos['layoutId'] = f(infos['channels'])
                
            else:

                infos['layoutId'] = av.lib.av_get_channel_layout(infos['channelLayout'])

                if 'channels' not in infos:
                    infos['channels'] = av.lib.av_get_channel_layout_nb_channels(infos['layoutId'])
        

        inAudio = self.resampler[streamIndex][0]
        queryAudioInfos(inAudio)
        
        outAudio = self.resampler[streamIndex][1]
        queryAudioInfos(outAudio)
      
        # try to setup decoder (faster) else use audio resampling 
        codecCtx = self.codecCtx[streamIndex]
        codec = av.lib.avcodec_find_decoder(codecCtx.contents.codec_id)
        newCodecCtx = av.lib.avcodec_alloc_context3(codec) 
        # TODO: check result
        res = av.lib.avcodec_copy_context(newCodecCtx, codecCtx)

        newCodecCtx.contents.request_sample_fmt = outAudio['sampleFmtId']
        newCodecCtx.contents.request_sample_rate = outAudio['sampleRate']
        newCodecCtx.contents.request_channel_layout = outAudio['layoutId']

        res = av.lib.avcodec_open2(newCodecCtx, codec, None)

        channelLayout = newCodecCtx.contents.channel_layout
        # workaround libav 9
        if channelLayout == 0:
            channelLayout = av.lib.av_get_default_channel_layout( newCodecCtx.contents.channels )

        if newCodecCtx.contents.sample_fmt == outAudio['sampleFmtId'] and newCodecCtx.contents.sample_rate == outAudio['sampleRate'] and channelLayout == outAudio['layoutId']:

            self.codecCtx[streamIndex] = newCodecCtx
            self.resamplingType = 'codec'
        else:
            if 'libswresample.so' in av.lib._libraries:
                self._addSwResampler(streamIndex, inAudio, outAudio)
            else:
                self._addAvResampler(streamIndex, inAudio, outAudio)
            self.resamplingType = 'resampler'

    def _addSwResampler(self, streamIndex, inAudio, outAudio):

        resampleCtx = av.lib.swr_alloc()
        
        # in
        av.lib.av_opt_set_int(resampleCtx, 'in_channel_layout', inAudio['layoutId'], 0)
        av.lib.av_opt_set_int(resampleCtx, 'in_sample_rate', inAudio['sampleRate'], 0)
        av.lib.av_opt_set_sample_fmt(resampleCtx, 'in_sample_fmt', 
                inAudio['sampleFmtId'], 0)
        
        # out
        av.lib.av_opt_set_int(resampleCtx, 'out_channel_layout', outAudio['layoutId'], 0)
        av.lib.av_opt_set_int(resampleCtx, 'out_sample_rate', outAudio['sampleRate'], 0)
        av.lib.av_opt_set_sample_fmt(resampleCtx, 'out_sample_fmt', 
                outAudio['sampleFmtId'], 0)
 
        result = av.lib.swr_init(resampleCtx)
        
        if result < 0: 
            raise RuntimeError(avError(result))
        
        self.resamplerCtx[streamIndex] = resampleCtx

    def _addAvResampler(self, streamIndex, inAudio, outAudio):

        resampleCtx = av.lib.avresample_alloc_context()
        
        # in
        av.lib.av_opt_set_int(resampleCtx, 'in_channel_layout', inAudio['layoutId'], 0)
        av.lib.av_opt_set_int(resampleCtx, 'in_sample_rate', inAudio['sampleRate'], 0)
        av.lib.av_opt_set_int(resampleCtx, 'in_sample_fmt', inAudio['sampleFmtId'], 0)
        
        # out
        av.lib.av_opt_set_int(resampleCtx, 'out_channel_layout', outAudio['layoutId'], 0)
        av.lib.av_opt_set_int(resampleCtx, 'out_sample_rate', outAudio['sampleRate'], 0)
        av.lib.av_opt_set_int(resampleCtx, 'out_sample_fmt', outAudio['sampleFmtId'], 0)
 
        result = av.lib.avresample_open(resampleCtx)
        
        if result < 0: 
            raise RuntimeError(avError(result))
        
        self.resamplerCtx[streamIndex] = resampleCtx

    def __copy__(self):

        p = Packet(self.f)
        
        #ctypes.memmove(p.pktRef, self.pktRef, ctypes.sizeof(av.lib.AVPacket))

        pkt = p.pkt
        srcPkt = self.pkt

        if hasattr(av.lib, 'av_packet_move_ref'):
            av.lib.av_packet_move_ref(pkt, srcPkt)
        else:
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
            pkt.data = ctypes.cast(av.lib.av_malloc(data_size), ctypes.POINTER(av.lib.uint8_t))
            # XXX: use memcpy from libavcodec?
            ctypes.memmove(pkt.data, srcPkt.data, data_size)
                    
            # side data copy
            side_data_size = pkt.side_data_elems * ctypes.sizeof(av.lib.N8AVPacket4DOT_30E)
            p.side_data = ctypes.cast(av.lib.av_malloc(side_data_size), 
                    ctypes.POINTER(av.lib.N8AVPacket4DOT_30E))

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
       
        for ctx in self.resamplerCtx:
            if ctx:
                
                if 'libswresample.so' in av.lib._libraries:
                    #av.lib.swr_close(ctx)
                    av.lib.swr_free(ctx)
                else:
                    #if av.lib.avresample_is_open(ctx):
                    av.lib.avresample_close(ctx)
                    av.lib.avresample_free(ctx)

        if self.swsFrame:
            av.lib.avpicture_free(ctypes.cast(self.swsFrame, ctypes.POINTER(av.lib.AVPicture)))
       
        if self.resampledFrame:
            av.lib.av_free(self.resampledFrame)

        av.lib.av_free(self.frame)
        av.lib.av_free_packet(ctypes.byref(self.pkt))
    
    def data(self):
        
        # burn current stream index & type in self._VAR?
        index = self.streamIndex()
        codecCtx = self.codecCtx[self.pkt.stream_index]
        codecType = codecCtx.contents.codec_type
        
        data = self.frame
        dataLen = data.contents.linesize[0]
        
        if codecType == av.lib.AVMEDIA_TYPE_VIDEO:
            
            if self.swsCtx[streamIndex]:
                data = self.swsFrame
                dataLen = data.contents.linesize[0]
        
        elif codecType == av.lib.AVMEDIA_TYPE_AUDIO:

            if self.resampler[index] and self.resamplingType == 'resampler':
                data = self.resampledFrame
                dataLen = data.contents.linesize[0]

        elif codecType == av.lib.AVMEDIA_TYPE_SUBTITLE:

            data = self.subtitle
            dataLen = data.num_rects
        
        return (data, dataLen)

    def streamIndex(self):
        return self.pkt.stream_index

    def decode(self):
       
        ''' Decode data
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
                    
                    resamplerCtx = self.resamplerCtx[self.pkt.stream_index]

                    if resamplerCtx:

                        resamplerInfos = self.resampler[self.pkt.stream_index]
                        
                        inData = self.frame.contents.extended_data
                        inLineSize = self.frame.contents.linesize[0]
                        inSamples = self.frame.contents.nb_samples 

                        if hasattr(av.lib, 'avresample_get_out_samples'):
                            outSamples = av.lib.avresample_get_out_samples(resamplerCtx,
                                inSamples)
                        else:
                            outSamples = _getOutSamples(resamplerCtx, inSamples, *resamplerInfos)
                       
                        if hasattr(av.lib, 'avresample_convert_frame'):
                        
                            # libav 11
                            self.resampledFrame = av.lib.avcodec_alloc_frame()
                            av.lib.avcodec_get_frame_defaults(self.resampledFrame) 
                            
                            self.frame.contents.channel_layout = resamplerInfos[0]['layoutId']
                            self.frame.contents.sample_rate = resamplerInfos[0]['sampleRate']
                            self.frame.contents.format = resamplerInfos[0]['sampleFmtId']

                            #self.resampledFrame.contents.nb_samples = outSamples 
                            self.resampledFrame.contents.channel_layout = resamplerInfos[1]['layoutId']
                            self.resampledFrame.contents.sample_rate =  resamplerInfos[1]['sampleRate']
                            self.resampledFrame.contents.format =  resamplerInfos[1]['sampleFmtId']
                            
                            #print 'avresample_convert_frame...'
                            result = av.lib.avresample_convert_frame(resamplerCtx,
                                    self.resampledFrame,
                                    self.frame)
                           
                            #print av.lib.AVERROR_INPUT_CHANGED
                            #print av.lib.AVERROR_OUTPUT_CHANGED
                            #print av.lib.AVERROR_INPUT_CHANGED|av.lib.AVERROR_OUTPUT_CHANGED

                            if result < 0:
                                raise RuntimeError(avError(result))


                        else:
                            # libav 9, 10

                            # alloc AVFrame

                            sampleFmt = resamplerInfos[1]['sampleFmtId']
                            channels = resamplerInfos[1]['channels']
                            bufSize = av.lib.av_samples_get_buffer_size(None, 
                                    channels, outSamples,
                                    sampleFmt, 0)
                            buf = ctypes.cast(av.lib.av_malloc(bufSize),
                                    ctypes.POINTER(ctypes.c_ubyte))
                            # silent sound - debug only
                            #ctypes.memset(buf, 0, bufSize)
                            
                            # TODO: free frame
                            self.resampledFrame = av.lib.avcodec_alloc_frame()

                            av.lib.avcodec_get_frame_defaults(self.resampledFrame) 
                            
                            self.resampledFrame.contents.nb_samples = outSamples 

                            res = av.lib.avcodec_fill_audio_frame(self.resampledFrame, 
                                    channels, sampleFmt, 
                                    buf, bufSize, 0)

                            if res < 0:
                                raise RuntimeError('fill audio frame failed: %s' % avError(res))

                            # end alloc AVFrame
                            
                            # convert
                            
                            if 'libswresample.so' in av.lib._libraries:
                                
                                outSamples = av.lib.swr_convert(resamplerCtx,
                                        self.resampledFrame.contents.extended_data,
                                        outSamples,
                                        inData, inSamples)

                            else:
                                
                                outSamples2 = av.lib.avresample_convert(resamplerCtx,
                                        self.resampledFrame.contents.extended_data,
                                        self.resampledFrame.contents.linesize[0],
                                        outSamples,
                                        inData, inLineSize, inSamples)
                            
                            #if result < 0:
                                #raise RuntimeError(avError(result))

                            # TODO: delay and flush resampler ctx

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


def versions():

    ''' Return version & config & license of C libav or ffmpeg libs
    
    :return: dict with keys: version, configuration, license, path
    :rtype: dict
    '''

    versions = {}
    for lib in av.lib._libraries:

            prefix = lib[3:-3]
            fversion = getattr(av.lib, prefix+'_version')
            fconfig = getattr(av.lib, prefix+'_configuration')
            flicense = getattr(av.lib, prefix+'_license')
            
            e = versions[lib[:-3]] = {}
            _version = fversion()
            # FIXME dup code in av.version
            e['version'] = (_version >> 16 & 0xFF, _version >> 8 & 0xFF, _version & 0xFF)
            e['configuration'] = fconfig()
            e['license'] = flicense()
            e['path'] = av.lib._libraries[lib]._name

    return versions


def avError(res):

    ''' Return an error message from an error code

    The libav or ffmpeg functions can return an error code, this function will
    do its best to translate it to an human readable error message. 

    :param res: error code
    :type res: int
    :return: error message
    :rtype: str

    .. note:: if error is unknown, return 'Unknown error code %d' 
    '''

    # cmdutils.c - print_error

    # setup error buffer
    # TODO: size 255?
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


def _guessChannelLayout(nbChannels):

    # reimplement avcodec_guess_channel_layout (not exposed in libav8)

    channelMap = {
            1: av.lib.AV_CH_LAYOUT_MONO,
            2: av.lib.AV_CH_LAYOUT_STEREO,
            3: av.lib.AV_CH_LAYOUT_SURROUND,
            4: av.lib.AV_CH_LAYOUT_QUAD,
            5: av.lib.AV_CH_LAYOUT_5POINT0,
            6: av.lib.AV_CH_LAYOUT_5POINT1,
            8: av.lib.AV_CH_LAYOUT_7POINT1,
            }

    res = 0
    if nbChannels in channelMap:
        res = channelMap[nbChannels]

    return res


def _getOutSamples(resampleCtx, inNbSamples, inAudio, outAudio):

    # reimplement avresample_get_out_samples 
    # (not present in libav9 & libav10 & ffmpeg 1.2)
    
    import math
    import errno

    if 'libswresample.so' in av.lib._libraries:

        samples = av.lib.av_rescale_rnd(av.lib.swr_get_delay(resampleCtx, outAudio['sampleRate'])
                + inNbSamples, 
                inAudio['sampleRate'], outAudio['sampleRate'],
                av.lib.AV_ROUND_UP)

        # check for int overflow?

    else:

        samples = av.lib.avresample_get_delay(resampleCtx) + inNbSamples

        # ~ resample_needed 
        if inAudio['sampleRate'] != outAudio['sampleRate']:
            samples = av.lib.av_rescale_rnd(samples,
                    inAudio['sampleRate'],
                    outAudio['sampleRate'],
                    av.lib.AV_ROUND_UP)

        samples += av.lib.avresample_available(resampleCtx)

        # max signed integer value
        maxInt = math.pow(2, ctypes.sizeof(ctypes.c_int)*8)/2
        if samples > maxInt:
            return -errno.EINVAL
   
    return samples


def codecs():

    ''' Get all supported codecs

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


def formats():

    ''' Get all supported formats 
    
    :return: a dict with 2 keys: muxing and demuxing
    :rtype: dict
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


def codecInfo(name, decode=True):

    ''' Retrieve specific codec information
    
    :param name: codec name
    :type name: str
    :param decode: codec decoder info. Set decode to False to get codec encoder info.
    :type name: bool
    :return: codec information
    :rtype: dict
    :raises: ValueError if codec name is unknown

    .. note::
        codec information keys:
        
        - name
        - longname
        - type: video, audio or subtitle 
        - thread: codec thread capacity
        - autoThread: auto thread support
        - framerates: supported frame rates 
        - samplerates: supported sample rates
        - pixFmts: supported pixel formats
        - profiles: supported encoding profiles
        - sampleFmts: supported sample formats

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
        ci['pixFmts'] = []
        ci['profiles'] = []
        ci['sampleFmts'] = []
        
        # thread caps
        caps = c.contents.capabilities & (av.lib.CODEC_CAP_FRAME_THREADS|av.lib.CODEC_CAP_SLICE_THREADS)
        if caps == (av.lib.CODEC_CAP_FRAME_THREADS|av.lib.CODEC_CAP_SLICE_THREADS):
            ci['thread'] = 'frame and slice'
        elif caps == av.lib.CODEC_CAP_FRAME_THREADS:
            ci['thread'] = 'frame'
        elif caps == av.lib.CODEC_CAP_SLICE_THREADS:
            ci['thread'] = 'slice'

        # support auto thread
        ci['autoThread'] = False
        caps = c.contents.capabilities & (av.lib.CODEC_CAP_AUTO_THREADS)
        if caps == av.lib.CODEC_CAP_AUTO_THREADS:
            ci['autoThread'] = True

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

                if hasattr(av.lib, 'avcodec_get_pix_fmt_name'):
                    f = av.lib.avcodec_get_pix_fmt_name
                else:
                    f = av.lib.av_get_pix_fmt_name
                ci['pixFmts'].append(f(p))

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
                if s == av.lib.AV_SAMPLE_FMT_NONE:
                    break
                ci['sampleFmts'].append(av.lib.av_get_sample_fmt_name(s))

    else:
        raise ValueError('Unable to find codec %s' % name)
    

    return ci


