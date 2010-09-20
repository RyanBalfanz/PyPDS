=====
PyPDS
=====

- Overview_
- Installation_
- Examples_
- CommandLineTools_

This python package is suitable for working with Planetary Data System (PDS) data products in your own projects.

Several command line tools are also available for viewing labels and image contents as well as image conversion.

.. _Overview:

Overview
========

PyPDS is a python interface to `Planetary Data System <http://pds.jpl.nasa.gov/>`_ (PDS) data products.
For more information please visit the `PyPDS Wiki <http://wiki.github.com/RyanBalfanz/PyPDS/>`_ and the Sphinx documentation included in the source.

.. _Installation:

Installation
============


An easy way to get started using PyPDS is to clone its GitHub repository. The repository includes a directory containing some example PDS files to work with.

The following will place a directory called PyPDS in your working directory.

	git clone git://github.com/RyanBalfanz/PyPDS.git
	
For instant gratification, change to the PyPDS/ directory and fire up a Python interpreter.

	cd PyPDS/
	python
	
From there you should be able to start playing with PyPDS and the some test files (several are available in Downloads).
	
Or, if you'd like to install PyPDS system wide, first grab a copy of the code as above. Then install with distutils. PyPDS is on PyPI (http://pypi.python.org/pypi/PyPDS) but not yet easy_install/pip installable.

	python setup.py install

.. _Examples:

Examples
========

First, you may want to run tests.py to verify that things seem to be working. That files was based on the interacitve examples below. There are more examples in the documentation.

Working with labels
-------------------

Before we may do anything, let's import some modules.

>>> import pprint
>>> from pds.core.common import open_pds
>>> from pds.core.parser import Parser

If we are to get all the labels from a PDS file, we'll need a Parser object.

>>> parser = Parser()

Now we use use it's ``parse`` method on a file. The file should first be opened with ``open_pds``.

>>> labels = parser.parse(open_pds("../test_data/pds.img"))

The return object is just a dictionary. Let's take a look.

>>> pprint.pprint(labels.keys()) # Inspect the top-level labels.
['IMAGE_HISTOGRAM',
 'IMAGE_MAP_PROJECTION_CATALOG',
 'FILE_RECORDS',
 'IMAGE_ID',
 'TARGET_NAME',
 'SOURCE_IMAGE_ID',
 'IMAGE',
 'LABEL_RECORDS',
 'SPACECRAFT_NAME',
 'NOTE',
 'RECORD_TYPE',
 'CCSD3ZF0000100000001NJPL3IF0PDS200000001',
 '^IMAGE',
 'INSTRUMENT_NAME',
 '^IMAGE_HISTOGRAM',
 'DATA_SET_ID',
 'RECORD_BYTES']

Some of the labels contain other labels, which are also dictionary objects.

>>> pprint.pprint(labels["IMAGE"]) # Inspect the image labels.
{'CHECKSUM': '12054227',
 'LINES': '320',
 'LINE_SAMPLES': '306',
 'SAMPLE_BITS': '8',
 'SAMPLE_BIT_MASK': '2#11111111#',
 'SAMPLE_TYPE': 'UNSIGNED_INTEGER'}

Working with the image
----------------------

PyPDS also takes care of the details about creating image objects. Behind the scenes all images are instances of PIL's Image class.

To get an image from a PDS file, create an ``ImageExtractor`` object and use its ``extract`` method. Don't forget to first open the PDS file.

>>> from pds.core.common import open_pds
>>> from pds.imageextractor import ImageExtractor
>>> ie = ImageExtractor()
>>> img, labels = ie.extract(open_pds("../test_data/pds.img"))

The ``extract`` method first parses the file, then creates the image. Since it goes to the trouble of doing so anyway, it provides the label as a freebie, along with the image.

Here, ``img`` is an instance of PIL's Image class. Do whatever you want to it.

>>> print (img.mode, img.size)
('L', (306, 320))
>>> img.show() # Open the image in the default viewer.
>>> img.save("pds.img.jpeg") # Write the image to disk in JPEG format.

Verify that the returned image has the proper dimensions.

>>> imageSize = map(int, \
... (labels["IMAGE"]["LINE_SAMPLES"], \
... labels["IMAGE"]["LINES"])) # Save the image dimensions with integers.
>>> tuple(imageSize) == img.size # The built-in map returns a list, but Image.size is a tuple.
True

By the way, an ``Image`` has a ``show`` method which should happily open the image in your default viewer.

.. _CommandLineTools:

Command Line Tools
==================

Sometimes you might not want to interact with PDS files programmatically. PyPDS also comes with several tools which are handy for working with PDS files at the command line.

Each has several options. For detailed information use ``--help``.

pds-convert.py
	Convert images to the specified format. 
	
pds-image.py
	Like pds-convert.py but dump to standard output.
	
pds-labels.py	
	Dump the labels to standard output.
	
pds-view.py
	View an image contained in a PDS file in the default viewer.
	