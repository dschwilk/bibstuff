#!/usr/bin/env python
# bib4txt.py
"""
Creates formatted references for a text document.
Useful for reStructuredText documents.
Interacts with a Bibtex-style database file
(without using LaTeX or bibtex).

Dependencies:

- Python 3.6 or higher
- SimpleParse (install with pip)
- pybtex (install with pip) is optional but recommended
- BibStuff (which you should have if you have this script)

The source text file should include citation references in reStructuredText format:
http://docutils.sourceforge.net/docs/user/rst/quickref.html#citations
Roughly: a citation key enclosed in brackets, followed by an underscore.
Citation keys cannot be all digits.

The source document can be output with formatted citation references substituted for the citation keys.
In this case, the reference list is added to the end of the file.   

A slight modification of the reStructuredText ``cite`` directive is currently allowed:

- Most characters are permitted.
  E.g., ``[Schwilk+Isaac:2006]_`` is now (2008) legal in reST and will be recognized by bib4txt.
- Comma separted multiple keys are permitted in a cite:  e.g., ``[Schwilk1999,Isaac2000]_``
  This is *not* legal reST.

The intent is for the formatted references to be written to a separate file.
You can then include this in your reST document with an ``include`` directive.

How it works:

- Uses SimpleParse_ to convert an EBNF_ grammar into an object for scanning reST files for citation references.
- Uses SimpleParse_ to convert an EBNF_ grammar into an object for scanning .bib files.  (See Bibstuff's bibgrammar.py.)
- Extracts the citation references from the input document.
- Outputs a sorted list of citation definitions, to be used in the References section of your documents.

:author: Alan G. Isaac
:date: 2006-07-27
:contact: http://www.american.edu/cas/econ/faculty/isaac/isaac1.htm
:copyright: 2006 by Alan G. Isaac
:license: MIT (see `license.txt`_)
:note: now allows multiple database (.bib) files
:note: bib4txt supercedes addrefs.py, by Dylan Schwilk
:TODO: address the TODOs in the associate BibStuff files, especially in bibstyles/shared.py

.. _EBNF: http://www.garshol.priv.no/download/text/bnf.html
.. _SimpleParse: http://simpleparse.sourceforge.net/
.. _`license.txt`: ../license.txt
"""
__docformat__ = "restructuredtext en"
__version__ = "1.2"
__needs__ = '3.6+'


###################  IMPORTS  ##################################################
#import from standard library
import importlib, os, sys
import logging
logging.basicConfig(format='\n%(levelname)s:\n%(message)s\n')
bib4txt_logger = logging.getLogger('bibstuff_logger')

#import dependencies
import simpleparse

#local imports
try:
    from bibstuff import bibfile, bibgrammar, bibstyles, ebnf_sp
except (ImportError, ModuleNotFoundError): #hack to allow user to run without installing
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    bibdir = os.path.dirname(scriptdir)
    sys.path.insert(0, bibdir)
    from bibstuff import bibfile, bibgrammar, bibstyles, ebnf_sp
################################################################################


###################  GLOBALS  ##################################################
# some globals are set when this file is run as a script
#    style
#    bibfile_processor

# note that the standard separator for multiple keys in one citation reference is a comma
# CITATION_SEP = ','
# set in styles/shared.py



def make_text_output(
    src_as_string,
    src_parser,
    parsed_bibfile,
    style,   # imported style module
    citations_only=True
    ):
    """Create intext citations and the bibliography"""
    #first: create a citation manager to handle the bibfile(s)
    bib4txt_logger.debug('create citation manager')
    citation_manager = style.CitationManager([parsed_bibfile],
                                            citekeys=None,
                                            citation_template=style.CITATION_TEMPLATE)
    #second: create CiteRefProcessor object to process cites during src parsing
    #        (and associate it with the citation_manager)
    bib4txt_logger.debug('create cite processor')
    cite_processor = bibstyles.shared.CiteRefProcessor(citation_manager)
    #third: parse the text (ignore `taglist`; it is a dummy container)
    bib4txt_logger.info('fill cite processor with keys')
    taglist = src_parser.parse(src_as_string, processor=cite_processor)
    """
    :note: Now cite_processor.all_citekeys holds the cite keys.
    It is also associated with citation_manager which holds the bibliography,
    so we can make a sorted entry list.  To do so need:
        - the keys for the citations referenced
        - a sort-key on which to base the sorting
    :note: Sorting is style dependent---e.g., might sort entries on citation_rank.
    """
    #set the citation manager citekeys to all found keys (an ordered list)
    #citation_manager.citekeys = cite_processor.all_citekeys
    #make the citation definitions for a list of References
    bib4txt_logger.info('make citations')
    result = citation_manager.make_citations() + "\n"
    #lastly, prepend the entire document, if desired
    if not citations_only:
        result = cite_processor.__repr__() + result
    return result

################################################################################




def bibfiles2string(
    bibfile_names,     #sequence of strings, the file paths
    encoding="ascii"   #file encoding (same for all files)
    ) -> str:
    """Return the provided .bib files as a single string.
    """
    bibfiles_as_strings = list()
    for bibfile_name in bibfile_names:
        if (os.path.splitext(bibfile_name)[-1]).lower() != ".bib":
            bib4txt_logger.warning(f"{bibfile_name} does not appear to be a .bib file.")
        try:
            with open(bibfile_name, 'r', encoding="ascii") as fh:
                bibfiles_as_strings.append( fh.read() )
        except IOError:
            bib4txt_logger.warning(f"{bibfile_name} not found.")
    return '\n'.join( bibfiles_as_strings )
        
        

def main():
    """Return None; provide command-line tool.
    See bib4txt.py -h for help.
    """
    _description = """
    %(prog)s creates formatted references for any text document
    that uses citation references in the syle of reStructuredText.
    It interacts with a Bibtex-style database file (without using LaTeX or bibtex).
    The references are valid reStructuredText citations.
    """
    _usage = """
    %(prog)s [options] BIB_DATABASE
    Or with standard options:
    %(prog)s -i reST_FILE  -n -o refs_FILE BIB_DATABASE
    """
    _epilog = """
    User defined styles are easy to add.
    See the default style for an example.
    """

    #set the default output
    _outfile = sys.stdout
    
    from argparse import ArgumentParser
    argparser = ArgumentParser(
        usage=_usage,
        description=_description,
        epilog=_epilog
        )

    argparser.add_argument("-v", "--version", action='version', version="version: {}".format(__version__))

    argparser.add_argument("-a", "--all", action="store_true", dest="entire_doc", default=False,
                      help="Output entire document, making citation reference substitutions, default=%(default)s")
    argparser.add_argument("-i", "--infile", action="store", dest="infile",
                      help="Parse FILE for citation references.", metavar="FILE")
    argparser.add_argument("-o", "--outfile", action="store", dest="outfile",
                      help="Write formatted references to FILE", metavar="FILE")
    argparser.add_argument("-n", "--nuke", action="store_true", dest="overwrite", default=False,
                      help="silently overwrite outfile, default=%(default)s")
    argparser.add_argument("--usePybtex", action="store_true", dest="usePybtex", default=False,
                      help="use the pybtex parse to parse .bib files (experimental)")
    argparser.add_argument("-F", "--stylefile", action="store",
                      dest="stylefile", default="default.py",
                      help="Specify user-chosen style file",metavar="FILE")
    argparser.add_argument("-s", "--style", action="store", 
                      dest="style", default="default",
                      help="Specify user-chosen style (by style name).")
    argparser.add_argument("-V", "--verbosity", action="store", type=int, dest="verbosity", default=0,
                      help="2: print DEBUG messages; 1: print INFO messages; default=%(default)s")
    argparser.add_argument("-L", "--logger-level", action="store", type=int, dest="logger_level",
                      help="Set logging level to integer value (per logging module).")
    argparser.add_argument("-x", "--xp", action="store_true", dest="xp_parse",
                      default=False, help="Use experimental document parser, default=%(default)s")
    argparser.add_argument("bibfiles", action="store", nargs='*',
                      help="The .bib files for the references.")

    args = argparser.parse_args()
    if args.logger_level:
        bib4txt_logger.setLevel(args.logger_level)
    elif 2==args.verbosity:
        bib4txt_logger.setLevel(logging.DEBUG)
    elif 1==args.verbosity:
        bib4txt_logger.setLevel(logging.INFO)

    if args.stylefile != "default.py":
        bib4txt_logger.info("It is currently recommended to pass styles with the -s option.")
        stylename = os.path.splitext(args.stylefile)[0]
    else:
        stylename = args.style
        if "." in stylename:
            bib4txt_logger.warn("use the -f option to pass a style by filename")
            stylename = os.path.splitext(stylename)[0]

    bib4txt_logger.info(
            "\n".join([
            "Script running:",
            " bibfiles=%s",
            " infile=%s",
            " outfile=%s",
            " style=%s"
            ])%(args.bibfiles, args.infile, args.outfile, stylename)
            )
    #import a bibliography style based on `stylefile` command-line option
    #TODO: add error handling for unknown styles
    style = importlib.import_module('bibstuff.bibstyles.%s'%stylename)

    # open output file for writing (default: stdout)
    if args.outfile:
        if os.path.exists(args.outfile) and not args.overwrite:
            _msg = """ABORTED because output file %s already exists:
            Use -n option to nuke (overwrite) this file.
            PLEASE CHECK FILE NAME CAREFULLY!
            """%(args.outfile)
            bib4txt_logger.error(_msg)
            sys.exit(1)
        _outfile = open(args.outfile,'w', encoding="utf8")


    _infile = sys.stdin #default
    # read input file if provided as option:
    if args.infile:
        try:
            _infile = open(args.infile, mode='r', encoding='utf-8')
        except:
            raise ValueError(f"Cannot open: {args.infile}.")

    if args.entire_doc:
        ebnf_dec = ebnf_sp.cites_rest
    else:
        ebnf_dec = ebnf_sp.cites_only_rest
    if args.xp_parse:
        ebnf_dec = ebnf_sp.cites_xp
    # Create a simpleparse.parser Parser based on the chosen grammar
    cite_parser = simpleparse.parser.Parser(ebnf_dec, root='src')

    # read database (.bib) files
    bibfile_names = args.bibfiles
    bibfile_as_string = bibfiles2string(bibfile_names)
    if 0 == len(bibfile_as_string):
        bib4txt_logger.error("No BibTeX databases found.")
        argparser.print_help()
        sys.exit(1)
    if args.usePybtex:
        import pybtex.errors
        pybtex.errors.set_strict_mode(False)
        from pybtex.database.input.bibtex import Parser
        bibdata = Parser().parse_string(bibfile_as_string)
        from bibstuff import bibfile4pybtex
        bibfile_processor = bibfile4pybtex.BibFile(bibdata)
    else:
        # create object to store parsed .bib file
        bibfile_processor = bibfile.BibFile()
        bib4txt_logger.debug('Ready to parse bib file.')
        #store parsed .bib files in the bibfile_processor
        bibgrammar.Parse(bibfile_as_string, bibfile_processor)

    bib4txt_logger.info('bib file parsed.')

    result = make_text_output(
        _infile.read(),
        cite_parser,
        bibfile_processor,  #a bibfile.BibFile or bibfile4pybtex.BibFile
        style,
        citations_only = not args.entire_doc)

    _outfile.write(result)        
    _outfile.close()
    _infile.close()



if __name__ == '__main__':
    main()
