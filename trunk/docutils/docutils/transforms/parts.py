#! /usr/bin/env python
"""
:Authors: David Goodger, Ueli Schlaepfer
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

Transforms related to document parts.

- `Contents`: Used to build a table of contents.
"""

__docformat__ = 'reStructuredText'


import re
import sys
from docutils import nodes, utils
from docutils.transforms import TransformError, Transform


class Contents(Transform):

    """
    This transform generates a table of contents from the entire document tree
    or from a single branch.  It locates "section" elements and builds them
    into a nested bullet list, which is placed within a "topic".  A title is
    either explicitly specified, taken from the appropriate language module,
    or omitted (local table of contents).  The depth may be specified.
    Two-way references between the table of contents and section titles are
    generated (requires Writer support).

    This transform requires a startnode, which which contains generation
    options and provides the location for the generated table of contents (the
    startnode is replaced by the table of contents "topic").
    """

    def transform(self):
        topic = nodes.topic(CLASS='contents')
        title = self.startnode.details['title']
        if self.startnode.details.has_key('local'):
            startnode = self.startnode.parent
            # @@@ generate an error if the startnode (directive) not at
            # section/document top-level? Drag it up until it is?
            while not isinstance(startnode, nodes.Structural):
                startnode = startnode.parent
        else:
            startnode = self.document
            if not title:
                title = nodes.title('', self.language.labels['contents'])
        contents = self.build_contents(startnode)
        if len(contents):
            if title:
                topic['name'] = title.astext()
                topic += title
            else:
                topic['name'] = self.language.labels['contents']
            topic += contents
            self.startnode.parent.replace(self.startnode, topic)
            self.document.note_implicit_target(topic)
        else:
            self.startnode.parent.remove(self.startnode)

    def build_contents(self, node, level=0):
        level += 1
        sections = []
        i = len(node) - 1
        while i >= 0 and isinstance(node[i], nodes.section):
            sections.append(node[i])
            i -= 1
        sections.reverse()
        entries = []
        depth = self.startnode.details.get('depth', sys.maxint)
        for section in sections:
            title = section[0]
            entrytext = self.copy_and_filter(title)
            reference = nodes.reference('', '', refid=section['id'],
                                        *entrytext)
            entry = nodes.paragraph('', '', reference)
            item = nodes.list_item('', entry)
            itemid = self.document.set_id(item)
            title['refid'] = itemid
            if level < depth:
                subsects = self.build_contents(section, level)
                item += subsects
            entries.append(item)
        if entries:
            entries = nodes.bullet_list('', *entries)
        return entries

    def copy_and_filter(self, node):
        """Return a copy of a title, with references, images, etc. removed."""
        visitor = ContentsFilter(self.document)
        node.walkabout(visitor)
        return visitor.get_entry_text()


class ContentsFilter(nodes.TreeCopyVisitor):

    def get_entry_text(self):
        return self.get_tree_copy().get_children()

    def visit_citation_reference(self, node):
        raise nodes.SkipNode

    def visit_footnote_reference(self, node):
        raise nodes.SkipNode

    def visit_image(self, node):
        if node.hasattr('alt'):
            self.parent.append(nodes.Text(node['alt']))
        raise nodes.SkipNode

    def ignore_node_but_process_children(self, node):
        raise nodes.SkipDeparture

    visit_interpreted = ignore_node_but_process_children
    visit_problematic = ignore_node_but_process_children
    visit_reference = ignore_node_but_process_children
    visit_target = ignore_node_but_process_children
