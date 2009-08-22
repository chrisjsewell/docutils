# $Id$
# Author: Engelbert Gruber <grubert@users.sourceforge.net>
# Copyright: This module has been placed in the public domain.

"""LaTeX2e document tree Writer."""

__docformat__ = 'reStructuredText'

# code contributions from several people included, thanks to all.
# some named: David Abrahams, Julien Letessier, Lele Gaifax, and others.
#
# convention deactivate code by two # i.e. ##.

import sys
import os
import time
import re
import string
from docutils import frontend, nodes, languages, writers, utils, transforms
from docutils.writers.newlatex2e import unicode_map

class Writer(writers.Writer):

    supported = ('latex','latex2e')
    """Formats this writer supports."""

    settings_spec = (
        'LaTeX-Specific Options',
        'The LaTeX "--output-encoding" default is "latin-1:strict".',
        (('Specify documentclass.  Default is "article".',
          ['--documentclass'],
          {'default': 'article', }),
         ('Specify document options.  Multiple options can be given, '
          'separated by commas.  Default is "a4paper".',
          ['--documentoptions'],
          {'default': 'a4paper', }),
         ('Use LaTeX footnotes (currently supports only numbered footnotes). '
          'Default: no, uses figures.',
          ['--use-latex-footnotes'],
          {'default': 0, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Format for footnote references: one of "superscript" or '
          '"brackets".  Default is "superscript".',
          ['--footnote-references'],
          {'choices': ['superscript', 'brackets'], 'default': 'superscript',
           'metavar': '<format>',
           'overrides': 'trim_footnote_reference_space'}),
         ('Use LaTeX citations. '
          'Default: no, uses figures which might get mixed with images.',
          ['--use-latex-citations'],
          {'default': 0, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Format for block quote attributions: one of "dash" (em-dash '
          'prefix), "parentheses"/"parens", or "none".  Default is "dash".',
          ['--attribution'],
          {'choices': ['dash', 'parentheses', 'parens', 'none'],
           'default': 'dash', 'metavar': '<format>'}),
        ('Specify LaTeX packages/stylesheets. '
         ' A style is referenced with \\usepackage if extension is '
         '".sty" or omitted and with \\input else. '
          ' Overrides previous --stylesheet and --stylesheet-path settings.',
          ['--stylesheet'],
          {'default': '', 'metavar': '<file>',
           'overrides': 'stylesheet_path'}),
         ('Like --stylesheet, but a relative path is converted from relative '
          'to the current working directory to relative to the output file. ',
          ['--stylesheet-path'],
          {'metavar': '<file>', 'overrides': 'stylesheet'}),
         ('Embed the stylesheet in the output LaTeX file.  The stylesheet '
          'file must be accessible during processing. '
          ' Default: link to stylesheets',
          ['--embed-stylesheet'],
          {'default': 0, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Link to the stylesheet(s) in the output file. '
          ' This is the default (if not changed in a config file).',
          ['--link-stylesheet'],
          {'dest': 'embed_stylesheet', 'action': 'store_false'}),
         ('Table of contents by Docutils (default) or LaTeX. '
          '(Docutils does not know of pagenumbers.) ',
          ['--use-latex-toc'],
          {'default': 0, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Add parts on top of the section hierarchy.',
          ['--use-part-section'],
          {'default': 0, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Enclose titlepage in LaTeX titlepage environment.',
          ['--use-titlepage-env'],
          {'default': 0, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Let LaTeX print author and date, do not show it in docutils '
          'document info.',
          ['--use-latex-docinfo'],
          {'default': 0, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ("Use LaTeX abstract environment for the document's abstract. "
          'Per default the abstract is an unnumbered section.',
          ['--use-latex-abstract'],
          {'default': 0, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Color of any hyperlinks embedded in text '
          '(default: "blue", "0" to disable).',
          ['--hyperlink-color'], {'default': 'blue'}),
         ('Enable compound enumerators for nested enumerated lists '
          '(e.g. "1.2.a.ii").  Default: disabled.',
          ['--compound-enumerators'],
          {'default': None, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Disable compound enumerators for nested enumerated lists. '
          'This is the default.',
          ['--no-compound-enumerators'],
          {'action': 'store_false', 'dest': 'compound_enumerators'}),
         ('Enable section ("." subsection ...) prefixes for compound '
          'enumerators.  This has no effect without --compound-enumerators.'
          'Default: disabled.',
          ['--section-prefix-for-enumerators'],
          {'default': None, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Disable section prefixes for compound enumerators.  '
          'This is the default.',
          ['--no-section-prefix-for-enumerators'],
          {'action': 'store_false', 'dest': 'section_prefix_for_enumerators'}),
         ('Set the separator between section number and enumerator '
          'for compound enumerated lists.  Default is "-".',
          ['--section-enumerator-separator'],
          {'default': '-', 'metavar': '<char>'}),
         ('When possibile, use the specified environment for literal-blocks. '
          'Default is quoting of whitespace and special chars.',
          ['--literal-block-env'],
          {'default': ''}),
         ('When possibile, use verbatim for literal-blocks. '
          'Compatibility alias for "--literal-block-env=verbatim".',
          ['--use-verbatim-when-possible'],
          {'default': 0, 'action': 'store_true',
           'validator': frontend.validate_boolean}),
         ('Table style. "standard" with horizontal and vertical lines, '
          '"booktabs" (LaTeX booktabs style) only horizontal lines '
          'above and below the table and below the header or "nolines".  '
          'Default: "standard"',
          ['--table-style'],
          {'choices': ['standard', 'booktabs','nolines'],
           'default': 'standard',
           'metavar': '<format>'}),
         ('LaTeX graphicx package option. '
          'Possible values are "dvips", "pdftex". "auto" includes LaTeX code '
          'to use "pdftex" if processing with pdf(la)tex and dvips otherwise. '
          'Default is no option.',
          ['--graphicx-option'],
          {'default': ''}),
         ('LaTeX font encoding. '
          'Possible values are "", "T1", "OT1", "LGR,T1" or any other '
          'combination of options to the `fontenc` package. '
          'Default is "" which does not load `fontenc`.',
          ['--font-encoding'],
          {'default': ''}),
         ('Per default the latex-writer puts the reference title into '
          'hyperreferences. Specify "ref*" or "pageref*" to get the section '
          'number or the page number.',
          ['--reference-label'],
          {'default': None, }),
         ('Specify style and database for bibtex, for example '
          '"--use-bibtex=mystyle,mydb1,mydb2".',
          ['--use-bibtex'],
          {'default': None, }),
          ),)

    settings_defaults = {'output_encoding': 'latin-1',
                         'sectnum_depth': 0 # updated by SectNum transform
                        }

    relative_path_settings = ('stylesheet_path',)

    config_section = 'latex2e writer'
    config_section_dependencies = ('writers',)

    visitor_attributes = ('head_prefix', 'stylesheet', 'head',
                          'body_prefix', 'body', 'body_suffix')

    output = None
    """Final translated form of `document`."""

    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = LaTeXTranslator

    # Override parent method to add latex-specific transforms
    ## def get_transforms(self):
    ##    # call the parent class' method
    ##    transforms = writers.Writer.get_transforms(self)
    ##    # print transforms
    ##    # TODO: footnote collection transform
    ##    # transforms.append(footnotes.collect)
    ##    return transforms

    def translate(self):
        visitor = self.translator_class(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()
        # copy parts
        for attr in self.visitor_attributes:
            setattr(self, attr, getattr(visitor, attr))

    def assemble_parts(self):
        writers.Writer.assemble_parts(self)
        for part in self.visitor_attributes:
            if part.startswith('body'):
                # body contains inline elements, so join without newline
                self.parts[part] = ''.join(getattr(self, part))
            else:
                self.parts[part] = '\n'.join(getattr(self, part))


class Babel(object):
    """Language specifics for LaTeX."""
    # country code by a.schlock.
    # partly manually converted from iso and babel stuff, dialects and some
    _ISO639_TO_BABEL = {
        'no': 'norsk',     #XXX added by hand ( forget about nynorsk?)
        'gd': 'scottish',  #XXX added by hand
        'hu': 'magyar',    #XXX added by hand
        'pt': 'portuguese',#XXX added by hand
        'sl': 'slovenian',
        'af': 'afrikaans',
        'bg': 'bulgarian',
        'br': 'breton',
        'ca': 'catalan',
        'cs': 'czech',
        'cy': 'welsh',
        'da': 'danish',
        'fr': 'french',
        # french, francais, canadien, acadian
        'de': 'ngerman',  #XXX rather than german
        # ngerman, naustrian, german, germanb, austrian
        'el': 'greek',
        'en': 'english',
        # english, USenglish, american, UKenglish, british, canadian
        'eo': 'esperanto',
        'es': 'spanish',
        'et': 'estonian',
        'eu': 'basque',
        'fi': 'finnish',
        'ga': 'irish',
        'gl': 'galician',
        'he': 'hebrew',
        'hr': 'croatian',
        'hu': 'hungarian',
        'is': 'icelandic',
        'it': 'italian',
        'la': 'latin',
        'nl': 'dutch',
        'pl': 'polish',
        'pt': 'portuguese',
        'ro': 'romanian',
        'ru': 'russian',
        'sk': 'slovak',
        'sr': 'serbian',
        'sv': 'swedish',
        'tr': 'turkish',
        'uk': 'ukrainian'
    }

    def __init__(self, lang):
        self.language = lang
        self.quote_index = 0
        self.quotes = ('``', "''")
        self.setup = '' # language dependent configuration code
        # double quotes are "active" in some languages (e.g. German).
        # TODO: use \textquotedbl in OT1 font encoding?
        self.literal_double_quote = '"'
        if self.language.startswith('de'):
            self.quotes = ('{\\glqq}', '\\grqq{}')
            self.literal_double_quote = '\\dq{}'
        if self.language.startswith('it'):
            self.literal_double_quote = r'{\char`\"}'
        if self.language.startswith('es'):
            # reset tilde ~ to the original binding (nobreakspace):
            self.setup = ('\n'
                  r'\addto\shorthandsspanish{\spanishdeactivate{."~<>}}')

    def next_quote(self):
        q = self.quotes[self.quote_index]
        self.quote_index = (self.quote_index+1) % 2
        return q

    def quote_quotes(self,text):
        t = None
        for part in text.split('"'):
            if t == None:
                t = part
            else:
                t += self.next_quote() + part
        return t

    def get_language(self):
        lang = self.language.split('_')[0]  # filter dialects
        return self._ISO639_TO_BABEL.get(lang, "")

# Building blocks for the latex preamble
# --------------------------------------

class SortableDict(dict):
    """Dictionary with additional sorting methods"""

    def sortedkeys(self):
        """Return sorted list of keys"""
        keys = self.keys()
        keys.sort()
        return keys

    def sortedvalues(self):
        """Return list of values sorted by keys"""
        return [self[key] for key in self.sortedkeys()]


# PreambleCmds
# `````````````
# A container for LaTeX code snippets that can be
# inserted into the preamble if required in the document.
#
# .. The package 'makecmds' would enable shorter definitions using the
#    \providelength and \provideenvironment commands.
#    However, it is pretty non-standard (texlive-latex-extra).

class PreambleCmds(object):
    """Building blocks for the latex preamble."""

PreambleCmds.abstract = r"""
% abstract title
\providecommand*{\DUtitleabstract}[1]{\centerline{\textbf{#1}}}"""

PreambleCmds.admonition = r"""
% admonition (specially marked topic)
\providecommand{\DUadmonition}[2][class-arg]{%
  % try \DUadmonition#1{#2}:
  \ifcsname DUadmonition#1\endcsname%
    \csname DUadmonition#1\endcsname{#2}%
  \else
    \begin{center}
      \fbox{\parbox{0.9\textwidth}{#2}}
    \end{center}
  \fi
}"""

## PreambleCmds.caption = r"""% configure caption layout
## \usepackage{caption}
## \captionsetup{singlelinecheck=false}% no exceptions for one-liners"""

PreambleCmds.color = r"""\usepackage{color}"""

PreambleCmds.docinfo = r"""
% docinfo (width of docinfo table)
\DUprovidelength{\DUdocinfowidth}{0.9\textwidth}"""
# PreambleCmds.docinfo._requirements = 'providelength'

PreambleCmds.embedded_package_wrapper = r"""\makeatletter
%% embedded stylesheet: %s
%s
\makeatother"""

PreambleCmds.dedication = r"""
% dedication topic
\providecommand{\DUtopicdedication}[1]{\begin{center}#1\end{center}}"""

PreambleCmds.error = r"""
% error admonition title
\providecommand*{\DUtitleerror}[1]{\DUtitle{\color{red}#1}}"""
# PreambleCmds.errortitle._requirements = 'color'

PreambleCmds.fieldlist = r"""
% fieldlist environment
\ifthenelse{\isundefined{\DUfieldlist}}{
  \newenvironment{DUfieldlist}%
    {\quote\description}
    {\enddescription\endquote}
}{}"""

PreambleCmds.float_settings = r"""\usepackage{float} % float configuration
\floatplacement{figure}{H} % place figures here definitely"""

PreambleCmds.footnote_floats = r"""% settings for footnotes as floats:
\setlength{\floatsep}{0.5em}
\setlength{\textfloatsep}{\fill}
\addtolength{\textfloatsep}{3em}
\renewcommand{\textfraction}{0.5}
\renewcommand{\topfraction}{0.5}
\renewcommand{\bottomfraction}{0.5}
\setcounter{totalnumber}{50}
\setcounter{topnumber}{50}
\setcounter{bottomnumber}{50}"""

PreambleCmds.graphicx_auto = r"""% Check output format
\ifx\pdftexversion\undefined
  \usepackage{graphicx}
\else
  \usepackage[pdftex]{graphicx}
\fi'))"""


PreambleCmds.inline = r"""
% inline markup (custom roles)
% \DUrole{#1}{#2} tries \DUrole#1{#2}
\providecommand*{\DUrole}[2]{%
  \ifcsname DUrole#1\endcsname%
    \csname DUrole#1\endcsname{#2}%
  \else% backwards compatibility: try \docutilsrole#1{#2}
    \ifcsname docutilsrole#1\endcsname%
      \csname docutilsrole#1\endcsname{#2}%
    \else%
      #2%
    \fi%
  \fi%
}"""

PreambleCmds.legend = r"""
% legend environment
\ifthenelse{\isundefined{\DUlegend}}{
  \newenvironment{DUlegend}{\small}{}
}{}"""

PreambleCmds.lineblock = r"""
% lineblock environment
\DUprovidelength{\DUlineblockindent}{2.5em}
\ifthenelse{\isundefined{\DUlineblock}}{
  \newenvironment{DUlineblock}[1]{%
    \list{}{\setlength{\partopsep}{\parskip}
            \addtolength{\partopsep}{\baselineskip}
            \setlength{\topsep}{0pt}
            \setlength{\itemsep}{0.15\baselineskip}
            \setlength{\parsep}{0pt}
            \setlength{\leftmargin}{#1}}
    \raggedright
  }
  {\endlist}
}{}"""
# PreambleCmds.lineblock._requirements = 'providelength'

PreambleCmds.linking = r"""
%% hyperref package (PDF hyperlinks):
\ifthenelse{\isundefined{\hypersetup}}{
  \usepackage[colorlinks=%s,linkcolor=%s,urlcolor=%s]{hyperref}
}{}"""

PreambleCmds.minitoc = r"""%% local table of contents
\usepackage{minitoc}"""

PreambleCmds.optionlist = r"""
% optionlist environment
\providecommand*{\DUoptionlistlabel}[1]{\bf #1 \hfill}
\DUprovidelength{\DUoptionlistindent}{3cm}
\ifthenelse{\isundefined{\DUoptionlist}}{
  \newenvironment{DUoptionlist}{%
    \list{}{\setlength{\labelwidth}{\DUoptionlistindent}
            \setlength{\rightmargin}{1cm}
            \setlength{\leftmargin}{\rightmargin}
            \addtolength{\leftmargin}{\labelwidth}
            \addtolength{\leftmargin}{\labelsep}
            \renewcommand{\makelabel}{\DUoptionlistlabel}}
  }
  {\endlist}
}{}"""
# PreambleCmds.optionlist._requirements = 'providelength'

PreambleCmds.providelength = r"""
% providelength (provide a length variable and set default, if it is new)
\providecommand*{\DUprovidelength}[2]{
  \ifthenelse{\isundefined{#1}}{\newlength{#1}\setlength{#1}{#2}}{}
}"""

PreambleCmds.rubric = r"""
% rubric (informal heading)
\providecommand*{\DUrubric}[2][class-arg]{%
  \subsubsection*{\centering\textit{\textmd{#2}}}}"""

PreambleCmds.sidebar = r"""
% sidebar (text outside the main text flow)
\providecommand{\DUsidebar}[2][class-arg]{%
  \begin{center}
    \colorbox[gray]{0.80}{\parbox{0.9\textwidth}{#2}}
  \end{center}
}"""

PreambleCmds.subtitle = r"""
% subtitle (for topic/sidebar)
\providecommand*{\DUsubtitle}[2][class-arg]{\par\emph{#2}\smallskip}"""

PreambleCmds.table = r"""\usepackage{longtable}
\usepackage{array}
\setlength{\extrarowheight}{2pt}
\newlength{\DUtablewidth} % internal use in tables"""

PreambleCmds.documenttitle = r"""
%%%%%% Title metadata
\title{%s}
\author{%s}
\date{%s}"""

PreambleCmds.titlereference = r"""
% titlereference role
\providecommand*{\DUroletitlereference}[1]{\textsl{#1}}"""

PreambleCmds.title = r"""
% title for topics, admonitions and sidebar
\providecommand*{\DUtitle}[2][class-arg]{%
  % call \DUtitle#1{#2} if it exists:
  \ifcsname DUtitle#1\endcsname%
    \csname DUtitle#1\endcsname{#2}%
  \else
    \smallskip\noindent\textbf{#2}\smallskip%
  \fi
}"""

PreambleCmds.topic = r"""
% topic (quote with heading)
\providecommand{\DUtopic}[2][class-arg]{%
  \ifcsname DUtopic#1\endcsname%
    \csname DUtopic#1\endcsname{#2}%
  \else
    \begin{quote}#2\end{quote}
  \fi
}"""

PreambleCmds.transition = r"""
% transition (break, fancybreak, anonymous section)
\providecommand*{\DUtransition}[1][class-arg]{%
  \hspace*{\fill}\hrulefill\hspace*{\fill}
  \vskip 0.5\baselineskip
}"""


class DocumentClass(object):
    """Details of a LaTeX document class."""

    def __init__(self, document_class, with_part=False):
        self.document_class = document_class
        self._with_part = with_part
        self.sections = ['section', 'subsection', 'subsubsection',
                         'paragraph', 'subparagraph']
        if self.document_class in ('book', 'memoir', 'report',
                                   'scrbook', 'scrreprt'):
            self.sections.insert(0, 'chapter')
        if self._with_part:
            self.sections.insert(0, 'part')

    def section(self, level):
        """Return the LaTeX section name for section `level`.

        The name depends on the specific document class.
        Level is 1,2,3..., as level 0 is the title.
        """

        if level <= len(self.sections):
            return self.sections[level-1]
        else:
            return self.sections[-1]


class Table(object):
    """Manage a table while traversing.

    Maybe change to a mixin defining the visit/departs, but then
    class Table internal variables are in the Translator.

    Table style might be

    :standard: horizontal and vertical lines
    :booktabs: only horizontal lines (requires "booktabs" LaTeX package)
    :nolines: (or borderless) no lines
    """
    def __init__(self,translator,latex_type,table_style):
        self._translator = translator
        self._latex_type = latex_type
        self._table_style = table_style
        self._open = 0
        # miscellaneous attributes
        self._attrs = {}
        self._col_width = []
        self._rowspan = []
        self.stubs = []
        self._in_thead = 0

    def open(self):
        self._open = 1
        self._col_specs = []
        self.caption = None
        self._attrs = {}
        self._in_head = 0 # maybe context with search
    def close(self):
        self._open = 0
        self._col_specs = None
        self.caption = None
        self._attrs = {}
        self.stubs = []
    def is_open(self):
        return self._open

    def set_table_style(self, table_style):
        if not table_style in ('standard','booktabs','borderless','nolines'):
            return
        self._table_style = table_style

    def get_latex_type(self):
        return self._latex_type

    def set(self,attr,value):
        self._attrs[attr] = value
    def get(self,attr):
        if attr in self._attrs:
            return self._attrs[attr]
        return None

    def get_vertical_bar(self):
        if self._table_style == 'standard':
            return '|'
        return ''

    # horizontal lines are drawn below a row,
    def get_opening(self):
        if self._latex_type == 'longtable':
            # otherwise longtable might move before paragraph and subparagraph
            prefix = '\\leavevmode\n'
        else:
            prefix = ''
        prefix += '\setlength{\DUtablewidth}{\linewidth}'
        return '%s\n\\begin{%s}[c]' % (prefix, self._latex_type)

    def get_closing(self):
        line = ''
        if self._table_style == 'booktabs':
            line = '\\bottomrule\n'
        elif self._table_style == 'standard':
            lines = '\\hline\n'
        return '%s\\end{%s}' % (line,self._latex_type)

    def visit_colspec(self, node):
        self._col_specs.append(node)
        # "stubs" list is an attribute of the tgroup element:
        self.stubs.append(node.attributes.get('stub'))

    def get_colspecs(self):
        """Return column specification for longtable.

        Assumes reST line length being 80 characters.
        Table width is hairy.

        === ===
        ABC DEF
        === ===

        usually gets to narrow, therefore we add 1 (fiddlefactor).
        """
        width = 80

        total_width = 0.0
        # first see if we get too wide.
        for node in self._col_specs:
            colwidth = float(node['colwidth']+1) / width
            total_width += colwidth
        self._col_width = []
        self._rowspan = []
        # donot make it full linewidth
        factor = 0.93
        if total_width > 1.0:
            factor /= total_width
        bar = self.get_vertical_bar()
        latex_table_spec = ''
        for node in self._col_specs:
            colwidth = factor * float(node['colwidth']+1) / width
            self._col_width.append(colwidth+0.005)
            self._rowspan.append(0)
            latex_table_spec += '%sp{%.3f\\DUtablewidth}' % (bar, colwidth+0.005)
        return latex_table_spec+bar

    def get_column_width(self):
        """Return columnwidth for current cell (not multicell)."""
        return '%.2f\\DUtablewidth' % self._col_width[self._cell_in_row-1]

    def get_caption(self):
        if not self.caption:
            return ''
        if 1 == self._translator.thead_depth():
            return r'\caption{%s}\\' '\n' % self.caption
        return r'\caption[]{%s (... continued)}\\' '\n' % self.caption

    def need_recurse(self):
        if self._latex_type == 'longtable':
            return 1 == self._translator.thead_depth()
        return 0

    def visit_thead(self):
        self._in_thead += 1
        if self._table_style == 'standard':
            return ['\\hline\n']
        elif self._table_style == 'booktabs':
            return ['\\toprule\n']
        return []
    def depart_thead(self):
        a = []
        #if self._table_style == 'standard':
        #    a.append('\\hline\n')
        if self._table_style == 'booktabs':
            a.append('\\midrule\n')
        if self._latex_type == 'longtable':
            if 1 == self._translator.thead_depth():
                a.append('\\endfirsthead\n')
            else:
                a.append('\\endhead\n')
                a.append(r'\multicolumn{%d}{c}' % len(self._col_specs) +
                         r'{\hfill ... continued on next page} \\')
                a.append('\n\\endfoot\n\\endlastfoot\n')
        # for longtable one could add firsthead, foot and lastfoot
        self._in_thead -= 1
        return a
    def visit_row(self):
        self._cell_in_row = 0
    def depart_row(self):
        res = [' \\\\\n']
        self._cell_in_row = None  # remove cell counter
        for i in range(len(self._rowspan)):
            if (self._rowspan[i]>0):
                self._rowspan[i] -= 1

        if self._table_style == 'standard':
            rowspans = [i+1 for i in range(len(self._rowspan))
                        if (self._rowspan[i]<=0)]
            if len(rowspans)==len(self._rowspan):
                res.append('\\hline\n')
            else:
                cline = ''
                rowspans.reverse()
                # TODO merge clines
                while 1:
                    try:
                        c_start = rowspans.pop()
                    except:
                        break
                    cline += '\\cline{%d-%d}\n' % (c_start,c_start)
                res.append(cline)
        return res

    def set_rowspan(self,cell,value):
        try:
            self._rowspan[cell] = value
        except:
            pass
    def get_rowspan(self,cell):
        try:
            return self._rowspan[cell]
        except:
            return 0
    def get_entry_number(self):
        return self._cell_in_row
    def visit_entry(self):
        self._cell_in_row += 1
    def is_stub_column(self):
        if len(self.stubs) >= self._cell_in_row:
            return self.stubs[self._cell_in_row-1]
        return False


class LaTeXTranslator(nodes.NodeVisitor):

    # When options are given to the documentclass, latex will pass them
    # to other packages, as done with babel.
    # Dummy settings might be taken from document settings

    # Templates
    # ---------

    latex_head = r'\documentclass[%s]{%s}'
    linking = PreambleCmds.linking # if false, hyperref is not loaded
    # TODO: use a config value?

    generator = '% generated by Docutils <http://docutils.sourceforge.net/>'

    # Config setting defaults
    # -----------------------

    # TODO: use mixins for different implementations.
    # list environment for docinfo. else tabularx
    ## use_optionlist_for_docinfo = False # TODO: NOT YET IN USE

    # Use compound enumerations (1.A.1.)
    compound_enumerators = 0

    # If using compound enumerations, include section information.
    section_prefix_for_enumerators = 0

    # This is the character that separates the section ("." subsection ...)
    # prefix from the regular list enumerator.
    section_enumerator_separator = '-'

    # default link color
    hyperlink_color = 'blue'

    # Auxiliary variables
    # -------------------

    has_latex_toc = False # is there a toc in the doc? (needed by minitoc)
    is_toc_list = False   # is the current bullet_list a ToC?
    section_level = 0

    # Flags to encode():
    # inside citation reference labels underscores dont need to be escaped
    inside_citation_reference_label = False
    verbatim = False                   # do not encode
    insert_non_breaking_blanks = False # replace blanks by "~"
    insert_newline = False     	       # add latex newline commands
    literal = False 	  	       # teletype: replace underscores
    literal_block = False # inside literal block: no quote mangling


    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.settings = settings = document.settings
        self.latex_encoding = self.to_latex_encoding(settings.output_encoding)
        self.use_latex_toc = settings.use_latex_toc
        self.use_latex_docinfo = settings.use_latex_docinfo
        self.use_latex_footnotes = settings.use_latex_footnotes
        self._use_latex_citations = settings.use_latex_citations
        self.embed_stylesheet = settings.embed_stylesheet
        self._reference_label = settings.reference_label
        self.hyperlink_color = settings.hyperlink_color
        self.compound_enumerators = settings.compound_enumerators
        self.font_encoding = settings.font_encoding
        self.section_prefix_for_enumerators = (
            settings.section_prefix_for_enumerators)
        self.section_enumerator_separator = (
            settings.section_enumerator_separator.replace('_', '\\_'))
        if self.hyperlink_color == '0':
            self.hyperlink_color = 'black'
            self.colorlinks = 'false'
        else:
            self.colorlinks = 'true'
        # literal blocks:
        self.literal_block_env = ''
        self.literal_block_options = ''
        if settings.literal_block_env != '':
            (none,
             self.literal_block_env,
             self.literal_block_options,
             none ) = re.split('(\w+)(.*)', settings.literal_block_env)
        elif settings.use_verbatim_when_possible:
            self.literal_block_env = 'verbatim'
        #
        if self.settings.use_bibtex:
            self.bibtex = self.settings.use_bibtex.split(',',1)
            # TODO avoid errors on not declared citations.
        else:
            self.bibtex = None
        # language: labels, bibliographic_fields, and author_separators.
        # to allow writing labes for specific languages.
        self.language = languages.get_language(settings.language_code)
        self.babel = Babel(settings.language_code)
        self.author_separator = self.language.author_separators[0]
        self.d_options = [self.settings.documentoptions,
                          self.babel.get_language()]
        self.d_options = ','.join([opt for opt in self.d_options if opt])
        self.d_class = DocumentClass(settings.documentclass,
                                     settings.use_part_section)
        # object for a table while proccessing.
        self.table_stack = []
        self.active_table = Table(self,'longtable',settings.table_style)

        # Two special dictionaries to collect document-specific requirements.
        # Values will be inserted
        #  * in alphabetic order of their keys,
        #  * only once, even if required multiple times.
        self.requirements = SortableDict() # inserted before style sheet
        self.fallbacks = SortableDict()    # inserted after style sheet

        # Page layout with typearea (if there are relevant document options).
        if (settings.documentclass.find('scr') == -1 and
            (self.d_options.find('DIV') != -1 or
             self.d_options.find('BCOR') != -1)):
            self.requirements['typearea'] = r'\usepackage{typearea}'

        if self.font_encoding == '':
            fontenc_header = r'%\usepackage[OT1]{fontenc}'
        else:
            fontenc_header = r'\usepackage[%s]{fontenc}' % self.font_encoding

        if self.settings.graphicx_option == '':
            self.graphicx_package = r'\usepackage{graphicx}'
        elif self.settings.graphicx_option.lower() == 'auto':
            self.graphicx_package = PreambleCmds.graphicx_auto
        else:
            self.graphicx_package = (r'\usepackage[%s]{graphicx}' %
                                     self.settings.graphicx_option)

        # include all supported sections in toc and PDF bookmarks
        # (or use documentclass-default (as currently))?
        ## if self.use_latex_toc:
        ##    self.requirements['tocdepth'] = (r'\setcounter{tocdepth}{%d}' %
        ##                                     len(self.d_class.sections))

        if not self.settings.sectnum_xform: # section numbering by LaTeX:
            sectnum_cmds = []
            # sectnum_depth:
            #   0     no "sectnum" directive -> no section numbers
            #   None  "sectnum" directive without depth arg -> LaTeX default
            #   else  value of the "depth" argument -> limit to supported
            #         section levels
            if settings.sectnum_depth is not None:
                sectnum_depth = min(settings.sectnum_depth,
                                    len(self.d_class.sections))
                sectnum_cmds.append(r'\setcounter{secnumdepth}{%d}' %
                                     sectnum_depth)
            # start with specified number:
            if (hasattr(settings, 'sectnum_start') and
                settings.sectnum_start != 1):
                sectnum_cmds.append(r'\setcounter{%s}{%d}' %
                                     (self.d_class.sections[0],
                                      settings.sectnum_start-1))
            # currently ignored (configure in a stylesheet):
            ## settings.sectnum_prefix
            ## settings.sectnum_suffix
            if sectnum_cmds:
                self.requirements['sectnum'] = '\n'.join(sectnum_cmds)


        # packages and/or stylesheets
        # ---------------------------
        self.stylesheet = ['\n%%% User specified packages and stylesheets']
        # get list of style sheets from settings
        styles = utils.get_stylesheet_list(settings)
        # adapt path if --stylesheet_path is used
        if settings.stylesheet_path and not(self.embed_stylesheet):
            styles = [utils.relative_path(settings._destination, sheet)
                      for sheet in styles]
        for sheet in styles:
            (base, ext) = os.path.splitext(sheet)
            is_package = ext in ['.sty', '']
            if self.embed_stylesheet:
                if is_package:
                    sheet = base + '.sty' # adapt package name
                    # wrap in \makeatletter, \makeatother
                    wrapper = PreambleCmds.embedded_package_wrapper
                else:
                    wrapper = '%% embedded stylesheet: %s\n%s'
                settings.record_dependencies.add(sheet)
                self.stylesheet.append(wrapper % (sheet, open(sheet).read()))
            else: # link to style sheet
                if is_package:
                    self.stylesheet.append(r'\usepackage{%s}' % base)
                else:
                    self.stylesheet.append(r'\input{%s}' % sheet)

        # Part of LaTeX preamble before style sheet(s)
        self.head_prefix = [
              self.generator,
              self.latex_head % (self.d_options,self.settings.documentclass),
              ## '%%% Requirements',
              # multi-language support (language is in document settings)
              '\\usepackage{babel}%s' % self.babel.setup,
              fontenc_header,
              r'\usepackage[%s]{inputenc}' % self.latex_encoding,
              r'\usepackage{ifthen}',
              r'\usepackage{fixltx2e} % fix LaTeX2e shortcomings',
              ] # custom requirements will be added later

        # Part of LaTeX preamble following the stylesheet
        self.head = []
        if self.linking: # and maybe check for pdf
            self.pdfinfo = []
            self.pdfauthor = []
            # pdftitle, pdfsubject, pdfauthor, pdfkeywords,
            # pdfcreator, pdfproducer
        else:
            self.pdfinfo = None

        # Title metadata: Title, Date, and Author(s)
        # separate title, so we can append subtitle.
        self.title = []
        # if use_latex_docinfo: collects lists of
        # author/organization/contact/address lines
        self.author_stack = []
        # an empty string supresses the "auto-date" feature of \maketitle
        self.date = ''

        self.body_prefix = ['\n%%% Body\n\\begin{document}\n']
        self.body = []
        self.body_suffix = ['\n\\end{document}\n']
        self.context = []

        # Stack of section counters so that we don't have to use_latex_toc.
        # This will grow and shrink as processing occurs.
        # Initialized for potential first-level sections.
        self._section_number = [0]

        # The current stack of enumerations so that we can expand
        # them into a compound enumeration.
        self._enumeration_counters = []

        # The maximum number of enumeration counters we've used.
        # If we go beyond this number, we need to create a new
        # counter; otherwise, just reuse an old one.
        self._max_enumeration_counters = 0

        self._bibitems = []
        self.docinfo = []
        self.literal_block_stack = []


    # Auxiliary Methods
    # -----------------

    def to_latex_encoding(self,docutils_encoding):
        """Translate docutils encoding name into LaTeX's.

        Default method is remove "-" and "_" chars from docutils_encoding.

        """
        tr = {  'iso-8859-1': 'latin1',     # west european
                'iso-8859-2': 'latin2',     # east european
                'iso-8859-3': 'latin3',     # esperanto, maltese
                'iso-8859-4': 'latin4',     # north european, scandinavian, baltic
                'iso-8859-5': 'iso88595',   # cyrillic (ISO)
                'iso-8859-9': 'latin5',     # turkish
                'iso-8859-15': 'latin9',    # latin9, update to latin1.
                'mac_cyrillic': 'maccyr',   # cyrillic (on Mac)
                'windows-1251': 'cp1251',   # cyrillic (on Windows)
                'koi8-r': 'koi8-r',         # cyrillic (Russian)
                'koi8-u': 'koi8-u',         # cyrillic (Ukrainian)
                'windows-1250': 'cp1250',   #
                'windows-1252': 'cp1252',   #
                'us-ascii': 'ascii',        # ASCII (US)
                # unmatched encodings
                #'': 'applemac',
                #'': 'ansinew',  # windows 3.1 ansi
                #'': 'ascii',    # ASCII encoding for the range 32--127.
                #'': 'cp437',    # dos latin us
                #'': 'cp850',    # dos latin 1
                #'': 'cp852',    # dos latin 2
                #'': 'decmulti',
                #'': 'latin10',
                #'iso-8859-6': ''   # arabic
                #'iso-8859-7': ''   # greek
                #'iso-8859-8': ''   # hebrew
                #'iso-8859-10': ''   # latin6, more complete iso-8859-4
             }
        encoding = docutils_encoding.lower()
        if encoding in tr:
            return tr[encoding]
        # convert: latin-1, latin_1, utf-8 and similar things
        encoding = encoding.replace('_', '').replace('-', '')
        # strip the error handler
        return encoding.split(':')[0]

    def language_label(self, docutil_label):
        return self.language.labels[docutil_label]

    latex_equivalents = {
        u'\u00A0' : '~',
        u'\u2013' : '{--}',
        u'\u2014' : '{---}',
        u'\u2018' : '`',
        u'\u2019' : "'",
        u'\u201A' : ',',
        u'\u201C' : '``',
        u'\u201D' : "''",
        u'\u201E' : ',,',
        u'\u2020' : '\\dag{}',
        u'\u2021' : '\\ddag{}',
        u'\u2026' : '\\dots{}',
        u'\u2122' : '\\texttrademark{}',
        u'\u21d4' : '$\\Leftrightarrow$',
        # greek alphabet ?
    }

    def unicode_to_latex(self,text):
        # see LaTeX codec
        # http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/252124
        # Only some special chracters are translated, for documents with many
        # utf-8 chars one should use the LaTeX unicode package.
        for uchar in self.latex_equivalents.keys():
            text = text.replace(uchar,self.latex_equivalents[uchar])
        return text

    def ensure_math(self, text):
        if not hasattr(self, 'ensure_math_re'):
            chars = { # lnot,pm,twosuperior,threesuperior,mu,onesuperior,times,div
                     'latin1' : '\xac\xb1\xb2\xb3\xb5\xb9\xd7\xf7' ,
                     # TODO?: also latin5 and latin9
                    }
            self.ensure_math_re = re.compile('([%s])' % chars['latin1'])
        text = self.ensure_math_re.sub(r'\\ensuremath{\1}', text)
        return text

    def encode(self, text):
        """Return text with special characters escaped.

        Escape the ten special printing characters ``# $ % & ~ _ ^ \ { }``,
        square brackets ``[ ]``, double quotes and (in OT1) ``< | >``.

        Separate ``-`` (and more in literal text) to prevent input ligatures.
        """
        if self.verbatim:
            return text
        # Bootstrapping: backslash and braces are also part of replacements
        # 1. backslash (terminated below)
        text = text.replace('\\', r'\textbackslash')
        # 2. braces
        text = text.replace('{', r'\{')
        text = text.replace('}', r'\}')
        # 3. terminate \textbackslash
        text = text.replace('\\textbackslash', '\\textbackslash{}')
        # 4. the remaining special printing characters
        text = text.replace('#', r'\#')
        text = text.replace('$', r'\$')
        text = text.replace('%', r'\%')
        text = text.replace('&', r'\&')
        text = text.replace('~', r'\textasciitilde{}')
        if not self.inside_citation_reference_label:
            text = text.replace('_', r'\_')
        text = text.replace('^', r'\textasciicircum{}')
        # Square brackets
        #
        #   \item and all the other commands with optional arguments check
        #   if the token right after the macro name is an opening bracket.
        #   In that case the contents between that bracket and the following
        #   closing bracket on the same grouping level are taken as the
        #   optional argument. What makes this unintuitive is the fact that
        #   the square brackets aren't grouping characters themselves, so in
        #   your last example \item[[...]] the optional argument consists of
        #   [... (without the closing bracket).
        #
        # How to escape?
        #
        # Square brackets are ordinary chars and cannot be escaped with '\',
        # so we put them in a group '{[}'. (Alternative: ensure that all
        # macros with optional arguments are terminated with {} and text
        # inside any optional argument is put in a group ``[{text}]``).
        # Commands with optional args inside an optional arg must be put
        # in a group, e.g. ``\item[{\hyperref[label]{text}}]``.
        text = text.replace('[', '{[}')
        text = text.replace(']', '{]}')
        # Workarounds for OT1 font-encoding
        if self.font_encoding in ['OT1', '']:
            # * out-of-order characters in cmtt
            if self.literal_block or self.literal:
                # replace underscore by underlined blank, because this has
                # correct width.
                text = text.replace(r'\_', r'\underline{ }')
                # the backslash doesn't work, so we use a mirrored slash.
                # \reflectbox is provided by graphicx:
                self.requirements['graphicx'] = self.graphicx_package
                text = text.replace(r'\textbackslash', r'\reflectbox{/}')
            # * ``< | >`` come out as different chars (except for cmtt):
            else:
                text = text.replace('|', '\\textbar{}')
                text = text.replace('<', '\\textless{}')
                text = text.replace('>', '\\textgreater{}')
        #
        # Separate compound characters, e.g. '--' to '-{}-'.  (The
        # actual separation is done later; see below.)
        separate_chars = '-'
        if self.literal_block or self.literal:
            # In monospace-font, we also separate ',,', '``' and "''"
            # and some other characters which can't occur in
            # non-literal text.
            separate_chars += ',`\'"<>'
            # double quotes are 'active' in some languages
            text = text.replace('"', self.babel.literal_double_quote)
        else:
            text = self.babel.quote_quotes(text)
        for char in separate_chars * 2:
            # Do it twice ("* 2") because otherwise we would replace
            # '---' by '-{}--'.
            text = text.replace(char + char, char + '{}' + char)
        if self.insert_newline or self.literal_block:
            # Literal line breaks (in address or literal blocks):
            # for blank lines, insert a protected space, to avoid
            # ! LaTeX Error: There's no line here to end.
            textlines = [line + '~'*(not line.lstrip())
                         for line in text.split('\n')]
            text = '\\\\\n'.join(textlines)
        if self.insert_non_breaking_blanks:
            text = text.replace(' ', '~')
        if not self.latex_encoding.startswith('utf8'):
            text = self.unicode_to_latex(text)
            text = self.ensure_math(text)
        if self.latex_encoding == 'utf8':
            # no-break space is not supported by (plain) utf8 input encoding
            text = text.replace(u'\u00A0', '~')
        return text

    def attval(self, text,
               whitespace=re.compile('[\n\r\t\v\f]')):
        """Cleanse, encode, and return attribute value text."""
        return self.encode(whitespace.sub(' ', text))

    def astext(self):
        """Assemble document parts and return as string."""
        head = '\n'.join(self.head_prefix + self.stylesheet + self.head)
        body = ''.join(self.body_prefix  + self.body + self.body_suffix)
        return head + '\n' + body

    def is_inline(self, node):
        """Check whether a node represents an inline element"""
        return isinstance(node.parent, nodes.TextElement)

    def append_hypertargets(self, node):
        """Append hypertargets for all ids of `node`"""
        # hypertarget places the anchor at the target's baseline,
        # so we raise it explicitely
        self.body.append('%\n'.join(['\\raisebox{1em}{\\hypertarget{%s}{}}' %
                                     id for id in node['ids']]))

    def ids_to_labels(self, node, set_anchor=True):
        """Return list of label definitions for all ids of `node`

        If `set_anchor` is True, an anchor is set with \phantomsection.
        """
        labels = ['\\label{%s}' % id for id in node.get('ids', [])]
        if set_anchor and labels:
            labels.insert(0, '\\phantomsection')
        return labels


    # Visitor methods
    # ---------------

    def visit_Text(self, node):
        self.body.append(self.encode(node.astext()))

    def depart_Text(self, node):
        pass

    def visit_address(self, node):
        self.visit_docinfo_item(node, 'address')

    def depart_address(self, node):
        self.depart_docinfo_item(node)

    def visit_admonition(self, node):
        self.fallbacks['admonition'] = PreambleCmds.admonition
        if node.tagname is 'admonition':
            classes = ','.join(node['classes'])
            title = ''
        else: # specific admonitions
            classes = node.tagname.replace('_', '-')
            title = '\\DUtitle[%s]{%s}\n' % (
               classes, self.language.labels.get(classes, classes))
        self.body.append('\n\\DUadmonition[%s]{\n%s' % (classes, title))

    def depart_admonition(self, node=None):
        self.body.append('}\n')

    def visit_attention(self, node):
        self.visit_admonition(node)

    def depart_attention(self, node):
        self.depart_admonition()

    def visit_author(self, node):
        self.visit_docinfo_item(node, 'author')

    def depart_author(self, node):
        self.depart_docinfo_item(node)

    def visit_authors(self, node):
        # not used: visit_author is called anyway for each author.
        pass

    def depart_authors(self, node):
        pass

    def visit_block_quote(self, node):
        self.body.append( '%\n\\begin{quote}\n')

    def depart_block_quote(self, node):
        self.body.append( '\n\\end{quote}\n')

    def visit_bullet_list(self, node):
        if self.is_toc_list:
            self.body.append( '%\n\\begin{list}{}{}\n' )
        else:
            self.body.append( '%\n\\begin{itemize}\n' )

    def depart_bullet_list(self, node):
        if self.is_toc_list:
            self.body.append( '\n\\end{list}\n' )
        else:
            self.body.append( '\n\\end{itemize}\n' )

    def visit_superscript(self, node):
        self.body.append(r'\textsuperscript{')
        if node['classes']:
            self.visit_inline(node)

    def depart_superscript(self, node):
        if node['classes']:
            self.depart_inline(node)
        self.body.append('}')

    def visit_subscript(self, node):
        self.body.append(r'\textsubscript{') # requires `fixltx2e`
        if node['classes']:
            self.visit_inline(node)

    def depart_subscript(self, node):
        if node['classes']:
            self.depart_inline(node)
        self.body.append('}')

    def visit_caption(self, node):
        self.body.append( '\\caption{' )

    def depart_caption(self, node):
        self.body.append('}\n')

    def visit_caution(self, node):
        self.visit_admonition(node)

    def depart_caution(self, node):
        self.depart_admonition()

    def visit_title_reference(self, node):
        self.fallbacks['titlereference'] = PreambleCmds.titlereference
        self.body.append(r'\DUroletitlereference{')
        if node['classes']:
            self.visit_inline(node)

    def depart_title_reference(self, node):
        if node['classes']:
            self.depart_inline(node)
        self.body.append( '}' )

    def visit_citation(self, node):
        # TODO maybe use cite bibitems
        if self._use_latex_citations:
            self.context.append(len(self.body))
        else:
            self.body.append(r'\begin{figure}[b]')
            self.append_hypertargets(node)

    def depart_citation(self, node):
        if self._use_latex_citations:
            size = self.context.pop()
            label = self.body[size]
            text = ''.join(self.body[size+1:])
            del self.body[size:]
            self._bibitems.append([label, text])
        else:
            self.body.append('\\end{figure}\n')

    def visit_citation_reference(self, node):
        if self._use_latex_citations:
            if not self.inside_citation_reference_label:
                self.body.append(r'\cite{')
                self.inside_citation_reference_label = 1
            else:
                assert self.body[-1] in (' ', '\n'),\
                        'unexpected non-whitespace while in reference label'
                del self.body[-1]
        else:
            href = ''
            if 'refid' in node:
                href = node['refid']
            elif 'refname' in node:
                href = self.document.nameids[node['refname']]
            self.body.append('[\\hyperlink{%s}{' % href)

    def depart_citation_reference(self, node):
        if self._use_latex_citations:
            followup_citation = False
            # check for a following citation separated by a space or newline
            next_siblings = node.traverse(descend=0, siblings=1,
                                          include_self=0)
            if len(next_siblings) > 1:
                next = next_siblings[0]
                if (isinstance(next, nodes.Text) and
                    next.astext() in (' ', '\n')):
                    if next_siblings[1].__class__ == node.__class__:
                        followup_citation = True
            if followup_citation:
                self.body.append(',')
            else:
                self.body.append('}')
                self.inside_citation_reference_label = False
        else:
            self.body.append('}]')

    def visit_classifier(self, node):
        self.body.append( '(\\textbf{' )

    def depart_classifier(self, node):
        self.body.append( '})\n' )

    def visit_colspec(self, node):
        self.active_table.visit_colspec(node)

    def depart_colspec(self, node):
        pass

    def visit_comment(self, node):
        # Precede every line with a comment sign, wrap in newlines
        self.body.append('\n%% %s\n' % node.astext().replace('\n', '\n% '))
        raise nodes.SkipNode

    def depart_comment(self, node):
        pass

    def visit_compound(self, node):
        pass

    def depart_compound(self, node):
        pass

    def visit_contact(self, node):
        self.visit_docinfo_item(node, 'contact')

    def depart_contact(self, node):
        self.depart_docinfo_item(node)

    def visit_container(self, node):
        pass

    def depart_container(self, node):
        pass

    def visit_copyright(self, node):
        self.visit_docinfo_item(node, 'copyright')

    def depart_copyright(self, node):
        self.depart_docinfo_item(node)

    def visit_danger(self, node):
        self.visit_admonition(node)

    def depart_danger(self, node):
        self.depart_admonition()

    def visit_date(self, node):
        self.visit_docinfo_item(node, 'date')

    def depart_date(self, node):
        self.depart_docinfo_item(node)

    def visit_decoration(self, node):
        pass

    def depart_decoration(self, node):
        pass

    def visit_definition(self, node):
        pass

    def depart_definition(self, node):
        self.body.append('\n')

    def visit_definition_list(self, node):
        self.body.append( '%\n\\begin{description}\n' )

    def depart_definition_list(self, node):
        self.body.append( '\\end{description}\n' )

    def visit_definition_list_item(self, node):
        pass

    def depart_definition_list_item(self, node):
        pass

    def visit_description(self, node):
        self.body.append(' ')

    def depart_description(self, node):
        pass

    def visit_docinfo(self, node):
        # tabularx: automatic width of columns, no page breaks allowed.
        self.requirements['tabularx'] = r'\usepackage{tabularx}'
        self.fallbacks['_providelength'] = PreambleCmds.providelength
        self.fallbacks['docinfo'] = PreambleCmds.docinfo
        self.docinfo = ['%' + '_'*75 + '\n',
                        '\\begin{center}\n',
                        '\\begin{tabularx}{\\DUdocinfowidth}{lX}\n']

    def depart_docinfo(self, node):
        self.docinfo.append('\\end{tabularx}\n')
        self.docinfo.append('\\end{center}\n')
        self.body = self.docinfo + self.body # prepend to self.body
        # clear docinfo, so field names are no longer appended.
        self.docinfo = None

    def visit_docinfo_item(self, node, name):
        if name == 'author':
            if self.pdfinfo is not None:
                self.pdfauthor += [self.attval(node.astext())]
        if self.use_latex_docinfo:
            if name in ('author', 'organization', 'contact', 'address'):
                # We attach these to the last author.  If any of them precedes
                # the first author, put them in a separate "author" group
                # (in lack of better semantics).
                if name == 'author' or not self.author_stack:
                    self.author_stack.append([])
                if name == 'address':   # newlines are meaningful
                    self.insert_newline = 1
                    text = self.encode(node.astext())
                    self.insert_newline = False
                else:
                    text = self.attval(node.astext())
                self.author_stack[-1].append(text)
                raise nodes.SkipNode
            elif name == 'date':
                self.date = self.attval(node.astext())
                raise nodes.SkipNode
        self.docinfo.append('\\textbf{%s}: &\n\t' % self.language_label(name))
        if name == 'address':
            self.insert_newline = 1
            self.docinfo.append('{\\raggedright\n')
            self.context.append(' } \\\\\n')
        else:
            self.context.append(' \\\\\n')
        self.context.append(self.docinfo)
        self.context.append(len(self.body))

    def depart_docinfo_item(self, node):
        size = self.context.pop()
        dest = self.context.pop()
        tail = self.context.pop()
        tail = self.body[size:] + [tail]
        del self.body[size:]
        dest.extend(tail)
        # for address we did set insert_newline
        self.insert_newline = False

    def visit_doctest_block(self, node):
        self.body.append( '\\begin{verbatim}' )
        self.verbatim = 1

    def depart_doctest_block(self, node):
        self.body.append( '\\end{verbatim}\n' )
        self.verbatim = False

    def visit_document(self, node):
        if self.settings.use_titlepage_env:
            self.body_prefix.append('\\begin{titlepage}\n')
        # titled document?
        if (self.use_latex_docinfo or len(node) and
            isinstance(node[0], nodes.title)):
            if node['ids']:
                self.title += self.ids_to_labels(node)
            self.body_prefix.append('\\maketitle\n\n')

    def depart_document(self, node):
        # Complete header with information gained from walkabout
        # a) conditional requirements (before style sheet)
        self.head_prefix += self.requirements.sortedvalues()
        # b) coditional fallback definitions (after style sheet)
        self.head.append(
            '\n%%% Fallback definitions for Docutils-specific commands')
        self.head += self.fallbacks.sortedvalues()
        # c) hyperlink setup and PDF metadata
        self.head.append(self.linking % (self.colorlinks,
                                         self.hyperlink_color,
                                         self.hyperlink_color))
        if self.pdfinfo is not None and self.pdfauthor:
            self.pdfauthor = self.author_separator.join(self.pdfauthor)
            self.pdfinfo.append('  pdfauthor={%s}' % self.pdfauthor)
        if self.pdfinfo:
            self.head += [r'\hypersetup{'] + self.pdfinfo + ['}']
        # d) Title metadata
        # NOTE: Docutils puts this into docinfo, so normally we do not want
        #   LaTeX author/date handling (via \maketitle).
        #   To deactivate it, self.astext() adds \title{...}, \author{...},
        #   \date{...}, even if the"..." are empty strings.
        if '\\maketitle\n\n' in self.body_prefix:
            title = [PreambleCmds.documenttitle % (
                     '%\n  '.join(self.title),
                     ' \\and\n'.join(['\\\\\n'.join(author_lines)
                                     for author_lines in self.author_stack]),
                     self.date)]
            self.head += title
        # Add bibliography
        # TODO insertion point of bibliography should be configurable.
        if self._use_latex_citations and len(self._bibitems)>0:
            if not self.bibtex:
                widest_label = ''
                for bi in self._bibitems:
                    if len(widest_label)<len(bi[0]):
                        widest_label = bi[0]
                self.body.append('\n\\begin{thebibliography}{%s}\n' %
                                 widest_label)
                for bi in self._bibitems:
                    # cite_key: underscores must not be escaped
                    cite_key = bi[0].replace(r'\_','_')
                    self.body.append('\\bibitem[%s]{%s}{%s}\n' %
                                     (bi[0], cite_key, bi[1]))
                self.body.append('\\end{thebibliography}\n')
            else:
                self.body.append('\n\\bibliographystyle{%s}\n' %
                                 self.bibtex[0])
                self.body.append('\\bibliography{%s}\n' % self.bibtex[1])
        # Make sure to generate a toc file if needed for local contents:
        if 'minitoc' in self.requirements and not self.has_latex_toc:
            self.body.append('\n\\faketableofcontents % for local ToCs\n')

    def visit_emphasis(self, node):
        self.body.append('\\emph{')
        if node['classes']:
            self.visit_inline(node)
        self.literal_block_stack.append('\\emph{')

    def depart_emphasis(self, node):
        if node['classes']:
            self.depart_inline(node)
        self.body.append('}')
        self.literal_block_stack.pop()

    def visit_entry(self, node):
        self.active_table.visit_entry()
        # cell separation
        # BUG: the following fails, with more than one multirow
        # starting in the second column (or later) see
        # ../../../test/functional/input/data/latex.txt
        if self.active_table.get_entry_number() == 1:
            # if the first row is a multirow, this actually is the second row.
            # this gets hairy if rowspans follow each other.
            if self.active_table.get_rowspan(0):
                count = 0
                while self.active_table.get_rowspan(count):
                    count += 1
                    self.body.append(' & ')
                self.active_table.visit_entry() # increment cell count
        else:
            self.body.append(' & ')
        # multirow, multicolumn
        # IN WORK BUG TODO HACK continues here
        # multirow in LaTeX simply will enlarge the cell over several rows
        # (the following n if n is positive, the former if negative).
        if 'morerows' in node and 'morecols' in node:
            raise NotImplementedError('Cells that '
            'span multiple rows *and* columns are not supported, sorry.')
        if 'morerows' in node:
            self.requirements['multirow'] = r'\usepackage{multirow}'
            count = node['morerows'] + 1
            self.active_table.set_rowspan(
                                self.active_table.get_entry_number()-1,count)
            self.body.append('\\multirow{%d}{%s}{%%' %
                             (count,self.active_table.get_column_width()))
            self.context.append('}')
        elif 'morecols' in node:
            # the vertical bar before column is missing if it is the first
            # column. the one after always.
            if self.active_table.get_entry_number() == 1:
                bar1 = self.active_table.get_vertical_bar()
            else:
                bar1 = ''
            count = node['morecols'] + 1
            self.body.append('\\multicolumn{%d}{%sl%s}{' %
                    (count, bar1, self.active_table.get_vertical_bar()))
            self.context.append('}')
        else:
            self.context.append('')

        # header / not header
        if isinstance(node.parent.parent, nodes.thead):
            self.body.append('\\textbf{%')
            self.context.append('}')
        elif self.active_table.is_stub_column():
            self.body.append('\\textbf{')
            self.context.append('}')
        else:
            self.context.append('')

    def depart_entry(self, node):
        self.body.append(self.context.pop()) # header / not header
        self.body.append(self.context.pop()) # multirow/column
        # if following row is spanned from above.
        if self.active_table.get_rowspan(self.active_table.get_entry_number()):
           self.body.append(' & ')
           self.active_table.visit_entry() # increment cell count

    def visit_row(self, node):
        self.active_table.visit_row()

    def depart_row(self, node):
        self.body.extend(self.active_table.depart_row())

    def visit_enumerated_list(self, node):
        # We create our own enumeration list environment.
        # This allows to set the style and starting value
        # and unlimited nesting.
        enum_style = {'arabic':'arabic',
                'loweralpha':'alph',
                'upperalpha':'Alph',
                'lowerroman':'roman',
                'upperroman':'Roman' }
        enum_suffix = ''
        if 'suffix' in node:
            enum_suffix = node['suffix']
        enum_prefix = ''
        if 'prefix' in node:
            enum_prefix = node['prefix']
        if self.compound_enumerators:
            pref = ''
            if self.section_prefix_for_enumerators and self.section_level:
                for i in range(self.section_level):
                    pref += '%d.' % self._section_number[i]
                pref = pref[:-1] + self.section_enumerator_separator
                enum_prefix += pref
            for ctype, cname in self._enumeration_counters:
                enum_prefix += '\\%s{%s}.' % (ctype, cname)
        enum_type = 'arabic'
        if 'enumtype' in node:
            enum_type = node['enumtype']
        if enum_type in enum_style:
            enum_type = enum_style[enum_type]

        counter_name = 'listcnt%d' % len(self._enumeration_counters)
        self._enumeration_counters.append((enum_type, counter_name))
        # If we haven't used this counter name before, then create a
        # new counter; otherwise, reset & reuse the old counter.
        if len(self._enumeration_counters) > self._max_enumeration_counters:
            self._max_enumeration_counters = len(self._enumeration_counters)
            self.body.append('\\newcounter{%s}\n' % counter_name)
        else:
            self.body.append('\\setcounter{%s}{0}\n' % counter_name)

        self.body.append('\\begin{list}{%s\\%s{%s}%s}\n' %
            (enum_prefix,enum_type,counter_name,enum_suffix))
        self.body.append('{\n')
        self.body.append('\\usecounter{%s}\n' % counter_name)
        # set start after usecounter, because it initializes to zero.
        if 'start' in node:
            self.body.append('\\addtocounter{%s}{%d}\n' %
                             (counter_name,node['start']-1))
        ## set rightmargin equal to leftmargin
        self.body.append('\\setlength{\\rightmargin}{\\leftmargin}\n')
        self.body.append('}\n')

    def depart_enumerated_list(self, node):
        self.body.append('\\end{list}\n')
        self._enumeration_counters.pop()

    def visit_error(self, node):
        self.fallbacks['error'] = PreambleCmds.error
        self.visit_admonition(node)

    def depart_error(self, node):
        self.depart_admonition()

    def visit_field(self, node):
        # real output is done in siblings: _argument, _body, _name
        pass

    def depart_field(self, node):
        self.body.append('\n')
        ##self.body.append('%[depart_field]\n')

    def visit_field_argument(self, node):
        self.body.append('%[visit_field_argument]\n')

    def depart_field_argument(self, node):
        self.body.append('%[depart_field_argument]\n')

    def visit_field_body(self, node):
        # BUG by attach as text we loose references.
        if self.docinfo:
            self.docinfo.append('%s \\\\\n' % self.encode(node.astext()))
            raise nodes.SkipNode
        # BUG: what happens if not docinfo

    def depart_field_body(self, node):
        pass
        ## self.body.append( '\n' )

    def visit_field_list(self, node):
        self.fallbacks['fieldlist'] = PreambleCmds.fieldlist
        if not self.docinfo:
            self.body.append('%\n\\begin{DUfieldlist}\n')

    def depart_field_list(self, node):
        if not self.docinfo:
            self.body.append('\\end{DUfieldlist}\n')

    def visit_field_name(self, node):
        # BUG this duplicates docinfo_item
        if self.docinfo:
            self.docinfo.append('\\textbf{%s}: &\n\t' %
                                self.encode(node.astext()))
            raise nodes.SkipNode
        else:
            # Commands with optional args inside an optional arg must be put
            # in a group, e.g. ``\item[{\hyperref[label]{text}}]``.
            self.body.append('\\item[{')

    def depart_field_name(self, node):
        if not self.docinfo:
            self.body.append(':}]')

    def visit_figure(self, node):
        self.requirements['float_settings'] = PreambleCmds.float_settings
        # ! the 'align' attribute should set "outer alignment" !
        # For "inner alignment" use LaTeX default alignment (similar to HTML)
        ## if ('align' not in node.attributes or
        ##     node.attributes['align'] == 'center'):
        ##     align = '\n\\centering'
        ##     align_end = ''
        ## else:
        ##     # TODO non vertical space for other alignments.
        ##     align = '\\begin{flush%s}' % node.attributes['align']
        ##     align_end = '\\end{flush%s}' % node.attributes['align']
        ## self.body.append( '\\begin{figure}%s\n' % align )
        ## self.context.append( '%s\\end{figure}\n' % align_end )
        self.body.append('\\begin{figure}')
        self.context.append('\\end{figure}\n')

    def depart_figure(self, node):
        self.body.append( self.context.pop() )

    def visit_footer(self, node):
        self.context.append(len(self.body))

    def depart_footer(self, node):
        start = self.context.pop()
        footer = (['\n\\begin{center}\small\n'] +
                  self.body[start:] + ['\n\\end{center}\n'])
        self.body_suffix[:0] = footer
        del self.body[start:]

    def visit_footnote(self, node):
        if self.use_latex_footnotes:
            num,text = node.astext().split(None,1)
            num = self.encode(num.strip())
            self.body.append('\\footnotetext['+num+']')
            self.body.append('{')
        else:
            # use key starting with ~ for sorting after small letters
            self.requirements['~footnote_floats'] = (
                                            PreambleCmds.footnote_floats)
            self.body.append('\\begin{figure}[b]')
            self.append_hypertargets(node)
            if node.get('id') == node.get('name'):  # explicite label
                self.body += self.ids_to_labels(node)

    def depart_footnote(self, node):
        if self.use_latex_footnotes:
            self.body.append('}\n')
        else:
            self.body.append('\\end{figure}\n')

    def visit_footnote_reference(self, node):
        if self.use_latex_footnotes:
            self.body.append('\\footnotemark['+self.encode(node.astext())+']')
            raise nodes.SkipNode
        href = ''
        if 'refid' in node:
            href = node['refid']
        elif 'refname' in node:
            href = self.document.nameids[node['refname']]
        format = self.settings.footnote_references
        if format == 'brackets':
            suffix = '['
            self.context.append(']')
        elif format == 'superscript':
            suffix = r'\textsuperscript{'
            self.context.append('}')
        else:                           # shouldn't happen
            raise AssertionError('Illegal footnote reference format.')
        self.body.append('%s\\hyperlink{%s}{' % (suffix,href))

    def depart_footnote_reference(self, node):
        if self.use_latex_footnotes:
            return
        self.body.append('}%s' % self.context.pop())

    # footnote/citation label
    def label_delim(self, node, bracket, superscript):
        if isinstance(node.parent, nodes.footnote):
            if self.use_latex_footnotes:
                raise nodes.SkipNode
            if self.settings.footnote_references == 'brackets':
                self.body.append(bracket)
            else:
                self.body.append(superscript)
        else:
            assert isinstance(node.parent, nodes.citation)
            if not self._use_latex_citations:
                self.body.append(bracket)

    def visit_label(self, node):
        """footnote or citation label: in brackets or as superscript"""
        self.label_delim(node, '[', '\\textsuperscript{')

    def depart_label(self, node):
        self.label_delim(node, ']', '}')

    # elements generated by the framework e.g. section numbers.
    def visit_generated(self, node):
        pass

    def depart_generated(self, node):
        pass

    def visit_header(self, node):
        self.context.append(len(self.body))

    def depart_header(self, node):
        start = self.context.pop()
        self.body_prefix.append('\n\\verb|begin_header|\n')
        self.body_prefix.extend(self.body[start:])
        self.body_prefix.append('\n\\verb|end_header|\n')
        del self.body[start:]

    def visit_hint(self, node):
        self.visit_admonition(node)

    def depart_hint(self, node):
        self.depart_admonition()

    def to_latex_length(self, length_str):
        """Convert string with rst lenght to LaTeX"""
        match = re.match('(\d*\.?\d*)\s*(\S*)', length_str)
        if not match:
            return length_str
        value, unit = match.groups()[:2]
        # no unit or "DTP" points (called 'bp' in TeX):
        if unit in ('', 'pt'):
            length_str = '%sbp' % value
        # percentage: relate to current line width
        elif unit == '%':
            length_str = '%.3f\\linewidth' % (float(value)/100.0)
        return length_str

    def visit_image(self, node):
        self.requirements['graphicx'] = self.graphicx_package
        attrs = node.attributes
        # Add image URI to dependency list, assuming that it's
        # referring to a local file.
        self.settings.record_dependencies.add(attrs['uri'])
        # alignment defaults:
        if not 'align' in attrs:
            # Set default align of image in a figure to 'center'
            if isinstance(node.parent, nodes.figure):
                attrs['align'] = 'center'
            # query 'align-*' class argument
            for cls in node['classes']:
                if cls.startswith('align-'):
                    attrs['align'] = cls.split('-')[1]
        # pre- and postfix (prefix inserted in reverse order)
        pre = []
        post = []
        include_graphics_options = []
        is_inline = self.is_inline(node)
        align_prepost = {
            # key == (<is_inline>, <align>)
            # By default latex aligns the bottom of an image.
            (True, 'bottom'): ('', ''),
            (True, 'middle'): (r'\raisebox{-0.5\height}{', '}'),
            (True, 'top'):    (r'\raisebox{-\height}{', '}'),
            (False, 'center'): (r'\noindent\makebox[\textwidth][c]{', '}'),
            (False, 'left'):   (r'\noindent{', r'\hfill}'),
            (False, 'right'):  (r'\noindent{\hfill', '}'),}
        if 'align' in attrs:
            try:
                pre.append(align_prepost[is_inline, attrs['align']][0])
                post.append(align_prepost[is_inline, attrs['align']][1])
            except KeyError:
                pass                    # TODO: warn?
        if 'height' in attrs:
            include_graphics_options.append('height=%s' %
                            self.to_latex_length(attrs['height']))
        if 'scale' in attrs:
            include_graphics_options.append('scale=%f' %
                                            (attrs['scale'] / 100.0))
            ## # Could also be done with ``scale`` option to
            ## # ``\includegraphics``; doing it this way for consistency.
            ## pre.append('\\scalebox{%f}{' % (attrs['scale'] / 100.0,))
            ## post.append('}')
        if 'width' in attrs:
            include_graphics_options.append('width=%s' %
                            self.to_latex_length(attrs['width']))
        if not is_inline:
            pre.append('\n')
            post.append('\n')
        pre.reverse()
        self.body.extend(pre)
        self.append_hypertargets(node)
        options = ''
        if include_graphics_options:
            options = '[%s]' % (','.join(include_graphics_options))
        self.body.append('\\includegraphics%s{%s}' %
                         (options, attrs['uri']))
        self.body.extend(post)

    def depart_image(self, node):
        pass

    def visit_important(self, node):
        self.visit_admonition(node)

    def depart_important(self, node):
        self.depart_admonition()

    def visit_interpreted(self, node):
        # @@@ Incomplete, pending a proper implementation on the
        # Parser/Reader end.
        self.visit_literal(node)

    def depart_interpreted(self, node):
        self.depart_literal(node)

    def visit_legend(self, node):
        self.fallbacks['legend'] = PreambleCmds.legend
        self.body.append('\\begin{DUlegend}')

    def depart_legend(self, node):
        self.body.append('\\end{DUlegend}\n')

    def visit_line(self, node):
        self.body.append('\item[] ')

    def depart_line(self, node):
        self.body.append('\n')

    def visit_line_block(self, node):
        self.fallbacks['_providelength'] = PreambleCmds.providelength
        self.fallbacks['lineblock'] = PreambleCmds.lineblock
        if isinstance(node.parent, nodes.line_block):
            self.body.append('\\item[]\n'
                             '\\begin{DUlineblock}{\\DUlineblockindent}\n')
        else:
            self.body.append('\n\\begin{DUlineblock}{0em}\n')

    def depart_line_block(self, node):
        self.body.append('\\end{DUlineblock}\n')

    def visit_list_item(self, node):
        self.body.append('\n\\item ')

    def depart_list_item(self, node):
        pass

    def visit_literal(self, node):
        self.literal = True
        self.body.append('\\texttt{')
        if node['classes']:
            self.visit_inline(node)

    def depart_literal(self, node):
        self.literal = False
        if node['classes']:
            self.depart_inline(node)
        self.body.append('}')

    # Literal blocks are used for '::'-prefixed literal-indented
    # blocks of text, where the inline markup is not recognized,
    # but are also the product of the "parsed-literal" directive,
    # where the markup is respected.
    #
    # In both cases, we want to use a typewriter/monospaced typeface.
    # For "real" literal-blocks, we can use \verbatim, while for all
    # the others we must use \mbox or \alltt.
    #
    # We can distinguish between the two kinds by the number of
    # siblings that compose this node: if it is composed by a
    # single element, it's either
    # * a real one,
    # * a parsed-literal that does not contain any markup, or
    # * a parsed-literal containing just one markup construct.
    def is_plaintext(self, node):
        """Check whether a node can be typeset verbatim"""
        return (len(node) == 1) and isinstance(node[0], nodes.Text)

    def visit_literal_block(self, node):
        """Render a literal block."""
        # environments and packages to typeset literal blocks
        packages = {'listing': r'\usepackage{moreverb}',
                    'lstlisting': r'\usepackage{listings}',
                    'Verbatim': r'\usepackage{fancyvrb}',
                    # 'verbatim': '',
                    'verbatimtab': r'\usepackage{moreverb}'}

        if not self.active_table.is_open():
            # no quote inside tables, to avoid vertical space between
            # table border and literal block.
            # BUG: fails if normal text preceeds the literal block.
            self.body.append('%\n\\begin{quote}')
            self.context.append('\n\\end{quote}\n')
        else:
            self.body.append('\n')
            self.context.append('\n')
        if self.literal_block_env != '' and self.is_plaintext(node):
            self.requirements['literal_block'] = packages.get(
                                                  self.literal_block_env, '')
            self.verbatim = 1
            self.body.append('\\begin{%s}%s\n' % (self.literal_block_env,
                                                  self.literal_block_options))
        else:
            self.literal_block = 1
            self.insert_non_breaking_blanks = 1
            self.body.append('{\\ttfamily \\raggedright \\noindent\n')

    def depart_literal_block(self, node):
        if self.verbatim:
            self.body.append('\n\\end{%s}\n' % self.literal_block_env)
            self.verbatim = False
        else:
            self.body.append('\n}')
            self.insert_non_breaking_blanks = False
            self.literal_block = False
        self.body.append(self.context.pop())

    ## def visit_meta(self, node):
    ##     self.body.append('[visit_meta]\n')
        # TODO: set keywords for pdf?
        # But:
        #  The reStructuredText "meta" directive creates a "pending" node,
        #  which contains knowledge that the embedded "meta" node can only
        #  be handled by HTML-compatible writers. The "pending" node is
        #  resolved by the docutils.transforms.components.Filter transform,
        #  which checks that the calling writer supports HTML; if it doesn't,
        #  the "pending" node (and enclosed "meta" node) is removed from the
        #  document.
        #  --- docutils/docs/peps/pep-0258.html#transformer

    ## def depart_meta(self, node):
    ##     self.body.append('[depart_meta]\n')

    def visit_note(self, node):
        self.visit_admonition(node)

    def depart_note(self, node):
        self.depart_admonition()

    def visit_option(self, node):
        if self.context[-1]:
            # this is not the first option
            self.body.append(', ')

    def depart_option(self, node):
        # flag tha the first option is done.
        self.context[-1] += 1

    def visit_option_argument(self, node):
        """Append the delimiter betweeen an option and its argument to body."""
        self.body.append(node.get('delimiter', ' '))

    def depart_option_argument(self, node):
        pass

    def visit_option_group(self, node):
        self.body.append('\n\\item[')
        # flag for first option
        self.context.append(0)

    def depart_option_group(self, node):
        self.context.pop() # the flag
        self.body.append('] ')

    def visit_option_list(self, node):
        self.fallbacks['_providelength'] = PreambleCmds.providelength
        self.fallbacks['optionlist'] = PreambleCmds.optionlist
        self.body.append('%\n\\begin{DUoptionlist}\n')

    def depart_option_list(self, node):
        self.body.append('\n\\end{DUoptionlist}\n')

    def visit_option_list_item(self, node):
        pass

    def depart_option_list_item(self, node):
        pass

    def visit_option_string(self, node):
        ##self.body.append(self.starttag(node, 'span', '', CLASS='option'))
        pass

    def depart_option_string(self, node):
        ##self.body.append('</span>')
        pass

    def visit_organization(self, node):
        self.visit_docinfo_item(node, 'organization')

    def depart_organization(self, node):
        self.depart_docinfo_item(node)

    def visit_paragraph(self, node):
        # no newline if the paragraph is first in a list item
        if ((isinstance(node.parent, nodes.list_item) or
             isinstance(node.parent, nodes.description)) and
            node is node.parent[0]):
            return
        index = node.parent.index(node)
        if (isinstance(node.parent, nodes.compound) and
            index > 0 and
            not isinstance(node.parent[index - 1], nodes.paragraph) and
            not isinstance(node.parent[index - 1], nodes.compound)):
            return
        self.body.append('\n')
        if node.get('ids'):
            self.body += self.ids_to_labels(node) + ['\n']

    def depart_paragraph(self, node):
        self.body.append('\n')

    def visit_problematic(self, node):
        self.requirements['color'] = PreambleCmds.color
        self.body.append('%\n')
        self.append_hypertargets(node)
        self.body.append(r'\hyperlink{%s}{\textbf{\color{red}' % node['refid'])

    def depart_problematic(self, node):
        self.body.append('}}')

    def visit_raw(self, node):
        if 'latex' in node.get('format', '').split():
            self.body.append(node.astext())
        raise nodes.SkipNode

    def visit_reference(self, node):
        # BUG: hash_char '#' is troublesome in LaTeX.
        # mbox and other environments do not like the '#'.
        hash_char = '\\#'
        if 'refuri' in node:
            href = node['refuri'].replace('#', hash_char)
            self.body.append('\\href{%s}{' % href.replace('%', '\\%'))
            return
        if 'refid' in node:
            href = node['refid']
        elif 'refname' in node:
            href = self.document.nameids[node['refname']]
        else:
            raise AssertionError('Unknown reference.')
        if not self.is_inline(node):
            self.body.append('\n')

        self.body.append('\\hyperref[%s]{' % href)
        if self._reference_label and 'refuri' not in node:
            self.body.append('\\%s{%s}}' % (self._reference_label,
                        href.replace(hash_char, '')))
            raise nodes.SkipNode

    def depart_reference(self, node):
        self.body.append('}')
        if not self.is_inline(node):
            self.body.append('\n')

    def visit_revision(self, node):
        self.visit_docinfo_item(node, 'revision')

    def depart_revision(self, node):
        self.depart_docinfo_item(node)

    def visit_section(self, node):
        self.section_level += 1
        # Initialize counter for potential subsections:
        self._section_number.append(0)
        # Counter for this section's level (initialized by parent section):
        self._section_number[self.section_level - 1] += 1

    def depart_section(self, node):
        # Remove counter for potential subsections:
        self._section_number.pop()
        self.section_level -= 1

    def visit_sidebar(self, node):
        self.requirements['color'] = PreambleCmds.color
        self.fallbacks['sidebar'] = PreambleCmds.sidebar
        self.body.append('\n\\DUsidebar{\n')

    def depart_sidebar(self, node):
        self.body.append('}\n')

    attribution_formats = {'dash': ('---', ''),
                           'parentheses': ('(', ')'),
                           'parens': ('(', ')'),
                           'none': ('', '')}

    def visit_attribution(self, node):
        prefix, suffix = self.attribution_formats[self.settings.attribution]
        self.body.append('\n\\begin{flushright}\n')
        self.body.append(prefix)
        self.context.append(suffix)

    def depart_attribution(self, node):
        self.body.append(self.context.pop() + '\n')
        self.body.append('\\end{flushright}\n')

    def visit_status(self, node):
        self.visit_docinfo_item(node, 'status')

    def depart_status(self, node):
        self.depart_docinfo_item(node)

    def visit_strong(self, node):
        self.body.append('\\textbf{')
        self.literal_block_stack.append('\\textbf{')
        if node['classes']:
            self.visit_inline(node)

    def depart_strong(self, node):
        if node['classes']:
            self.depart_inline(node)
        self.body.append('}')
        self.literal_block_stack.pop()

    def visit_substitution_definition(self, node):
        raise nodes.SkipNode

    def visit_substitution_reference(self, node):
        self.unimplemented_visit(node)

    def visit_subtitle(self, node):
        if isinstance(node.parent, nodes.document):
            self.title.append(r'\\ % subtitle')
            self.title.append(r'\large{%s}' % self.encode(node.astext()))
            self.title += self.ids_to_labels(node, set_anchor=False)
            raise nodes.SkipNode
        # Section subtitle -> always "starred": no number, not in ToC
        elif isinstance(node.parent, nodes.section):
            self.body.append(r'\%s*{' %
                             self.d_class.section(self.section_level + 1))
        else:
            self.fallbacks['subtitle'] = PreambleCmds.subtitle
            self.body.append('\n\\DUsubtitle[%s]{' % node.parent.tagname)

    def depart_subtitle(self, node):
        self.body.append('}\n')

    def visit_system_message(self, node):
        self.requirements['color'] = PreambleCmds.color
        self.fallbacks['error'] = PreambleCmds.error
        self.visit_admonition(node) # error or warning
        self.append_hypertargets(node)
        try:
            line = ', line~%s' % node['line']
        except KeyError:
            line = ''
        self.body.append('\n\n{\color{red}%s/%s} in \\texttt{%s}%s\n' %
                         (node['type'], node['level'],
                          self.encode(node['source']), line))
        if len(node['backrefs']) == 1:
            self.body.append('\n\\hyperlink{%s}{' % node['backrefs'][0])
            self.context.append('}')
        else:
            backrefs = ['\\hyperlink{%s}{%d}' % (href, i+1)
                        for (i, href) in enumerate(node['backrefs'])]
            self.context.append('backrefs: ' + ' '.join(backrefs))

    def depart_system_message(self, node):
        self.body.append(self.context.pop())
        self.depart_admonition()

    def visit_table(self, node):
        self.requirements['table'] = PreambleCmds.table
        if self.active_table.is_open():
            self.table_stack.append(self.active_table)
            # nesting longtable does not work (e.g. 2007-04-18)
            self.active_table = Table(self,'tabular',self.settings.table_style)
        self.active_table.open()
        for cls in node['classes']:
            self.active_table.set_table_style(cls)
        if self.active_table._table_style == 'booktabs':
            self.requirements['booktabs'] = r'\usepackage{booktabs}'
        self.body.append('\n' + self.active_table.get_opening())

    def depart_table(self, node):
        self.body.append(self.active_table.get_closing() + '\n')
        self.active_table.close()
        if len(self.table_stack)>0:
            self.active_table = self.table_stack.pop()
        else:
            self.active_table.set_table_style(self.settings.table_style)

    def visit_target(self, node):
        # Skip indirect targets:
        if ('refuri' in node       # external hyperlink
            or 'refid' in node     # resolved internal link
            or 'refname' in node): # unresolved internal link
            ## self.body.append('%% %s\n' % node)   # for debugging
            return
        self.body.append('%\n')
        self.body += self.ids_to_labels(node)

    def depart_target(self, node):
        pass

    def visit_tbody(self, node):
        # BUG write preamble if not yet done (colspecs not [])
        # for tables without heads.
        if not self.active_table.get('preamble written'):
            self.visit_thead(None)
            self.depart_thead(None)

    def depart_tbody(self, node):
        pass

    def visit_term(self, node):
        """definition list term"""
        # Commands with optional args inside an optional arg must be put
        # in a group, e.g. ``\item[{\hyperref[label]{text}}]``.
        self.body.append('\\item[{')

    def depart_term(self, node):
        # \leavevmode results in a line break if the
        # term is followed by an item list.
        self.body.append('}] \leavevmode ')

    def visit_tgroup(self, node):
        #self.body.append(self.starttag(node, 'colgroup'))
        #self.context.append('</colgroup>\n')
        pass

    def depart_tgroup(self, node):
        pass

    _thead_depth = 0
    def thead_depth (self):
        return self._thead_depth

    def visit_thead(self, node):
        self._thead_depth += 1
        if 1 == self.thead_depth():
            self.body.append('{%s}\n' % self.active_table.get_colspecs())
            self.active_table.set('preamble written',1)
        self.body.append(self.active_table.get_caption())
        self.body.extend(self.active_table.visit_thead())

    def depart_thead(self, node):
        if node is not None:
            self.body.extend(self.active_table.depart_thead())
            if self.active_table.need_recurse():
                node.walkabout(self)
        self._thead_depth -= 1

    def visit_tip(self, node):
        self.visit_admonition(node)

    def depart_tip(self, node):
        self.depart_admonition()

    def bookmark(self, node):
        """Return label and pdfbookmark string for titles."""
        result = ['']
        if self.settings.sectnum_xform: # "starred" section cmd
            # add to the toc and pdfbookmarks
            section_name = self.d_class.section(max(self.section_level, 1))
            section_title = self.encode(node.astext())
            result.append(r'\phantomsection')
            result.append(r'\addcontentsline{toc}{%s}{%s}' %
                          (section_name, section_title))
        result += self.ids_to_labels(node.parent, set_anchor=False)
        return '%\n  '.join(result) + '%\n'

    def visit_title(self, node):
        """Append section and other titles."""
        # Document title
        if node.parent.tagname == 'document':
            self.title.insert(0, self.encode(node.astext()))
            if not self.pdfinfo == None:
                self.pdfinfo.append('  pdftitle={%s},' %
                                    self.encode(node.astext()) )
            raise nodes.SkipNode
        # Topic titles (topic, admonition, sidebar)
        elif (isinstance(node.parent, nodes.topic) or
              isinstance(node.parent, nodes.admonition) or
              isinstance(node.parent, nodes.sidebar)):
            self.fallbacks['title'] = PreambleCmds.title
            classes = ','.join(node.parent['classes'])
            if not classes:
                classes = node.tagname
            self.body.append('\\DUtitle[%s]{' % classes)
            self.context.append('}\n')
        # Table caption
        elif isinstance(node.parent, nodes.table):
            # caption must be written after column spec
            self.active_table.caption = self.encode(node.astext())
            raise nodes.SkipNode
        # Section title
        else:
            self.body.append('\n\n')
            self.body.append('%' + '_' * 75)
            self.body.append('\n\n')
            #
            section_name = self.d_class.section(self.section_level)
            # number sections?
            if (self.settings.sectnum_xform # numbering by Docutils
                or (self.section_level > len(self.d_class.sections))):
                section_star = '*'
            else: # LaTeX numbered sections
                section_star = ''
            self.body.append(r'\%s%s{' % (section_name, section_star))
            # System messages heading in red:
            if ('system-messages' in node.parent['classes']):
                self.requirements['color'] = PreambleCmds.color
                self.body.append('\color{red}')
            # label and ToC entry:
            self.context.append(self.bookmark(node) + '}\n')
            # MAYBE postfix paragraph and subparagraph with \leavemode to
            # ensure floats stay in the section and text starts on a new line.

    def depart_title(self, node):
        self.body.append(self.context.pop())

    def minitoc(self, title, depth):
        """Generate a local table of contents with LaTeX package minitoc"""
        section_name = self.d_class.section(self.section_level)
        # name-prefix for current section level
        minitoc_names = {'part': 'part', 'chapter': 'mini'}
        if 'chapter' not in self.d_class.sections:
            minitoc_names['section'] = 'sect'
        try:
            minitoc_name = minitoc_names[section_name]
        except KeyError: # minitoc only supports part- and toplevel
            warn = self.document.reporter.warning
            warn('Skipping local ToC at %s level.\n' % section_name +
                 '  Feature not supported with option "use-latex-toc"')
            return
        # Requirements/Setup
        self.requirements['minitoc'] = PreambleCmds.minitoc
        self.requirements['minitoc-'+minitoc_name] = (r'\do%stoc' %
                                                      minitoc_name)
        # depth: (Docutils defaults to unlimited depth)
        maxdepth = len(self.d_class.sections)
        self.requirements['minitoc-%s-depth' % minitoc_name] = (
            r'\mtcsetdepth{%stoc}{%d}' % (minitoc_name, maxdepth))
        # Process 'depth' argument (!Docutils stores a relative depth while
        # minitoc  expects an absolute depth!):
        offset = {'sect': 1, 'mini': 0, 'part': 0}
        if 'chapter' in self.d_class.sections:
            offset['part'] = -1
        if depth:
            self.body.append('\\setcounter{%stocdepth}{%d}' %
                             (minitoc_name, depth + offset[minitoc_name]))
        # title:
        self.body.append('\\mtcsettitle{%stoc}{%s}\n' % (minitoc_name, title))
        # the toc-generating command:
        self.body.append('\\%stoc\n' % minitoc_name)

    def visit_topic(self, node):
        # Topic nodes can be generic topic, abstract, dedication, or ToC
        # table of contents:
        if 'contents' in node['classes']:
            self.body.append('\n')
            self.body += self.ids_to_labels(node)
            if self.settings.use_titlepage_env:
                # TODO: move this to a save place
                # (what if the contents are at the end of the document?)
                self.body.append('\\end{titlepage}\n')
            # add contents to PDF bookmarks sidebar
            if isinstance(node.next_node(), nodes.title):
                self.body.append('\n\\pdfbookmark[%d]{%s}{%s}\n' %
                                 (self.section_level+1,
                                  node.next_node().astext(),
                                  node.get('ids', ['contents'])[0]
                                 ))
            if self.use_latex_toc:
                title = ''
                if isinstance(node.next_node(), nodes.title):
                    title = self.encode(node.pop(0).astext())
                depth = node.get('depth', 0)
                if 'local' in node['classes']:
                    self.minitoc(title, depth)
                    self.context.append('')
                    return
                if depth:
                    self.body.append('\\setcounter{tocdepth}{%d}\n' % depth)
                if title != 'Contents':
                    self.body.append('\\renewcommand{\\contentsname}{%s}\n'
                                     % title)
                self.body.append('\\tableofcontents\n\n')
                self.has_latex_toc = True
            else: # Docutils generated contents list
                # set flag for visit_bullet_list() and visit_title()
                self.is_toc_list = True
            self.context.append('')
        elif ('abstract' in node['classes'] and
              self.settings.use_latex_abstract):
            self.body.append('\\begin{abstract}')
            self.context.append('\\end{abstract}\n')
        else:
            self.fallbacks['topic'] = PreambleCmds.topic
            # special topics:
            if 'abstract' in node['classes']:
                self.fallbacks['abstract'] = PreambleCmds.abstract
            if 'dedication' in node['classes']:
                self.fallbacks['dedication'] = PreambleCmds.dedication
            self.body.append('\n\\DUtopic[%s]{\n' % ','.join(node['classes']))
            self.context.append('}\n')

    def depart_topic(self, node):
        self.body.append(self.context.pop())
        self.is_toc_list = False

    def visit_inline(self, node): # <span>, i.e. custom roles
        # insert fallback definition
        self.fallbacks['inline'] = PreambleCmds.inline
        self.body += [r'\DUrole{%s}{' % cls for cls in node['classes']]
        self.context.append('}' * (len(node['classes'])))

    def depart_inline(self, node):
        self.body.append(self.context.pop())

    def visit_rubric(self, node):
        self.fallbacks['rubric'] = PreambleCmds.rubric
        self.body.append('\n\\DUrubric{')
        self.context.append('}\n')

    def depart_rubric(self, node):
        self.body.append(self.context.pop())

    def visit_transition(self, node):
        self.fallbacks['transition'] = PreambleCmds.transition
        self.body.append('\n\n')
        self.body.append('%' + '_' * 75 + '\n')
        self.body.append(r'\DUtransition')
        self.body.append('\n\n')

    def depart_transition(self, node):
        pass

    def visit_version(self, node):
        self.visit_docinfo_item(node, 'version')

    def depart_version(self, node):
        self.depart_docinfo_item(node)

    def visit_warning(self, node):
        self.visit_admonition(node)

    def depart_warning(self, node):
        self.depart_admonition()

    def unimplemented_visit(self, node):
        raise NotImplementedError('visiting unimplemented node type: %s' %
                                  node.__class__.__name__)

#    def unknown_visit(self, node):
#    def default_visit(self, node):

# vim: set ts=4 et ai :
