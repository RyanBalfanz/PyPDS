#!/usr/bin/env python
# encoding: utf-8
"""
common.py

Created by Ryan Matthew Balfanz on 2009-06-24.

Copyright (c) 2009 Ryan Matthew Balfanz. All rights reserved.
"""

import sys

# from contextlib import contextmanager
from contextlib import closing

PDS_END_OF_LINE = r"\r\n"
PDS_END_OF_HEADER = r"END"
PDS_CONTAINERS = {"OBJECT":"END_OBJECT", "GROUP":"END_GROUP"}

def isValidPDSFile(filename):
	"""Check if a PDS file is valid by performing a series of mini-checks.
	
	The following check are performed
		* Filesize is equal to (RECORD_BYTES * FILE_RECORDS),
		based afrigeri's comment to issue 3 (http://github.com/RyanBalfanz/PyPDS/issues/#issue/3).
		Note that this check creates it's own Parser instance, for only two lookups.
	"""
	# Filesize check
	import os
	fileBytes = os.path.getsize(filename)
	from parser import Parser
	parser = Parser()
	labels = parser.parse(open_pds(filename))
	expectedFileBytes = int(labels["FILE_RECORDS"]) * int(labels["RECORD_BYTES"])
	
	validityChecks = (# lambda : True, # lambda : False,
		lambda : fileBytes == expectedFileBytes and True or False,)
	checkVals = (check() for check in validityChecks)
	
	return False not in checkVals

def open_pds(source):
	"""Open a PDS data file source (flexibly).
	
	This method generalizes the standard open() function call.
	The *source* may be a file-like object, a file, a URL, or a string.
	"""
	# if isinstance(source, file):
	# 	return source
	if hasattr(source, "read"):
		#sys.stderr.write("Identified a file-like object by read() method existence\n")
		return source

	try:
		# For universal newlines -- i.e. newlines are automatically converted to "\n", use mode "U".
		# For preserved newlines -- e.g. "\r", "\r\n", "\n", use mode "rb".
		# PDS style newlines are "\r\n", however, http://pds.jpl.nasa.gov/documents/qs/sample_image.lbl uses "\n".
		# Check if hasattr(open, 'newlines') to verify that universal newline support is enabeled.
		f = open(source, "rb")

		#reading the file as a byte-like object. Try to decode if necessary
		try:
			f = f.decode('utf-8')
		except(UnicodeDecodeError, AttributeError):
			pass
		return f
	except (IOError, OSError):
		# sys.stderr.write("Could not open source\n")
		raise
	else:
		# sys.stderr.write("Opened source\n")
		# Re-raise to catch something hairy.
		raise
	finally:
		pass
		# sys.stderr.write("Closing previously opened file\n")
		# f.close()
		
	if isinstance(source, str):
		try:
			import cStringIO as StringIO
		except ImportError:
			import StringIO
		else:
			# sys.stderr.write("Making a file-like object from string source\n")
			return StringIO.StringIO(str(source))
			
	# try:
	# 	import urllib
	# 	f = urllib.urlopen(source)
	# 	return f
	# except (IOError, OSError):
	# 	pass
	# else:
	# 	# Re-raise to catch something hairy.
	# 	raise
	# finally:
	# 	pass

if __name__ == '__main__':
	pass
	