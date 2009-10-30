.. PyPDS documentation master file, created by sphinx-quickstart on Sun Oct  4 20:08:03 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to PyPDS's documentation!
=================================

Contents:

.. toctree::
   :maxdepth: 2

   common.rst
   reader.rst
   parser.rst
   extractorbase.rst
   imageextractor.rst

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

About the Project
=================

From the Planetary Data System's `Quick-Start Introduction to PDS Archiving`_

  PDS labels are written in the Object Description Language (ODL), as are all PDS catalog files. ODL consists of a series of lines of the form "keyword = value", with certain keywords (for example,OBJECT) being used to delimit structures within the label. PDS prefers to use non-cryptic keywords, so that the data labels are more easily interpreted by users browsing through them.

This library provides a python interface to PDS files. It parses a data product's attached labels into a parse tree of dictionaries which maintain structure. It also provides convenient methods to extract image data from a data product with attached labels.

The *[pds.core.reader]* module is the lowest level software stack. It generates a tuple for all (keyword, value) pairs. This module preforms some preprocessing on the data by stripping blank lines and comments.

The *pds.core.parser* module consumes these tuples and adds information the parse tree. It is within this module that type conversion should performed, as well as any other transformation on the labels.

The *pds.imageextractor* module provides a convenient way to extract images from PDS data products. Use of this module keeps the parsing details and knowledge of the PDS specification under the hood.

References & Footnotes
======================

.. _Quick-Start Introduction to PDS Archiving: http://pds.jpl.nasa.gov/documents/qs/labels.html
