#!/usr/bin/env python
"""
Provides tests for the bibstuff.bibadd module

:author: Dylan Schwilk
:contact: http://www.schwilk.org
:license: MIT (see `license.txt`_)
:date: 2014-04-30

.. _`license.txt`: ../../license.txt

"""

import unittest

from bibstuff import bibadd
from bibstuff.bibfile import MONTH_DICT

#redfine raw_input
bibinput = ['article', "", 'M. Me and Y. You', '2014', 'My Title', 'jtrix', '2', '3', 'jan', '99--100']
def test_raw_input(arg,stuff = bibinput[:]): return stuff.pop(0)


class TestBibadd(unittest.TestCase):
	"""Tests for `bibadd.py`"""

	def test_make_entry(self):
		"""Test bibadd.py make_entry_function"""
		e = bibadd.make_entry(raw_input=test_raw_input)
		self.assertEqual(e['title'], bibinput[4])
		self.assertEqual(e['journal'], bibinput[5])
		self.assertEqual(e['volume'], bibinput[6])
		self.assertEqual(e['number'], bibinput[7])
		self.assertEqual(e['month'], MONTH_DICT[bibinput[8]])
		self.assertEqual(e['pages'], bibinput[9])


		
