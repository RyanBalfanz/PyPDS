#!/usr/bin/env python
# encoding: utf-8
"""
reader.py

Created by Ryan Matthew Balfanz on 2009-05-20.

Copyright (c) 2009 Ryan Matthew Balfanz. All rights reserved.
"""


# In Python 2.5,
# the with statement is only allowed
# when the with_statement feature has been enabled.
# It will always be enabled in Python 2.6.
from __future__ import with_statement

import logging
import re
import sys
import unittest

#from common import open_pds


class Reader(object):
	"""Read a PDS formatted file into meaningful (*key*, *value*) pairs.
	
	Instances of this class are reusable; multiple files may by read consecutively.
	
	A key is denoted by a token immediately before a '=' character 
	and a value by joining of all tokens preceding the next key.
	While reading the file, extraneous whitespace as well as comments are discarded.
	More importantly, records spanning more than one physical line are flattened.
	
	Currently, there are several assertions in place to try and find bugs and poorly formatted files.
	As usual, when an assertion fails an AssertionError is raised. This type of behavior may not be desired 
	or expected, since it will halt execution, especially when addressing multiple files in a production environment.
	
	Future versions may do away with assertions altogether and utilize the logging facility.
	Logging is not very mature at this stage, but usable.
	In might be convenient to also return metadata about each (key, value) pair 
	such as the linenumber(s) associated with it. This would make mean not discarding whitespace and comments.

	Notes: See http://personalpages.tds.net/~kent37/kk/00004.html. Maybe?
	
	Simple Usage Example
	
	>>> from reader import Reader
	>>> # Notice that the Reader instance is reused to process multiple files
	>>> pdsreader = Reader()
	>>> for f in ['pds1.lbl', 'pds2.lbl']:
	>>> 	# Loop over all records and process each in turn
	>>> 	for record in pdsreader.read(open(f, 'rb')):
	>>> 		process(record)
	
	>>> # Using a list comprehension to consume and store all records
	>>> records = [record for record in pdsreader.read(open('pdsFile.lbl', 'rb')]
	>>> process(records)
	"""

	def __init__(self, log=None):
		super(Reader, self).__init__()
		
		self.log = log
		if log:
			self._init_logging()		
		
	def _init_logging(self):
		"""docstring for init_logging"""
		# Set the message format.
		format = logging.Formatter("%(levelname)s:%(name)s:%(asctime)s:%(message)s")

		# Create the message handler.
		stderr_hand = logging.StreamHandler(sys.stderr)
		stderr_hand.setLevel(logging.DEBUG)
		stderr_hand.setFormatter(format)

		# Create a handler for routing to a file.
		logfile_hand = logging.FileHandler(self.log + '.log')
		logfile_hand.setLevel(logging.DEBUG)
		logfile_hand.setFormatter(format)

		# Create a top-level logger.
		self.log = logging.getLogger(self.log)
		self.log.setLevel(logging.DEBUG)
		self.log.addHandler(logfile_hand)
		self.log.addHandler(stderr_hand)

		self.log.debug('Initializing logger')

	#def __iter__(self):
	#	"""This is an iterator."""
	#	return self

	def next(self, source):
		"""Return the next record.
		
		This method is a generator i.e. it yields values and preserves state.
		Keep in mind that this method reads the entire file contents at once the first time it is called.
		Additionally, after the file has been read, all comments and blank lines are stripped.
		This preprocessing occurs before any result is returned.
		After the first yield, subsequent calls may be markedly faster due to its generator nature.
		"""
		if self.log: self.log.debug("Reading '%s'" % (source.name))
		# File Preprocessing
		# ==================
		# Read file contents to a string.
		# Break into lines by splitting on PDS-style newlines.
		# Then split stripped lines on spaces.
		#splitLines = [x.strip().split(' ') for x in source.read().split('\r\n')]
		#for i, line in enumerate(splitLines):
		#	if '/*' not in line:
		#		errorMessage = "Multi-line comments are not supported.\nAlso, check for spaces around '/*' and '*/'."
		#		assert '*/' not in line, errorMessage
		#		[tokens.append(t) for t in line if t]
		#	else:
		#		errorMessage = 'Comment appears invalid.'
		#		assert (line[0][0:2] == '/*') and (line[-1][len(line[-1])-2:] == '*/'), errorMessage
		#	if 'END' in line:
		#		errorMessage = "Found garbage near 'END' token."
		#		assert len(line) == 1, errorMessage
		#		break
		
		# Explicitly create an iterator with a sentinal for more control
		# Using an iterator produces a bug which causes execution to hang when reading files with "\n" style newlines
		# Scratch that, it looks like the bug appeared while reading a .DS_Store file -- i.e. breaks if sentinal DNE.
		#if source.mode in ("U", "rU"):
		#	it = iter(source.readline, "END\n")
		#elif source.mode in ("r", "rb"):
		#	it = iter(source.readline, "END\r\n")
		#else:
		#	if self.log: self.log.error("Unrecognized file mode '%s'" % source.mode)
		commentStart = re.compile(r"/\*")
		commentEnd = re.compile(r"\*/")

		if self.log: self.log.debug('Tonekization')
		tokens = []
		for i, line in enumerate(source):
			#decode if this is a bytes-like object
			try:
				line = line.decode('utf-8')
			except(UnicodeDecodeError, AttributeError):
				pass

		#for i, line in enumerate(it):
			line = line.strip()
			print(line)
			if not line:
				continue

			elif commentStart.match(line):
				if not commentEnd.search(line):
					if self.log: self.log.warn("Detected possible multiline comment near line %d" % i)
			elif line == r"END":
				# We only really need this check if not using a sentinal.
				# But its not going to hurt anyone being around anyway.
				break
			else:
				[tokens.append(token) for token in line.split() if token]
			
		# Locate each record by indentifying the index of each record denoting token.
		magicRecordFindingToken = '='
		recordIndicies = [i for i, t in enumerate(tokens) if t == magicRecordFindingToken]
		#recordIndicies = (i for i, t in enumerate(tokens) if t == magicRecordFindingToken)
		if self.log: self.log.info('Found %d possible key, value pairs' % (len(recordIndicies)))

		# Assemble each record from its key and value pair.
		for i, recIndx in enumerate(recordIndicies):
			keyIndex = recIndx - 1
			dataStartIndex = recIndx + 1
			try:
				dataEndIndex = recordIndicies[i + 1] - 1
			except IndexError as  e:
				errorMessage = 'i: %d, Number of tokens: %d' % (i, len(tokens))
				assert i == (len(recordIndicies) - 1), errorMessage
				dataEndIndex = len(tokens) - 1
			finally:
				if dataStartIndex == dataEndIndex:
					yield tokens[keyIndex], ' '.join(tokens[dataStartIndex:])
				yield tokens[keyIndex], ' '.join(tokens[dataStartIndex:dataEndIndex])
		#yield None
		#raise StopIteration

	#@property
	#def reader(self):
	#	"""Provide property-like access to next()."""
	#	return self.next()
		
	def read(self, source):
		"""A convenience function to initiate iteration via a next() call."""
		return self.next(source)


class ReaderTests(unittest.TestCase):
	"""Unit tests for class Reader"""
	def setUp(self):
		pass

	def test_no_exceptions(self):
		"""Check that all test files are read without any Exception"""
		import os
		
		from common import open_pds
		
		testDataDir = '../../../test_data/'
		pdsreader = Reader(log="Reader_Unit_Tests")
		for root, dirs, files in os.walk(testDataDir):
			for name in files:
				filename = os.path.join(root, name)
				try:
					for record in pdsreader.read(open_pds(filename)):
						#print record
						pass
				except Exception as e:
					# Re-raise the exception, causing this test to fail.
					raise
				else:
					# The following is executed if and when control flows off the end of the try clause.
					assert True


if __name__ == '__main__':
	unittest.main()
	