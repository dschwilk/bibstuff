#! /usr/bin/env python
# -*- coding: latin-1 -*-
# File: add2bib.py
'''
Add entry/entries to .bib file.
Default format produces citekeys like:
Schwilk+Isaac:2002 and Isaac+Schwilk+etal:2006.

:WARNING: works but currently *very* crude and rough!  (no special characters; macros alpha-lower only)
:author: Alan G Isaac
:contact: http://www.american.edu/cas/econ/faculty/isaac/isaac1.htm
:copyright: 2006 by Alan Isaac
:license: MIT (see `license.txt`_)
:date: 2006-08-14
:since: 2006-08-04
:change: 2006-09-24 move isbn to optional2 for books (not strictly correct, but often wanted)
:change: 2006-08-04 eliminated that final comma (believe illegal)
:change: 2006-08-24 add make_entry_citekey
:change: 2006-08-24 add label styles
:TODO: fix make_entry_citekey to use one name + 'etal'? or just '+'?
:TODO: add checking for unique key
:TODO: allow multiple entries
:TODO: allow correcting entries
:TODO: use style file for HTML formatting
:TODO: check for macros against @string defs in .bib file
:TODO: macro handling (journals)

.. _license.txt: ./license.txt
'''
__docformat__ = "restructuredtext en"
__authors__  =    ['Alan G. Isaac']
__version__ =    '0.3.1'
__needs__ = '2.4'


###################  IMPORTS  ##################################################
# import from standard library
#from string import ascii_lowercase
import os, shutil
import logging
logging.basicConfig(format='\n%(levelname)s:\n%(message)s\n')
add2bib_logger = logging.getLogger('bibstuff_logger')

# bibstuff imports
import bibfile
import bibstyles
################################################################################

entry_types = ("article","booklet","book","conference","inbook","incollection","inproceedings","manual","mastersthesis","misc","phdthesis","proceedings","techreport","unpublished")
valid_fields = dict(
)

article = dict(
required = 'ATjY',
optional1 = 'vnpm',
optional2 = 'z',
extras = 'kiu'
)
book = dict(
required = '�TPY',
optional1 = 'ae',
optional2 = 'vnsmzi',
extras = 'ku'
)
booklet = dict(
required = 'T',
optional1 = 'AhY',
optional2 = 'amz',
)
inbook = dict(
required = '�TcpPY',
optional1 = 'a',
optional2 = 'vnsuemz',
extras = 'kiu'
)
incollection = dict(
required = 'ATbPY',
optional1 = 'Ecpa',
optional2 = 'vnsuemz',
extras = 'kiu'
)
inproceedings = dict(
required = 'ATbY',
optional1 = 'EpaOP',
optional2 = 'vnsmz',
extras = 'kiu'
)
manual = dict(
required = 'T',
optional1 = 'Oa',
optional2 = 'AemYz',
)
mastersthesis = dict(
required = 'ATSY',
optional1 = 'a',
optional2 = 'umz',
)
misc = dict(
required = '',
optional1 = 'AThY',
optional2 = 'mz',
)
phdthesis = dict(
required = 'ATSY',
optional1 = 'a',
optional2 = 'umz',
)
proceedings = dict(
required = 'TY',
optional1 = 'EaO',
optional2 = 'vnsmPz',
)
techreport = dict(
required = 'ATIY',
optional1 = 'una',
optional2 = 'mz',
)
unpublished = dict(
required = 'ATz',
optional1 = 'Y',
optional2 = 'm',
)

#for testing script:
#def raw_input(arg,stuff = ['','M. Me and Y. You', '2006', 'My Title', 'jtrix', '2', '3', 'jan', '99--100']): return stuff.pop(0)


# requires author *or* editor

"""
address(a),author(A),booktitle(b),chapter(c),crossref(x),edition(e),editor(E),howpublished(h),institution(I),isbn(i),journal(j),key(k),month(m),note(z),number(n),organization(O),pages(p),publisher(P),school(S),series(s),title(T),type(t),url(u),volume(v),year(y),unused(fgl)

Will not current provide the crossref field since crossrefs must be prepended. (Just warn?)
"""

def make_entry(choosetype='',options=False,extras=False):
	"""
	:author: Alan G. Isaac
	:date: 2006-08-11
	"""
	entry = bibfile.BibEntry()
	while not choosetype in entry_types:
		choosetype=raw_input("From\n"+", ".join(entry_types)+"\nchoose type: ")
	entry.type = choosetype
	field_dict = eval(choosetype)
	#:TODO: test cite key against existing keys
	citekey = raw_input("Press return for autogenerated citekey.\nOr enter citekey (e.g., jones02aer): ")
	entry.citekey = citekey
	fields = field_dict['required'] + field_dict['optional1']
	if options or extras:
		fields = fields + field_dict['optional2']
	if extras:
		fields = fields + field_dict['extras']
	if 'A' in fields or '�' in fields:
		entry['author'] = raw_input("author(s)? ").strip()
	if 'E' in fields or '�' in fields:
		entry['editor'] = raw_input("editor(s)? ").strip()
	if 'Y' in fields:
		entry['year'] = raw_input("year? ").strip()
	if 'T' in fields:
		entry['title'] = raw_input("title? ").strip()
	if 'b' in fields:
		entry['booktitle'] = raw_input("booktitle? ").strip()
	if 'e' in fields:
		entry['edition'] = raw_input("edition? (E.g., 2nd)  ").strip()
	if 'c' in fields:
		entry['chapter'] = raw_input("chapter? ").strip()
	if 'j' in fields: #:TODO: journal key handling (all lower only?)
		entry['journal'] = raw_input("journal name? ").strip()
	if 'v' in fields:
		entry['volume'] = raw_input("volume? ").strip()
	if 'n' in fields:
		entry['number'] = raw_input("number? ").strip()
	if 'm' in fields: #:TODO: macro handling
		entry['month'] = raw_input("month? ").strip()
	if 'p' in fields:
		entry['pages'] = raw_input("pages? ").strip()
	if 'P' in fields:
		entry['publisher'] = raw_input("Publisher? ").strip()
	if 'a' in fields:
		entry['address'] = raw_input("address? ").strip()
	if 'h' in fields:
		entry['howpublished'] = raw_input("howpublished? ").strip()
	if 'I' in fields:
		entry['institution'] = raw_input("Institution? ").strip()
	if 'O' in fields:
		entry['organization'] = raw_input("Organization? ").strip()
	if 'S' in fields:
		entry['school'] = raw_input("School? ").strip()
	if 's' in fields:
		entry['series'] = raw_input("series? ").strip()
	if 't' in fields:
		entry['type'] = raw_input("type? (E.g., Working Paper) ").strip()
	if 'i' in fields:
		entry['isbn'] = raw_input("isbn? ").strip()
	if 'u' in fields:
		entry['url'] = raw_input("url? ").strip()
	if 'k' in fields:
		entry['key'] = raw_input("key (*not* citekey)? ").strip()
	if not citekey:
		citekey = make_entry_citekey(entry,[],label_style2)
		entry.citekey = citekey
	return entry


# for a discussion of name templates, see the NameFormatter docstring
# a style must always define a default entry_type
# use_max_names True -> first max_names names included, then etal
# use_max_names False -> first name included, then etal
label_style1 = dict(
name_template = 'v_|l{_}',
max_names = 2,
use_max_names = True,
name_name_sep = ('+','+'),
etal = 'etal',
anonymous = 'anon',
lower_name = False,
article = "%(names)s:%(year)s",
book = "%(names)s:%(year)s",
misc = "%(names)s:%(year)s",
default_type = "%(names)s:%(year)s",
)

#style2 shd be rst compatible
label_style2 = dict(
name_first = 'l{_}',
name_other = 'l{_}',
max_names = 2,
use_max_names = False,
name_name_sep = ('.','.'),
etal = '',
lower_name = True,
anonymous = 'anon',
article = "%(names)s-%(year)s-%(jrnl)s",
book = "%(names)s-%(year)s",
misc = "%(names)s-%(year)s",
default_type = "%(names)s-%(year)s",
)

#:note: this is a variant of a function in biblabel.py
#:TODO: make this a BibEntry method
#:TODO: integrate styles with CITATION_TEMPLATE styles (note: anon, lower_name, templates (names))
def make_entry_citekey(entry, used_citekeys,style=label_style1):
	"""return new entry key (as string)
	"""

	format_dict = {}
	entry_type = entry.type.lower()
	try:
		label_template = style[entry_type]
	except KeyError:
		label_template = style['default_type']

	name_template = style['name_first']  #:TODO: ? adjust this ?
	max_names = style['max_names']
	name_name_sep = style['name_name_sep'][0] #:TODO: ? adjust this ?
	#name_parts_sep = style['name_parts_sep'] #superfluous if name templates used correctly; just in case ...
	lower_name = style['lower_name']
	etal = style['etal']

	#first, make names
	name_formatter = bibstyles.shared.NameFormatter(template = name_template)
	names_dicts = entry.get_names().get_names_dicts()
	#make list of 'v_|l' last names, which can possibly have multiple tokens (e.g., two piece last names)
	ls = [name_formatter.format_name(name_dict) for name_dict in names_dicts]
	if len(ls) > max_names:
		if use_max_names:
			ls = ls[:max_names] + [etal]
		else:
			ls = ls[0] + [etal]
	#for each name, join the tokens with an underscore (i.e., split on whitespace and then join with '_').
	#ls = [name_parts_sep.join( s.split() )  for s in ls]  #shd handle this with name template
	names =  name_name_sep.join(ls)
	if lower_name:
		names = names.lower()
	format_dict['names'] = names
	year = entry['year'] or '????'
	format_dict['year'] = year
	if entry_type == "article":
		jrnl = entry['journal']
		jrnl = ''.join(jrnl.split()).lower()  #keep macro; ow abbreviate (TODO: adjust this)
		jrnl = jrnl.replace("journal","j",1)
		format_dict['jrnl'] = jrnl  #short form, no spaces

	#make unique result: if needed, append suffix (sfx) b or c or d . . . to year
	sfx = ''; c = 1
	#while result+sfx in used_citekeys:
	while label_template%format_dict in used_citekeys:
		sfx = ascii_lowercase[c%26]*(1+c//26)  #:note: lowercase since BibTeX does not distinguish case
		format_dict['year'] = year+sfx
		c += 1
	result = label_template%format_dict

	return result

###########  HTML formatting  ########################
html_templates = dict(
journal = '''<p id='%(citekey)s' class='ref'>
<span class='author'>%(author)s</span>,
<span class='date'>%(year)s</span>,
&ldquo;<span class='title'>%(title)s</span>,&rdquo;
%(pubinfo)s.
</p>
''',
book = '''<p id='%(citekey)s class='ref'>
<span class='author'>%(auted)s</span>,
<span class='date'>%(year)s</span>,
%(titleinfo)s
%(pubinfo)s.
</p>
''',
)
text_templates = dict(
journal = '''%(author)s, %(year)s,
"%(title)s"
%(pubinfo)s.
''',
book = '''%(auted)s, %(year)s,
%(titleinfo)s
%(pubinfo)s.
''',
incollection = '''%(author)s, %(year)s,
%(titleinfo)s
%(pubinfo)s.
''',
)

#:TODO: !!!!
def is_macro(s):
	return False

def text_format(entry):
	entry_type = entry.type.lower()
	info = {}.update(entry)
	add2bib_logger.info("entry_type = "%(entry_type))
	if entry_type == "article":
		info['journal'] = get_journal(entry)
		volnum = get_volnum(entry)
		if pages:
			pubinfo += pages
		result = text_templates['journal']%info
	elif entry_type in ["incollection","book"]:
		if entry_type == "book":
			if not author and entry['editor']:
				author = entry['editor'] + " (ed)"
			info['title'] = "%s,"%(title)
		else: #-> entry_type == "incollection":
			if entry['editor']:
				info['auted'] = "%(author)s, in %(editor)s (ed)"%(entry)
				info['title']="%(title)s, in %(booktitle)s,"%(entry)
		info['pubinfo']="(%(address)s: %(publisher)s)\nisbn: %(isbn)s"%(entry)
		#result = html_templates[entry_type]%dict(citekey=entry.citekey,auted=auted,year=year,titleinfo=titleinfo,pubinfo=pubinfo)
		result = html_templates[entry_type]%info
	return result
		
def get_journal(entry,jrnl_lst=None): #TODO: extract fr journal list
	#if jrnlkey =~ "{.\+}", let journal=substitute(jrnlkey,'[{}]','','g')
	if entry.type == "article":
		if is_macro(entry['journal']):
			journal = raw_input("Journal? (no braces) (Press enter to use '%s') "%(entry['journal']))
			if journal:
				info['journal'] = journal
	return journal

def get_volnum(entry):
	if volume:
		volnum = str(volume)
		if number:
			volnum = str(volume) + "(" + str(number) + ")"
	elif number:
		volnume = str(number)
	else:
		volnum = ""
	return volnum

def get_pages(entry,dash='--',pagespref=('p. ','pp. ')):
	pages = entry['pages']
	if pages:
		if '--' in pages:
			pages = pagespref[1] + dash.join(pages.split("--"))
		elif '-' in pages:
			pages = pagespref[1] + dash.join("-".split(pages))
		else:
			pages = pagespref[0] + pages
	return pages

def html_format(entry):
	entry_type = entry.type.lower()
	info = {}.update(entry)
	add2bib_logger.info("entry_type = "%(entry_type))
	if entry_type == "article":
		info['journal'] = get_journal(entry['journal'])
		pubinfo="<span class='journal'>" + journal + "</span>"
		volume = entry['volume']
		number = entry['number']
		volnum = get_volnum(entry)
		if volnum:
			pubinfo += " " + volnum
		pages = get_pages(entry,'&ndash;')
		if pages:
			pubinfo += pages
		#result = html_templates['journal']%dict(citekey=citekey,author=author,year=year,title=title,pubinfo=pubinfo)
		info['pubinfo'] = pubinfo
		result = html_templates[entry_type]%info
	elif entry_type in ["incollection","book"]:
		if entry_type == "book":
			if not author and entry['editor']:
				author = entry['editor'] + " (ed)"
			title = "<span class='booktitle'>%s</span>,"%(title)
		else: #-> entry_type == "incollection":
			if entry['editor']:
				info['auted'] = "%(author)s, in %(editor)s (ed)"%(entry)
				info['title']="<em>%(title)s</em>, in <span class='booktitle'>%(booktitle)s</span>,"%(entry)
		info['pubinfo']="(%(address)s: %(publisher)s)\nisbn: %(isbn)s"%(entry)
		#result = html_templates[entry_type]%dict(citekey=entry.citekey,auted=auted,year=year,titleinfo=titleinfo,pubinfo=pubinfo)
		result = html_templates[entry_type]%info
	return result

		  

#-- Command line version of tool
def main():
	"""Command-line tool.
	See bibsearch.py -h for help.
	"""

	import sys
	import bibgrammar

	input = sys.stdin
	output = sys.stdout
	
	from optparse import OptionParser
	
	usage = """
	%prog [options]
	example: %prog -mt article -bo BIB_DATABASE
	"""


	parser = OptionParser(usage=usage, version ="%prog " + __version__)
	parser.add_option("-f", "--format", action="store",
	                  dest="format", default='b',
					  help="set format(s) of output\nb: BibTeX\nh: HTML\nt: text", metavar="FORMAT")
	parser.add_option("-m", "--more_fields", action="store_true",
					  dest="more_fields", default = False, help="input less common fields")
	parser.add_option("-M", "--MORE_FIELDS", action="store_true",
					  dest="MORE_FIELDS", default = False, help="input all relevant fields")
	parser.add_option("-v", "--verbose", action="store_true",
	                  dest="verbose", default=False,
					  help="Print INFO messages to stdout, default=%default")
	parser.add_option("-V", "--very_verbose", action="store_true",
	                  dest="very_verbose", default=False,
					  help="Print DEBUG messages to stdout, default=%default")
	parser.add_option("-t", "--type", action="store",
	                  dest="entry_type", default='',
					  help="set type of entry", metavar="TYPE")
	parser.add_option("-o", "--outfile", action="store", type="string", dest="outfile",
					  help="Write formatted references to FILE", metavar="FILE")
	parser.add_option("-n", "--nuke", action="store_true", dest="overwrite", default=False,
					  help="CAUTION! silently overwrite outfile, default=%default")
	parser.add_option("-b", "--backup", action="store_true", dest="backup", default=False,
					  help="backup FILE to FILE.bak, default=%default")

	"""
	#TODO:
	example usage: %prog -no new_bibfile BIB_DATABASE
	parser.add_option("-m", "--maxnames", action="store", type="int",
					  dest="maxnames",  default = 2, help="Max names to add to key")
	parser.add_option("-e", "--etal", action="store", type="string", \
					  dest="etal",  default = 'etal',help="What to add after max names")
	parser.add_option("-i", "--infile", action="store", type="string", dest="infile",
					  help="Parse FILE for citation references.", metavar="FILE")
	parser.add_option("-s", "--stylefile", action="store", dest="stylefile", default="default.py",
					  help="Specify user-chosen style file",metavar="FILE")
	"""

	# get options
	(options, args) = parser.parse_args()
	if options.verbose:
		add2bib_logger.setLevel(logging.INFO)
	if options.very_verbose:
		add2bib_logger.setLevel(logging.DEBUG)
	add2bib_logger.info("Script running.\nargs=%s"%(args))

	'''
	# get database as text from .bib file(s) or stdin
	if len(args) > 0 :
		try :
		   src = ''.join(open(f).read() for f in args)
		except:
			print 'Error in filelist'
	else :
		src = sys.stdin.read()

	 
	bibfile_name = args[-1]
	if (os.path.splitext(bibfile_name)[-1]).lower() != ".bib":
		bib4txt_logger.warning(bibfile_name + " does not appear to be a .bib file")
	try :
		bibfile_as_string = open(bibfile_name,'r').read()
	except :
		print "Database file not found."
		sys.exit(1)

	# read input file (default: stdin)
	if options.infile:
		try:
			input = open(options.infile,'r')
		except:
			print "Cannot open: "+options.infile
			sys.exit(1)

	# create object to store parsed .bib file
	bibfile_processor = bibfile.BibFile()
	#store parsed .bib file in the bibfile_processor
	#  TODO: allow multiple .bib files
	bibgrammar.Parse(bibfile_as_string, bibfile_processor)

	bfile = bibfile.BibFile()
	bibgrammar.Parse(src, bfile)
	used_citekeys = [] # stores created keys
	'''
	# open output file for writing (default: stdout)
	if options.outfile:
		if options.backup and os.path.exists(options.outfile):
			shutil.copyfile(options.outfile,options.outfile+".bak")
		if options.overwrite or not os.path.exists(options.outfile):
			output = open(options.outfile,'w')
		else:
			add2bib_logger.info("Appending to %s.\n(Use -n option to nuke (overwrite) the old output file.)"
			                     %options.outfile)
			output = open(options.outfile,'a')

	entry = make_entry(options.entry_type,options.more_fields,options.MORE_FIELDS)
	output.write(str(entry))
	print entry
	if 'h' in options.format:
		output.write( html_format(entry) )
	if 't' in options.format:
		output.write( text_format(entry) )

if __name__ == '__main__':
	main()

