#!/usr/bin/env python
"""
Provides tests for the bibstuff.bibname module

:author: Dylan Schwilk and Alan Isaac
:contact: http://www.schwilk.org
:license: MIT (see `license.txt`_)
:date: 2021-08-06

.. _`license.txt`: ../../license.txt

"""

#standard library imports:
import unittest

from bibstuff import bibname

class TestBibname(unittest.TestCase):
	"""Tests for `bibname.py`"""

	def test_number_names_von_parts(self):
		"""Should find 2 names"""
		n = bibname.BibName("Joe von Hagel and van der Meer, Jako")
		self.assertTrue(len(n.get_names_dicts()) == 2)

	def test_parts_names_von_parts(self):
		"""Find correct parts"""
		n = bibname.BibName("Joe von Hagel and van der Meer, Jako")
		(a, b) = n.get_last_names()
		self.assertEqual(a,"Hagel")
		self.assertEqual(b, "Meer")

	def test_latex_accents_chars(self):
		"LaTeX accents and non English characters"
		n=bibname.BibName(r"J\orgen M\"{a}rtin and Sven \AAs")
		self.assertEqual(n.get_names_dicts()[1]["first"][0], "Sven")

	def test_first_middle(self):
		"first and middle name vs last"
		n=bibname.BibName("Alan Glen Isaac and Dylan Schwilk")
		self.assertEqual(n.get_names_dicts()[0]["first"][0], "Alan")
		self.assertEqual(n.get_names_dicts()[0]["first"][1], "Glen")
		self.assertEqual(n.get_names_dicts()[0]["last"][0], "Isaac")
		self.assertEqual(n.get_names_dicts()[1]["first"][0], "Dylan")
		self.assertEqual(n.get_names_dicts()[1]["last"][0], "Schwilk")
