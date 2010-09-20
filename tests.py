#!/usr/bin/env python2.6
# encoding: utf-8
"""
tests.py

Created by Balfanz, Ryan on 2010-09-19.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""

import os
import unittest

from pds.core.common import open_pds
from pds.core.parser import Parser
from pds.imageextractor import ImageExtractor


class untitledTests(unittest.TestCase):
	def setUp(self):
		self.parser = Parser()
		self.imageExtractor = ImageExtractor()
		self.testImagePath = "./I18584006BTR.IMG"
		assert os.path.exists(self.testImagePath)
		
	def test_open_pds(self):
		"""docstring for test_open_pds_file"""
		p = self.parser
		try:
			f = open_pds(self.testImagePath)
			p.parse(f)
		except:
			raise
			
	def test_get_labels(self):
		"""docstring for test_get_labels"""
		p = self.parser
		labels = p.parse(open_pds(self.testImagePath))
		self.assertNotEqual(None, labels)
		
	def test_get_image(self):
		"""docstring for test_get_image"""
		ie = self.imageExtractor
		img, labels = ie.extract(open_pds(self.testImagePath))
		self.assertNotEqual(None, img)
		imageSize = map(int, (labels["IMAGE"]["LINE_SAMPLES"], labels["IMAGE"]["LINES"]))
		self.assertEqual(tuple(imageSize), img.size)
		
		
if __name__ == '__main__':
	unittest.main()
