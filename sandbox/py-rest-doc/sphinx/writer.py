# -*- coding: utf-8 -*-
"""
    sphinx.writer
    ~~~~~~~~~~~~~

    docutils writers handling Sphinx' custom nodes.

    :copyright: 2007 by Georg Brandl.
    :license: Python license.
"""

from docutils import nodes
from docutils.writers.html4css1 import Writer, HTMLTranslator as BaseTranslator

from .smartypants import sphinx_smarty_pants


class HTMLWriter(Writer):
    def __init__(self, config):
        Writer.__init__(self)
        if config.get('use_smartypants', False):
            self.translator_class = SmartyPantsHTMLTranslator
        else:
            self.translator_class = HTMLTranslator


version_text = {
    'deprecated': 'Deprecated in version %s',
    'versionchanged': 'Changed in version %s',
    'versionadded': 'New in version %s',
}

class HTMLTranslator(BaseTranslator):
    """
    Our custom HTML translator.
    """

    def __init__(self, *args, **kwds):
        self.no_smarty = 0
        BaseTranslator.__init__(self, *args, **kwds)
        self.highlightlang = 'python'

    def visit_desc(self, node):
        self.body.append(self.starttag(node, 'dl', CLASS=node['desctype']))
    def depart_desc(self, node):
        self.body.append('</dl>\n\n')

    def visit_desc_signature(self, node):
        # the id is set automatically
        self.body.append(self.starttag(node, 'dt'))
        # anchor for per-desc interactive data
        if node.parent['desctype'] != 'describe' and node['ids'] and node['first']:
            self.body.append('<!--#%s#-->' % node['ids'][0])
        if node.parent['desctype'] in ('class', 'exception'):
            self.body.append('%s ' % node.parent['desctype'])
    def depart_desc_signature(self, node):
        self.body.append('</dt>\n')

    def visit_desc_classname(self, node):
        self.body.append(self.starttag(node, 'tt', '', CLASS='descclassname'))
    def depart_desc_classname(self, node):
        self.body.append('</tt>')

    def visit_desc_name(self, node):
        self.body.append(self.starttag(node, 'tt', '', CLASS='descname'))
    def depart_desc_name(self, node):
        self.body.append('</tt>')

    def visit_desc_parameterlist(self, node):
        self.body.append('<big>(</big>')
        self.first_param = 1
    def depart_desc_parameterlist(self, node):
        self.body.append('<big>)</big>')

    def visit_desc_parameter(self, node):
        if not self.first_param:
            self.body.append(', ')
        else:
            self.first_param = 0
        if not node.hasattr('noemph'):
            self.body.append('<em>')
    def depart_desc_parameter(self, node):
        if not node.hasattr('noemph'):
            self.body.append('</em>')

    def visit_desc_optional(self, node):
        self.body.append('<span class="optional">[</span>')
    def depart_desc_optional(self, node):
        self.body.append('<span class="optional">]</span>')

    def visit_desc_content(self, node):
        self.body.append(self.starttag(node, 'dd', ''))
    def depart_desc_content(self, node):
        self.body.append('</dd>')

    def visit_refcount(self, node):
        self.body.append(self.starttag(node, 'em', '', CLASS='refcount'))
    def depart_refcount(self, node):
        self.body.append('</em>')

    def visit_versionmodified(self, node):
        self.body.append(self.starttag(node, 'p'))
        text = version_text[node['type']] % node['version']
        if len(node):
            text += ': '
        else:
            text += '.'
        self.body.append('<span class="versionmodified">%s</span>' % text)
    def depart_versionmodified(self, node):
        self.body.append('</p>\n')

    # overwritten -- we don't want source comments to show up in the HTML
    def visit_comment(self, node):
        raise nodes.SkipNode

    # overwritten
    def visit_admonition(self, node, name=''):
        self.body.append(self.start_tag_with_title(
            node, 'div', CLASS=('admonition ' + name)))
        if name and name != 'seealso':
            node.insert(0, nodes.title(name, self.language.labels[name]))
        self.set_first_last(node)

    def visit_seealso(self, node):
        self.visit_admonition(node, 'seealso')
    def depart_seealso(self, node):
        self.depart_admonition(node)

    # overwritten
    def visit_title(self, node, move_ids=1):
        # if we have a section we do our own processing in order
        # to have ids in the hN-tags and not in additional a-tags
        if isinstance(node.parent, nodes.section):
            h_level = self.section_level + self.initial_header_level - 1
            if node.parent.get('ids'):
                attrs = {'ids': node.parent['ids']}
            else:
                attrs = {}
            self.body.append(self.starttag(node, 'h%d' % h_level, '', **attrs))
            self.context.append('</h%d>\n' % h_level)
        else:
            BaseTranslator.visit_title(self, node, move_ids)

    # overwritten
    def visit_literal_block(self, node):
        from .highlighting import highlight_block
        self.body.append(highlight_block(node.rawsource, self.highlightlang))
        raise nodes.SkipNode

    def visit_productionlist(self, node):
        self.body.append(self.starttag(node, 'pre'))
        names = []
        for production in node:
            names.append(production['tokenname'])
        maxlen = max(len(name) for name in names)
        for production in node:
            if production['tokenname']:
                self.body.append(self.starttag(production, 'strong', ''))
                self.body.append(production['tokenname'].ljust(maxlen) +
                                 '</strong> ::= ')
                lastname = production['tokenname']
            else:
                self.body.append('%s     ' % (' '*len(lastname)))
            production.walkabout(self)
            self.body.append('\n')
        self.body.append('</pre>\n')
        raise nodes.SkipNode
    def depart_productionlist(self, node):
        pass

    def visit_production(self, node):
        pass
    def depart_production(self, node):
        pass

    def visit_centered(self, node):
        self.body.append(self.starttag(node, 'center') + '<strong>')
    def depart_centered(self, node):
        self.body.append('</strong></center>')

    def visit_compact_paragraph(self, node):
        pass
    def depart_compact_paragraph(self, node):
        pass

    def visit_highlightlang(self, node):
        self.highlightlang = node['lang']
    def depart_highlightlang(self, node):
        pass

    def visit_toctree(self, node):
        # this only happens when formatting a toc from env.tocs -- in this
        # case we don't want to include the subtree
        raise nodes.SkipNode

    def visit_index(self, node):
        raise nodes.SkipNode


class SmartyPantsHTMLTranslator(HTMLTranslator):
    """
    Handle ordinary text via smartypants, converting quotes and dashes
    to the correct entities.
    """

    def __init__(self, *args, **kwds):
        self.no_smarty = 0
        HTMLTranslator.__init__(self, *args, **kwds)

    def visit_literal(self, node):
        self.no_smarty += 1
        try:
            # this raises SkipNode
            HTMLTranslator.visit_literal(self, node)
        finally:
            self.no_smarty -= 1

    def visit_productionlist(self, node):
        self.no_smarty += 1
        try:
            HTMLTranslator.visit_productionlist(self, node)
        finally:
            self.no_smarty -= 1

    def encode(self, text):
        text = HTMLTranslator.encode(self, text)
        if self.no_smarty <= 0:
            text = sphinx_smarty_pants(text)
        return text
