#!/usr/bin/env python
# encoding: utf-8
"""
extractorbase.py

Created by Ryan Matthew Balfanz on 2009-05-28.

Copyright (c) 2009 Ryan Matthew Balfanz. All rights reserved.
"""


import unittest


class ExtractorError(Exception):
	"""Base class for exceptions raised by ``ExtractorBase`` and its subclasses."""

	def __init__(self, *args, **kwargs):
		super(ExtractorError, self).__init__(*args, **kwargs)


class ExtractorBase(object):
	"""The base class from which various extractors shall derive.
	
	Programs may define their own extractors by creating a new extractor.
	
	Any subclass should override the ``extract`` method, otherwise a NotImplementedError is raised.
	"""
	def __init__(self, *args, **kwargs):
		super(ExtractorBase, self).__init__(*args, **kwargs)
		pass
		
	def extract(self, *args, **kwargs):
		"""This method should be overwritten by a subclass."""
		raise NotImplementedError


class ExtractorTests(unittest.TestCase):
	"""Unit tests for class ExtractorBase"""
	def setUp(self):
		self.eb = ExtractorBase()
		
	def test_not_implemented(self):
		"""Method ``extract`` must be overloaded"""
		self.assertRaises(NotImplementedError, self.eb.extract)


if __name__ == '__main__':
	unittest.main()