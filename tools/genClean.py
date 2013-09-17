#!/usr/bin/env python

'''
pyav tools/build.py

Generate clean binding
'''

import yaml

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

def wAssignement(fp, yamlDict, src, key):

    with open(src, 'r') as f:
		
	#write_line = False
        line = f.readline()
        while line:
            for t in yamlDict[key]:
                if line.startswith( '%s =' % t ):
                    fp.write(line)
		    break
	    line = f.readline()
        fp.write('\n')

def wClassFields(fp, yamlDict, src):

    with open(src, 'r') as f:

        write_line = False
        line = f.readline()
        while line:
            for c in yamlDict['class']:
                if line.startswith( '%s._fields_' % c ):
                    write_line = True
                    break

            if line.startswith(']'):
                if write_line:
                    fp.write(line)
                    write_line = False

            if write_line:
                fp.write(line)

            line = f.readline()
    fp.write('\n')

def wFunctions(fp, yamlDict, src):

    with open(src, 'r') as f:

        line = f.readline()
        while line:
            for fct in yamlDict['function']:
                if line.startswith(fct):
                    fp.write(line)


            line = f.readline()

    fp.write('\n')


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
