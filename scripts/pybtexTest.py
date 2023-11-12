#see https://bitbucket.org/pybtex-devs/pybtex/src/master/pybtex/database/input/bibtex.py
import pybtex
import pybtex.errors
pybtex.errors.set_strict_mode(False)
print(dir(pybtex))
from pybtex.database.input.bibtex import Parser
from pybtex.database import Person
bibdata = Parser().parse_file(filename="./examples/example.bib")

test = bibdata.entries["vanWilgen:1910"]
print(f"{test} has type {type(test)}")
print(test.persons)
print(test.persons["author"][0])
print(test.persons.get("editor"))

bibdata = Parser().parse_file(filename="C:/Users/aisaac/git/econpy/text/tex/ejabbr.bib")
print(f"{type(bibdata)}: {bibdata}")
print(dir(bibdata))
# entries is a dict that is case-insenstive for keys
for k,v in bibdata.entries.items():
    print(f"{k}: {v}")

me = Person('Alan G. Isaac')
print(dir(me))
print(f"{me} = {me.first_names} + {me.middle_names}")

