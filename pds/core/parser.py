#!/usr/bin/env python
# encoding: utf-8
"""
parser.py

Created by Ryan Matthew Balfanz on 2009-05-27.

Copyright (c) 2009 Ryan Matthew Balfanz. All rights reserved.
"""


# In Python 2.5,
# the with statement is only allowed when the with_statement feature has been enabled.
# It will always be enabled in Python 2.6.
from __future__ import with_statement

import logging
import sys
import unittest

#from common import open_pds
from .reader import Reader


class ParserError(Exception):
	"""Base class for exceptions in this module."""

	def __init__(self, *args, **kwargs):
		super(ParserError, self).__init__(*args, **kwargs)
		
		
class DuplicateKeyError(ParserError):
	"""docstring for DuplicateKeyError"""
	def __init__(self, *args, **kwargs):
		super(DuplicateKeyError, self).__init__(*args, **kwargs)
		
		
class IOError(ParserError):
	"""Exception raised on I/O errors in this module."""

	def __init__(self, *args, **kwargs):
		super(IOError, self).__init__(*args, **kwargs)


class ParserNode(object):
	"""A tree-like node structure to maintain structure within PDS labels."""
	def __init__(self, children=None, parent=None):
		super(ParserNode, self).__init__()
		if not children:
			children = {}
			
		self.children = children
		self.parent = parent


class Parser(object):
	"""Parse PDS files into a dictionary.
	
	Instances of this module are reusable.
	
	Parsing a PDS data product results in a dictionary whose keys correspond to unchanged PDS labels --
	i.e. label['RECORD_TYPE'] is not the same as label['record_type'].
	Grouped labels are stored as nested dictionaries, nesting may be arbitrarily deep.
	Internally, these groups are called *containers* and must be in {OBJECT, GROUP}.
	
	This module makes use of assertions to find bugs and detect poorly formatted files.
	As usual, when an assertion fails an AssertionError is raised. This type of behavior may not be desired 
	or expected, since it will halt execution, especially when addressing multiple files in a production environment.
	Assertions are not checked in -O mode, use that to temporarily override this behavior.
	
	Future versions may do away with assertions altogether and utilize the logging facility.
	Logging is not very mature at this stage, but usable.
	Although this feature is not supported at this time, a future version may perform automatic type conversion
	as per the PDS specification.
	
	Simple Usage Example
	
	>>> from parser import Parser
	>>> pdsParser = Parser()
	>>> for f in ['file1.lbl', 'file2.lbl']:
	>>> 	labelDict = pdsParser.parse(open(f, 'rb'))
	"""
	def __init__(self, log=None):
		"""Initialize a reusable instance of the class."""
		super(Parser, self).__init__()
		self._reader = Reader()
		
		self.log = log
		if log:
			self._init_logging()		

	def _init_logging(self):
		"""Initialize logging."""
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
		
	def __str__(self):
		"""Print a friendly, user readable representation of an instance."""
		strItems = []
		strItems.append('PDSParser: %s' % (repr(self),))
		return '\n'.join(strItems)
			
	def parse(self, source):
		"""Parse the source PDS data."""
		# if self.log: self.log.debug("Parsing '%s'" % (source.name,))
		self._labels = self._parse_header(source)
		if self.log: self.log.debug("Parsed %d top-level labels" % (len(self._labels)))
		return self._labels

	def _parse_header(self, source):
		"""Parse the PDS header.
		
		For grouped data, supported containers belong to {'OBJECT', 'GROUP'}.
		Unidentified containers will be parsed as simple labels and will not create a child dictionary.
		"""
		if self.log: self.log.debug('Parsing header')
		CONTAINERS = {'OBJECT':'END_OBJECT', 'GROUP':'END_GROUP'}
		CONTAINERS_START = CONTAINERS.keys()
		CONTAINERS_END = CONTAINERS.values()
		
		root = ParserNode({}, None)
		currentNode = root
		expectedEndQueue = []
		for record in self._reader.read(source):
			k, v = record[0], record[1]
			assert k == k.strip() and v == v.strip(), ('Found extraneous whitespace near %s and %s') % (k, v)

			if k in CONTAINERS_START:
				expectedEndQueue.append((CONTAINERS[k], v))
				currentNode = ParserNode({}, currentNode)
				#print expectedEndQueue
			elif k in CONTAINERS_END:
				try:
					expectedEnd = expectedEndQueue.pop()
					newParent = currentNode.parent
					newParent.children[v] = currentNode.children
					currentNode = newParent
				except IndexError:
					# Verifiy that we are back at the root.
					assert currentNode.parent is None, ('Parent node is not None.')
			else:
				assert not k.startswith('END_'), ('Detected a possible uncaught nesting %s.') % (k,)
				currentNode.children[k] = v
		assert not expectedEndQueue, ('Detected hanging chads, very gory... %s') % (expectedEndQueue,)

		assert currentNode.parent is None, ('Parent is not None, did not make it back up the tree')
		return root.children


class ParserTests(unittest.TestCase):
	"""Unit tests for class Parser"""
	def setUp(self):
		pass

	def test_no_exceptions(self):
		"""Check that all test files are parsed without any Exception"""
		import os
		
		from common import open_pds

		testDataDir = '../../../test_data/'
		pdsparser = Parser(log="Parser_Unit_Tests")
		for root, dirs, files in os.walk(testDataDir):
			for name in files:
				filename = os.path.join(root, name)
				try:
					labels = pdsparser.parse(open_pds(filename))
					# labels = pdsparser.labels # Old usage, depriciated.
				except Exception as e:
					# Re-raise the exception, causing this test to fail.
					raise
				else:
					# The following is executed if and when control flows off the end of the try clause.
					assert True


if __name__ == '__main__':
	#unittest.main()
		
	from common import open_pds
	filename = '../../../test_data/FHA01118.LBL'
	pdsparser = Parser()
	labels = pdsparser.parse(open_pds(filename))
	# labels = pdsparser.labels # Old usage, depriciated.
	print(labels.keys())
	print(labels['IMAGE END'])