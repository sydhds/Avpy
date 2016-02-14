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

