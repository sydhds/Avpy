import os
import re
from ctypes import CDLL, RTLD_GLOBAL
from ctypes import Structure, POINTER, CFUNCTYPE
from ctypes import c_int, c_uint, c_char, c_void_p, c_char_p, c_ubyte
from ctypes import c_short
from ctypes import c_ulong
from ctypes import c_int8, c_uint8
from ctypes import c_int16, c_uint16
from ctypes import c_int32, c_uint32
from ctypes import c_int64, c_uint64
from ctypes import c_float
from ctypes import c_double
from ctypes import util

if 'AVPY_AVCODEC' in os.environ:
    fold, base = os.path.split(os.environ['AVPY_AVCODEC'])
    libavutil = os.environ.get('AVPY_AVUTIL')
    if not libavutil:
        libavutil = os.path.join(fold, re.sub('avcodec', 'avutil', base))
    libavformat = os.environ.get('AVPY_AVFORMAT')
    if not libavformat:
        libavformat = os.path.join(fold, re.sub('avcodec', 'avformat', base))
    libavdevice = os.environ.get('AVPY_AVDEVICE')
    if not libavdevice:
        libavdevice = os.path.join(fold, re.sub('avcodec', 'avdevice', base))
    libswscale = os.environ.get('AVPY_SWSCALE')
    if not libswscale:
        libswscale = os.path.join(fold, re.sub('avcodec', 'swscale', base))
    libavcodec = os.environ['AVPY_AVCODEC']
else:
    libavutil = util.find_library('avutil')
    libavcodec = util.find_library('avcodec')
    libavformat = util.find_library('avformat')
    libavdevice = util.find_library('avdevice')
    libswscale = util.find_library('swscale')

CDLL(libavutil, RTLD_GLOBAL)
_libraries = {}
_libraries['libavutil.so'] = CDLL(libavutil, mode=RTLD_GLOBAL)
_libraries['libavcodec.so'] = CDLL(libavcodec, mode=RTLD_GLOBAL)
_libraries['libavformat.so'] = CDLL(libavformat, mode=RTLD_GLOBAL)
_libraries['libavdevice.so'] = CDLL(libavdevice, mode=RTLD_GLOBAL)
_libraries['libswscale.so'] = CDLL(libswscale, mode=RTLD_GLOBAL)
_libraries['name'] = 'libav'
_libraries['version'] = 0.8

STRING = c_char_p
size_t = c_ulong
AVSampleFormat = c_int # enum
CodecID = c_int # enum
AVDiscard = c_int # enum
AVColorPrimaries = c_int # enum
AVColorTransferCharacteristic = c_int # enum
AVColorSpace = c_int # enum
AVColorRange = c_int # enum
AVChromaLocation = c_int # enum
AVLPCType = c_int # enum
AVAudioServiceType = c_int # enum
int16_t = c_int16
AVPacketSideDataType = c_int # enum
int64_t = c_int64
uint8_t = c_uint8
AVPictureType = c_int # enum
int8_t = c_int8
uint32_t = c_uint32
uint64_t = c_uint64
AVFieldOrder = c_int # enum
PixelFormat = c_int # enum
AVMediaType = c_int # enum
uint16_t = c_uint16
AVSubtitleType = c_int # enum
AVStreamParseType = c_int # enum
int32_t = c_int32

AV_SAMPLE_FMT_NONE = -1
SUBTITLE_ASS = 3
SUBTITLE_BITMAP = 1
AV_DICT_IGNORE_SUFFIX = 2 # Variable c_int '2'
AV_SAMPLE_FMT_S16 = 1
AVMEDIA_TYPE_SUBTITLE = 3
CODEC_ID_MPEG1VIDEO = 1
AVMEDIA_TYPE_AUDIO = 1
AVMEDIA_TYPE_VIDEO = 0
SUBTITLE_TEXT = 2
PIX_FMT_YUV420P = 0
PIX_FMT_RGB8 = 22
PIX_FMT_RGB24 = 2
CODEC_ID_MPEG2VIDEO = 2
PIX_FMT_NONE = -1
CODEC_ID_NONE = 0
SUBTITLE_NONE = 0
AVSEEK_FLAG_BACKWARD = 1 # Variable c_int '1'
SWS_BILINEAR = 2 # Variable c_int '2'
AVFMT_GLOBALHEADER = 64 # Variable c_int '64'
CODEC_CAP_AUTO_THREADS = 32768 # Variable c_int '32768'
AV_PKT_FLAG_KEY = 1 # Variable c_int '1'
CODEC_CAP_FRAME_THREADS = 4096 # Variable c_int '4096'
SWS_SINC = 256 # Variable c_int '256'
CODEC_FLAG_GLOBAL_HEADER = 4194304 # Variable c_int '4194304'
SWS_LANCZOS = 512 # Variable c_int '512'
SWS_BICUBIC = 4 # Variable c_int '4'
FF_COMPLIANCE_STRICT = 1 # Variable c_int '1'
AVFMT_NOFILE = 1 # Variable c_int '1'
AVIO_FLAG_WRITE = 2 # Variable c_int '2'
SWS_FAST_BILINEAR = 1 # Variable c_int '1'
AV_LOG_QUIET = -8 # Variable c_int '-0x00000000000000008'
AVSEEK_FLAG_FRAME = 8 # Variable c_int '8'
FF_COMPLIANCE_NORMAL = 0 # Variable c_int '0'
SWS_GAUSS = 128 # Variable c_int '128'
SWS_BICUBLIN = 64 # Variable c_int '64'
CODEC_CAP_SLICE_THREADS = 8192 # Variable c_int '8192'
AVSEEK_FLAG_ANY = 4 # Variable c_int '4'
AV_TIME_BASE = 1000000 # Variable c_int '1000000'
SWS_SPLINE = 1024 # Variable c_int '1024'
SWS_AREA = 32 # Variable c_int '32'
AVSEEK_FLAG_BYTE = 2 # Variable c_int '2'

AV_NOPTS_VALUE = 9223372036854775808 # Variable c_ulong '-9223372036854775808ul'

class N8AVPacket4DOT_30E(Structure):
	pass

class N8AVStream4DOT_30E(Structure):
	pass

class N8AVOption4DOT_30E(Structure):
	pass

class AVProfile(Structure):
	pass

class AVPanScan(Structure):
	pass

class AVCodec(Structure):
	pass

class RcOverride(Structure):
	pass

class AVFrame(Structure):
	pass

class AVPaletteControl(Structure):
	pass

class AVHWAccel(Structure):
	pass

class AVCodecParser(Structure):
	pass

class AVFormatParameters(Structure):
	pass

class AVCodecContext(Structure):
	pass

class AVCodecParserContext(Structure):
	pass

class AVIndexEntry(Structure):
	pass

class AVDictionary(Structure):
	pass

class AVIOContext(Structure):
	pass

class AVOption(Structure):
	pass

class AVCodecTag(Structure):
	pass

class AVMetadataConv(Structure):
	pass

class AVProbeData(Structure):
	pass

class AVRational(Structure):
	pass

class AVFrac(Structure):
	pass

class AVClass(Structure):
	pass

class AVInputFormat(Structure):
	pass

class AVOutputFormat(Structure):
	pass

class AVStream(Structure):
	pass

class AVPacketList(Structure):
	pass

class AVStream(Structure):
	pass

class AVPacket(Structure):
	pass

class AVProgram(Structure):
	pass

class AVChapter(Structure):
	pass

class AVPacketList(Structure):
	pass

class AVFormatContext(Structure):
	pass

class AVPicture(Structure):
	pass

class SwsContext(Structure):
	pass

class SwsFilter(Structure):
	pass

class SwsVector(Structure):
	pass

class AVCodecInternal(Structure):
	pass

class AVCodecDefault(Structure):
	pass

class AVIOInterruptCB(Structure):
	pass

class AVDictionaryEntry(Structure):
	pass

class AVSubtitle(Structure):
	pass

class AVSubtitleRect(Structure):
	pass

AV_CH_LAYOUT_5POINT0 = 1543 # Variable c_int '1543'
AV_CH_LAYOUT_MONO = 4 # Variable c_int '4'
AV_CH_LAYOUT_STEREO = 3 # Variable c_int '3'
AV_CH_LAYOUT_QUAD = 51 # Variable c_int '51'
AV_CH_LAYOUT_5POINT1 = 1551 # Variable c_int '1551'
AV_CH_LAYOUT_7POINT1 = 1599 # Variable c_int '1599'
AV_CH_LAYOUT_SURROUND = 7 # Variable c_int '7'
AVMetadata = AVDictionary
ByteIOContext = AVIOContext
AVOptionType = c_int # enum

RcOverride._fields_ = [
    ('start_frame', c_int),
    ('end_frame', c_int),
    ('qscale', c_int),
    ('quality_factor', c_float),
]
AVPanScan._fields_ = [
    ('id', c_int),
    ('width', c_int),
    ('height', c_int),
    ('position', int16_t * 2 * 3),
]
AVPacket._fields_ = [
    ('pts', int64_t),
    ('dts', int64_t),
    ('data', POINTER(uint8_t)),
    ('size', c_int),
    ('stream_index', c_int),
    ('flags', c_int),
    ('side_data', POINTER(N8AVPacket4DOT_30E)),
    ('side_data_elems', c_int),
    ('duration', c_int),
    ('destruct', CFUNCTYPE(None, POINTER(AVPacket))),
    ('priv', c_void_p),
    ('pos', int64_t),
    ('convergence_duration', int64_t),
]
N8AVPacket4DOT_30E._fields_ = [
    ('data', POINTER(uint8_t)),
    ('size', c_int),
    ('type', AVPacketSideDataType),
]
AVRational._fields_ = [
    ('num', c_int),
    ('den', c_int),
]
AVFrame._fields_ = [
    ('data', POINTER(uint8_t) * 4),
    ('linesize', c_int * 4),
    ('base', POINTER(uint8_t) * 4),
    ('key_frame', c_int),
    ('pict_type', AVPictureType),
    ('pts', int64_t),
    ('coded_picture_number', c_int),
    ('display_picture_number', c_int),
    ('quality', c_int),
    ('age', c_int),
    ('reference', c_int),
    ('qscale_table', POINTER(int8_t)),
    ('qstride', c_int),
    ('mbskip_table', POINTER(uint8_t)),
    ('motion_val', POINTER(int16_t * 2) * 2),
    ('mb_type', POINTER(uint32_t)),
    ('motion_subsample_log2', uint8_t),
    ('opaque', c_void_p),
    ('error', uint64_t * 4),
    ('type', c_int),
    ('repeat_pict', c_int),
    ('qscale_type', c_int),
    ('interlaced_frame', c_int),
    ('top_field_first', c_int),
    ('pan_scan', POINTER(AVPanScan)),
    ('palette_has_changed', c_int),
    ('buffer_hints', c_int),
    ('dct_coeff', POINTER(c_short)),
    ('ref_index', POINTER(int8_t) * 2),
    ('reordered_opaque', int64_t),
    ('hwaccel_picture_private', c_void_p),
    ('pkt_pts', int64_t),
    ('pkt_dts', int64_t),
    ('owner', POINTER(AVCodecContext)),
    ('thread_opaque', c_void_p),
    ('nb_samples', c_int),
    ('extended_data', POINTER(POINTER(uint8_t))),
    ('sample_aspect_ratio', AVRational),
    ('width', c_int),
    ('height', c_int),
    ('format', c_int),
]
AVCodecInternal._fields_ = [
]
AVCodecContext._fields_ = [
    ('av_class', POINTER(AVClass)),
    ('bit_rate', c_int),
    ('bit_rate_tolerance', c_int),
    ('flags', c_int),
    ('sub_id', c_int),
    ('me_method', c_int),
    ('extradata', POINTER(uint8_t)),
    ('extradata_size', c_int),
    ('time_base', AVRational),
    ('width', c_int),
    ('height', c_int),
    ('gop_size', c_int),
    ('pix_fmt', PixelFormat),
    ('draw_horiz_band', CFUNCTYPE(None, POINTER(AVCodecContext), POINTER(AVFrame), POINTER(c_int), c_int, c_int, c_int)),
    ('sample_rate', c_int),
    ('channels', c_int),
    ('sample_fmt', AVSampleFormat),
    ('frame_size', c_int),
    ('frame_number', c_int),
    ('delay', c_int),
    ('qcompress', c_float),
    ('qblur', c_float),
    ('qmin', c_int),
    ('qmax', c_int),
    ('max_qdiff', c_int),
    ('max_b_frames', c_int),
    ('b_quant_factor', c_float),
    ('rc_strategy', c_int),
    ('b_frame_strategy', c_int),
    ('codec', POINTER(AVCodec)),
    ('priv_data', c_void_p),
    ('rtp_payload_size', c_int),
    ('rtp_callback', CFUNCTYPE(None, POINTER(AVCodecContext), c_void_p, c_int, c_int)),
    ('mv_bits', c_int),
    ('header_bits', c_int),
    ('i_tex_bits', c_int),
    ('p_tex_bits', c_int),
    ('i_count', c_int),
    ('p_count', c_int),
    ('skip_count', c_int),
    ('misc_bits', c_int),
    ('frame_bits', c_int),
    ('opaque', c_void_p),
    ('codec_name', c_char * 32),
    ('codec_type', AVMediaType),
    ('codec_id', CodecID),
    ('codec_tag', c_uint),
    ('workaround_bugs', c_int),
    ('luma_elim_threshold', c_int),
    ('chroma_elim_threshold', c_int),
    ('strict_std_compliance', c_int),
    ('b_quant_offset', c_float),
    ('error_recognition', c_int),
    ('get_buffer', CFUNCTYPE(c_int, POINTER(AVCodecContext), POINTER(AVFrame))),
    ('release_buffer', CFUNCTYPE(None, POINTER(AVCodecContext), POINTER(AVFrame))),
    ('has_b_frames', c_int),
    ('block_align', c_int),
    ('parse_only', c_int),
    ('mpeg_quant', c_int),
    ('stats_out', STRING),
    ('stats_in', STRING),
    ('rc_qsquish', c_float),
    ('rc_qmod_amp', c_float),
    ('rc_qmod_freq', c_int),
    ('rc_override', POINTER(RcOverride)),
    ('rc_override_count', c_int),
    ('rc_eq', STRING),
    ('rc_max_rate', c_int),
    ('rc_min_rate', c_int),
    ('rc_buffer_size', c_int),
    ('rc_buffer_aggressivity', c_float),
    ('i_quant_factor', c_float),
    ('i_quant_offset', c_float),
    ('rc_initial_cplx', c_float),
    ('dct_algo', c_int),
    ('lumi_masking', c_float),
    ('temporal_cplx_masking', c_float),
    ('spatial_cplx_masking', c_float),
    ('p_masking', c_float),
    ('dark_masking', c_float),
    ('idct_algo', c_int),
    ('slice_count', c_int),
    ('slice_offset', POINTER(c_int)),
    ('error_concealment', c_int),
    ('dsp_mask', c_uint),
    ('bits_per_coded_sample', c_int),
    ('prediction_method', c_int),
    ('sample_aspect_ratio', AVRational),
    ('coded_frame', POINTER(AVFrame)),
    ('debug', c_int),
    ('debug_mv', c_int),
    ('error', uint64_t * 4),
    ('me_cmp', c_int),
    ('me_sub_cmp', c_int),
    ('mb_cmp', c_int),
    ('ildct_cmp', c_int),
    ('dia_size', c_int),
    ('last_predictor_count', c_int),
    ('pre_me', c_int),
    ('me_pre_cmp', c_int),
    ('pre_dia_size', c_int),
    ('me_subpel_quality', c_int),
    ('get_format', CFUNCTYPE(PixelFormat, POINTER(AVCodecContext), POINTER(PixelFormat))),
    ('dtg_active_format', c_int),
    ('me_range', c_int),
    ('intra_quant_bias', c_int),
    ('inter_quant_bias', c_int),
    ('color_table_id', c_int),
    ('internal_buffer_count', c_int),
    ('internal_buffer', c_void_p),
    ('global_quality', c_int),
    ('coder_type', c_int),
    ('context_model', c_int),
    ('slice_flags', c_int),
    ('xvmc_acceleration', c_int),
    ('mb_decision', c_int),
    ('intra_matrix', POINTER(uint16_t)),
    ('inter_matrix', POINTER(uint16_t)),
    ('stream_codec_tag', c_uint),
    ('scenechange_threshold', c_int),
    ('lmin', c_int),
    ('lmax', c_int),
    ('palctrl', POINTER(AVPaletteControl)),
    ('noise_reduction', c_int),
    ('reget_buffer', CFUNCTYPE(c_int, POINTER(AVCodecContext), POINTER(AVFrame))),
    ('rc_initial_buffer_occupancy', c_int),
    ('inter_threshold', c_int),
    ('flags2', c_int),
    ('error_rate', c_int),
    ('antialias_algo', c_int),
    ('quantizer_noise_shaping', c_int),
    ('thread_count', c_int),
    ('execute', CFUNCTYPE(c_int, POINTER(AVCodecContext), CFUNCTYPE(c_int, POINTER(AVCodecContext), c_void_p), c_void_p, POINTER(c_int), c_int, c_int)),
    ('thread_opaque', c_void_p),
    ('me_threshold', c_int),
    ('mb_threshold', c_int),
    ('intra_dc_precision', c_int),
    ('nsse_weight', c_int),
    ('skip_top', c_int),
    ('skip_bottom', c_int),
    ('profile', c_int),
    ('level', c_int),
    ('lowres', c_int),
    ('coded_width', c_int),
    ('coded_height', c_int),
    ('frame_skip_threshold', c_int),
    ('frame_skip_factor', c_int),
    ('frame_skip_exp', c_int),
    ('frame_skip_cmp', c_int),
    ('border_masking', c_float),
    ('mb_lmin', c_int),
    ('mb_lmax', c_int),
    ('me_penalty_compensation', c_int),
    ('skip_loop_filter', AVDiscard),
    ('skip_idct', AVDiscard),
    ('skip_frame', AVDiscard),
    ('bidir_refine', c_int),
    ('brd_scale', c_int),
    ('crf', c_float),
    ('cqp', c_int),
    ('keyint_min', c_int),
    ('refs', c_int),
    ('chromaoffset', c_int),
    ('bframebias', c_int),
    ('trellis', c_int),
    ('complexityblur', c_float),
    ('deblockalpha', c_int),
    ('deblockbeta', c_int),
    ('partitions', c_int),
    ('directpred', c_int),
    ('cutoff', c_int),
    ('scenechange_factor', c_int),
    ('mv0_threshold', c_int),
    ('b_sensitivity', c_int),
    ('compression_level', c_int),
    ('min_prediction_order', c_int),
    ('max_prediction_order', c_int),
    ('lpc_coeff_precision', c_int),
    ('prediction_order_method', c_int),
    ('min_partition_order', c_int),
    ('max_partition_order', c_int),
    ('timecode_frame_start', int64_t),
    ('request_channels', c_int),
    ('drc_scale', c_float),
    ('reordered_opaque', int64_t),
    ('bits_per_raw_sample', c_int),
    ('channel_layout', uint64_t),
    ('request_channel_layout', uint64_t),
    ('rc_max_available_vbv_use', c_float),
    ('rc_min_vbv_overflow_use', c_float),
    ('hwaccel', POINTER(AVHWAccel)),
    ('ticks_per_frame', c_int),
    ('hwaccel_context', c_void_p),
    ('color_primaries', AVColorPrimaries),
    ('color_trc', AVColorTransferCharacteristic),
    ('colorspace', AVColorSpace),
    ('color_range', AVColorRange),
    ('chroma_sample_location', AVChromaLocation),
    ('execute2', CFUNCTYPE(c_int, POINTER(AVCodecContext), CFUNCTYPE(c_int, POINTER(AVCodecContext), c_void_p, c_int, c_int), c_void_p, POINTER(c_int), c_int)),
    ('weighted_p_pred', c_int),
    ('aq_mode', c_int),
    ('aq_strength', c_float),
    ('psy_rd', c_float),
    ('psy_trellis', c_float),
    ('rc_lookahead', c_int),
    ('crf_max', c_float),
    ('log_level_offset', c_int),
    ('lpc_type', AVLPCType),
    ('lpc_passes', c_int),
    ('slices', c_int),
    ('subtitle_header', POINTER(uint8_t)),
    ('subtitle_header_size', c_int),
    ('pkt', POINTER(AVPacket)),
    ('is_copy', c_int),
    ('thread_type', c_int),
    ('active_thread_type', c_int),
    ('thread_safe_callbacks', c_int),
    ('vbv_delay', uint64_t),
    ('audio_service_type', AVAudioServiceType),
    ('request_sample_fmt', AVSampleFormat),
    ('err_recognition', c_int),
    ('internal', POINTER(AVCodecInternal)),
    ('field_order', AVFieldOrder),
]
AVProfile._fields_ = [
    ('profile', c_int),
    ('name', STRING),
]
AVCodecDefault._fields_ = [
]
AVCodec._fields_ = [
    ('name', STRING),
    ('type', AVMediaType),
    ('id', CodecID),
    ('priv_data_size', c_int),
    ('init', CFUNCTYPE(c_int, POINTER(AVCodecContext))),
    ('encode', CFUNCTYPE(c_int, POINTER(AVCodecContext), POINTER(uint8_t), c_int, c_void_p)),
    ('close', CFUNCTYPE(c_int, POINTER(AVCodecContext))),
    ('decode', CFUNCTYPE(c_int, POINTER(AVCodecContext), c_void_p, POINTER(c_int), POINTER(AVPacket))),
    ('capabilities', c_int),
    ('next', POINTER(AVCodec)),
    ('flush', CFUNCTYPE(None, POINTER(AVCodecContext))),
    ('supported_framerates', POINTER(AVRational)),
    ('pix_fmts', POINTER(PixelFormat)),
    ('long_name', STRING),
    ('supported_samplerates', POINTER(c_int)),
    ('sample_fmts', POINTER(AVSampleFormat)),
    ('channel_layouts', POINTER(uint64_t)),
    ('max_lowres', uint8_t),
    ('priv_class', POINTER(AVClass)),
    ('profiles', POINTER(AVProfile)),
    ('init_thread_copy', CFUNCTYPE(c_int, POINTER(AVCodecContext))),
    ('update_thread_context', CFUNCTYPE(c_int, POINTER(AVCodecContext), POINTER(AVCodecContext))),
    ('defaults', POINTER(AVCodecDefault)),
    ('init_static_data', CFUNCTYPE(None, POINTER(AVCodec))),
    ('encode2', CFUNCTYPE(c_int, POINTER(AVCodecContext), POINTER(AVPacket), POINTER(AVFrame), POINTER(c_int))),
]
AVHWAccel._fields_ = [
    ('name', STRING),
    ('type', AVMediaType),
    ('id', CodecID),
    ('pix_fmt', PixelFormat),
    ('capabilities', c_int),
    ('next', POINTER(AVHWAccel)),
    ('start_frame', CFUNCTYPE(c_int, POINTER(AVCodecContext), POINTER(uint8_t), uint32_t)),
    ('decode_slice', CFUNCTYPE(c_int, POINTER(AVCodecContext), POINTER(uint8_t), uint32_t)),
    ('end_frame', CFUNCTYPE(c_int, POINTER(AVCodecContext))),
    ('priv_data_size', c_int),
]
AVPicture._fields_ = [
    ('data', POINTER(uint8_t) * 4),
    ('linesize', c_int * 4),
]
AVPaletteControl._fields_ = [
    ('palette_changed', c_int),
    ('palette', c_uint * 256),
]
AVSubtitleRect._fields_ = [
    ('x', c_int),
    ('y', c_int),
    ('w', c_int),
    ('h', c_int),
    ('nb_colors', c_int),
    ('pict', AVPicture),
    ('type', AVSubtitleType),
    ('text', STRING),
    ('ass', STRING),
]
AVSubtitle._fields_ = [
    ('format', uint16_t),
    ('start_display_time', uint32_t),
    ('end_display_time', uint32_t),
    ('num_rects', c_uint),
    ('rects', POINTER(POINTER(AVSubtitleRect))),
    ('pts', int64_t),
]
AVCodecParserContext._fields_ = [
    ('priv_data', c_void_p),
    ('parser', POINTER(AVCodecParser)),
    ('frame_offset', int64_t),
    ('cur_offset', int64_t),
    ('next_frame_offset', int64_t),
    ('pict_type', c_int),
    ('repeat_pict', c_int),
    ('pts', int64_t),
    ('dts', int64_t),
    ('last_pts', int64_t),
    ('last_dts', int64_t),
    ('fetch_timestamp', c_int),
    ('cur_frame_start_index', c_int),
    ('cur_frame_offset', int64_t * 4),
    ('cur_frame_pts', int64_t * 4),
    ('cur_frame_dts', int64_t * 4),
    ('flags', c_int),
    ('offset', int64_t),
    ('cur_frame_end', int64_t * 4),
    ('key_frame', c_int),
    ('convergence_duration', int64_t),
    ('dts_sync_point', c_int),
    ('dts_ref_dts_delta', c_int),
    ('pts_dts_delta', c_int),
    ('cur_frame_pos', int64_t * 4),
    ('pos', int64_t),
    ('last_pos', int64_t),
]
AVCodecParser._fields_ = [
    ('codec_ids', c_int * 5),
    ('priv_data_size', c_int),
    ('parser_init', CFUNCTYPE(c_int, POINTER(AVCodecParserContext))),
    ('parser_parse', CFUNCTYPE(c_int, POINTER(AVCodecParserContext), POINTER(AVCodecContext), POINTER(POINTER(uint8_t)), POINTER(c_int), POINTER(uint8_t), c_int)),
    ('parser_close', CFUNCTYPE(None, POINTER(AVCodecParserContext))),
    ('split', CFUNCTYPE(c_int, POINTER(AVCodecContext), POINTER(uint8_t), c_int)),
    ('next', POINTER(AVCodecParser)),
]
AVMetadataConv._fields_ = [
]
AVDictionaryEntry._fields_ = [
    ('key', STRING),
    ('value', STRING),
]
AVFrac._fields_ = [
    ('val', int64_t),
    ('num', int64_t),
    ('den', int64_t),
]
AVCodecTag._fields_ = [
]
AVProbeData._fields_ = [
    ('filename', STRING),
    ('buf', POINTER(c_ubyte)),
    ('buf_size', c_int),
]
AVFormatParameters._fields_ = [
    ('time_base', AVRational),
    ('sample_rate', c_int),
    ('channels', c_int),
    ('width', c_int),
    ('height', c_int),
    ('pix_fmt', PixelFormat),
    ('channel', c_int),
    ('standard', STRING),
    ('mpeg2ts_raw', c_uint, 1),
    ('mpeg2ts_compute_pcr', c_uint, 1),
    ('initial_pause', c_uint, 1),
    ('prealloced_context', c_uint, 1),
]
AVOutputFormat._fields_ = [
    ('name', STRING),
    ('long_name', STRING),
    ('mime_type', STRING),
    ('extensions', STRING),
    ('priv_data_size', c_int),
    ('audio_codec', CodecID),
    ('video_codec', CodecID),
    ('write_header', CFUNCTYPE(c_int, POINTER(AVFormatContext))),
    ('write_packet', CFUNCTYPE(c_int, POINTER(AVFormatContext), POINTER(AVPacket))),
    ('write_trailer', CFUNCTYPE(c_int, POINTER(AVFormatContext))),
    ('flags', c_int),
    ('set_parameters', CFUNCTYPE(c_int, POINTER(AVFormatContext), POINTER(AVFormatParameters))),
    ('interleave_packet', CFUNCTYPE(c_int, POINTER(AVFormatContext), POINTER(AVPacket), POINTER(AVPacket), c_int)),
    ('codec_tag', POINTER(POINTER(AVCodecTag))),
    ('subtitle_codec', CodecID),
    ('metadata_conv', POINTER(AVMetadataConv)),
    ('priv_class', POINTER(AVClass)),
    ('query_codec', CFUNCTYPE(c_int, CodecID, c_int)),
    ('next', POINTER(AVOutputFormat)),
]
AVInputFormat._fields_ = [
    ('name', STRING),
    ('long_name', STRING),
    ('priv_data_size', c_int),
    ('read_probe', CFUNCTYPE(c_int, POINTER(AVProbeData))),
    ('read_header', CFUNCTYPE(c_int, POINTER(AVFormatContext), POINTER(AVFormatParameters))),
    ('read_packet', CFUNCTYPE(c_int, POINTER(AVFormatContext), POINTER(AVPacket))),
    ('read_close', CFUNCTYPE(c_int, POINTER(AVFormatContext))),
    ('read_seek', CFUNCTYPE(c_int, POINTER(AVFormatContext), c_int, int64_t, c_int)),
    ('read_timestamp', CFUNCTYPE(int64_t, POINTER(AVFormatContext), c_int, POINTER(int64_t), int64_t)),
    ('flags', c_int),
    ('extensions', STRING),
    ('value', c_int),
    ('read_play', CFUNCTYPE(c_int, POINTER(AVFormatContext))),
    ('read_pause', CFUNCTYPE(c_int, POINTER(AVFormatContext))),
    ('codec_tag', POINTER(POINTER(AVCodecTag))),
    ('read_seek2', CFUNCTYPE(c_int, POINTER(AVFormatContext), c_int, int64_t, int64_t, int64_t, c_int)),
    ('metadata_conv', POINTER(AVMetadataConv)),
    ('priv_class', POINTER(AVClass)),
    ('next', POINTER(AVInputFormat)),
]
AVIndexEntry._fields_ = [
    ('pos', int64_t),
    ('timestamp', int64_t),
    ('flags', c_int, 2),
    ('size', c_int, 30),
    ('min_distance', c_int),
]
AVStream._fields_ = [
    ('index', c_int),
    ('id', c_int),
    ('codec', POINTER(AVCodecContext)),
    ('r_frame_rate', AVRational),
    ('priv_data', c_void_p),
    ('first_dts', int64_t),
    ('pts', AVFrac),
    ('time_base', AVRational),
    ('pts_wrap_bits', c_int),
    ('stream_copy', c_int),
    ('discard', AVDiscard),
    ('quality', c_float),
    ('start_time', int64_t),
    ('duration', int64_t),
    ('need_parsing', AVStreamParseType),
    ('parser', POINTER(AVCodecParserContext)),
    ('cur_dts', int64_t),
    ('last_IP_duration', c_int),
    ('last_IP_pts', int64_t),
    ('index_entries', POINTER(AVIndexEntry)),
    ('nb_index_entries', c_int),
    ('index_entries_allocated_size', c_uint),
    ('nb_frames', int64_t),
    ('disposition', c_int),
    ('probe_data', AVProbeData),
    ('pts_buffer', int64_t * 17),
    ('sample_aspect_ratio', AVRational),
    ('metadata', POINTER(AVDictionary)),
    ('cur_ptr', POINTER(uint8_t)),
    ('cur_len', c_int),
    ('cur_pkt', AVPacket),
    ('reference_dts', int64_t),
    ('probe_packets', c_int),
    ('last_in_packet_buffer', POINTER(AVPacketList)),
    ('avg_frame_rate', AVRational),
    ('codec_info_nb_frames', c_int),
    ('info', POINTER(N8AVStream4DOT_30E)),
]
N8AVStream4DOT_30E._fields_ = [
    ('last_dts', int64_t),
    ('duration_gcd', int64_t),
    ('duration_count', c_int),
    ('duration_error', c_double * 725),
    ('codec_info_duration', int64_t),
    ('nb_decoded_frames', c_int),
]
AVProgram._fields_ = [
    ('id', c_int),
    ('flags', c_int),
    ('discard', AVDiscard),
    ('stream_index', POINTER(c_uint)),
    ('nb_stream_indexes', c_uint),
    ('metadata', POINTER(AVDictionary)),
]
AVChapter._fields_ = [
    ('id', c_int),
    ('time_base', AVRational),
    ('start', int64_t),
    ('end', int64_t),
    ('metadata', POINTER(AVDictionary)),
]
AVIOInterruptCB._fields_ = [
    ('callback', CFUNCTYPE(c_int, c_void_p)),
    ('opaque', c_void_p),
]
AVFormatContext._fields_ = [
    ('av_class', POINTER(AVClass)),
    ('iformat', POINTER(AVInputFormat)),
    ('oformat', POINTER(AVOutputFormat)),
    ('priv_data', c_void_p),
    ('pb', POINTER(AVIOContext)),
    ('nb_streams', c_uint),
    ('streams', POINTER(POINTER(AVStream))),
    ('filename', c_char * 1024),
    ('timestamp', int64_t),
    ('ctx_flags', c_int),
    ('packet_buffer', POINTER(AVPacketList)),
    ('start_time', int64_t),
    ('duration', int64_t),
    ('file_size', int64_t),
    ('bit_rate', c_int),
    ('cur_st', POINTER(AVStream)),
    ('data_offset', int64_t),
    ('mux_rate', c_int),
    ('packet_size', c_uint),
    ('preload', c_int),
    ('max_delay', c_int),
    ('loop_output', c_int),
    ('flags', c_int),
    ('loop_input', c_int),
    ('probesize', c_uint),
    ('max_analyze_duration', c_int),
    ('key', POINTER(uint8_t)),
    ('keylen', c_int),
    ('nb_programs', c_uint),
    ('programs', POINTER(POINTER(AVProgram))),
    ('video_codec_id', CodecID),
    ('audio_codec_id', CodecID),
    ('subtitle_codec_id', CodecID),
    ('max_index_size', c_uint),
    ('max_picture_buffer', c_uint),
    ('nb_chapters', c_uint),
    ('chapters', POINTER(POINTER(AVChapter))),
    ('debug', c_int),
    ('raw_packet_buffer', POINTER(AVPacketList)),
    ('raw_packet_buffer_end', POINTER(AVPacketList)),
    ('packet_buffer_end', POINTER(AVPacketList)),
    ('metadata', POINTER(AVDictionary)),
    ('raw_packet_buffer_remaining_size', c_int),
    ('start_time_realtime', int64_t),
    ('fps_probe_size', c_int),
    ('error_recognition', c_int),
    ('interrupt_callback', AVIOInterruptCB),
]
AVPacketList._fields_ = [
    ('pkt', AVPacket),
    ('next', POINTER(AVPacketList)),
]
AVIOContext._fields_ = [
    ('buffer', POINTER(c_ubyte)),
    ('buffer_size', c_int),
    ('buf_ptr', POINTER(c_ubyte)),
    ('buf_end', POINTER(c_ubyte)),
    ('opaque', c_void_p),
    ('read_packet', CFUNCTYPE(c_int, c_void_p, POINTER(uint8_t), c_int)),
    ('write_packet', CFUNCTYPE(c_int, c_void_p, POINTER(uint8_t), c_int)),
    ('seek', CFUNCTYPE(int64_t, c_void_p, int64_t, c_int)),
    ('pos', int64_t),
    ('must_flush', c_int),
    ('eof_reached', c_int),
    ('write_flag', c_int),
    ('is_streamed', c_int),
    ('max_packet_size', c_int),
    ('checksum', c_ulong),
    ('checksum_ptr', POINTER(c_ubyte)),
    ('update_checksum', CFUNCTYPE(c_ulong, c_ulong, POINTER(uint8_t), c_uint)),
    ('error', c_int),
    ('read_pause', CFUNCTYPE(c_int, c_void_p, c_int)),
    ('read_seek', CFUNCTYPE(int64_t, c_void_p, c_int, int64_t, c_int)),
    ('seekable', c_int),
]
AVDictionary._fields_ = [
]
N8AVOption4DOT_30E._fields_ = [
    ('dbl', c_double),
    ('str', STRING),
    ('i64', int64_t),
    ('q', AVRational),
]
AVOption._fields_ = [
    ('name', STRING),
    ('help', STRING),
    ('offset', c_int),
    ('type', AVOptionType),
    ('default_val', N8AVOption4DOT_30E),
    ('min', c_double),
    ('max', c_double),
    ('flags', c_int),
    ('unit', STRING),
]
AVClass._fields_ = [
    ('class_name', STRING),
    ('item_name', CFUNCTYPE(STRING, c_void_p)),
    ('option', POINTER(AVOption)),
    ('version', c_int),
    ('log_level_offset_offset', c_int),
    ('parent_log_context_offset', c_int),
    ('child_next', CFUNCTYPE(c_void_p, c_void_p, c_void_p)),
    ('child_class_next', CFUNCTYPE(POINTER(AVClass), POINTER(AVClass))),
]
SwsVector._fields_ = [
    ('coeff', POINTER(c_double)),
    ('length', c_int),
]
SwsFilter._fields_ = [
    ('lumH', POINTER(SwsVector)),
    ('lumV', POINTER(SwsVector)),
    ('chrH', POINTER(SwsVector)),
    ('chrV', POINTER(SwsVector)),
]
SwsContext._fields_ = [
]

av_init_packet = _libraries['libavcodec.so'].av_init_packet
av_init_packet.restype = None
av_init_packet.argtypes = [POINTER(AVPacket)]
av_free_packet = _libraries['libavcodec.so'].av_free_packet
av_free_packet.restype = None
av_free_packet.argtypes = [POINTER(AVPacket)]
avpicture_alloc = _libraries['libavcodec.so'].avpicture_alloc
avpicture_alloc.restype = c_int
avpicture_alloc.argtypes = [POINTER(AVPicture), PixelFormat, c_int, c_int]
avpicture_free = _libraries['libavcodec.so'].avpicture_free
avpicture_free.restype = None
avpicture_free.argtypes = [POINTER(AVPicture)]
avpicture_fill = _libraries['libavcodec.so'].avpicture_fill
avpicture_fill.restype = c_int
avpicture_fill.argtypes = [POINTER(AVPicture), POINTER(uint8_t), PixelFormat, c_int, c_int]
avpicture_get_size = _libraries['libavcodec.so'].avpicture_get_size
avpicture_get_size.restype = c_int
avpicture_get_size.argtypes = [PixelFormat, c_int, c_int]
avcodec_get_pix_fmt_name = _libraries['libavcodec.so'].avcodec_get_pix_fmt_name
avcodec_get_pix_fmt_name.restype = STRING
avcodec_get_pix_fmt_name.argtypes = [PixelFormat]
av_codec_next = _libraries['libavcodec.so'].av_codec_next
av_codec_next.restype = POINTER(AVCodec)
av_codec_next.argtypes = [POINTER(AVCodec)]
avcodec_version = _libraries['libavcodec.so'].avcodec_version
avcodec_version.restype = c_uint
avcodec_version.argtypes = []
avcodec_configuration = _libraries['libavcodec.so'].avcodec_configuration
avcodec_configuration.restype = STRING
avcodec_configuration.argtypes = []
avcodec_license = _libraries['libavcodec.so'].avcodec_license
avcodec_license.restype = STRING
avcodec_license.argtypes = []
avcodec_find_encoder = _libraries['libavcodec.so'].avcodec_find_encoder
avcodec_find_encoder.restype = POINTER(AVCodec)
avcodec_find_encoder.argtypes = [CodecID]
avcodec_find_encoder_by_name = _libraries['libavcodec.so'].avcodec_find_encoder_by_name
avcodec_find_encoder_by_name.restype = POINTER(AVCodec)
avcodec_find_encoder_by_name.argtypes = [STRING]
avcodec_find_decoder = _libraries['libavcodec.so'].avcodec_find_decoder
avcodec_find_decoder.restype = POINTER(AVCodec)
avcodec_find_decoder.argtypes = [CodecID]
avcodec_find_decoder_by_name = _libraries['libavcodec.so'].avcodec_find_decoder_by_name
avcodec_find_decoder_by_name.restype = POINTER(AVCodec)
avcodec_find_decoder_by_name.argtypes = [STRING]
avcodec_get_context_defaults3 = _libraries['libavcodec.so'].avcodec_get_context_defaults3
avcodec_get_context_defaults3.restype = c_int
avcodec_get_context_defaults3.argtypes = [POINTER(AVCodecContext), POINTER(AVCodec)]
avcodec_alloc_context3 = _libraries['libavcodec.so'].avcodec_alloc_context3
avcodec_alloc_context3.restype = POINTER(AVCodecContext)
avcodec_alloc_context3.argtypes = [POINTER(AVCodec)]
avcodec_copy_context = _libraries['libavcodec.so'].avcodec_copy_context
avcodec_copy_context.restype = c_int
avcodec_copy_context.argtypes = [POINTER(AVCodecContext), POINTER(AVCodecContext)]
avcodec_get_frame_defaults = _libraries['libavcodec.so'].avcodec_get_frame_defaults
avcodec_get_frame_defaults.restype = None
avcodec_get_frame_defaults.argtypes = [POINTER(AVFrame)]
avcodec_alloc_frame = _libraries['libavcodec.so'].avcodec_alloc_frame
avcodec_alloc_frame.restype = POINTER(AVFrame)
avcodec_alloc_frame.argtypes = []
avcodec_open2 = _libraries['libavcodec.so'].avcodec_open2
avcodec_open2.restype = c_int
avcodec_open2.argtypes = [POINTER(AVCodecContext), POINTER(AVCodec), POINTER(POINTER(AVDictionary))]
avcodec_decode_audio4 = _libraries['libavcodec.so'].avcodec_decode_audio4
avcodec_decode_audio4.restype = c_int
avcodec_decode_audio4.argtypes = [POINTER(AVCodecContext), POINTER(AVFrame), POINTER(c_int), POINTER(AVPacket)]
avcodec_decode_video2 = _libraries['libavcodec.so'].avcodec_decode_video2
avcodec_decode_video2.restype = c_int
avcodec_decode_video2.argtypes = [POINTER(AVCodecContext), POINTER(AVFrame), POINTER(c_int), POINTER(AVPacket)]
avcodec_decode_subtitle2 = _libraries['libavcodec.so'].avcodec_decode_subtitle2
avcodec_decode_subtitle2.restype = c_int
avcodec_decode_subtitle2.argtypes = [POINTER(AVCodecContext), POINTER(AVSubtitle), POINTER(c_int), POINTER(AVPacket)]
avsubtitle_free = _libraries['libavcodec.so'].avsubtitle_free
avsubtitle_free.restype = None
avsubtitle_free.argtypes = [POINTER(AVSubtitle)]
avcodec_encode_audio2 = _libraries['libavcodec.so'].avcodec_encode_audio2
avcodec_encode_audio2.restype = c_int
avcodec_encode_audio2.argtypes = [POINTER(AVCodecContext), POINTER(AVPacket), POINTER(AVFrame), POINTER(c_int)]
avcodec_fill_audio_frame = _libraries['libavcodec.so'].avcodec_fill_audio_frame
avcodec_fill_audio_frame.restype = c_int
avcodec_fill_audio_frame.argtypes = [POINTER(AVFrame), c_int, AVSampleFormat, POINTER(uint8_t), c_int, c_int]
avcodec_encode_video = _libraries['libavcodec.so'].avcodec_encode_video
avcodec_encode_video.restype = c_int
avcodec_encode_video.argtypes = [POINTER(AVCodecContext), POINTER(uint8_t), c_int, POINTER(AVFrame)]
avcodec_close = _libraries['libavcodec.so'].avcodec_close
avcodec_close.restype = c_int
avcodec_close.argtypes = [POINTER(AVCodecContext)]
avdevice_version = _libraries['libavdevice.so'].avdevice_version
avdevice_version.restype = c_uint
avdevice_version.argtypes = []
avdevice_configuration = _libraries['libavdevice.so'].avdevice_configuration
avdevice_configuration.restype = STRING
avdevice_configuration.argtypes = []
avdevice_license = _libraries['libavdevice.so'].avdevice_license
avdevice_license.restype = STRING
avdevice_license.argtypes = []
avformat_version = _libraries['libavformat.so'].avformat_version
avformat_version.restype = c_uint
avformat_version.argtypes = []
avformat_configuration = _libraries['libavformat.so'].avformat_configuration
avformat_configuration.restype = STRING
avformat_configuration.argtypes = []
avformat_license = _libraries['libavformat.so'].avformat_license
avformat_license.restype = STRING
avformat_license.argtypes = []
av_register_all = _libraries['libavformat.so'].av_register_all
av_register_all.restype = None
av_register_all.argtypes = []
av_iformat_next = _libraries['libavformat.so'].av_iformat_next
av_iformat_next.restype = POINTER(AVInputFormat)
av_iformat_next.argtypes = [POINTER(AVInputFormat)]
av_oformat_next = _libraries['libavformat.so'].av_oformat_next
av_oformat_next.restype = POINTER(AVOutputFormat)
av_oformat_next.argtypes = [POINTER(AVOutputFormat)]
avformat_alloc_context = _libraries['libavformat.so'].avformat_alloc_context
avformat_alloc_context.restype = POINTER(AVFormatContext)
avformat_alloc_context.argtypes = []
avformat_free_context = _libraries['libavformat.so'].avformat_free_context
avformat_free_context.restype = None
avformat_free_context.argtypes = [POINTER(AVFormatContext)]
avformat_new_stream = _libraries['libavformat.so'].avformat_new_stream
avformat_new_stream.restype = POINTER(AVStream)
avformat_new_stream.argtypes = [POINTER(AVFormatContext), POINTER(AVCodec)]
avformat_open_input = _libraries['libavformat.so'].avformat_open_input
avformat_open_input.restype = c_int
avformat_open_input.argtypes = [POINTER(POINTER(AVFormatContext)), STRING, POINTER(AVInputFormat), POINTER(POINTER(AVDictionary))]
av_find_stream_info = _libraries['libavformat.so'].av_find_stream_info
av_find_stream_info.restype = c_int
av_find_stream_info.argtypes = [POINTER(AVFormatContext)]
avformat_find_stream_info = _libraries['libavformat.so'].avformat_find_stream_info
avformat_find_stream_info.restype = c_int
avformat_find_stream_info.argtypes = [POINTER(AVFormatContext), POINTER(POINTER(AVDictionary))]
av_read_frame = _libraries['libavformat.so'].av_read_frame
av_read_frame.restype = c_int
av_read_frame.argtypes = [POINTER(AVFormatContext), POINTER(AVPacket)]
av_seek_frame = _libraries['libavformat.so'].av_seek_frame
av_seek_frame.restype = c_int
av_seek_frame.argtypes = [POINTER(AVFormatContext), c_int, int64_t, c_int]
avformat_close_input = _libraries['libavformat.so'].avformat_close_input
avformat_close_input.restype = None
avformat_close_input.argtypes = [POINTER(POINTER(AVFormatContext))]
av_write_header = _libraries['libavformat.so'].av_write_header
av_write_header.restype = c_int
av_write_header.argtypes = [POINTER(AVFormatContext)]
av_interleaved_write_frame = _libraries['libavformat.so'].av_interleaved_write_frame
av_interleaved_write_frame.restype = c_int
av_interleaved_write_frame.argtypes = [POINTER(AVFormatContext), POINTER(AVPacket)]
av_write_trailer = _libraries['libavformat.so'].av_write_trailer
av_write_trailer.restype = c_int
av_write_trailer.argtypes = [POINTER(AVFormatContext)]
av_guess_format = _libraries['libavformat.so'].av_guess_format
av_guess_format.restype = POINTER(AVOutputFormat)
av_guess_format.argtypes = [STRING, STRING, STRING]
av_guess_codec = _libraries['libavformat.so'].av_guess_codec
av_guess_codec.restype = CodecID
av_guess_codec.argtypes = [POINTER(AVOutputFormat), STRING, STRING, STRING, AVMediaType]
av_codec_get_id = _libraries['libavformat.so'].av_codec_get_id
av_codec_get_id.restype = CodecID
av_codec_get_id.argtypes = [POINTER(POINTER(AVCodecTag)), c_uint]
avformat_query_codec = _libraries['libavformat.so'].avformat_query_codec
avformat_query_codec.restype = c_int
avformat_query_codec.argtypes = [POINTER(AVOutputFormat), CodecID, c_int]
avio_open = _libraries['libavformat.so'].avio_open
avio_open.restype = c_int
avio_open.argtypes = [POINTER(POINTER(AVIOContext)), STRING, c_int]
avio_close = _libraries['libavformat.so'].avio_close
avio_close.restype = c_int
avio_close.argtypes = [POINTER(AVIOContext)]
av_get_channel_layout = _libraries['libavutil.so'].av_get_channel_layout
av_get_channel_layout.restype = uint64_t
av_get_channel_layout.argtypes = [STRING]
av_get_channel_layout_string = _libraries['libavutil.so'].av_get_channel_layout_string
av_get_channel_layout_string.restype = None
av_get_channel_layout_string.argtypes = [STRING, c_int, c_int, uint64_t]
avutil_version = _libraries['libavutil.so'].avutil_version
avutil_version.restype = c_uint
avutil_version.argtypes = []
avutil_configuration = _libraries['libavutil.so'].avutil_configuration
avutil_configuration.restype = STRING
avutil_configuration.argtypes = []
avutil_license = _libraries['libavutil.so'].avutil_license
avutil_license.restype = STRING
avutil_license.argtypes = []
av_dict_get = _libraries['libavutil.so'].av_dict_get
av_dict_get.restype = POINTER(AVDictionaryEntry)
av_dict_get.argtypes = [POINTER(AVDictionary), STRING, POINTER(AVDictionaryEntry), c_int]
av_dict_set = _libraries['libavutil.so'].av_dict_set
av_dict_set.restype = c_int
av_dict_set.argtypes = [POINTER(POINTER(AVDictionary)), STRING, STRING, c_int]
av_strerror = _libraries['libavutil.so'].av_strerror
av_strerror.restype = c_int
av_strerror.argtypes = [c_int, STRING, size_t]
av_log_set_level = _libraries['libavutil.so'].av_log_set_level
av_log_set_level.restype = None
av_log_set_level.argtypes = [c_int]
av_malloc = _libraries['libavutil.so'].av_malloc
av_malloc.restype = c_void_p
av_malloc.argtypes = [size_t]
av_free = _libraries['libavutil.so'].av_free
av_free.restype = None
av_free.argtypes = [c_void_p]
av_get_pix_fmt = _libraries['libavutil.so'].av_get_pix_fmt
av_get_pix_fmt.restype = PixelFormat
av_get_pix_fmt.argtypes = [STRING]
av_get_sample_fmt_name = _libraries['libavutil.so'].av_get_sample_fmt_name
av_get_sample_fmt_name.restype = STRING
av_get_sample_fmt_name.argtypes = [AVSampleFormat]
av_get_sample_fmt = _libraries['libavutil.so'].av_get_sample_fmt
av_get_sample_fmt.restype = AVSampleFormat
av_get_sample_fmt.argtypes = [STRING]
av_get_bytes_per_sample = _libraries['libavutil.so'].av_get_bytes_per_sample
av_get_bytes_per_sample.restype = c_int
av_get_bytes_per_sample.argtypes = [AVSampleFormat]
av_samples_get_buffer_size = _libraries['libavutil.so'].av_samples_get_buffer_size
av_samples_get_buffer_size.restype = c_int
av_samples_get_buffer_size.argtypes = [POINTER(c_int), c_int, c_int, AVSampleFormat, c_int]
swscale_version = _libraries['libswscale.so'].swscale_version
swscale_version.restype = c_uint
swscale_version.argtypes = []
swscale_configuration = _libraries['libswscale.so'].swscale_configuration
swscale_configuration.restype = STRING
swscale_configuration.argtypes = []
swscale_license = _libraries['libswscale.so'].swscale_license
swscale_license.restype = STRING
swscale_license.argtypes = []
sws_freeContext = _libraries['libswscale.so'].sws_freeContext
sws_freeContext.restype = None
sws_freeContext.argtypes = [POINTER(SwsContext)]
sws_getContext = _libraries['libswscale.so'].sws_getContext
sws_getContext.restype = POINTER(SwsContext)
sws_getContext.argtypes = [c_int, c_int, PixelFormat, c_int, c_int, PixelFormat, c_int, POINTER(SwsFilter), POINTER(SwsFilter), POINTER(c_double)]
sws_scale = _libraries['libswscale.so'].sws_scale
sws_scale.restype = c_int
sws_scale.argtypes = [POINTER(SwsContext), POINTER(POINTER(uint8_t)), POINTER(c_int), c_int, c_int, POINTER(POINTER(uint8_t)), POINTER(c_int)]

