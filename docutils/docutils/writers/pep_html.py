#! /usr/bin/env python

"""
:Author: David Goodger
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

PEP HTML Writer.
"""

__docformat__ = 'reStructuredText'


import sys
#import random
from docutils import nodes, optik
from docutils.writers import html4css1


class Writer(html4css1.Writer):

    cmdline_options = html4css1.Writer.cmdline_options + (
        'PEP/HTML-Specific Options',
        None,
        (("Specify a PEP stylesheet file.  Default is --stylesheet's value.  "
          'If given, --pep-stylesheet overrides --stylesheet.',
          ['--pep-stylesheet'],
          {'metavar': '<file>'}),
         ('Specify a template file.  Default is "pep-html-template".',
          ['--pep-template'],
          {'default': 'pep-html-template', 'metavar': '<file>'}),
         ('Python\'s home URL.  Default is ".." (parent directory).',
          ['--python-home'],
          {'default': '..', 'metavar': '<URL>'}),
         ('Home URL prefix for PEPs.  Default is "." (current directory).',
          ['--pep-home'],
          {'default': '.', 'metavar': '<URL>'}),
         # Workaround for SourceForge's broken Python
         # (``import random`` causes a segfault).
         (optik.SUPPRESS_HELP,
          ['--no-random'], {'action': 'store_true'}),))

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTMLTranslator

    def translate(self):
        html4css1.Writer.translate(self)
        options = self.document.options
        template = open(options.pep_template).read()
        stylesheet = options.pep_stylesheet
        if stylesheet is None:
            stylesheet = options.stylesheet
        stylesheet = utils.relative_uri(options.destination, stylesheet)
        pyhome = options.python_home
        pephome = options.pep_home
        if pyhome == '..':
            pepindex = '.'
        else:
            pepindex = pyhome + '/peps/'
        index = self.document.first_child_matching_class(nodes.field_list)
        header = self.document[index]
        pep = header[0][1].astext()
        if options.no_random:
            banner = 0
        else:
            import random
            banner = random.randrange(64)
        try:
            pepnum = '%04i' % int(pep)
        except:
            pepnum = pep
        title = header[1][1].astext()
        body = ''.join(self.body)
        body_suffix = ''.join(self.body_suffix)
        self.output = template % locals()


class HTMLTranslator(html4css1.HTMLTranslator):

    def depart_field_list(self, node):
        html4css1.HTMLTranslator.depart_field_list(self, node)
        if node.hasattr('class') and node['class'] == 'rfc2822':
             self.body.append('<hr />\n')
