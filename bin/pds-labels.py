#!/usr/bin/env python
# encoding: utf-8
"""
pds-labels.py

Created by Ryan Balfanz on 2009-11-19.
Copyright (c) 2009 Ryan Balfanz. All rights reserved.
"""

import optparse
import sys

import cStringIO as StringIO

from pds.core.common import open_pds
from pds.core.parser import Parser
 
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
	parser.set_defaults(log=None)
	parser.set_defaults(pretty_print=True)
	parser.set_defaults(pprint_indent=1)
	parser.set_defaults(pprint_width=80)
	parser.set_defaults(pprint_depth=None)
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
	parser.add_option("-v", "--verbose",
		action="store_true", dest="verbose",
		help="make lots of noise")
	parser.add_option("-q", "--quiet",
		action="store_false", dest="verbose",
		help="surpress output")
	parser.add_option("--log",
		action="store", dest="log",
		help="optional log filename, the extension '.log' will automatically be added", metavar="FILE")
	parser.add_option("--step-through",
		action="store_true", dest="step_through",
		help="step through input files incrementally on user input [default=%default]")
	parser.add_option("--pretty-print",
		action="store_false", dest="pretty_print",
		help="pretty print PDS labels [default=%default]")
	parser.add_option("--pprint-indent",
		dest="pprint_indent", type="int",
		help="the amount of indentation added for each recursive level [default=%default]", metavar="INT")
	parser.add_option("--pprint-width",
		dest="pprint_width", type="int",
		help="the desired output width [default=%default]", metavar="INT")
	parser.add_option("--pprint-depth",
		dest="pprint_depth", type="int",
		help="the number of levels which may be printed  [default=%default]", metavar="INT")
		
	return parser
		
		
if __name__ == '__main__':
	optParser = setUpOptionParser()
	(options, args) = optParser.parse_args()
		
	if not args:
		# sys.stderr.write("Listening on stdin\n")
		# *** In this case gfiles() can't split files.
		# It will only generate a single result.
		# Can try to handle this in the Reader/Parser or,
		# probably the better way, is to fix gfiles() - if possible.
		optParser.error("you must specifiy at least one input file argument")
	
	pdsParser = Parser(log=options.log)
	for pdsFilename, pdsContents in gfiles(files=args, mode="U"):
		# Python issue 1286 (http://bugs.python.org/issue1286)
		# discusses the with statement context manager and its 
		# support for fileinput and *StringIO.
		# with StringIO.StringIO(pdsContents) as pdsFile:
		# with open_pds(pdsContents) as pdsFile:
		pdsFile = open_pds(StringIO.StringIO(pdsContents))
		# pdsFile = open_pds(pdsContents)
		if options.step_through:
			sys.stderr.write("stepping through files... press enter to continue\n")
			raw_input()

		if options.verbose:
			errorMessage = "Reading input from '%s'\n" % (pdsFilename)
			sys.stderr.write(errorMessage)

		labels = None
		try:
			labels = pdsParser.parse(pdsFile)
			# labels = pdsParser.parse(open_pds(pdsFile))
		except:
			if options.ignore_exceptions:
				if options.verbose:
					errorMessage = "Warn: Caught exception raised while parsing of '%s', ignoring\n" % (pdsFilename)
					sys.stderr.write(errorMessage)
			else:
				# If not ignoring caught exceptions, re-raise.
				raise
		finally:
			pdsFile.close()

		if not labels:
			errorMessage = "Error: Could not parse %s: no labels were found\n" % (options.filename)
			sys.stderr.write(errorMessage)
		else:
			if options.pretty_print:
				import pprint
				pprint.pprint(labels, indent=options.pprint_indent,
					width=options.pprint_width,
					depth=options.pprint_depth)
			else:
				print labels
