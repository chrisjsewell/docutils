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
from docutils import nodes, optik, utils
from docutils.writers import html4css1


class Writer(html4css1.Writer):

    cmdline_options = html4css1.Writer.cmdline_options + (
        'PEP/HTML-Specific Options',
        'The HTML --footnote-references option is set to "brackets" by '
        'default.',
        (('Specify a PEP stylesheet URL, used verbatim.  Default is '
          '--stylesheet\'s value.  If given, --pep-stylesheet overrides '
          '--stylesheet.',
          ['--pep-stylesheet'],
          {'metavar': '<URL>'}),
         ('Specify a PEP stylesheet file.  The path is interpreted relative '
          'to the output HTML file.  Overrides --pep-stylesheet.',
          ['--pep-stylesheet-path'],
          {'metavar': '<path>'}),
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

    option_default_overrides = {'footnote_references': 'brackets'}

    relative_path_options = ('pep_stylesheet_path', 'pep_template')

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = HTMLTranslator

    def translate(self):
        html4css1.Writer.translate(self)
        options = self.document.options
        template = open(options.pep_template).read()
        # Substitutions dict for template:
        subs = {}
        subs['encoding'] = options.output_encoding
        if options.pep_stylesheet_path:
            stylesheet = utils.relative_path(options._destination,
                                             options.pep_stylesheet_path)
        elif options.pep_stylesheet:
            stylesheet = options.pep_stylesheet
        elif options._stylesheet_path:
            stylesheet = utils.relative_path(options._destination,
                                             options.stylesheet_path)
        else:
            stylesheet = options.stylesheet
        subs['stylesheet'] = stylesheet
        pyhome = options.python_home
        subs['pyhome'] = pyhome
        subs['pephome'] = options.pep_home
        if pyhome == '..':
            subs['pepindex'] = '.'
        else:
            subs['pepindex'] = pyhome + '/peps/'
        index = self.document.first_child_matching_class(nodes.field_list)
        header = self.document[index]
        pepnum = header[0][1].astext()
        subs['pep'] = pepnum
        if options.no_random:
            subs['banner'] = 0
        else:
            import random
            subs['banner'] = random.randrange(64)
        try:
            subs['pepnum'] = '%04i' % int(pepnum)
        except:
            subs['pepnum'] = pepnum
        subs['title'] = header[1][1].astext()
        subs['body'] = ''.join(
            self.body_pre_docinfo + self.docinfo + self.body)
        subs['body_suffix'] = ''.join(self.body_suffix)
        self.output = template % subs


class HTMLTranslator(html4css1.HTMLTranslator):

    def depart_field_list(self, node):
        html4css1.HTMLTranslator.depart_field_list(self, node)
        if node.hasattr('class') and node['class'] == 'rfc2822':
             self.body.append('<hr />\n')
