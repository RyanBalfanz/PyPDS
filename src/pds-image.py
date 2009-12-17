#!/usr/bin/env python
# encoding: utf-8
"""
pds-image.py

Created by Ryan Balfanz on 2009-12-06.
Copyright (c) 2009 Ryan Balfanz. All rights reserved.
"""

import optparse
import sys

import cStringIO as StringIO

from pds.imageextractor import ImageExtractor

def gfiles(*args, **kwargs):
	"""Generate chunked files from input provided by fileinput.input().
	
	Yields a filename and contents, with line endings preserved.
	"""
	import fileinput
	import cStringIO as StringIO
	
	from collections import deque
	
	d = deque()
	for line in fileinput.input(*args, **kwargs):
		if fileinput.isfirstline():
			try:
				fname, fhandle = d.pop()
				yield fname, fhandle.getvalue()
			except IndexError:
				pass
			d.append((fileinput.filename(), StringIO.StringIO()))
			buf = d[-1][1]
		buf.write(line)
		
	fname, fhandle = d.pop()
	yield fname, fhandle.getvalue()

def setUpOptionParser():
	"""docstring for setUpOptionParser"""
	usage = "usage: %prog [options] args"
	parser = optparse.OptionParser(usage=usage, version="%prog-dev")
	
	# Define the option parser default values.
	parser.set_defaults(filename=sys.stdin)
	parser.set_defaults(verbose=False)
	parser.set_defaults(format=None)
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
	
	parser.add_option("-v", "--verbose",
		action="store_true", dest="verbose",
		help="make lots of noise")
	parser.add_option("-q", "--quiet",
		action="store_false", dest="verbose",
		help="surpress output")
	parser.add_option("--log",
		action="store", dest="log",
		help="optional log filename, .log extension will be added", metavar="FILE")
	parser.add_option("--format",
		action="store", dest="format",
		help="output format [default=%default]", metavar="FRMT")
	parser.add_option("--step-through",
		action="store_true", dest="step_through",
		help="step through input files incrementally on user input [default=%default]")
		
	return parser
		
		
if __name__ == '__main__':
	parser = setUpOptionParser()
	(options, args) = parser.parse_args()
		
	if not args:
		parser.error("you must specifiy at least one input file argument")
		
	extractor = ImageExtractor(log=options.log)
	for pdsFilename, pdsContents in gfiles(files=args, mode="rb"):
		pdsFile = StringIO.StringIO(pdsContents)
		
		if options.step_through:
			sys.stderr.write("stepping through files... press enter to continue\n")
			raw_input()
			
		if options.verbose:
			errorMessage = "Reading input from '%s'\n" % (pdsFilename)
			sys.stderr.write(errorMessage)
		
		img = None
		try:
			img, labels = extractor.extract(pdsFile)
		except:
			if options.ignore_exceptions:
				if options.verbose:
					errorMessage = "Warn: Caught exception raised during extraction from '%s', ignoring\n" % (pdsFilename)
					sys.stderr.write(errorMessage)
			else:
				# If not ignoring caught exceptions, re-raise.
				raise
			
		if not img:
			errorMessage = "Error: Could not extract image from '%s': no image found\n" % (pdsFilename)
			sys.stderr.write(errorMessage)
		else:
			if options.format:
				f = StringIO.StringIO()
				img.save(f, format=options.format)
				sys.stdout.write(f.getvalue())
				f.close()
			else:
				sep = "\n"
				width, height = img.size
				imgString = img.tostring()
				# import base64
				# imgString = base64.b64encode(img.tostring())
				imgBytes = len(imgString)
				dispVars = [width, height, imgBytes, imgString]
				sys.stdout.write(sep.join(map(str, dispVars)))
			# sys.stdout.flush()
			