#!/usr/bin/env python

'''
Burn special structure according to config

gen.py will generate some dynamic class like:
- N8AVPacket4_34E or N8AVPacket3_23E
fix.py will replace the corresponding class found by the one defined in config:
- N8AVPacket4_34E -> N8AVPacket4_30E
'''

import os
import re
from functools import partial

import yaml

if __name__ == '__main__':

    from optparse import OptionParser
    
    usage = '%prog -s av008.py -d av008_fix.py -c config/libav08.yml'
    parser = OptionParser(usage=usage)

    parser.add_option('-s', '--src', help='python source')
    parser.add_option('-d', '--dst', help='python destination')
    parser.add_option('-c', '--cfg', help='config file')

    (options, args) = parser.parse_args()
    
    # find dynamic class in config file
    # and build a dict:
    # Option: N8AVOption4_30E
    with open(options.cfg, 'r') as cfp:
        y = yaml.load(cfp.read())
    
    dcMap = {
        'Option': None,
        'Stream': None,
        'Packet': None,
        }

    for cls in y['class']:
        rgx = re.search('^(N8AV(%s))' % '|'.join(dcMap), cls)
        if rgx:
            dcMap[rgx.group(2)] = cls

    fixCount = 0
    print('writing %s...' % options.dst)
    with open(options.src, 'r') as sfp:
        with open(options.dst, 'w') as dfp:
            for line in sfp:

                # fonction call by re.sub
                def replClass(dcMap, count, matchobj):
                    global fixCount
                    fixCount += 1
                    return dcMap[matchobj.group(1)]
        
                # brute force!
                nline = re.sub('N8AV(%s)\dDOT_\d+E' % '|'.join(dcMap), 
                        partial(replClass, dcMap, [fixCount]),
                        line)

                dfp.write(nline)

    print('%d line(s) fixed!' % fixCount)

