#!/usr/bin/env python
# encoding: utf-8
"""
common.py

Created by Ryan Matthew Balfanz on 2009-06-24.

Copyright (c) 2009 Ryan Matthew Balfanz. All rights reserved.
"""

PDS_END_OF_LINE = r"\r\n"
PDS_END_OF_HEADER = r"END"
PDS_CONTAINERS = {"OBJECT":"END_OBJECT", "GROUP":"END_GROUP"}

def open_pds(source):
	"""Open a PDS data file source (flexibly).
	
	This method generalizes the standard open() function call.
	The *source* may be a file-like object, a file, a URL, or a string.
	"""
	if hasattr(source, 'read'):
		return source

	try:
		# For universal newlines -- i.e. newlines are automatically converted to "\n", use mode "U".
		# For preserved newlines -- e.g. "\r", "\r\n", "\n", use mode "rb".
		# PDS style newlines are "\r\n", however, http://pds.jpl.nasa.gov/documents/qs/sample_image.lbl uses "\n".
		# Check if hasattr(open, 'newlines') to verify that universal newline support is enabeled.
		f = open(source, "U")
		return f
	except (IOError, OSError):
		pass
	else:
		# Re-raise to catch something hairy.
		raise
	finally:
		pass
		#f.close()
		
	import urllib
	try:
		f = urllib.urlopen(source)
		return f
	except (IOError, OSError):
		pass
	else:
		# Re-raise to catch something hairy.
		raise
	finally:
		pass

	try:
		import cStringIO as StringIO
	except ImportError:
		import StringIO
	return StringIO.StringIO(str(source))

if __name__ == '__main__':
	pass