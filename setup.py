#!/usr/bin/env python

import sys
import os

try:
    from setuptools import setup, find_packages, Command
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages, Command

import restclient

def read_file(name):
    return open(os.path.join(os.path.dirname(__file__), name)).read()

readme = read_file('README.rst')
changes = read_file('CHANGES.rst')

if sys.version_info[:2] < (2, 5):
    install_requires.append('simplejson>=2.2.1')

setup(
    name='restclient',
    version='.'.join(map(str, restclient.__version__)),
    description='RestClient allows you to interact with resources as if they were objects.',
    long_description='\n\n'.join([readme, changes]),
    author='Joeri Bekker',
    author_email='joeri@maykinmedia.nl',
    license='MIT',
    platforms=['any'],
    url='http://github.com/joeribekker/restclient',
    install_requires = [
    'httplib>=0.7.1',
    ],
    include_package_data=True,
    packages=find_packages(exclude=('tests', 'examples')),
    zip_safe=False,
    test_suite='runtests.runtests',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development',
    ],
)
