#!/usr/bin/env python
"""
Provides tests for the bibstuff.bibstyles modules

:author: Dylan Schwilk
:contact: http://www.schwilk.org
:license: MIT (see `license.txt`_)
:date: 2014-04-30

.. _`license.txt`: ../../../license.txt

"""

import unittest

from bibstuff import bibname, bibgrammar, bibfile, bibstyles

class TestNameFormatter(unittest.TestCase):
	"""Test the single name formatter NameNormatter in shared.py"""
	
	def test_name_formatter_simple(self):
		"""Test single name formatting"""
		namedict = {"first": ["Dylan",],"last":["Schwilk",],"von":[],"jr":[]}
		name_template = 'v{~}~|l,| j,| f{. }'
		formatter = bibstyles.shared.NameFormatter(template = name_template)
		# make list of 'v_|l' last names, which can possibly have multiple
		# tokens (e.g., two piece last names)
		r = formatter.format_name(namedict)
		self.assertEqual(r, "Schwilk, Dylan")


	def test_name_formatter_multiple_von(self):
		"""Test single name formatting"""
		namedict1 = {"first": ["Jako",],"last":["Meer",],"von":["van","der"],"jr":[]}
		namedict2 = {"first": ["Heimo",],"last":["Van","Stadt"],"von":[],"jr":[]}
		name_template = 'v{_}-|l{_}'
		formatter = bibstyles.shared.NameFormatter(template = name_template)
		# make list of 'v_|l' last names, which can possibly have multiple
		# tokens (e.g., two piece last names)
		self.assertEqual(formatter.format_name(namedict1), "van_der-Meer")
		self.assertEqual(formatter.format_name(namedict2), "Van_Stadt")


class TestBibNamesFormatter(unittest.TestCase):
	"""Tests name formatting using `bibname.py` and bibstyles"""
	names_formatter_initials = bibstyles.shared.NamesFormatter(
		template_list=['f{.}. |v |l| j']*2, initials="f")
	names_formatter_no_initials = bibstyles.shared.NamesFormatter(
		template_list=['f{.}. |v |l| j']*2)	  
	names_formatter_last_first = bibstyles.shared.NamesFormatter(
		template_list=['v{~}~|l,| j,| f{. }.']*2, initials='f')	  

	def test_formatter_no_initials(self):
		"""test template"""
		n = bibname.BibName(r"J\orgen M\"{a}rtin and Sven \AAs")
		f = n.format(self.names_formatter_no_initials)
		self.assertEqual(f, 'J\\orgen. M\\"{a}rtin, and Sven. \\AAs')

	def test_formatter_initials(self):
		"""test template"""
		n = bibname.BibName(r"J\orgen M\"{a}rtin and Sven \AAs")
		f = n.format(self.names_formatter_initials)
		self.assertEqual(f, 'J. M\\"{a}rtin, and S. \\AAs')

	def test_formatter_last_first(self):
		"""test template"""
		n = bibname.BibName(r"J\orgen M\"{a}rtin and Sven von der Stadt")
		f = n.format(self.names_formatter_last_first)
		self.assertEqual(f, 'M\\"{a}rtin, J., and von~der~Stadt, S.')

class TestBibEntryFormatter(unittest.TestCase):
	"""Test BibEntry formatting"""
	default_citation_template = bibstyles.default_templates.DEFAULT_CITATION_TEMPLATE

	test_entry = r"""@article{vanWilgen:1910,
	author={van Baer Wilgen, jr , Edward Charles},
	title =		   {A vljf test},
	year =		   1910,
	journal =	   {Testing quarterly},
	volume =	   {1},
	pages =		   {21--30}
}"""

	tbib = bibfile.BibFile()
	bibgrammar.Parse(test_entry, tbib)

	def test_bibentry_formatter(self):
		"""Test the formatter"""
		test_entry = self.tbib.entries[0]
		formatter = bibstyles.shared.EntryFormatter(self.default_citation_template)
		res = formatter.format_entry(test_entry)
		correct = "van Baer Wilgen, jr, Edward Charles. (1910) A vljf test. *Testing quarterly* 1, 21--30.  "
		self.assertEqual(res, correct)

if __name__ == '__main__':
 	unittest.main()

