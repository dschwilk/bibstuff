#!/usr/bin/env python

import unittest

from bibstuff import bibname, bibstyles

default_citation_template = bibstyles.default_templates.DEFAULT_CITATION_TEMPLATE

class TestBibnameFormatter(unittest.TestCase):
    """Tests name formatting using `bibname.py` and bibstyles"""
    names_formatter_initials = bibstyles.shared.NamesFormatter(
        template_list=['f{.}. |v |l| jr']*2, initials="f")
    names_formatter_no_initials = bibstyles.shared.NamesFormatter(
        template_list=['f{.}. |v |l| jr']*2)      

    def test_formatter_no_initials(self):
        """test template"""
        n = bibname.BibName(r"J\orgen M\"{a}rtin and Sven \AAs")
        f = n.format(self.names_formatter_no_initials)
        self.assertTrue(f=='J\\orgen. M\\"{a}rtin, and Sven. \\AAs')

    def test_formatter_no_initials(self):
        """test template"""
        n = bibname.BibName(r"J\orgen M\"{a}rtin and Sven \AAs")
        f = n.format(self.names_formatter_initials)
        self.assertEqual(f, 'J. M\\"{a}rtin, and S. \\AAs')


# class TestEntryFormatter(unittest.TestCase):
#     from bibstuff import bibfile
#     from bibstuff import bibgrammar

#     test_entry = r"""@article{vanWilgen:1910,
#   author={van Baer Wilgen, jr , Edward Charles},
#   title =        {A vljf test},
#   year =         1910,
#   journal =      {Testing quarterly},
#   volume =       {1},
#   pages =        {21--30}
# }"""
    
#     test_bib = bibfile.BibFile()
#     bibgrammar.Parse(test_entry, bfile)

#     def test_bibentry_formatter(self):
#         test_entry = test_bib.entries[0]
        
if __name__ == '__main__':
    unittest.main() 

