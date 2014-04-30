#! /usr/bin/env python
# File: biblabel.py
'''
Simple script to generate automatic labels (keys)
for bibtex database entries.
Default format produces citekeys like:
Schwilk+Isaac:2002 and Isaac+Schwilk+etal:2006.

:author: Dylan Schwilk
:contact: http://www.schwilk.org
:author: Alan G Isaac (esp. refactoring)
:contact: http://www.american.edu/cas/econ/faculty/isaac/isaac1.htm
:copyright: 2006 by Dylan Schwilk
:license: MIT (see `license.txt`_)
:date: $Date: 2006/08/29 15:48:05 $

.. _`license.txt`: ../license.txt
'''
__docformat__ = "restructuredtext en"
__authors__  =    ['Dylan Schwilk','Alan G. Isaac']
__version__ =    '1.9.1'
__needs__ = '2.4'


###################  IMPORTS  ##################################################
# import from standard library
from string import ascii_lowercase
import logging
logging.basicConfig(format='\n%(levelname)s:\n%(message)s\n')
biblabel_logger = logging.getLogger('bibstuff_logger')

# bibstuff imports
from bibstuff import bibfile, bibstyles

################################################################################


citekey_label_style1 = dict(
	name_template = 'v{_}_|l{}',
	max_names = 2,
	name_name_sep = '+',
	etal = 'etal',
	anonymous = 'anon',
	lower_name = False,
	article = "%(names)s:%(year)s",
	book = "%(names)s:%(year)s",
	misc = "%(names)s:%(year)s",
	default_type = "%(names)s:%(year)s",
)


#-- Command line version of tool
def main():
	'''Command line version of tool'''
	import sys
	from optparse import OptionParser
	from bibstuff import bibgrammar
	
	usage = "%prog [options] filename(s)"

	parser = OptionParser(usage=usage, version ="%prog " + __version__)
	# :TODO: Add option to read label style from file
	# parser.add_option("-s", "--style", action="store", type="string", \
	# 				  dest="style", default = '', help="File with label format (json)")
	parser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False,
					  help="Print INFO messages to stdout, default=%default")

	# get options
	(options, args) = parser.parse_args()
	if options.verbose:
		biblabel_logger.setLevel(logging.INFO)

	# get database as text from .bib file(s) or stdin
	if len(args) > 0 :
		try :
		   src = ''.join(open(f).read() for f in args)
		except:
			print 'Error in filelist'
	else :
		src = sys.stdin.read()
	 
	bfile = bibfile.BibFile()
	bibgrammar.Parse(src, bfile)
	used_citekeys = [] # stores created keys
	for entry in bfile.entries:
		label = entry.make_citekey(used_citekeys, citekey_label_style1)
		entry.citekey = label
		used_citekeys.insert(0,label) # prepend to take advantage (in
									  # make_entry_citekey) of possibly sorted
									  # bfile
	for entry in bfile.entries:
		print entry

if __name__ == '__main__':
	main()
