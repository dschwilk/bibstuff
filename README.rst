================================
     README: BibStuff
================================

:authors: Dylan W. Schwilk, Alan G. Isaac and others see AUTHORS
:source code: https://github.com/dschwilk/bibstuff

See LICENSE_, which must be included when this software is distributed and AUTHORS_ for contributors to the project.

This project contains the bibstuff python package which provides modules and classes for interacting with BibTeX style databases of citation references. The package contains classes for parsing and storing BibTeX files and for defining citation styles.

The project also includes command-line scripts for searching and labeling BibTeX entries and a utility for replacing in-text citations in a reStructured text document.

Installation
============

  1. clone repository::

       git clone https://github.com/dschwilk/bibstuff

  2. In the cloned directory run::

       python setup.py install

bibstuff module
===============

The module documentation is at http://dschwilk.github.io/bibstuff

Command-line tools (scripts)
============================
 
These tools are installed in you python scripts directory or they can
be run directly from where they were unpacked. Each of these tools has
a command line interface and provides the -h option to describe usage.

   * biblabel.py 
      Creates unique keys for entries bibtex database(s).  default keys
      look like Schwilk+Isaac:2006 or Smith+Johnson+etal:1999 Command
      line options allow you to change the default behavior.


   * bibsearch.py
      Search through a bibtex database for entries by key or by
      regular expression.  Results can be output as a (minimally)
      formatted reference, a full bibtex entry, or by key.  Note that
      bibsearch always takes a database by name (-f option or first
      argument) standard input is used for search terms.


   * bib4txt.py
      Creates formatted references for a text dodument.  (Useful for
      reStructuredText documents.) Interacts with a Bibtex style
      database file (without using LaTeX or bibtex).  The source text
      file should include citation references in reStructuredText
      format: a citation key enclosed in brackets, followed by an
      underscore.  Citation keys cannot be all digits.  The source
      document can be output with formatted citation references
      substituted.  In this case, the reference list is added to the
      end of the file.


   * bibname.py
      Create list of author/editor names for a bibtex database.
      Options allow you to specify a name template.  See the module
      documentation for details.

   * jabbrev.py
      Replaces all journal names in a bibtex file with alternative
      names (abbreviations).  The abbreviation file should be in the
      format: <ABBREVIATION> = <LONG_NAME> (see
      /examples/journal_names.txt).  I've also provides a short script
      in the /examples directory that will take the list of journal
      abbreviations at
      http://www.csa.com/htbin/sjldisp.cgi?filename=/wais/data/srcjnl/biologset
      and produce a format readable by jabbrev.py


   * reflist.py
      Creates a list of keys from a latex .bbl file.  This tool simply
      extracts reference keys from the bbl file.  This is useful for
      creating a bibtex database limited to those references which
      occur only in a single latex file.
      
      example: reflist.py my_doc.bbl | bibsearch.py -l my_db.bib > new_db.bib

Modules
=======

Package: bibstuff

Package: bibstuff/bibstyles

Testing
=======

Tests are located in /tests and use the unittest module. To run all tests::

  python -m unittest discover

Related Projects
================

For more information on BibTeX, see the excellent discussion in
chapter 13 section 4 of `The LaTeX Companion`_.

.. _AUTHORS: ./AUTHORS.rst

.. _LICENSE: ./license.txt

.. _`The LaTeX Companion`: http://www.awprofessional.com/bookstore/product.asp?isbn=0201362996&rl=1
