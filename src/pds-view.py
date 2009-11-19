#!/usr/bin/env python
# encoding: utf-8
"""
pds-view.py

Created by Ryan Balfanz on 2009-11-18.
Copyright (c) 2009 Ryan Balfanz. All rights reserved.
"""

import optparse
import sys

from pds.imageextractor import ImageExtractor

def setUpOptionParser():
	"""docstring for setUpOptionParser"""
	usage = "usage: %prog [options] args"
	parser = optparse.OptionParser(usage=usage, version="%prog-dev")
	
	# Define the option parser default values.
	parser.set_defaults(filename=sys.stdin)
	parser.set_defaults(verbose=False)
	parser.set_defaults(show_labels=False)
	parser.set_defaults(ignore_exceptions=False)
	parser.set_defaults(step_through=False)
	
	# Define option parser groups.
	dangerGroup = optparse.OptionGroup(parser, "Dangerous/Experimental Options",
		"Caution: use these options at your own risk."
		"It is believed that some of them bite.")
	dangerGroup.add_option("--ignore-exceptions",
		action="store_true", dest="ignore_exceptions",
		help="Ignore exceptions raised on image extraction. Turn on verbose output to examine.")
	parser.add_option_group(dangerGroup)
	
	# Define the options we accept.
	# parser.add_option("-f", "--file", dest="filename",
	# 	help="read data from FILENAME")
	parser.add_option("-v", "--verbose",
		action="store_true", dest="verbose",
		help="make lots of noise")
	parser.add_option("-q", "--quiet",
		action="store_false", dest="verbose",
		help="surpress output")
	parser.add_option("--show-labels",
		action="store_false", dest="show_labels",
		help="pretty print PDS labels [default=%default]")
	parser.add_option("--step-through",
		action="store_true", dest="step_through",
		help="step through input files incrementally on user input [default=%default]")
		
	return parser
		
		
if __name__ == '__main__':
	parser = setUpOptionParser()
	(options, args) = parser.parse_args()
		
	if not args:
		parser.error("you must specifiy at least one input file argument")
	
	extractor = ImageExtractor()
	for pdsFile in args:
		if options.step_through:
			sys.stderr.write("stepping through files... press key to continue\n")
			raw_input()
			
		if options.verbose:
			errorMessage = "Reading input from '%s'\n" % (pdsFile)
			sys.stderr.write(errorMessage)
		
		img = None
		try:
			img, labels = extractor.extract(pdsFile)
		except:
			if options.ignore_exceptions:
				if options.verbose:
					errorMessage = "Warn: Caught exception raised during extraction of '%s', ignoring\n" % (pdsFile)
					sys.stderr.write(errorMessage)
			else:
				# If not ignoring caught exceptions, re-raise
				raise
			
		if not img:
			errorMessage = "Error: Could not extract image from %s\n" % (options.filename)
			sys.stderr.write(errorMessage)
		else:
			if options.show_labels:
				import pprint
				pprint.pprint(labels)
			img.show()
			