#!/usr/bin/env python

import unittest

from bibstuff import bibfile, bibgrammar

## test data

bib1 = r"""
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

@article{schwilk+isaac:2010,
  author =       {Dylan Walker Schwilk and Alan G. Isaac},
  title =        {Using Dangerous Names},
  year =         2010,
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

	def test_simple_read(self):
		"""Check for read success on a simple .bib file"""
	bfile = bibfile.BibFile()
		bibgrammar.Parse(bib1, bfile)
		self.assertTrue(len(bfile.entries) == 5)

	def test_search_bibentry(self):
		"""Check search"""
	bfile = bibfile.BibFile()
		bibgrammar.Parse(bib1, bfile)
		ck = bfile.search_entries("Schwilk")[1]["citekey"]
		self.assertTrue(ck == "schwilk+isaac:2010")


if __name__ == '__main__':
	unittest.main() 
