from distutils.core import setup

setup(
    name='openallure',
    version='0.1d0',
    author='John Graves',
    author_email='john.graves@aut.ac.nz',
    packages=['openallure', 'openallure.test'],
    url='http://openallureds.org',
    license='LICENSE.txt',
    description='Voice-and-vision enabled dialog system',
    long_description=open('README.txt').read()
)
