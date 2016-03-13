from distutils.core import setup

setup(
    name='Avpy',
    version='0.1.2',
    author='Sylvain Delhomme',
    author_email='sydhds@gmail.com',
    packages=['avpy', 'avpy.version'],
    url='https://bitbucket.org/sydh/avpy',
    license='LGPL v2.1+',
    description='ctypes binding for libav and ffmpeg',
    long_description=open('README.txt').read(),
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',

        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Conversion',
        'Topic :: Multimedia :: Video',
        'Topic :: Multimedia :: Video :: Conversion',
    ],
    install_requires=[
    ],
)
