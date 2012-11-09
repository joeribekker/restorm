#!/usr/bin/env python
from distribute_setup import use_setuptools
use_setuptools()

import os
import sys
import restorm
from setuptools import setup, find_packages


def read_file(name):
    return open(os.path.join(os.path.dirname(__file__), name)).read()


readme = read_file('README.rst')
changes = read_file('CHANGES.rst')


install_requires = [
    'httplib2>=0.7.1',
]
tests_require = [
    'nose',
    'unittest2',
]
examples_require = [
    'oauth2',
]

if sys.version_info[:2] < (2, 5):
    install_requires.append('simplejson>=2.2.1')


setup(
    name='restorm',
    version='.'.join(map(str, restorm.__version__)),

    # Packaging.
    packages=find_packages(exclude=('tests', 'examples')),
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'test': tests_require,
        'examples': examples_require,
    },
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',

    # Metadata for PyPI.
    description='RestORM allows you to interact with resources as if they were objects.',
    long_description='\n\n'.join([readme, changes]),
    author='Joeri Bekker',
    author_email='joeri@maykinmedia.nl',
    license='MIT',
    platforms=['any'],
    url='http://github.com/joeribekker/restorm',
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
