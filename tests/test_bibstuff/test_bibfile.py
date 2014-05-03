#!/usr/bin/env python
"""
Provides tests for the bibstuff.bibfile module

:author: Dylan Schwilk
:contact: http://www.schwilk.org
:license: MIT (see `license.txt`_)
:date: 2014-04-30

.. _`license.txt`: ../../license.txt

"""
import unittest

from bibstuff import bibfile, bibgrammar

## test data

bib1 = r"""
@string{jorr="Journal of Occasionally Reproducible Results"}
@article{vonHagel+vonHagel:2000,
  author =       {Joe von Hagel and van der Meer, Jako},
  title =        {Von test},
  year =         2010,
  journal =      jorr,
  volume =       2,
  pages =        {1--100}
}

@article{isaac.schwilk-2010,
  author =       {Isaac, Alan G. and
Dylan Schwilk},
  title =        {Using Interoperable Names},
  year =         2010,
  journal =      jorr,
  volume =       1,
  pages =        {1--100},
}

@article{schwilk_isaac_etal:2012,
  author =       {Dylan Walker Schwilk and Alan G. Isaac and Henno Martin},
  title =        {Using Dangerous Names},
  year =         2012,
  journal =      jorr,
  volume =       2,
  pages =        {1--100},
}

@article{man-2010,
  author =       {Man, Nowhere},
  title =        {Using Dangerous Syntax},
  year =         2010,
  journal =      jorr,
  volume =       3,
  pages =        {1--100},
}

@article{martin-2008-jds,
  author =       {Henno M\"artin},
  title =        "Using {\"a}ccents",
  year =         2008,
  journal =      {Journal of Desert Studies},
  volume =       1,
  pages =        {1--10}
}"""

class TestBibFile(unittest.TestCase):
	"""Tests for `bibfile.py`"""

	# setup
	bfile = bibfile.BibFile()
	bibgrammar.Parse(bib1, bfile)

	def test_simple_read(self):
		"""Check for read success on a simple .bib file"""
		self.assertEqual(len(self.bfile.entries), 5)
		self.assertEqual(self.bfile.entries[-1]['journal'], 'Journal of Desert Studies')

	def test_string_read(self):
		"""Test if @string was read correctly"""
		s = 'Journal of Occasionally Reproducible Results'
		self.assertEqual(self.bfile.entries[-2]['journal'], s)

	def test_search_bibentry(self):
		"""Check search"""
		ck = self.bfile.search_entries("Schwilk")[0]["citekey"]
		self.assertEqual(ck, "isaac.schwilk-2010")



class TestBibEntry(unittest.TestCase):
	"""Tests for BibEntry class in `bibfile.py`"""

	# setup
	bfile = bibfile.BibFile()
	bibgrammar.Parse(bib1, bfile)


	## setup for make_citekey tests
	label_style = dict(
		name_template = 'v{}_|l{}',
		max_names = 2,
		name_name_sep = '+',
		etal = 'etal',
		anonymous = 'anon',
		lower_name = False,
		article = "%(names)s-%(year)s",
		book = "%(names)s-%(year)s",
		misc = "%(names)s-%(year)s",
		default_type = "%(names)s-%(year)s",
	)
	
	def test_make_citation_key_simple(self):
		"""Make a citation key from an entry"""
		ck = self.bfile.entries[1].make_citekey(style = self.label_style)
		self.assertEqual(ck, "Isaac+Schwilk-2010")

	def test_make_citation_key_von(self):
		"""Make a citation key from an entry with von parts"""
		ck = self.bfile.entries[0].make_citekey(style= self.label_style)
		self.assertEqual(ck, "von_Hagel+vander_Meer-2010")

	def test_make_citation_three_names(self):
		"""Make a citation key from an entry with more than two names"""
		ck = self.bfile.entries[2].make_citekey(style= self.label_style)
		self.assertEqual(ck, "Schwilk+Isaac+etal-2012")

if __name__ == '__main__':
	unittest.main() 
