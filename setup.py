from distutils.core import setup

setup(
    name='Pyav',
    version='0.0.1',
    author='Sylvain Delhomme',
    author_email='sydhds@gmail.com',
    packages=['pyav', 'pyav.version'],
    url='',
    license='LICENSE.txt',
    description='ctypes python binding for libav',
    long_description=open('README.txt').read(),
    install_requires=[
    ],
)
