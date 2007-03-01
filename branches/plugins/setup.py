#!/usr/bin/env python
# $Id$
# Copyright: This file has been placed in the public domain.

import ez_setup
ez_setup.use_setuptools()

import sys
import os
import glob

from setuptools import setup, find_packages

#print find_packages('docutils')

# try:
#     from distutils.core import setup
#     #from distutils.command.build_py import build_py
#     #from distutils.command.install_data import install_data
# except ImportError:
#     print 'Error: The "distutils" standard module, which is required for the '
#     print 'installation of Docutils, could not be found.  You may need to '
#     print 'install a package called "python-devel" (or similar) on your '
#     print 'system using your package manager.'
#     sys.exit(1)


# class smart_install_data(install_data):

#     # Hack for Python > 2.3.
#     # From <http://wiki.python.org/moin/DistutilsInstallDataScattered>,
#     # by Pete Shinners.

#     def run(self):
#         #need to change self.install_dir to the library dir
#         install_cmd = self.get_finalized_command('install')
#         self.install_dir = getattr(install_cmd, 'install_lib')
#         return install_data.run(self)


def do_setup():
    kwargs = package_data.copy()
    kwargs['classifiers'] = classifiers
    # Install data files properly.
    #kwargs['cmdclass'] = {'install_data': smart_install_data}
    dist = setup(**kwargs)
    return dist

# s5_theme_files = []
# for dir in glob.glob('docutils/writers/s5_html/themes/*'):
#     if os.path.isdir(dir):
#         theme_files = glob.glob('%s/*' % dir)
#         s5_theme_files.append((dir, theme_files))

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
    #'package_dir': {'': ''},
    'packages': find_packages('.'),
    'include_package_data': True,
#     'packages': ['docutils',
#                  'docutils.languages',
#                  'docutils.parsers',
#                  'docutils.parsers.rst',
#                  'docutils.parsers.rst.directives',
#                  'docutils.parsers.rst.languages',
#                  'docutils.readers',
#                  'docutils.readers.python',
#                  'docutils.transforms',
#                  'docutils.writers',
#                  'docutils.writers.html4css1',
#                  'docutils.writers.pep_html',
#                  'docutils.writers.s5_html',
#                  'docutils.writers.latex2e',
#                  'docutils.writers.newlatex2e'],
#     'data_files': ([('docutils/parsers/rst/include',
#                      glob.glob('docutils/parsers/rst/include/*.txt')),
#                     ('docutils/writers/html4css1',
#                      ['docutils/writers/html4css1/html4css1.css',
#                       'docutils/writers/html4css1/template.txt']),
#                     ('docutils/writers/latex2e',
#                      ['docutils/writers/latex2e/latex2e.tex']),
#                     ('docutils/writers/newlatex2e',
#                      ['docutils/writers/newlatex2e/base.tex']),
#                     ('docutils/writers/pep_html',
#                      ['docutils/writers/pep_html/pep.css',
#                       'docutils/writers/pep_html/template.txt']),
#                     ('docutils/writers/s5_html/themes',
#                      ['docutils/writers/s5_html/themes/README.txt']),]
#                    + s5_theme_files),
    'scripts' : ['tools/rst2html.py',
                 'tools/rst2s5.py',
                 'tools/rst2latex.py',
                 'tools/rst2newlatex.py',
                 'tools/rst2xml.py',
                 'tools/rst2pseudoxml.py'],}
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
