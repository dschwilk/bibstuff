#! /usr/bin/env python
"""
Script to produce a list of reference keys from a .bbl file created by bibtex.

The output is useful in combination with bibsearch.py.
(Pass the output to bibsearch.py to create a
custom database for a particular latex document. This avoids the
necessity of sending a huge bibtex database along with a manuscript
when submitting to a journal.)

:author: Dylan Schwilk
:contact: http://www.schwilk.org
:author: Alan G Isaac (small changes)
:copyright: 2006 by Dylan Schwilk
:license: MIT (see `license.txt`_)
:date: $Date: 2007-09-03 $

.. _`license.txt`: ../license.txt
"""
__docformat__ = "restructuredtext en"
__authors__  =    ["Dylan W. Schwilk", "Alan G. Isaac"]
__version__ = "1.5.4"
__needs__ = '2.7+'


###################  IMPORTS  ##################################################
#import from standard library
import sys
import logging

#configure logger
logging.basicConfig(format='\n%(levelname)s:\n%(message)s\n', stream=sys.stderr)
reflist_logger = logging.getLogger('bibstuff_logger')
################################################################################

def get_braces_contents(s):
    result = list()
    word = list()
    lvl = 0
    for c in s:
        if c == '}': lvl -= 1
        if lvl > 0:
            word.append(c)
        if c == '{': lvl += 1
        if lvl==0 and word:
            result.append(''.join(word))
            word = list()
    return result

def main():
    """Command-line tool"""
        
    from argparse import ArgumentParser
    _usage = """usage: %(prog)s FILE
    
    For example, to create a stripped down database
    for a particular latex document:
    python %(prog)s FILE.bbl | python bibsearch.py DB.bib -l > NEW_DB.bib
    """
    parser = ArgumentParser(usage=_usage)
    parser.add_argument('--version', action='version', version=__version__)

    parser.add_argument("-V", "--verbosity", action="store", dest="verbosity",
                      type=int, default=0,
                      help="Print {1:INFO,2:DEBUG} messages to stderr, default=%(default)s")
    parser.add_argument("bblFile", action="store")
       
    args = parser.parse_args()
    if 1 == args.verbosity:
        reflist_logger.setLevel(logging.INFO)
    if 2 == args.verbosity:
        reflist_logger.setLevel(logging.DEBUG)
    reflist_logger.info("Script running with bbl file=%s"%(args.bblFile))

    try :
        src = open(args.bblFile).read()
        reflist_logger.debug('successfully read %s'%args.bblFile)
    except :
        src = sys.stdin.read()

    items = src.split('\n\n')
    for i in items :
        i = i.strip()
        if (i.startswith('\\bibitem')) :
            i = i[8:].strip()
            if i[0] == '[':
                i = i[i.find(']') + 1:]
            print(get_braces_contents(i)[0])
        elif (i.startswith('\\harvarditem')) :
            print(get_braces_contents(i)[2])


if __name__ == '__main__':
    main()

