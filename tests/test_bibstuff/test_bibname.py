#!/usr/bin/env python

import unittest

from bibstuff import bibname
from bibstuff import bibstyles

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
		self.assertTrue(a == "Hagel" and b == "Meer")

	def test_latex_accents_chars(self):
		"LaTeX accents and non English characters"
		n=bibname.BibName(r"J\orgen M\"{a}rtin and Sven \AAs")
		self.assertTrue(n.get_names_dicts()[1]["first"][0] == "Sven")


