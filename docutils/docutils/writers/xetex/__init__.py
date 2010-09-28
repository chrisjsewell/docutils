# .. coding: utf8
# :Author: Günter Milde <milde@users.berlios.de>
# :Revision: $Revision$
# :Date: $Date: 2005-06-28$
# :Copyright: © 2005, 2009 Günter Milde.
#             Released  without warranties or conditions of any kind
#             under the terms of the Apache License, Version 2.0
#             http://www.apache.org/licenses/LICENSE-2.0

"""
XeLaTeX document tree Writer.

A variant of Docutils' standard 'latex2e' writer producing output
suited for processing with XeLaTeX (http://tug.org/xetex/).
"""

__docformat__ = 'reStructuredText'

import os
import os.path
import re

import docutils
from docutils import frontend, nodes, utils, writers, languages
from docutils.writers import latex2e

class Writer(latex2e.Writer):
    """A writer for Unicode-based LaTeX variants (XeTeX, LuaTeX)"""

    supported = ('xetex','xelatex','luatex')
    """Formats this writer supports."""

    default_template = 'xelatex.tex'
    default_preamble = '\n'.join([
        r'% Linux Libertine (free, wide coverage, not only for Linux',
        r'\setmainfont{Linux Libertine O}',
        r'\setsansfont{Linux Biolinum O}',
        r'\setmonofont[HyphenChar=None]{DejaVu Sans Mono}',
    ])

    config_section = 'xetex writer'
    config_section_dependencies = ('writers', 'latex2e writer')

    settings_spec = frontend.filter_settings_spec(
        latex2e.Writer.settings_spec,
        'font_encoding',
        template=('Template file. Default: "%s".' % default_template,
          ['--template'], {'default': default_template, 'metavar': '<file>'}),
        latex_preamble=('Customization by LaTeX code in the preamble. '
          'Default: select PDF standard fonts (Times, Helvetica, Courier).',
          ['--latex-preamble'],
          {'default': default_preamble}),
        )

    def __init__(self):
        latex2e.Writer.__init__(self)
        self.settings_defaults.update({'fontencoding': ''}) # use default (EU1)
        self.translator_class = XeLaTeXTranslator


class Babel(latex2e.Babel):
    """Language specifics for XeTeX.

    Use `polyglossia` instead of `babel` and adapt settings.
    """
    language_codes = latex2e.Babel.language_codes.copy()
    # Additionally supported or differently named languages:
    language_codes.update({
        # code          Polyglossia-name       comment
        'cop':          'coptic',
        'de':           'german', # new spelling (de_1996)
        'de_1901':      'ogerman', # old spelling
        'dsb':          'lsorbian',
        'el_polyton':   'polygreek',
        'fa':           'farsi',
        'grc':          'ancientgreek',
        'hsb':          'usorbian',
        'sh-cyrl':      'serbian', # Serbo-Croatian, Cyrillic script
        'sh-latn':      'croatian', # Serbo-Croatian, Latin script
        'sq':           'albanian',
        'sr':           'serbian', # Cyrillic script (sr-cyrl)
        'th':           'thai',
        # zh-latn:      ???        #     Chinese Pinyin
        })
    # Languages without Polyglossia support:
    for key in ('af',           # 'afrikaans',
                'de_at',        # 'naustrian',
                'de_at_1901',   # 'austrian',
                'fr_ca',        # 'canadien',
                'grc_x_ibycus', # 'ibycus',   Ibycus encoding
                'sr-latn',      # 'serbian script=latin'
                'vi'):          # 'vietnam',
        del(language_codes[key])

    def __init__(self, language_code, reporter):
        self.language_code = language_code
        self.language = self.get_language(language_code)
        if self.language == '':
            reporter.warning('Language "%s" ' % self.language_code +
                'not supported by XeTeX (polyglossia), defaulting to "english".' )
        # don't use polyglossia for (american) English or unknown languages:
        if self.language in ('english', ''):
            self.setup = []
        else:
            self.setup = [r'\usepackage{polyglossia}',
                          r'\setdefaultlanguage{%s}' % self.language]
        self.quote_index = 0
        self.quotes = ('"', '"')
        # language dependent configuration:
        # double quotes are "active" in some languages (e.g. German).
        self.literal_double_quote = u'"' # TODO: use \textquotedbl

class XeLaTeXTranslator(latex2e.LaTeXTranslator):

    def __init__(self, document):
        latex2e.LaTeXTranslator.__init__(self, document, Babel)
        requirements = [r'\usepackage{ifthen}'] + self.babel.setup
        if self.latex_encoding != 'utf8':
            requirements.append(r'\XeTeXinputencoding %s '
                                % self.latex_encoding)
        self.requirements['_static'] = '\n'.join(requirements)

    # XeTeX does not know the length unit px
    # Use \pdfpxdimen, the macro to set the value of 1 px in pdftex
    # this way, configuring works the same for pdftex and xetex.
    def to_latex_length(self, length_str, px=r'\pdfpxdimen'):
        """Convert string with rst lenght to LaTeX length"""
        return latex2e.LaTeXTranslator.to_latex_length(self, length_str, px)

    # Simpler variant of encode, as XeTeX understands utf8 Unicode:
    def encode(self, text):
        """Return text with 'problematic' characters escaped.

        Escape the ten special printing characters ``# $ % & ~ _ ^ \ { }``,
        square brackets ``[ ]``, double quotes and (in OT1) ``< | >``.
        """
        if self.verbatim:
            return text
        # LaTeX encoding maps:
        special_chars = {
            ord('#'): ur'\#',
            ord('$'): ur'\$',
            ord('%'): ur'\%',
            ord('&'): ur'\&',
            ord('~'): ur'\textasciitilde{}',
            ord('_'): ur'\_',
            ord('^'): ur'\textasciicircum{}',
            ord('\\'): ur'\textbackslash{}',
            ord('{'): ur'\{',
            ord('}'): ur'\}',
        # Square brackets are ordinary chars and cannot be escaped with '\',
        # so we put them in a group '{[}'. (Alternative: ensure that all
        # macros with optional arguments are terminated with {} and text
        # inside any optional argument is put in a group ``[{text}]``).
        # Commands with optional args inside an optional arg must be put
        # in a group, e.g. ``\item[{\hyperref[label]{text}}]``.
            ord('['): ur'{[}',
            ord(']'): ur'{]}'
        }
        # Unicode chars that are not properly handled by XeTeX
        unsupported_unicode_chars = {
            0x00AD: ur'\-', # SOFT HYPHEN
        }
        # set up the translation table:
        table = special_chars
        # keep the underscore in citation references
        if self.inside_citation_reference_label:
            del(table[ord('_')])
        if self.insert_non_breaking_blanks:
            table[ord(' ')] = ur'~'
        if self.literal:
            # double quotes are 'active' in some languages
            table[ord('"')] = self.babel.literal_double_quote
        else:
            text = self.babel.quote_quotes(text)
        # Unicode chars:
        table.update(unsupported_unicode_chars)

        text = text.translate(table)

        # Literal line breaks (in address or literal blocks):
        if self.insert_newline:
            # for blank lines, insert a protected space, to avoid
            # ! LaTeX Error: There's no line here to end.
            textlines = [line + '~'*(not line.lstrip())
                         for line in text.split('\n')]
            text = '\\\\\n'.join(textlines)
        if self.literal and not self.insert_non_breaking_blanks:
            # preserve runs of spaces but allow wrapping
            text = text.replace('  ', ' ~')
        return text
