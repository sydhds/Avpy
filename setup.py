from distutils.core import setup

setup(
    name='Avpy',
    version='0.1.0',
    author='Sylvain Delhomme',
    author_email='sydhds@gmail.com',
    packages=['avpy', 'avpy.version'],
    url='',
    license='LICENSE.txt',
    description='ctypes python binding for libav',
    long_description=open('README.txt').read(),
    install_requires=[
    ],
)
