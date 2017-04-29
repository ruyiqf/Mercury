# coding:utf8
from setuptools import setup

import vob

long_desc = """

mecury
===============

* Backing test and trading platform for quantitative investment of financial asset

Installation
--------------


Upgrade
---------------


Quick Start
--------------

"""

setup(
    name='mecury',
    version=vob.__version__,
    description='A system for investing financial asset',
    long_description=long_desc,
    author='ruyiqf',
    author_email='mingqian_tech@ruyiqf.com',
    license='BSD',
    url='https://github.com/ruyiqf/Mercury.git'
    keywords='Quantitative financial investment',
    install_requires=[
            'click',
            'tarfile',
            'shultil',
            'bcolz',
    ],
    classifiers=['Development Status :: 4 - Beta',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'License :: OSI Approved :: BSD License'],
    packages=['vob'],
    package_data={'': ['*.json'], 'config': ['*.json']},
)
