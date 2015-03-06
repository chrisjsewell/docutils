# .. coding: utf8
# :Author: Günter Milde <milde@users.berlios.de>
# :Revision: $Revision$
# :Date: $Date: 2005-06-28$
# :Copyright: © 2005, 2009 Günter Milde.
# :License: Released under the terms of the `2-Clause BSD license`_, in short:
#
#    Copying and distribution of this file, with or without modification,
#    are permitted in any medium without royalty provided the copyright
#    notice and this notice are preserved.
#    This file is offered as-is, without any warranty.
#
# .. _2-Clause BSD license: http://www.spdx.org/licenses/BSD-2-Clause

"""
Strict HyperText Markup Language document tree Writer.

This is a variant of Docutils' standard 'html4css1' writer.

GOAL:
 * The output conforms to the XHTML version 1.1 DTD.
 * It contains no hard-coded formatting information that would prevent
   layout design by cascading style sheets.
"""

__docformat__ = 'reStructuredText'

import os
import os.path
import re

import docutils
from docutils import frontend, nodes, utils, writers, languages
from docutils.writers import html4css1

class Writer(html4css1.Writer):

    supported = ('html', 'xhtml', 'xhtml1',
                 'html4strict', 'xhtml1strict',
                 'xhtml11', 'xhtml1css2')
    """Formats this writer supports."""

    default_stylesheets = ['html-base.css', 'xhtml11.css']
    default_stylesheet_dirs = ['.',
        os.path.abspath(os.path.dirname(__file__)),
        # for math.css:                            
        os.path.abspath(os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 'html4css1'))
       ]

    config_section = 'xhtml11 writer'
    config_section_dependencies = ('writers', 'html4css1 writer')

    settings_spec = frontend.filter_settings_spec(
        html4css1.Writer.settings_spec,
        'field_name_limit', 'option_limit', # removed options
        stylesheet_path = (
          'Comma separated list of stylesheet paths. '
          'Relative paths are expanded if a matching file is found in '
          'the --stylesheet-dirs. With --link-stylesheet, '
          'the path is rewritten relative to the output HTML file. '
          'Default: "%s"' % ','.join(default_stylesheets),
          ['--stylesheet-path'],
          {'metavar': '<file[,file,...]>', 'overrides': 'stylesheet',
           'validator': frontend.validate_comma_separated_list,
           'default': default_stylesheets}),
        stylesheet_dirs = (
          'Comma-separated list of directories where stylesheets are found. '
          'Used by --stylesheet-path when expanding relative path arguments. '
          'Default: "%s"' % default_stylesheet_dirs,
          ['--stylesheet-dirs'],
          {'metavar': '<dir[,dir,...]>',
           'validator': frontend.validate_comma_separated_list,
           'default': default_stylesheet_dirs}),
        math_output = ('Math output format, one of "MathML", "HTML", '
            '"MathJax" or "LaTeX". Default: "MathML"',
            ['--math-output'],
            {'default': 'MathML'}))

    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = HTMLTranslator


class HTMLTranslator(html4css1.HTMLTranslator):
    """
    This writer generates XHTML 1.1
    without formatting that interferes with a CSS stylesheet.
    """
    doctype = ('<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" '
               '"http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">\n')
    doctype_mathml = (
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1 plus MathML 2.0//EN" '
        '"http://www.w3.org/Math/DTD/mathml2/xhtml-math11-f.dtd">\n')

    # there is no attribute "lang" in XHTML 1.1
    head_prefix_template = ('<html xmlns="http://www.w3.org/1999/xhtml"'
                            ' xml:lang="%(lang)s">\n<head>\n')
    lang_attribute = 'xml:lang' # changed from 'lang' in XHTML 1.0

    def __init__(self, document):
        html4css1.HTMLTranslator.__init__(self, document)
        self.in_footnote_list = False

    # Do not  mark the first child with 'class="first"' and the last
    # child with 'class="last"' in definitions, table cells, field
    # bodies, option descriptions, and list items. Use the
    # ``:first-child`` and ``:last-child`` selectors instad.

    def set_first_last(self, node):
        pass

    # Compact lists
    # ------------
    # Include definition lists and field lists (in addition to ordered
    # and unordered lists) in the test if a list is "simple"  (cf. the
    # html4css1.HTMLTranslator docstring and the SimpleListChecker class at
    # the end of this file).

    def is_compactable(self, node):
        # print "is_compactable %s ?" % node.__class__,
        # explicite class arguments have precedence
        if 'compact' in node['classes']:
            # print "explicitely compact"
            return True
        if 'open' in node['classes']:
            # print "explicitely open"
            return False
        # check config setting:
        if (isinstance(node, nodes.field_list) or
            isinstance(node, nodes.definition_list)
           ) and not self.settings.compact_field_lists:
            # print "`compact-field-lists` is False"
            return False
        if (isinstance(node, nodes.enumerated_list) or
            isinstance(node, nodes.bullet_list)
           ) and not self.settings.compact_lists:
            # print "`compact-lists` is False"
            return False
        # more special cases:
        if (self.topic_classes == ['contents']): # TODO: self.in_contents
            return True
        # check the list items:
        visitor = SimpleListChecker(self.document)
        try:
            node.walk(visitor)
        except nodes.NodeFound:
            # print "complex node"
            return False
        else:
            # print "simple list"
            return True

    # address, literal block, and doctest block: no newline after <pre> tag
    # (leads to blank line in XHTML1.1)
    def visit_address(self, node):
        self.visit_docinfo_item(node, 'address', meta=False)
        self.body.append(self.starttag(node, 'pre',suffix='',
                                       CLASS='address'))

    # author, authors
    # ---------------
    # Use paragraphs instead of hard-coded linebreaks.

    def visit_author(self, node):
        if not(isinstance(node.parent, nodes.authors)):
            self.visit_docinfo_item(node, 'author')
        self.body.append('<p>')

    def depart_author(self, node):
        self.body.append('</p>')
        if isinstance(node.parent, nodes.authors):
            self.body.append('\n')
        else:
            self.depart_docinfo_item()

    def visit_authors(self, node):
        self.visit_docinfo_item(node, 'authors')

    def depart_authors(self, node):
        self.depart_docinfo_item()

    # citations
    # ---------
    # Use definition list instead of table for bibliographic references.
    # Join adjacent citation entries.

    def visit_citation(self, node):
        if not self.in_footnote_list:
            self.body.append('<dl class="citation">\n')
            self.in_footnote_list = True

    def depart_citation(self, node):
        self.body.append('</dd>\n')
        if not isinstance(node.next_node(descend=False, siblings=True),
                          nodes.citation):
            self.body.append('</dl>\n')
            self.in_footnote_list = False

    # classifier
    # ----------
    # don't insert classifier-delimiter here (done by CSS)

    def visit_classifier(self, node):
        self.body.append(self.starttag(node, 'span', '', CLASS='classifier'))

    def depart_classifier(self, node):
        self.body.append('</span>')

    # definition list
    # ---------------
    # check for simple/complex list and set class attribute

    def visit_definition_list(self, node):
        classes = node.setdefault('classes', [])
        if self.is_compactable(node):
            classes.append('simple')
        self.body.append(self.starttag(node, 'dl'))

    def depart_definition_list(self, node):
        self.body.append('</dl>\n')

    # docinfo
    # -------
    # use definition list instead of table

    def visit_docinfo(self, node):
        classes = 'docinfo'
        if (self.is_compactable(node)):
            classes += ' simple'
        self.body.append(self.starttag(node, 'dl', CLASS=classes))

    def depart_docinfo(self, node):
        self.body.append('</dl>\n')
        
    def visit_docinfo_item(self, node, name, meta=True):
        if meta:
            meta_tag = '<meta name="%s" content="%s" />\n' \
                       % (name, self.attval(node.astext()))
            self.add_meta(meta_tag)
        self.body.append('<dt class="%s">%s</dt>\n'
                         % (name, self.language.labels[name]))
        self.body.append(self.starttag(node, 'dd', '', CLASS=name))

    def depart_docinfo_item(self):
        self.body.append('</dd>\n')

    # doctest-block
    # -------------
    # no line-break
    # TODO: RSt-parser should treat this as code-block with class "pycon".
    
    def visit_doctest_block(self, node):
        self.body.append(self.starttag(node, 'pre', suffix='',
                                       CLASS='code pycon doctest-block'))

    # enumerated lists
    # ----------------
    # The 'start' attribute does not conform to HTML4/XHTML1 Strict
    # (it will resurface in HTML5)

    def visit_enumerated_list(self, node):
        atts = {}
        if 'start' in node:
            atts['style'] = 'counter-reset: item %d;' % (node['start'] - 1)
        classes = node.setdefault('classes', [])
        if 'enumtype' in node:
            classes.append(node['enumtype'])
        if self.is_compactable(node):
            classes.append('simple')
        self.body.append(self.starttag(node, 'ol', **atts))

    def depart_enumerated_list(self, node):
        self.body.append('</ol>\n')

    # field-list
    # ----------
    # set as definition list, styled with CSS

    def visit_field_list(self, node):
        # Keep simple paragraphs in the field_body to enable CSS
        # rule to start body on new line if the label is too long
        classes = 'field-list'
        if (self.is_compactable(node)):
            classes += ' simple'
        self.body.append(self.starttag(node, 'dl', CLASS=classes))

    def depart_field_list(self, node):
        self.body.append('</dl>\n')

    def visit_field(self, node):
        pass

    def depart_field(self, node):
        pass

    def visit_field_name(self, node):
        self.body.append(self.starttag(node, 'dt', ''))

    def depart_field_name(self, node):
        self.body.append('</dt>\n')

    def visit_field_body(self, node):
        self.body.append(self.starttag(node, 'dd', ''))

    def depart_field_body(self, node):
        self.body.append('</dd>\n')

    # footnotes
    # ---------
    # use definition list instead of table for footnote text

    def visit_footnote(self, node):
        if not self.in_footnote_list:
            self.body.append('<dl class="footnote">\n')
            self.in_footnote_list = True

    def depart_footnote(self, node):
        self.body.append('</dd>\n')
        if not isinstance(node.next_node(descend=False, siblings=True),
                          nodes.footnote):
            self.body.append('</dl>\n')
            self.in_footnote_list = False

    # footnote and citation label
    def label_delim(self, node, bracket, superscript):
        """put brackets around label?"""
        if isinstance(node.parent, nodes.footnote):
            if self.settings.footnote_references == 'brackets':
                return bracket
            else:
                return superscript
        assert isinstance(node.parent, nodes.citation)
        return bracket

    def visit_label(self, node):
        # pass parent node to get id into starttag:
        self.body.append(self.starttag(node.parent, 'dt', '', CLASS='label'))
        # footnote/citation backrefs:
        if self.settings.footnote_backlinks:
            backrefs = node.parent['backrefs']
            if len(backrefs) == 1:
                self.body.append('<a class="fn-backref" href="#%s">'
                                 % backrefs[0])
        self.body.append(self.label_delim(node, '[', ''))

    def depart_label(self, node):
        self.body.append(self.label_delim(node, ']', ''))
        if self.settings.footnote_backlinks:
            backrefs = node.parent['backrefs']
            if len(backrefs) == 1:
                self.body.append('</a>')
            elif len(backrefs) > 1:
                # Python 2.4 fails with enumerate(backrefs, 1)
                backlinks = ['<a href="#%s">%s</a>' % (ref, i+1)
                             for (i, ref) in enumerate(backrefs)]
                self.body.append('<span class="fn-backref">(%s)</span>'
                                 % ','.join(backlinks))
        self.body.append('</dt>\n<dd>')

    def visit_generated(self, node):
        if 'sectnum' in node['classes']:
            # get section number (strip trailing no-break-spaces)
            sectnum = node.astext().rstrip(u' ')
            # print sectnum.encode('utf-8')
            self.body.append('<span class="sectnum">%s</span> '
                                    % self.encode(sectnum))
            # Content already processed:
            raise nodes.SkipNode

    # def depart_generated(self, node):
    #     pass

    # Image types to place in an <object> element
    # SVG as <img> supported since IE version 9
    # (but rendering problems remain (see standalonge_rst2xhtml11.xhtml test output)
    # object_image_types = {'.swf': 'application/x-shockwave-flash'}

    # Do not  mark the first child with 'class="first"'
    def visit_list_item(self, node):
        self.body.append(self.starttag(node, 'li', ''))

    # inline literal
    def visit_literal(self, node):
        # special case: "code" role
        classes = node.get('classes', [])
        if 'code' in classes:
            # filter 'code' from class arguments
            node['classes'] = [cls for cls in classes if cls != 'code']
            self.body.append(self.starttag(node, 'code', ''))
            return
        self.body.append(
            self.starttag(node, 'tt', '', CLASS='literal'))
        text = node.astext()
        # remove hard line breaks (except if in a parsed-literal block)
        if not isinstance(node.parent, nodes.literal_block):
            text = text.replace('\n', ' ')
        # Protect text like ``--an-option`` and the regular expression
        # ``[+]?(\d+(\.\d*)?|\.\d+)`` from bad line wrapping
        for token in self.words_and_spaces.findall(text):
            if token.strip() and self.sollbruchstelle.search(token):
                self.body.append('<span class="pre">%s</span>'
                                    % self.encode(token))
            else:
                self.body.append(self.encode(token))
        self.body.append('</tt>')
        # Content already processed:
        raise nodes.SkipNode

    def depart_literal(self, node):
        # skipped unless literal element is from "code" role:
        self.body.append('</code>')

    def visit_literal_block(self, node,):
        self.body.append(self.starttag(node, 'pre', suffix='',
                                       CLASS='literal-block'))

    # Meta tags: 'lang' attribute replaced by 'xml:lang' in XHTML 1.1
    def visit_meta(self, node):
        if node.hasattr('lang'):
            node['xml:lang'] = node['lang']
            del(node['lang'])
        meta = self.emptytag(node, 'meta', **node.non_default_attributes())
        self.add_meta(meta)


    # option-list as definition list, styled with CSS
    # ----------------------------------------------

    def visit_option_list(self, node):
        self.body.append(
            self.starttag(node, 'dl', CLASS='option-list'))

    def depart_option_list(self, node):
        self.body.append('</dl>\n')

    def visit_option_list_item(self, node):
        pass

    def depart_option_list_item(self, node):
        pass

    def visit_option_group(self, node):
        self.body.append(self.starttag(node, 'dt', ''))
        self.body.append('<kbd>')

    def depart_option_group(self, node):
        self.body.append('</kbd></dt>\n')

    def visit_option(self, node):
        self.body.append(self.starttag(node, 'span', '', CLASS='option'))

    def depart_option(self, node):
        self.body.append('</span>')
        if isinstance(node.next_node(descend=False, siblings=True),
                      nodes.option):
            self.body.append(', ')

    def visit_description(self, node):
        self.body.append(self.starttag(node, 'dd', ''))

    def depart_description(self, node):
        self.body.append('</dd>\n')

    # Do not omit <p> tags
    # --------------------
    #
    # The HTML4CSS1 writer does this to "produce
    # visually compact lists (less vertical whitespace)". This writer
    # relies on CSS rules for"visual compactness".
    #
    # * In XHTML 1.1, e.g. a <blockquote> element may not contain
    #   character data, so you cannot drop the <p> tags.
    # * Keeping simple paragraphs in the field_body enables a CSS
    #   rule to start the field-body on a new line if the label is too long
    # * it makes the code simpler.
    #
    # TODO: omit paragraph tags in simple table cells?

    def visit_paragraph(self, node):
        self.body.append(self.starttag(node, 'p', ''))

    def depart_paragraph(self, node):
        self.body.append('</p>')
        if not (isinstance(node.parent, (nodes.list_item, nodes.entry)) and
                (len(node.parent) == 1)
               ):
            self.body.append('\n')

    # tables
    # ------
    # no hard-coded border setting in the table head::

    def visit_table(self, node):
        classes = [cls.strip(u' \t\n')
                   for cls in self.settings.table_style.split(',')]
        tag = self.starttag(node, 'table', CLASS=' '.join(classes))
        self.body.append(tag)

    def depart_table(self, node):
        self.body.append('</table>\n')

    # no hard-coded vertical alignment in table body::

    def visit_tbody(self, node):
        self.write_colspecs()
        self.body.append(self.context.pop()) # '</colgroup>\n' or ''
        self.body.append(self.starttag(node, 'tbody'))


class SimpleListChecker(html4css1.SimpleListChecker):

    """
    Raise `nodes.NodeFound` if non-simple list item is encountered.

    Here "simple" means a list item containing nothing other than a single
    paragraph, a simple list, or a paragraph followed by a simple list.

    This version also checks for simple field lists and docinfo.
    """
    # # debugging: copy of parent methods with `print` calls
    # def default_visit(self, node):
    #     print "found", node.__class__, "in", node.parent.__class__
    #     raise nodes.NodeFound

    def _pass_node(self, node):
        pass

    def _simple_node(self, node):
        # nodes that are never complex (can contain only inline nodes)
        raise nodes.SkipNode

    def visit_list_item(self, node):
        # print "visiting list item", node.__class__
        children = [child for child in node.children
                    if not isinstance(child, nodes.Invisible)]
        # print "has %s visible children" % len(children)
        if (children and isinstance(children[0], nodes.paragraph)
            and (isinstance(children[-1], nodes.bullet_list) or
                 isinstance(children[-1], nodes.enumerated_list) or
                 isinstance(children[-1], nodes.field_list))):
            children.pop()
        # print "%s children remain" % len(children)
        if len(children) <= 1:
            return
        else:
            # print "found", child.__class__, "in", node.__class__
            raise nodes.NodeFound

    # Docinfo nodes:
    visit_docinfo = _pass_node
    visit_author = _simple_node
    visit_authors = visit_list_item
    visit_address = visit_list_item
    visit_contact = _pass_node
    visit_copyright = _simple_node
    visit_date = _simple_node
    visit_organization = _simple_node
    visit_status = _simple_node
    visit_version = visit_list_item

    # Definition list:
    visit_definition_list = _pass_node
    visit_definition_list_item = _pass_node
    visit_term = _pass_node
    visit_classifier = _pass_node
    visit_definition = visit_list_item

    # Field list:
    visit_field_list = _pass_node
    visit_field = _pass_node
    # the field body corresponds to a list item
    visit_field_body = visit_list_item
    visit_field_name = html4css1.SimpleListChecker.invisible_visit

    # Inline nodes
    visit_Text = _pass_node
