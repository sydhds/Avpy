#!/usr/bin/env python

'''
pyav tools/build.py

Generate clean binding
'''

import re

import yaml

def longCb(line):

    # handle long value and remove L at the end of line
    # for python3 support
    return re.sub('(\d+)L', '\g<1>', line)

def wHeader(fp, yamlDict):

    for l in yamlDict['import']:
        if not l:
            l = ''
        fp.write(l+'\n')
    fp.write('\n')
    for l in yamlDict['cdll']:
        fp.write(l+'\n')
    fp.write('\n')

def wClass(fp, yamlDict):

    for l in yamlDict['class']:
        fp.write('class %s(Structure):\n\tpass\n\n' % l)

def wAssignement(fp, yamlDict, src, key, cb=None):

    with open(src, 'r') as f:
	
        found = set()
	#write_line = False
        line = f.readline()
        while line:
            for t in yamlDict[key]:
                if line.startswith( '%s =' % t ):
                    
                    if cb:
                        fp.write(cb(line))
                    else:
                        fp.write(line)
		    found.add(t)
                    break
	    line = f.readline()
        fp.write('\n')

    notFound = set(yamlDict[key]) - found
    if notFound:
        print 'Could not find:'
        for t in notFound:
            print '- %s' % t

def wClassFields(fp, yamlDict, src):

    with open(src, 'r') as f:

        write_line = False
        line = f.readline()
        classFound = set()
        while line:
            for c in yamlDict['class']:
                if line.startswith( '%s._fields_' % c ):
                    write_line = True
                    classFound.add(c)
                    break

            if line.startswith(']'):
                if write_line:
                    fp.write(line)
                    write_line = False

            if write_line:
                fp.write(line)

            line = f.readline()
    fp.write('\n')

    notFound = set(yamlDict['class']) - classFound
    if notFound:
        print 'Could not find class(es):'
        for c in notFound:
            print '- %s' % c


def wFunctions(fp, yamlDict, src):

    fcts = yamlDict['function']
    dupFunctions = set([x for x in fcts if fcts.count(x) > 1])
    for f in dupFunctions:
        print 'Warning: duplicated functions in config: %s' % f

    with open(src, 'r') as f:

        line = f.readline()
        functionFound = set()
        while line:
            for fct in fcts:
                if re.search('%s(\ =|\.argtypes|\.restype)' % fct, 
                        line):
                    fp.write(line)
                    functionFound.add(fct)

            line = f.readline()

    fp.write('\n')

    notFound = set(yamlDict['function']) - functionFound
    if notFound:
        print 'Could not find function(s):'
        for f in notFound:
            print '- %s' % f


def main(options):

    y = {}
    with open(options.cfg, 'r') as f:
        y = yaml.load(f.read())

    fd = open(options.dst, 'w')	
    print 'writing:'
    print 'header...'
    wHeader(fd, y)
    print 'type...'
    wAssignement(fd, y, options.src, 'type')
    print 'define...'
    wAssignement(fd, y, options.src, 'define')
    print 'define long...'
    wAssignement(fd, y, options.src, 'defineLong', longCb)
    print 'class...'
    wClass(fd, y)
    print 'alias...'
    wAssignement(fd, y, options.src, 'alias')
    print 'class data...'
    wClassFields(fd, y, options.src)
    print 'functions...'
    wFunctions(fd, y, options.src)
    print 'done: %s' % options.dst

if __name__ == '__main__':

    from optparse import OptionParser
    
    usage = '%prog -s av08.py -d av8.py -c config/libav08.yml'
    parser = OptionParser(usage=usage)

    parser.add_option('-s', '--src', help='python source')
    parser.add_option('-d', '--dst', help='python destination')
    parser.add_option('-c', '--cfg', help='config file')

    (options, args) = parser.parse_args()

    main(options)
