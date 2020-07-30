#use with python35
import sys
sys.path.insert(0, 'C:/Users/aisaac/git/python-bibtexparser')
import bibtexparser
fin = r'C:\Users\aisaac\svn\aisaac\localtexmf\bibtex\bib\misc\alan.bib'
with open(fin) as bibfile:
    bibtex_database = bibtexparser.bparser.BibTexParser(common_strings=True).parse_file(bibfile)
    #bibtex_database = bibtexparser.load(parsedEntries)
    for (i,item) in enumerate(bibtex_database.entries):
        if (i < 10):
            print(item)
