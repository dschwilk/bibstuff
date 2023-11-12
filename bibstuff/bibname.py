#! /usr/bin/env python
#File: bibname.py
"""
:mod:`bibstuff.bibname`: Name Parser and Formatter
--------------------------------------------------

Parses bibtex-formatted author/editor raw names and provides
formatting functions (e.g., via bibstyles/shared.NamesFormatter).

:copyright: 2009-2021 Dylan Schwilk and Alan G Isaac, see AUTHORS
:license: MIT (see LICENSE)

:note: Major change as of 2021-08-02: depends on pybtex.
:note: Major change as of 2008-07-02. Now the ebnf grammar and processor
       handles parsing of a list of names (a bibtex names field such as editor
       or author) and parses the single author name into its fvlj parts. This
       eliminates the need for the original hand-coded parse_raw_names_parts
       function. Moved to using names_dicts rather than names_parts. The
       grammar handles latex accents and ligatures as well as braces strings so
       that a name such as {Barnes and Noble, Inc} is parsed as a single name
       and not split on the " and ".
:todo: The dispatch processor does not currently strip the leading and trailing
       braces from latex/bibtex strings. Not hard to add (see bibfile.py). This
       should be done eventually.
:todo: The grammar does not support quoted strings, only braces strings. Could
       be added fairly simply

:note: see https://www.tug.org/TUGboat/tb27-2/tb87hufflen.pdf
       for BibTeX name details.
:dependences: simpleparse and pybtex
"""
__docformat__ = "restructuredtext en"
__authors__  =    ["Dylan W. Schwilk", "Alan G. Isaac"]
__version__ =    '2.03'
__needs__ = '3.6'


################ IMPORTS #############################
# import from standard library
from typing import Optional
import logging
logging.basicConfig(format='\n%(levelname)s:\n%(message)s\n')
bibname_logger = logging.getLogger('bibstuff_logger')

# import dependencies
import simpleparse
from simpleparse.dispatchprocessor import dispatch
import pybtex.database
#from string import maketrans

# BibStuff imports
from . import bibstyles, bibfile, bibgrammar
######################################################


################## Global Variables ##################

# constant needed for populating dicts in names_dicts with empty lists for
# missing parts
nameparts = ("first","last","von","jr")

# The EBNF description of a bibtex name field (such as a list of author names).
ebnf_bibname = r"""
namelist := sp*, name, (_and_, name)*
<_and_>  := sp+, "and", sp+
name     := vlf / fvl / fl / vljf / fvlj / l
>l<      :=  last
>vlf<    := (von, sp+)*, last, (sp+, last)*, comma, (sp*, first)+
>fl<     := first, sp+, (first, sp+, ?(capitalized/capstring))*, last
>fvl<    := (first, sp+)+, (von, sp+)+, last, (sp+, last)*
>fvlj<   := fvl, comma, jr
>vljf<   := (von, sp+)*, last, (sp+, last)*, comma, jr,  comma,  first, (sp+ , first)*
von      := lowercase / lowerstring
first    := capitalized / capstring
last     := capitalized / capstring
jr       := "jr" / "Jr" / "JR" /  "Junior" / "junior" /
            "Sr" / "sr" / "II" / "III" / "IV" / "2nd" / "3rd" / "4th"
<comma>           := sp*, ',', sp*
<capitalized>     := capital  , anyc*
<lowercase>       := ?lowerc, -"and ", anyc*  # Mustn't grab the delimiter _and_ for a part
<ltx_accent>      := '\\`' / "\\'" / '\\^' / '\\"'  /  '\\H' / '\\~' / '\\c' / '\\=' / '\\b' / '\\.' /
                      '\\d' / '\\u' / '\\v' / '\\t'
<ltx_ij_accent>   := '\\^{\\i}' / '\\"{\\i}' / '\\^{\\j}' / '\\"{\\j}'
<ltx_ligature_uc> := '\\AE' / '\\OE' / '\\AA' / '\\O'
<ltx_ligature_lc> := '\\ae' / '\\oe' / '\\aa' / '\\o' / '\\ss'
<capital>         := ('{',capital,'}') / [A-Z] /
                     (ltx_accent, [A-Z]) / (ltx_accent, '{' , [A-Z] , '}') /
                     ltx_ligature_uc
<lowerc>          := ('{',lowerc,'}') / [a-z] / (ltx_accent, [a-z]) /
                     (ltx_accent, '{' , [a-z] , '}') /
                     ltx_ij_accent / ltx_ligature_lc
<anyc>            := [~'-] / capital / lowerc / '.'
<string>              :=  '{' , braces_string?, '}'
<capstring>           := '{' , cap_braces_string?, '}'
<lowerstring>         := '{' , lower_braces_string?, '}'
<cap_braces_string>   := ( (capital, -[{}]*) / capstring)+ 
<lower_braces_string> := ( (capital, -[{}]*) / lowerstring)+
<braces_string>       := (-[{}]+ / string)+
<sp>                  := [ \t\n\r.]
"""

bibnamelist_parser = simpleparse.parser.Parser(ebnf_bibname, 'namelist')

######################################################

# ----------- Public Classes and Functions -----------------#

class Person(pybtex.database.Person):
    def __init__(self, string="", **kwargs):
        super().__init__(string=string, **kwargs)
        self._raw = string
        
    def fvlj(self):
        firsts = self.first_names + self.middle_names
        result = dict(
            first=firsts,
            von=self.prelast_names,
            last=self.last_names,
            jr=self.lineage_names
            )
        return result



class BibName( simpleparse.dispatchprocessor.DispatchProcessor ):
    """Provides a parser processor for bibtex names.
    Processes a bibtex names entry (author, editor, etc) and
    stores the resulting raw_names_parts.
    
    :note: a BibName object should be bibstyle independent.
    """
    def __init__(self,
        raw_names=None,
        from_field=None
        ) :  #:note: 2006-07-25 add initialization based on raw name
        """initialize a BibName instance
        
        :Parameters:
            `raw_names` : str
                the raw names (e.g., unparsed author field of a BibEntry instance)
            `from_field` : str
                the entry field for the raw name

        :note: 2006-08-02 add `from_field` argument (set by `BibEntry.make_names`)
        """
        self.from_field = from_field
        self.raw_names = raw_names
        self._names_dicts = []
        self.persons = []
        #populate self._names_dicts from raw_names
        if raw_names:
            self.parse_raw_names(raw_names)

    ###############  PRODUCTION FUNCTIONS  #######################
    # Handle each name by adding new dict to list "_names_dicts", then
    # handle each name part by adding to last dict in _names_dict list.

    def name(self, tuple4, abuffer):
        """Prduction function to process a single name in a nameslist"""
        tag, start, stop, subtags = tuple4
        newdict = dict()
        self._names_dicts.append(newdict) # add new dict to list
        '''transition to pybtex
        for part in subtags:
            dispatch(self, part, abuffer)
        # Create empty lists for missing parts
        for p in nameparts: # ("first","last","von","jr"), see declaration above
            if p not in newdict:
                newdict[p] = []
        '''
        self.persons.append(Person(abuffer[start:stop]))

    '''transition to pybtex
    def last(self, tuple4, buffer ):
        """Processes last name part in a single name of a bibtex names field"""
        tag, start, stop, subtags = tuple4
        if 'last' in self._names_dicts[-1]:
            self._names_dicts[-1]["last"].append(buffer[start:stop])
        else:
            self._names_dicts[-1]["last"] = [buffer[start:stop],]

    def first(self, tuple4, buffer ):
        """Processes first name part in a single name of a bibtex names field"""
        tag, start, stop, subtags = tuple4
        if 'first' in self._names_dicts[-1]:
            self._names_dicts[-1]["first"].append(buffer[start:stop])
        else:
            self._names_dicts[-1]["first"] = [buffer[start:stop],]

    def von(self, tuple4, buffer ): 
        """Processes von name part in a single name of a bibtex names field"""
        tag, start, stop, subtags = tuple4
        if 'von' in self._names_dicts[-1]:
            self._names_dicts[-1]["von"].append(buffer[start:stop])
        else:
            self._names_dicts[-1]["von"] = [buffer[start:stop],]

    def jr(self, tuple4, buffer ):
        """Processes jr name part in a single name of a bibtex names field"""
        tag, start, stop, subtags = tuple4
        # Just on jr part so simple add list with one item
        self._names_dicts[-1]["jr"] = [ buffer[start:stop],]
    '''
        
    ##############  HELPER FUNCTIONS  ######################

    def parse_raw_names(self,
        raw_name
        ):
        """Populate an empty BibName instance *or* replace
        all the name values currently contained in an instance.
        Parses the names field with the bibname grammar."""
        self._names_dicts = []  # Replace extant list of  names
        bibnamelist_parser.parse(raw_name,  processor =  self)

    def get_names_dicts(self):  #:note: renamed
        """
        Return a list of name dicts,
        one dict per name,
        having the fields: first , von, last, jr
        """
        #starting transition to pybtex:
        #return self._names_dicts
        return list(p.fvlj() for p in self.persons)

    
    #ai: method to get last names, which is needed by bibstyle.py and by
    #some style sortkeys
    def get_last_names(self):
        """Return list of strings, where each string is a last name.
        
        :TODO: graceful handling of missing names parts
        """
        #result = list(' '.join(name_dict['last']) for name_dict in self._names_dicts)
        #bibname_logger.debug("BibName.get_last_names result: "+str(result))
        #start transition to pybtex:
        names_dicts = self.get_names_dicts()
        result = list(' '.join(name_dict['last']) for name_dict in names_dicts)
        return result

    def format(self, names_formatter):
        """
        Format a BibName as a string useful for citations,
        handling correctly multiple names with multiple parts.

        :note: called by the BibEntry class in bibfile.py when entry formatting
            is requested
        """
        return names_formatter.format_names(self)


# command-line version

## TODO: move this to script

if __name__ =="__main__":
    import sys
    from optparse import OptionParser
    from bibstyles.default import DEFAULT_CITATION_TEMPLATE

    defaultformat = DEFAULT_CITATION_TEMPLATE['name_first']

    _description = """
    %(prog)s parses bibtex-formatted author/editor raw names and provides
    formatting(e.g., via bibstyles/shared.NamesFormatter).
    """

    _usage = "usage: %(prog)s [options] filenames"

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
    argparser.add_argument("-t", "--template", action="store", type="string", \
                      dest="template", default = defaultformat, help="Name format template")
    argparser.add_argument("-i", "--initials", action="store_true", dest="initials", \
                      default = True, help="Initialize first names")
    argparser.add_argument("-I", "--no-initials", action="store_false", dest="initials", \
                      default = True, help="do not initialize first names")
    argparser.add_argument("-l", "--last-names", action="store_true", dest="last_names", \
                      default = False, help="Print last names only.")
    argparser.add_argument("-V", "--verbosity", action="store", type=int, dest="verbosity", default=0,
                      help="2: print DEBUG messages; 1: print INFO messages; default=%(default)s")
    argparser.add_argument("-L", "--logger-level", action="store", type=int, dest="logger_level",
                      help="Set logging level to integer value (per logging module).")

    # get options
    args = argparser.parse_args()
    if args.logger_level:
        bib4txt_logger.setLevel(args.logger_level)
    elif 2==args.verbosity:
        bib4txt_logger.setLevel(logging.DEBUG)
    elif 1==args.verbosity:
        bib4txt_logger.setLevel(logging.INFO)

    if args.last_names:
        options.template = 'l'
    if args.initials:
        initials = 'f'  # only first names.  Does any style ever use initials for anything else?
    else:
        initials = ''

    if len(args) == 0:
        src = sys.stdin.read()
    else :
        flist = list()
        for fname in args:
            try:
                flist.append(open(fname,'r'))
            except IOError :
                bibname_logger.warn('Error in filelist: %s.'%fname)
        src = '\n'.join(f.read() for f in flist)
        map(lambda f: f.close(), flist)

    if not src:
        bibname_logger.error("No bibtex source database found")
        sys.exit(1)
    else:
        bfile = bibfile.BibFile()
        bibgrammar.Parse(src, bfile)

    names_formatter = bibstyles.shared.NamesFormatter(template_list=[options.template]*2,initials=initials)
    for entry in bfile.entries:
        print(entry.format_names(names_formatter))

