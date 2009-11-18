#!/usr/bin/env python
# encoding: utf-8
"""
pdsview.py

Created by Ryan Matthew Balfanz on 2009-11-18.
Copyright (c) 2009 Ryan Matthew Balfanz. All rights reserved.
"""

import optparse
import sys

from pds.imageextractor import ImageExtractor

if __name__ == '__main__':
	parser = optparse.OptionParser()
	parser.set_defaults(filename=sys.stdin)
	parser.set_defaults(verbose=True)
	parser.add_option("-f", "--file", dest="filename",
		help="read data from FILENAME")
	parser.add_option("-v", "--verbose",
		action="store_true", dest="verbose",
		help="make lots of noise [default]")
	parser.add_option("-q", "--quiet",
		action="store_false", dest="verbose",
		help="be vewwy quiet (I'm hunting wabbits)")
	(options, args) = parser.parse_args()
	
	extractor = ImageExtractor()
	if options.verbose:
		sys.stderr.write("Reading input from '%s'\n" % (options.filename))
	img, labels = extractor.extract(options.filename)
	if img:
		if options.verbose:
			import pprint
			pprint.pprint(labels)
		img.show()
	else:
		sys.stderr.write("ERROR: Could not extract image from %s\n" % (options.filename))