#!/usr/bin/env python2.6
# vim: set noexpandtab
# encoding: utf-8
"""
basic_mer_tests.py

Created by Austin Godber - 2013-01-12.
Copyright (c) 2013 Austin Godber. All rights reserved.
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
		self.testDataPath = "../test_data/MER"
		self.testImages = ["1F345867992EFFB0J3P1212L0M1.IMG",
											 "1N345854840EFFB0IEP1994L0M1.IMG",
											 "1P345688456EFFB0EJP2363L2C1.IMG"]
		self.testImagePath = self.testDataPath + "/" + self.testImages[0]

	def test_existence(self):
		assert os.path.exists(self.testImagePath)

	def test_open_pds(self):
		"""Opening a single image without an exception"""
		p = self.parser
		try:
			f = open_pds(self.testImagePath)
			p.parse(f)
		except:
			raise

	def test_get_labels(self):
		"""Parsing labels returns something other than None"""
		p = self.parser
		labels = p.parse(open_pds(self.testImagePath))
		self.assertNotEqual(None, labels)

	def test_get_image(self):
		"""Verify that the extracted image dimensions match those in the label"""
		ie = self.imageExtractor
		img, labels = ie.extract(open_pds(self.testImagePath))
		self.assertNotEqual(None, img)
		imageSize = map(int, (labels["IMAGE"]["LINE_SAMPLES"], labels["IMAGE"]["LINES"]))
		self.assertEqual(tuple(imageSize), img.size)

	def test_write_images(self):
		"""docstring for test_write_image"""
		ie = self.imageExtractor
		for image in self.testImages:
				img, labels = ie.extract(open_pds(self.testDataPath + '/' + image))
				img.save(image + '.jpg')

if __name__ == '__main__':
	unittest.main()
