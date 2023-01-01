#!/usr/bin/env python
# encoding: utf-8
"""
setup.py

Created by Ryan Balfanz on 2010-01-30.
Copyright (c) 2010 Ryan Balfanz. All rights reserved.
"""

from distutils.core import setup

with open("README.rst", "r") as f:
	long_description_readme = f.read()

setup(
	name='PyPDS',
	version='1.0.1',
	description='PyPDS is a Python interface to Planetary Data System (PDS) data products',
	long_description=long_description_readme,
	author='Ryan Balfanz',
	author_email='ryan@ryanbalfanz.net',
	url='http://github.com/RyanBalfanz/PyPDS',
	packages=['pds', 'pds.core'],
	scripts=['bin/pds-labels.py', 'bin/pds-image.py', 'bin/pds-view.py', 'bin/pds-convert.py'],)
