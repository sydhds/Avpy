from pprint import pprint

from pyav import avMedia

if __name__ == '__main__':

    # cmdline
    from optparse import OptionParser

    usage = "usage: %prog -f"
    parser = OptionParser(usage=usage)
    parser.add_option('-f', '--formats',
            action='store_true',
            help='print supported formats')
    parser.add_option('-c', '--codecs',
            default='all',
            help='print supported codecs (default: %default): all, video, audio, subtitle')
    (options, args) = parser.parse_args()
    
    print('Using pyav version %s' % avMedia.__version__)
    pprint(avMedia.versions())
    
    if options.formats:
        pprint(avMedia.formats())

    if options.codecs:
        codecs = avMedia.codecs()

        if options.codecs in ['audio', 'video', 'subtitle']:
            pprint(codecs[options.codecs])
        else:
            pprint(codecs)

