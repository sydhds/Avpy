import sys

PY3 = True if sys.version_info >= (3, 0) else False

def toString(astr):

    if PY3:
        return astr.decode()
    else:
        return astr

def toCString(astr):

    if PY3:
        return astr.encode('utf-8')
    else:
        return astr

def _guessChannelLayout(nbChannels):

    # reimplement avcodec_guess_channel_layout (not exposed in libav 0.8)

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

def _guessScaling(scaling):

    #av.lib.SWS_X -> experimental?
    #av.lib.SWS_POINT -> nearest neighbor?
    scalingMap = {
        'fast_bilinear' : av.lib.SWS_FAST_BILINEAR,
        'bilinear'      : av.lib.SWS_BILINEAR,
        'bicubic'       : av.lib.SWS_BICUBIC,
        'area'          : av.lib.SWS_AREA,
        'bicubiclin'    : av.lib.SWS_BICUBLIN,
        'gaus'          : av.lib.SWS_GAUSS,
        'sinc'          : av.lib.SWS_SINC,
        'lanczos'       : av.lib.SWS_LANCZOS,
        'spline'        : av.lib.SWS_SPLINE,
        }

    return scalingMap.get(scaling, None)

