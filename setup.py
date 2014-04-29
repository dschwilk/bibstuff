#!/usr/bin/env python

# bibstuff setup script
# Date: 2014-04-27

from os.path import join as pjoin
import glob

from distutils.core import setup
setup(name="bibstuff",
	version= __import__('bibstuff').__version__,
	description="Bibtex database utilities",
	author="Dylan W. Schwilk and Alan G. Isaac and others",
	author_email="dylan@schwilk.org",
	url = "https://github.com/dschwilk/bibstuff",
	license = "MIT",
	packages = ["bibstuff",
			"bibstuff.bibstyles"
		     ],
	package_data = {'bibstuff':
					[pjoin('data', '*'),
					pjoin('examples', '*'),
					 			    ]},
	scripts=glob.glob(pjoin('scripts', '*')))
