"""
#Duplicate the functionality of bibfile.py,
#when using pybtex's bibliography parser.

Provide two classes, BibFile and BibEntry for accessing the parts of a bibtex
database.

:copyright:  Alan G Isaac, see AUTHORS
:license: MIT (see LICENSE)
:requires: Python 3.8_
"""
__docformat__ = "restructuredtext en"
__authors__  = ["Alan G. Isaac"]
__version__ = '0.1'
__needs__ = '3.8'

# options:
# __strict__ = False allows empty citekeys
__strict__ = False # should we be strict with bibtex format?


####################### IMPORTS #####################################
# imports from standard library:
import re, logging
bibfile_logger = logging.getLogger('bibstuff_logger')
from typing import Optional, Sequence


###############  GLOBAL VARIABLES  ##################################
months_en = ('January','February','March','April','May','June',
             'July','August','September','October','November','December')
monthslower_en = [m.lower() for m in months_en]
monthmacros_en = [m[:3] for m in monthslower_en]
MONTH_DICT = dict( zip(monthmacros_en, months_en) )
#####################################################################


class BibEntry(dict):
    """Provides access to a single bibliographic entry,
    with a dictionary interface to the fields.
    Field keys are case-insensitive and fields are stored
    in the order added.
    
    :note: uses 'citekey' instead of 'key' since BibTeX allows a 'key' field
    :note: uses 'entry_type' instead of 'type' since BibTeX allows a 'type' field
    """
    def __init__(self,
        citekey: str,
        entry
        ): #see BibFile (below)
        dict.__init__(self,
            citekey=citekey,
            entry_type=entry.type)
        self._fields = list(x[0] for x in entry.fields)
        self.update(((k.lower(), v) for (k,v) in entry.fields.items()))
        persons = entry.persons
        #recover the raw names (TODO: remove this ridiculous workaround)
        for k,ps in persons.items():
            self[k.lower()] = " and ".join(str(p) for p in ps)
        self.entry_type = entry.type
        self.citekey = citekey

    def __repr__(self):
        """return string representation of entry
        """
        stringrep = '@%s{%s,\n' % (self.entry_type.upper() , self.citekey)
        try:
            mlen = max( len(key_str) for key_str in self._fields )  # for pretty format
        except ValueError: #no fields (not a true entry)
            mlen = 0
            bibfile_logger.warn("Entry apparently has no fields.")
        field_list = []
        for key in self._fields:
            addbraces = True
            addquotes = False
            #spacer = ' '*(mlen - len(key) )
            val = self[key]
            #handle crossref
            if key == 'crossref':
                try: val = val['citekey'] #might be an entry
                except TypeError: pass    #->must be a string
            elif key == 'journal':
                if val.isalpha() and val.islower(): #:TODO: allow punctuation!!
                    addbraces = False  #i.e., assume it is a macro
            elif key == 'month':
                # always use month macros if possible
                if val.lower() in monthslower_en + monthmacros_en:
                    val = val[:3].lower()
                    addbraces = False
            elif key in ("year","number","volume","chapter"):
                try:
                    addbraces = not int(val)
                except:
                    pass
            if '@' in val:  # need to protect '@'
                addquotes = True
            if addquotes:
                    val = '"' + val + '"'
            elif addbraces:
                val = "{" + val + "}"
            field_list.append("  %-*s = %s" % (mlen, key, val))
        stringrep += ",\n".join(field_list)
        stringrep += '\n}\n'
        return stringrep

    def __setitem__(self, key, val):
        key = key.lower()
        dict.__setitem__(self, key, val)
        if key == "key":
            bibfile_logger.info(
            "Setting 'key' as an entry *field*. (Recall 'citekey' holds the entry id.)")
        if key not in self._fields and key not in ["citekey","entry_type"] and val:
            self._fields.append(key)

    def __getitem__(self, field):  #field is usually a BibTeX field but can be a citekey
        field = field.lower()
        if field == "key":
            bibfile_logger.info(
            "Seeking 'key' as an entry *field*. (Recall 'citekey' holds the entry id.)")
        try:
            result = dict.__getitem__(self, field)
        except KeyError:
            crossref = self.get('crossref', '')
            if isinstance(crossref, self.__class__):
                result = crossref[field]
            else:
                #:note: instead of None, KeyError returns '', which is used for formatting
                result = ''
        #:note: 20080331 add handling of month macros
        if field == 'month' and result in monthmacros_en:
            result = MONTH_DICT[result]
        return result
    
    def __delitem__(self,key) :
        key = key.lower()
        try:
            dict.__delitem__(self, key)
        except KeyError:
            pass
        try:
            self._fields.remove(key)
        except ValueError:
            pass

    @property
    def get_entry_type(self):
        return self["entry_type"]
    '''
    def set_entry_type(self, val):
        self["entry_type"] = val.lower()  #:note: entry_type stored as lowercase
    entry_type = property(get_entry_type, set_entry_type, None, "property: 'entry_type'")
    '''

    @property
    def get_citekey(self):
        return self["citekey"]
    '''
    def set_citekey(self, val):
        self["citekey"] = val
    citekey = property(get_citekey,set_citekey,None,"property: 'citekey'")
    '''

    def get_fields(self):
        return self._fields
    def set_fields(self, lst):
        self._fields = lst
    fields = property(get_fields, set_fields, None, "property: 'fields'")

    def search_fields(self, string_or_compiled, field='', ignore_case=True):
        """Find regular expression in entry. 

        Return MatchObject if string_or_compiled found in entry else None. If
        field is omitted, search is through all fields.
        
        :note: used by BibFile's find_re method, which is used in turn by bibsearch.py
        :Parameters:
          `string_or_compiled` : string to compile or compiled regex
            pattern for searching
          `field` : string
            field to search in self (default: search all fields)

        """
        if isinstance(string_or_compiled, str):
            if ignore_case:
                reo = re.compile(string_or_compiled, re.MULTILINE | re.IGNORECASE)
            else:
                reo = re.compile(string_or_compiled, re.MULTILINE)
        else: #must have a compiled regular expression
            reo = string_or_compiled
        if not field: #->try all fields (but not citekey)
            for f in self.get_fields():
                found = reo.search( self[f] )
                if found: break # no need to check more fields 

        # :note: CAN test 'field in self' (even though an entry will not raise
        #KeyError! see TODO above) BUT do not test 'field in self' bc want test
        #for empty fields below
        elif self[field]:
            found = reo.search( self[field] )
        else:
            if field in self:
                bibfile_logger.info("Empty field %s in entry\n%s.\n."%(self,field))
            found = None
        return found

    def format_names(self, names_formatter):
        """return formatted BibName-object if possible else raw name

        :type `names_formatter`: NamesFormatter
        :note: called by CitationManager in format_citation
        :note: 2006-08-08 no longer sets a `_names` attribute
        :TODO: add default name_template useful for .bib files?
        """
        bibfile_logger.debug(f"BibEntry.format_names: arg is: {names_formatter}")
        names = self.get_names()  #get a BibName instance (or possibly, a string)
        #keep string if stuck with it
        if isinstance(names,str):
            result = names
        else: #assume a BibName instance
            #ask BibName instance to format itself (and it asks a NamesFormatter to do it)
            result = names.format(names_formatter)
        bibfile_logger.debug(f"BibEntry.format_names result = {result}")
        return result

    def get_names(self, entry_formatter=None, try_fields=None):
        """return (BibName-object if possible else string)

        :note: does NOT set `self._names`
        """
        if entry_formatter is None:
            if not try_fields:
                try_fields = ['author','editor','organization']
        return self.make_names(entry_formatter, try_fields=try_fields)

    def make_names(
        self,
        entry_formatter=None,
        try_fields=None
        ):
        """Return (BibName-object if possible else string)
        (from "raw" names).
        
        :change: 2006-08-02 altered to return BibName instance and not set _names
        :note: self returns None if field missing (-> no KeyError)
        :note: this method introduces the only dependence on simpleparse (via bibname)
        :TODO: return BibName instance for each available name field??
        :Parameters:
          - `entry_formatter`: EntryFormatter instance to provide style information
          - `try_fields`: list of field names to try sequentially; none empty filed -> name
        """
        # importing bibname here to avoid recursive import
        from bibstuff import bibname #ai: shd move all bibname into here? possibly
        if entry_formatter is None:
            for field in try_fields:
                raw_names = self[field]
                if raw_names:
                    break
        else:
            raw_names, field = entry_formatter.pick_raw_names(self, try_fields)
        return  bibname.BibName(raw_names, from_field=field)  #names are in a BibName object

    def format_with(self, entry_formatter):
        bibfile_logger.debug("BibEntry.format_with: arg is:"+str(entry_formatter))
        #ask the EntryFormatter to do it
        return entry_formatter.format_entry(self)

    # A default label style for citekeys created by make_citekey()
    # first max_names names included, then etal
    citekey_label_style1 = dict(
        name_template = 'v{_}_|l{}', # "van_der_Meer" or "van_DerStadt"
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

    #style2 shd be rst compatible
    # citekey_label_style2 = dict(
    #     name_first = 'l{_}',
    #     name_other = 'l{_}',
    #     max_names = 2,
    #     use_max_names = False,
    #     name_name_sep = ('.','.'),
    #     etal = '',
    #     lower_name = True,
    #     anonymous = 'anon',
    #     article = "%(names)s-%(year)s-%(jrnl)s",
    #     book = "%(names)s-%(year)s",
    #     misc = "%(names)s-%(year)s",
    #     default_type = "%(names)s-%(year)s",
    # )


    def make_citekey(self, used_citekeys = [], style = citekey_label_style1):
        """Create and return a new citekey based on the entry's data. This is for
        creating predictable and useful citekey (labels) for BibEntry objects.
        This is not integrated with the citation styles in bibstuff.bibstyles;
        but it serves a very different purpose. This is to create consistent
        citation keys that are easy to type and guess and that are valid BibTeX
        citation keys. 

        :Parameters:
            - used_citekeys : list
                a list of the already taken citation keys
                so that the function can avoid duplicates (by adding a,b,c,d... etc)
            - style : str
                The format of the citetekey is determined by a `label_style` (see below)

        :Returns: string
            the citation key (label)

        Example:
            The label style is a dict with the following fields::

               citekey_label_style1 = dict(
               name_template = 'v{_}_|l{}', # see NameFormatter class
               max_names = 2,
               name_name_sep = "+",
               etal = 'etal',
               anonymous = 'anon',
               lower_name = False,
               article = "%(names)s-%(year)s",
               book = "%(names)s-%(year)s",
               misc = "%(names)s-%(year)s",
               default_type = "%(names)s-%(year)s")
        

        :TODO: Strip LaTeX accent characters from names when making label

        """

        from .bibstyles.shared import NameFormatter
        from string import ascii_lowercase

        format_dict = {}
        entry_type = self.entry_type.lower()
        try:
            label_template = style[entry_type]
        except KeyError:
            label_template = style['default_type']

        name_template = style['name_template']
        max_names = style['max_names']
        name_name_sep = style['name_name_sep']
        lower_name = style['lower_name']
        etal = style['etal']

        # first, make names
        name_formatter = NameFormatter(template = name_template)
        names_dicts = self.get_names().get_names_dicts()
        # make list of 'v_|l' last names, which can possibly have multiple
        # tokens (e.g., two piece last names)
        ls = [name_formatter.format_name(name_dict) for name_dict in names_dicts]
        if len(ls) > max_names:
            ls = ls[:max_names] + [etal]

        names =  name_name_sep.join(ls)
        if lower_name:
            names = names.lower()
        format_dict['names'] = names
        year = self['year'] or '????'
        format_dict['year'] = year
        if entry_type == "article":
            jrnl = self['journal']
            jrnl = ''.join(jrnl.split()).lower()  # keep macro
            jrnl = jrnl.replace("journal","j",1)
            format_dict['jrnl'] = jrnl  # short form, no spaces

        # make unique result: if needed, append suffix b or c or d... to year
        sfx = ''; c = 1
        # while result+sfx in used_citekeys:
        while label_template%format_dict in used_citekeys:
            sfx = ascii_lowercase[c%26]*(1+c//26)  # :note: lowercase since
                                                   # BibTeX does not
                                                   # distinguish case
            format_dict['year'] = year+sfx
            c += 1

        result = label_template%format_dict
        return result




# ----------------------------------------------------------
# Bibfile
# -------
# Provides storage for bibtex files.
# ----------------------------------------------------------
class BibFile(object):
    """Stores parsed bibtex file.  Access entries by key.

    :note: a BibFile object should simply *store* .bib file parts
           (a list of entries and a macro map) and provide access
           to these parts
    :called by: shared.find_entries bibstyles/shared.py
    :used by: ../scripts/bib4txt.py
    """
    def __init__(self,
        pybtexBibFile  #map (citekey to pybtex Entry)
        ):
        self.pybtexBibFile = pybtexBibFile
        self.entries = []
        self._macroMap = {}

    def get_entrylist(self,
        citekeys,
        discard=True #False used by styles?
        ) -> list:
        """Return list of found BibEntry instances
        (and None for entries not found, unless discard is True).
        """
        if not citekeys:
            bibfile_logger.warning("""get_entrylist:
                No keys provided; returning empty cited-entry list.""")
            return []
        temp = list( (citekey, self.pybtexBibFile.entries.get(citekey))
                     for citekey in citekeys)
        bad_keys = list(pair[0] for pair in temp if not pair[1])
        if bad_keys and discard:
            bibfile_logger.warning("Database entries not found for the following keys:\n"+"\n".join(bad_keys))
        if discard:
            result = list(BibEntry(*pair) for pair in temp if pair[1])
        else: #keep None when occurs in entry list
            result = list(BibEntry(*pair) if pair[1] else None for pair in temp)
            #result =  [pair[1] for pair in temp]
        #attach cross references
        for entry in result:
            if (entry is not None):
                crossref = entry.get('crossref', None)
                if isinstance(crossref, str):
                    crossref = self.pybtexBibFile.entries.get(crossref)
                    if crossref:
                        entry['crossref'] = crossref
        return result

    """PRODUCTION FUNCTIONS:
    for parsing, must provide a function for each production name.
    """

    '''
    def string(self, tuple4, buffer ):
        """Return a string, stripping leading and trailing markers"""
        (tag,start,stop,subtags) = tuple4
        return buffer[start+1:stop-1]

    def number(self, tuple4, buffer ):
        """return a number as a string"""
        (tag,start,stop,subtags) = tuple4
        return buffer[start:stop]

    def entry_type( self, tuple4, buffer ):
        """Return the entry type"""
        (tag,start,stop,subtags) = tuple4
        return getString((tag,start,stop,subtags), buffer)

    def citekey( self, tuple4, buffer ):
        """Return the entry's citekey"""
        (tag,start,stop,subtags) = tuple4
        return getString((tag,start,stop,subtags), buffer)

    # macro name
    def name(self, tuple4, buffer ):
        """Return lookup on name or name if not in map."""
        (tag,start,stop,subtags) = tuple4
        return self._macroMap.get(buffer[start:stop],buffer[start:stop])

    def field(self, tuple4, buffer ):
        """Process a bibentry field and return tuple of name, value."""
        (tag,start,stop,subtags) = tuple4
        str = ''
        for t in subtags[1][3]:
            if(t) :
                str += dispatch(self, t, buffer) # concatenate hashed together strings
        return (dispatch(self, subtags[0], buffer), str)
                
    def entry( self, tuple4, buffer ):
        """Process the bibentry and its children.
        """
        (tag,start,stop,subtags) = tuple4
        entry = BibEntry()
        entry.entry_type = dispatch(self, subtags[0], buffer)
        entry.citekey  = dispatch(self, subtags[1], buffer)
        for field in subtags[2][3] :
            #bibfile_logger.debug("entry: ready to add field: "+str(dispatch(self, field, buffer)))
            k,v = dispatch(self, field, buffer)
            #:note: entry will force k to lowercase
            entry[k] = v
        self.entries.append(entry)
    

    def macro( self, tuple4, buffer ):
        """Process a macro entry and add macros to macro map"""
        (tag,start,stop,subtags) = tuple4
        name, str = dispatch(self, subtags[0], buffer)
        """
        the_type = getString(subtags[0], buffer)
        if  the_type.upper() != 'STRING' :
            # it looks like  a macro, but is not: could be a regular entry with no key
            lineno = lines(0, start, buffer)+1
            bibfile_logger.warning("Entry at line %d has macro syntax, but entry_type is %s" % (lineno ,  the_type))
            if not __strict__: # we can add a dummy key and treat this entry as a regular entry
                entry = BibEntry()
                entry.entry_type = dispatch(self, subtags[0], buffer)
                entry.citekey  = 'KEY'  # dummy key -- or should we be strict?
                for field in subtags[1][3] :
                    k,v = dispatch(self, field, buffer)
                    #:note: entry will force k to lowercase
                    entry[k] = v
                self.entries.append(entry)
                bibfile_logger.warning("Dummy key added to entry at line %d" % lineno)
        else :  # otherwise it is really a macro entry
            for field in subtags[1][3]:
                name, str = dispatch(self, field, buffer)
                self._macroMap[name] = str  
        """
        self._macroMap[name] = str  
        

    def preamble( self, tuple4, buffer ):
        """Process the given production and it's children"""
        (tag,start,stop,subtags) = tuple4
        the_type = getString(subtags[0], buffer)
        lineno = lines(0,start,buffer)+1
        if  the_type.upper() != 'PREAMBLE' :
            bibfile_logger.warning("Entry at line %d has preamble syntax but entry_type is %s" % (lineno,the_type))
        else :
            bibfile_logger.warning("Preamble entry on line %d:" % lineno + "\n" + buffer[start:stop])

    def comment_entry(self, tuple4, buffer):
        """Process the given production and it's children"""
        (tag,start,stop,subtags) = tuple4
        the_type = getString(subtags[0], buffer)
        lineno = spdp.lines(0, start, buffer) + 1
        if  the_type.upper() != 'COMMENT' :
            bibfile_logger.warning("""Entry at line %d has comment syntax
            but entry_type is %s:
            Details: %s""" % (lineno, the_type, getString(subtags[1], buffer)))
        else :
            bibfile_logger.info("Comment entry on line %d:" % lineno + " " + getString(subtags[1], buffer))
    '''

    def search_entries(self, string_or_compiled, field='', ignore_case=True):
        """Return list of matching entries.
        Search for regular expression in the fields of each entry.
        If field is omitted, search is through all fields.
        
        :note: used by bibsearch.py
        :Parameters:
          - `string_or_compiled` : string to compile or compiled regex
            pattern for searching
          - `field` : string
              field to search in self (default: search all fields)
        """
        if isinstance(string_or_compiled, str):
            if ignore_case:
                reo = re.compile(string_or_compiled, re.MULTILINE | re.IGNORECASE)
            else:
                reo = re.compile(string_or_compiled, re.MULTILINE)
        else: #->must have a compiled regular expression
            reo = string_or_compiled
        """
        Find regex in bib_entry.
        If field is omitted, search is through all fields.
        
        :note: used by bibsearch.py
        """
        ls = [entry for entry in self.entries
            if entry.search_fields(string_or_compiled=reo, field=field, ignore_case=ignore_case)]
        return ls


# self test
# -------------------------
# usage: bibfile.py DATABASE_FILE
# if __name__ == "__main__":
#     import sys
#     if len(sys.argv) > 1 :
#         src = open(sys.argv[1]).read()
#         bfile = BibFile()
#         bibgrammar.Parse(src, bfile)
#         for entry in bfile.entries :
#             print entry

#     else :
#         print "self test usage: bibfile.py DATABASE_FILE"

