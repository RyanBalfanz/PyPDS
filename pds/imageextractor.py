#!/usr/bin/env python
# encoding: utf-8
"""
imageextractor.py

Created by Ryan Matthew Balfanz on 2009-05-28.

Copyright (c) 2009 Ryan Matthew Balfanz. All rights reserved.
"""


import hashlib
import logging
import os
import sys
import unittest

import Image

from core.common import open_pds
from core.parser import Parser
from core.extractorbase import ExtractorBase, ExtractorError


class ImageExtractorError(ExtractorError):
	"""Base class for exceptions in this module."""

	def __init__(self, *args, **kwargs):
		super(ExtractorError, self).__init__(*args, **kwargs)
		
		
class ImageNotSupportedError(object):
	"""docstring for ImageNotSupportedError"""
	def __init__(self):
		super(ImageNotSupportedError, self).__init__()
		
		
class ChecksumError(ImageExtractorError):
	"""Error raised when verification of a secure hash fails."""

	def __init__(self, *args, **kwargs):
		super(ChecksumError, self).__init__(*args, **kwargs)
		
		
class ImageExtractor(ExtractorBase):
	"""Extract an image embedded within a PDS file.
	
	Returned images are instances of the Python Imaging Library Image class.
	As such, this module depends on PIL.
	
	An attached image may be extracted from by 
	determining its location within the file and identifying its size.
	Not all PDS images are supported at this time.
	
	Currently this module only supports FIXED_LENGTH as the RECORD_TYPE,
	8 as the SAMPLE_BITS and either UNSIGNED_INTEGER or MSB_UNSIGNED_INTEGER as the SAMPLE_TYPE.
	Attempts to extract an image that is not supported will result in None being returned.
	
	Simple Example Usage
	
	>>> import Image
	>>> from imageextractor import ImageExtractor
	>>> ie = ImageExtractor()
	>>> img = ie.extract('pdsFileWithAnImage.lbl')
	>>>	if img:
	>>> 	img.save('extractedImage.jpg')
	>>> else:
	>>> 	print "The image was not supported."
	"""
	
	def __init__(self, log=None, raisesChecksumError=True, raisesImageNotSupportedError=True):
		super(ImageExtractor, self).__init__()
		
		self.log = log
		self.raisesChecksumError = raisesChecksumError
		self.raisesImageNotSupportedError = raisesImageNotSupportedError
		if log:
			self._init_logging()
		# self.fh = None
		# self.imageDimensions = None
		
		# self.PILSettings = {}
		# self.PILSettings["mode"] = "L"
		# self.PILSettings["decoder"] = "raw"
		
		# self.verifySecureHash = True

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
		
	def extract(self, source):
		"""Extract an image from *source*.
		
		If the image is supported an instance of PIL's Image is returned, otherwise None.
		"""
		p = Parser()
		f = open_pds(source)
		if self.log: self.log.debug("Parsing '%s'" % (source))
		self.labels = p.parse(f)
		if self.log: self.log.debug("Found %d labels" % (len(self.labels)))
		if self._check_image_is_supported():
			if self.log: self.log.debug("Image in '%s' is supported" % (source))
			dim = self._get_image_dimensions()
			loc = self._get_image_location()
			md5Checksum = self._get_image_checksum()
			if self.log: self.log.debug("Image dimensions should be %s" % (str(dim)))
			if self.log: self.log.debug("Seeking to image data at %d" % (loc))
			f.seek(loc)
			readSize = dim[0] * dim[1]
			if self.log: self.log.debug("Seek successful, reading data (%s)" % (readSize))
			# rawImageData = f.readline()
			# f.seek(-int(self.labels["RECORD_BYTES"]), os.SEEK_CUR)
			rawImageData = f.read(readSize)
			if md5Checksum:
				rawImageChecksum = hashlib.md5(rawImageData).hexdigest()
				checksumVerificationPassed = rawImageChecksum == md5Checksum and True or False
				if not checksumVerificationPassed:
					if self.log: self.log.debug("Secure hash verification failed")
					if self.raisesChecksumError:
						errorMessage = "Verification failed! Expected '%s' but got '%s'." % (md5Checksum, rawImageChecksum)
						raise ChecksumError, errorMessage
				else:
					if self.log: self.log.debug("Secure hash verification passed")
			if self.log: self.log.debug("Read successful (len: %d), creating Image object" % (len(rawImageData)))
			# The frombuffer defaults may change in a future release;
			# for portability, change the call to read:
			# frombuffer(mode, size, data, 'raw', mode, 0, 1).
			img = Image.frombuffer('L', dim, rawImageData, 'raw', 'L', 0, 1)
			if self.log:
				self.log.debug("Image result: %s" % (str(img)))
				self.log.debug("Image info: %s" % (str(img.info)))
				self.log.debug("Image mode: %s" % (str(img.mode)))
				self.log.debug("Image size: %s" % (str(img.size)))
		else:
			if self.log: self.log.error("Image is not supported '%s'" % (source))
			img = None
		f.close()
				
		return img, self.labels
			
	def _check_image_is_supported(self):
		"""Check that the image is supported."""
		SUPPORTED = {}
		SUPPORTED['RECORD_TYPE'] = 'FIXED_LENGTH',
		SUPPORTED['SAMPLE_BITS'] = 8,
		SUPPORTED['SAMPLE_TYPE'] = 'UNSIGNED_INTEGER', 'MSB_UNSIGNED_INTEGER', 'LSB_INTEGER'
		
		imageIsSupported = True
				
		if not self.labels.has_key('IMAGE'):
			if self.log: self.log.warn("No image data found")
			imageIsSupported = False
			
		recordType = self.labels['RECORD_TYPE']
		imageSampleBits = int(self.labels['IMAGE']['SAMPLE_BITS'])
		imageSampleType = self.labels['IMAGE']['SAMPLE_TYPE']

		if recordType not in SUPPORTED['RECORD_TYPE']:
			errorMessage = ("RECORD_TYPE '%s' is not supported") % (recordType)
			if self.raisesImageNotSupportedError:
				raise ImageNotSupportedError(errorMessage)
			imageIsSupported = False
		if imageSampleBits not in SUPPORTED['SAMPLE_BITS']:
			errorMessage = ("SAMPLE_BITS '%s' is not supported") % (imageSampleBits)
			if self.raisesImageNotSupportedError:
				raise ImageNotSupportedError(errorMessage)
			imageIsSupported = False
		if imageSampleType not in SUPPORTED['SAMPLE_TYPE']:
			errorMessage = ("SAMPLE_TYPE '%s' is not supported") % (imageSampleType)
			if self.raisesImageNotSupportedError:
				raise ImageNotSupportedError(errorMessage)
			imageIsSupported = False
			
		return imageIsSupported
			
	def _get_image_dimensions(self):
		"""Return the dimensions of the image as (width, height).
		
		The image size is expected to be defined by the labels LINES_SAMPLES and LINES as width and height, respectively.
		"""
		imageWidth = int(self.labels['IMAGE']['LINE_SAMPLES'])
		imageHeight = int(self.labels['IMAGE']['LINES'])
		return imageWidth, imageHeight
			
	def _get_image_location(self):
		"""Return the seek-able position of the image.
		
		The seek byte is defined by the ^IMAGE pointer.
		It may be a single value or a value accompanied by its units.
		
		If only a single value is given the image location is given by 
		the product of the (value - 1) and RECORD_BYTES.
		
		If the units are given along with the value, they must be <BYTES>.
		The image location is given by the value.
		
		This may raise a ValueError.
		"""
		imagePointer = self.labels['^IMAGE'].split()
		if len(imagePointer) == 1:
			recordBytes = int(self.labels['RECORD_BYTES'])
			imageLocation = (int(imagePointer[0]) - 1) * recordBytes
		elif len(imagePointer) == 2:
			units = imagePointer[1]
			if not units == '<BYTES>':
				errorMessage = ("Expected <BYTES> image pointer units but found %s") % (units)
				raise ValueError, (errorMessage)
			else:
				imageLocation = int(imagePointer[0])
		else:
			errorMessage = ("^IMAGE contains extra information") % (imageSampleType)
			raise ValueError(errorMessage)
		return imageLocation
		
	def _get_image_checksum(self):
		"""Return the md5 checksum of the image.
		
		The checksum is retrieved from self.labels['IMAGE']['MD5_CHECKSUM'].
		This may raise a KeyError.
		"""
		ignoreKeyError = True
		
		md5Checksum = None
		try:
			md5Checksum = self.labels['IMAGE']["MD5_CHECKSUM"]
		except KeyError:
			if self.log: self.log.debug("Did not find md5 checksum")
			if not ignoreKeyError:
				raise
			pass
		else:
			if self.log: self.log.debug("Found md5 checksum")
			md5Checksum = md5Checksum[1:-1]
			
		return md5Checksum
		
		
class ImageExtractorTests(unittest.TestCase):
	"""Unit tests for class ImageExtractor"""
	def setUp(self):
		pass

	def test_no_exceptions(self):
		import os

		from core import open_pds

		testDataDir = '../../test_data/'
		outputDir = '../../tmp/'
		imgExtractor = ImageExtractor(log="ImageExtractor_Unit_Tests")
		for root, dirs, files in os.walk(testDataDir):
			for name in files:
				filename = os.path.join(root, name)
				print filename
				img, _ = imgExtractor.extract(open_pds(filename))
				try:
					if img:
						img.save(outputDir + name + '.jpg')
				except Exception, e:
					# Re-raise the exception, causing this test to fail.
					raise
				else:
					# The following is executed if and when control flows off the end of the try clause.
					assert True


if __name__ == '__main__':
	unittest.main()
	