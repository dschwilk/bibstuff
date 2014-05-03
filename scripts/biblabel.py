#! /usr/bin/env python
# File: biblabel.py
'''Script to generate automatic labels (keys) for bibtex database
entries. Default format produces citekeys like: Schwilk+Isaac:2002 and
Isaac+van_der_Stad+etal-2006. See the -h option and the BibEntry.make_citekey()
method for more information

:author: Dylan Schwilk
:contact: http://www.schwilk.org
:author: Alan G Isaac (esp. refactoring)
:contact: http://www.american.edu/cas/econ/faculty/isaac/isaac1.htm
:copyright: 2006-2014
:license: MIT (see `license.txt`_)
:date: 2014-05-02

.. _`license.txt`: ../license.txt

'''
__docformat__ = "restructuredtext en"
__authors__  =    ['Dylan Schwilk','Alan G. Isaac']
__version__ =    '2.0.0'
__needs__ = '2.6'


###################  IMPORTS  ##################################################
# import from standard library
import logging
logging.basicConfig(format='\n%(levelname)s:\n%(message)s\n')
biblabel_logger = logging.getLogger('bibstuff_logger')

# bibstuff imports
from bibstuff import bibfile, bibgrammar

################################################################################

# The citekey_label_style describes how to fomrat a BibEntry citation key
# (label) from the entry's data. The name_template is the same as that used by
# the NameFormatter class in bibstuff.bibstyles.shared.

citekey_label_style = dict(
	name_template = 'v{_}_|l{}',
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


#-- Command line version of tool
def main():
	'''Command line version of tool'''
	import sys
	import optparse
	import json

	class MyParser(optparse.OptionParser):
		def format_epilog(self, formatter):
			return self.epilog

	usage = "%prog [options] filename(s)"

	parser = MyParser(usage=usage, version ="%prog " + __version__, epilog = 
"""
More information:
The ``--style`` option takes a file name. See the file `citekey-style.json` in the
examples directory: The file must include only a valid JSON structure of the form:
{
  "name_template" : "v{_}_|l{}",
   "max_names" : "2",
   "name_name_sep" : "+",
   "etal" : "etal",
   "anonymous" : "anon",
   "lower_name" : "False",
   "article" : "%(names)s:%(year)s",
   "book" : "%(names)s:%(year)s",
   "misc" : "%(names)s:%(year)s",
   "default_type" : "%(names)s:%(year)s"
 }
""")
	
	parser.add_option("-s", "--style", action="store", type="string", \
	 				  dest="style", default = '', help="File with label format (json)")
	parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
					  help="Print INFO messages to stdout, default=%default")
	# :TODO: Add an options group stype_opts and an option for each style item
	# in the style dictionary.

	# get options	
	(options, args) = parser.parse_args()
	if options.verbose:
		biblabel_logger.setLevel(logging.INFO)

	# update label style
	if options.style:
		try :
			new_style = json.load(open(options.style))
			citekey_label_style.update(new_style)
		except IOError:
			biblabel_logger.error("Missing style file: %s" % options.style, exc_info=True)
			exit(1)
		except ValueError:
			biblabel_logger.error("Invalid style file: %s.  Style file should be JSON format dictionary" % options.style, exc_info=True)
			exit(1)

	# get database as text from .bib file(s) or stdin
	if len(args) > 0 :
		try :
		   src = ''.join(open(f).read() for f in args)
		except :
			biblabel_logger.error( 'Error in filelist')
	else :
		src = sys.stdin.read()
	 
	bfile = bibfile.BibFile()
	bibgrammar.Parse(src, bfile)
	used_citekeys = [] # stores created keys
	for entry in bfile.entries:
		label = entry.make_citekey(used_citekeys, citekey_label_style)
		entry.citekey = label
		used_citekeys.insert(0,label) # prepend to take advantage (in
									  # make_entry_citekey) of possibly sorted
									  # bfile
	for entry in bfile.entries:
		print entry

if __name__ == '__main__':
	main()
