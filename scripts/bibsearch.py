#! /usr/bin/env python
# File: bibsearch.py
"""
Utility for extracting references from bibtex database file.
Extract formatted reference, citekey, or entry from a bibtex file.
Search by key or by regular expression.

bibsearchy.py -h gives usage options.

The script allows style based formatting.  The default style
produces a reference for pasting into a plain text file.

Example::

    python bibsearch.py my_database.bib Smith:1998
       -> produces a formated reference if citekey Smith:1998 is found
    
    cat ref_list.txt | python bibsearch.py -l my_database.bib
        -> produces a bibtex-format file of all references in list.


:author: Dylan Schwilk
:contact: http://www.schwilk.org
:author: Alan G Isaac
:contact: http://www.american.edu/cas/econ/faculty/isaac/isaac1.htm
:license: MIT (see `license.txt`_)
:date: 2006-08-19
:see: reflist.py (useful in conjuction with bibsearch.py)
:TODO: add additional search capabilities
:TODO: add HTML output option
:TODO: add output options (e.g., to file)

.. _`license.txt`: ./license.txt
"""
__docformat__ = "restructuredtext en"
__authors__  =    ["Dylan W. Schwilk", "Alan G. Isaac"]
__version__ = "1.8.3"
__needs__ = '2.7+'


###################  IMPORTS  ##################################################
#imports from standard library
import importlib, string, sys, os
import logging
logging.basicConfig(format='\n%(levelname)s:\n%(message)s\n')
bibsearch_logger = logging.getLogger('bibstuff_logger')

#local imports
try:
	from bibstuff import bibfile, bibgrammar, bibstyles, ebnf_sp
except ImportError: #allow user to run without installing
	scriptdir = os.path.dirname(os.path.realpath(__file__))
	bibdir = os.path.dirname(scriptdir)
	sys.path.append(bibdir)
	from bibstuff import bibfile, bibgrammar, bibstyles, ebnf_sp
################################################################################

 
def main():
    """Command-line tool.
    See bibsearch.py -h for help.
    """
    #set default input and output
    _infile = sys.stdin
    _outfile = sys.stdout
    
    from argparse import ArgumentParser
    _usage = "usage: %(prog)s [options] BIBTEX_FILE [search strings]"
    #from optparse import OptionParser
    #parser = OptionParser(usage=usage, version ="%prog " + __version__)
    
    parser = ArgumentParser(usage=_usage)
    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument("-k", "--key", action="store_true", dest="citekey_output", 
                      default=False, help="Output citekey rather than reference")
    parser.add_argument("-l", "--long", action="store_true", dest="long_output", 
                      default=False, help="Output entire bibtex entry")
    parser.add_argument("-r", "--regex", action="store_true", dest="search_input", 
                      default=False, help="Search for regular expression rather than key")
    parser.add_argument("-F", "--stylefile", action="store", dest="stylefile", default="default.py",
                      help="Specify user-chosen style file",metavar="FILE")
    parser.add_argument("-s", "--style", action="store", dest="style", default="default",
                      help="Specify user-chosen style")
    parser.add_argument("-f", "--field", action="store", dest="field",
                      default=None,
                      help="Search only FIELD; default=%default.",
                      metavar="FIELD")
    #parser.add_argument("-v", "--verbose", action="store_true", dest="verbose", default=False, help="Print INFO messages to stdout, default=%default")
    parser.add_argument("-V", "--verbosity", action="store", dest="verbosity",
                      type=int, default=0,
                      help="Print DEBUG messages to stdout, default=%default")
    parser.add_argument("bibtexFile", action="store",
                      help="The bibtex file to search for the references.")
    parser.add_argument("searchstrings", action="store", nargs='*',
                      help="The strings to search for in the references.")
    
    args = parser.parse_args()
    if 1 == args.verbosity:
        bibsearch_logger.setLevel(logging.INFO)
    if 2 == args.verbosity:
        bibsearch_logger.setLevel(logging.DEBUG)
    bibsearch_logger.debug("Script running.\nargs=%s\nstyle file=%s"
                 %(args, args.stylefile)
                )

    try:
        src = open(args.bibtexFile).read()
    except :
        print("Error: No bibtex file found.")
        sys.exit(1)
    # If no search string was sepcified was specified, read search strings from stdin
    if 0 == len(args.searchstrings):
        searches = string.split(sys.stdin.read())
    else :
        searches = args.searchstrings

    # create object to store parsed .bib file
    parsed_bibfile = bibfile.BibFile()
    # store a parsed .bib file in parsed_bibfile
    bibgrammar.Parse(src, parsed_bibfile)

    # list of entries
    entrylist = []
    if args.field:
        for s in searches:
            entrylist.extend( parsed_bibfile.search_entries(s, field=args.field) )
    elif args.search_input:
        for s in searches:
            entrylist.extend(parsed_bibfile.search_entries(s))
    else:
        entrylist = parsed_bibfile.get_entrylist(searches, discard=True)

    if entrylist:  #found some matches -> output the list in desired format
        result = ""
        if args.citekey_output:
            result = "\n".join(e.citekey for e in entrylist )
        elif args.long_output :
            result = "\n".join(str(e) for e in entrylist)
        else :
            #import a formatting style based on `style` command-line option
            style = importlib.import_module('bibstuff.bibstyles.%s'%args.style)
            """
            str2exec = "import bibstuff.bibstyles.%s as style"%stylename
            workaround = {}  #work around Python 2 exec vs Python 3 exec
            exec(str2exec, {}, workaround)
            style = workaround['style']
            #exec("import bibstuff.bibstyles.%s as style"%os.path.splitext(args.stylefile)[0])
            """
            str2exec = "import bibstuff.bibstyles.%s as style"%os.path.splitext(args.stylefile)[0]
            workaround = {}  #work around Python 2 exec vs Python 3 exec
            exec(str2exec, {}, workaround)
            style = workaround['style']
            citation_manager = style.CitationManager([parsed_bibfile],
                                                     citekeys=[e.citekey for e in entrylist],
                                                     citation_template=style.CITATION_TEMPLATE)
            cite_processor = bibstyles.shared.CiteRefProcessor(citation_manager)
            result = citation_manager.make_citations()
        print(result)
    else: #did not find any matches
        bibsearch_logger.info("No matches.")


 
if __name__ == '__main__':
    main()
