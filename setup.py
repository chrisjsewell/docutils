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
    'install_requires': 'setuptools>=0.6c5',
    'packages': find_packages(),
    'include_package_data': True,
    'scripts' : ['tools/rst2html.py',
                 'tools/rst2s5.py',
                 'tools/rst2latex.py',
                 'tools/rst2newlatex.py',
                 'tools/rst2xml.py',
                 'tools/rst2pseudoxml.py'],
    'entry_points': {
        'docutils.readers':
        ['doctree = docutils.readers.doctree:Reader',
         'pep = docutils.readers.pep:Reader',
         'python = docutils.readers.python:Reader',
         'standalone = docutils.readers.standalone:Reader'],
        'docutils.parsers':
        ['null = docutils.parsers.null:Parser',
         'rst = docutils.parsers.rst:Parser',
         'restructuredtext = docutils.parsers.rst:Parser',
         'rest = docutils.parsers.rst:Parser',
         'rstx = docutils.parsers.rst:Parser',
         'rtxt = docutils.parsers.rst:Parser'],
        'docutils.writers':
        ['docutils_xml = docutils.writers.docutils_xml:Writer',
         'html = docutils.writers.html4css1:Writer',
         'html4css1 = docutils.writers.html4css1:Writer',
         'latex = docutils.writers.latex2e:Writer',
         'latex2e = docutils.writers.latex2e:Writer',
         'newlatex2e = docutils.writers.newlatex2e:Writer',
         'null = docutils.writers.null:Writer',
         'pep_html = docutils.writers.pep_html:Writer',
         'pformat = docutils.writers.pseudoxml:Writer',
         'pprint = docutils.writers.pseudoxml:Writer',
         'pseudoxml = docutils.writers.pseudoxml:Writer',
         's5 = docutils.writers.s5_html:Writer',
         's5_html = docutils.writers.s5_html:Writer',
         'xml = docutils.writers.docutils_xml:Writer'],
        'docutils.parsers.rst.directives':
        ['attention = docutils.parsers.rst.directives.admonitions:Attention',
         'caution = docutils.parsers.rst.directives.admonitions:Caution',
         'danger = docutils.parsers.rst.directives.admonitions:Danger',
         'error = docutils.parsers.rst.directives.admonitions:Error',
         'important = docutils.parsers.rst.directives.admonitions:Important',
         'note = docutils.parsers.rst.directives.admonitions:Note',
         'tip = docutils.parsers.rst.directives.admonitions:Tip',
         'hint = docutils.parsers.rst.directives.admonitions:Hint',
         'warning = docutils.parsers.rst.directives.admonitions:Warning',
         'admonition = docutils.parsers.rst.directives.admonitions:Admonition',
         'sidebar = docutils.parsers.rst.directives.body:Sidebar',
         'topic = docutils.parsers.rst.directives.body:Topic',
         'line-block = docutils.parsers.rst.directives.body:LineBlock',
         'parsed-literal = docutils.parsers.rst.directives.body:ParsedLiteral',
         'rubric = docutils.parsers.rst.directives.body:Rubric',
         'epigraph = docutils.parsers.rst.directives.body:Epigraph',
         'highlights = docutils.parsers.rst.directives.body:Highlights',
         'pull-quote = docutils.parsers.rst.directives.body:PullQuote',
         'compound = docutils.parsers.rst.directives.body:Compound',
         'container = docutils.parsers.rst.directives.body:Container',
         #'questions = docutils.parsers.rst.directives.body:question_list',
         'table = docutils.parsers.rst.directives.tables:RSTTable',
         'csv-table = docutils.parsers.rst.directives.tables:CSVTable',
         'list-table = docutils.parsers.rst.directives.tables:ListTable',
         'image = docutils.parsers.rst.directives.images:Image',
         'figure = docutils.parsers.rst.directives.images:Figure',
         'contents = docutils.parsers.rst.directives.parts:Contents',
         'sectnum = docutils.parsers.rst.directives.parts:Sectnum',
         'header = docutils.parsers.rst.directives.parts:Header',
         'footer = docutils.parsers.rst.directives.parts:Footer',
         #'footnotes = docutils.parsers.rst.directives.parts:footnotes',
         #'citations = docutils.parsers.rst.directives.parts:citations',
         'target-notes = docutils.parsers.rst.directives.references:TargetNotes',
         'meta = docutils.parsers.rst.directives.html:Meta',
         #'imagemap = docutils.parsers.rst.directives.html:imagemap',
         'raw = docutils.parsers.rst.directives.misc:Raw',
         'include = docutils.parsers.rst.directives.misc:Include',
         'replace = docutils.parsers.rst.directives.misc:Replace',
         'unicode = docutils.parsers.rst.directives.misc:Unicode',
         'class = docutils.parsers.rst.directives.misc:Class',
         'role = docutils.parsers.rst.directives.misc:Role',
         'default-role = docutils.parsers.rst.directives.misc:DefaultRole',
         'title = docutils.parsers.rst.directives.misc:Title',
         'date = docutils.parsers.rst.directives.misc:Date',
         'restructuredtext-test-directive = docutils.parsers.rst.directives.misc:TestDirective'],
        'docutils.parsers.rst.roles':
        ['abbreviation = docutils.parsers.rst.roles:abbreviation',
         'acronym = docutils.parsers.rst.roles:acronym',
         'emphasis = docutils.parsers.rst.roles:emphasis',
         'literal = docutils.parsers.rst.roles:literal',
         'strong = docutils.parsers.rst.roles:strong',
         'subscript = docutils.parsers.rst.roles:subscript',
         'superscript = docutils.parsers.rst.roles:superscript',
         'title-reference = docutils.parsers.rst.roles:title_reference',
         'pep-reference = docutils.parsers.rst.roles:pep_reference_role',
         'rfc-reference = docutils.parsers.rst.roles:rfc_reference_role',
         'raw = docutils.parsers.rst.roles:raw_role',
         'index = docutils.parsers.rst.roles:unimplemented_role',
         'named-reference = docutils.parsers.rst.roles:unimplemented_role',
         'anonymous-reference = docutils.parsers.rst.roles:unimplemented_role',
         'uri-reference = docutils.parsers.rst.roles:unimplemented_role',
         'footnote-reference = docutils.parsers.rst.roles:unimplemented_role',
         'citation-reference = docutils.parsers.rst.roles:unimplemented_role',
         'substitution-reference = docutils.parsers.rst.roles:unimplemented_role',
         'target = docutils.parsers.rst.roles:unimplemented_role',
         'restructuredtext-unimplemented-role = docutils.parsers.rst.roles:unimplemented_role'],
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
