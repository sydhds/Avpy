from pprint import pprint

from pyav import avMedia

if __name__ == '__main__':

    print('Using pyav version %s' % avMedia.__version__)
    pprint(avMedia.versions())

