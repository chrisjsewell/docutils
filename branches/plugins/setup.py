#!/usr/bin/env python
# $Id$
# Copyright: This file has been placed in the public domain.

import ez_setup
ez_setup.use_setuptools()

import sys
import os
import glob

from setuptools import setup, find_packages


def do_setup():
    kwargs = package_data.copy()
    kwargs['classifiers'] = classifiers
    dist = setup(**kwargs)
    return dist

package_data = {
    'name': 'docutils',
    'description': 'Docutils -- Python Documentation Utilities',
    'long_description': """\
Docutils is a modular system for processing documentation
into useful formats, such as HTML, XML, and LaTeX.  For
input Docutils supports reStructuredText, an easy-to-read,
what-you-see-is-what-you-get plaintext markup syntax.""", # wrap at col 60
    'url': 'http://docutils.sourceforge.net/',
    'version': '0.5',
    'author': 'David Goodger',
    'author_email': 'goodger@python.org',
    'license': 'public domain, Python, BSD, GPL (see COPYING.txt)',
    'platforms': 'OS-independent',
    'packages': find_packages(),
    'include_package_data': True,
    'scripts' : ['tools/rst2html.py',
                 'tools/rst2s5.py',
                 'tools/rst2latex.py',
                 'tools/rst2newlatex.py',
                 'tools/rst2xml.py',
                 'tools/rst2pseudoxml.py'],
    'entry_points': {
        'docutils.writers': ['docutils_xml = docutils.writers.docutils_xml',
                             'html4css1 = docutils.writers.html4css1',
                             'latex2e = docutils.writers.latex2e',
                             'newlatex2e = docutils.writers.newlatex2e',
                             'null = docutils.writers.null',
                             'pseudoxml = docutils.writers.pseudoxml',
                             's5_html = docutils.writers.s5_html'],
        }
    }
"""Setup parameters."""

classifiers = [
    'Development Status :: 3 - Alpha',
    'Environment :: Console',
    'Intended Audience :: End Users/Desktop',
    'Intended Audience :: Other Audience',
    'Intended Audience :: Developers',
    'Intended Audience :: System Administrators',
    'License :: Public Domain',
    'License :: OSI Approved :: Python Software Foundation License',
    'License :: OSI Approved :: BSD License',
    'License :: OSI Approved :: GNU General Public License (GPL)',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Topic :: Documentation',
    'Topic :: Software Development :: Documentation',
    'Topic :: Text Processing',
    'Natural Language :: English',      # main/default language, keep first
    'Natural Language :: Afrikaans',
    'Natural Language :: Esperanto',
    'Natural Language :: French',
    'Natural Language :: German',
    'Natural Language :: Italian',
    'Natural Language :: Russian',
    'Natural Language :: Slovak',
    'Natural Language :: Spanish',
    'Natural Language :: Swedish',]
"""Trove classifiers for the "register" command."""


if __name__ == '__main__' :
    do_setup()
