# Author: David Goodger
# Contact: goodger@python.org
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Directives for additional body elements.

See `docutils.parsers.rst.directives` for API details.
"""

__docformat__ = 'reStructuredText'


import sys
from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.parsers.rst.roles import set_classes


# XXX David, can you think of a nice name for this?
class TopicOrSidebarThingy(Directive):

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True
    options = {'class': directives.class_option}

    # Must be set in subclasses.
    node_class = None

    def run(self):
        if not (self.state_machine.match_titles
                or isinstance(self.state_machine.node, nodes.sidebar)):
            error = self.state_machine.reporter.error(
                'The "%s" directive may not be used within topics or body '
                'elements.' % self.name, nodes.literal_block(
                self.block_text, self.block_text), line=self.lineno)
            return [error]
        if not self.content:
            warning = self.state_machine.reporter.warning(
                'Content block expected for the "%s" directive; none found.'
                % self.name, nodes.literal_block(
                self.block_text, self.block_text), line=self.lineno)
            return [warning]
        title_text = self.arguments[0]
        textnodes, messages = self.state.inline_text(title_text, self.lineno)
        titles = [nodes.title(title_text, '', *textnodes)]
        # Sidebar uses this code.
        if self.options.has_key('subtitle'):
            textnodes, more_messages = self.state.inline_text(
                self.options['subtitle'], self.lineno)
            titles.append(nodes.subtitle(self.options['subtitle'], '',
                                         *textnodes))
            messages.extend(more_messages)
        text = '\n'.join(self.content)
        node = self.node_class(text, *(titles + messages))
        node['classes'] += self.options.get('class', [])
        if text:
            self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class Topic(TopicOrSidebarThingy):

    node_class = nodes.topic


class Sidebar(TopicOrSidebarThingy):

    node_class = nodes.sidebar

    options = TopicOrSidebarThingy.options.copy()
    options['subtitle'] = directives.unchanged_required

    def run(self):
        if isinstance(self.state_machine.node, nodes.sidebar):
            error = self.state_machine.reporter.error(
                'The "%s" directive may not be used within a sidebar element.'
                % self.name, nodes.literal_block(
                self.block_text, self.block_text), line=self.lineno)
            return [error]
        return TopicOrSidebarThingy.run(self)


def line_block(name, arguments, options, content, lineno,
               content_offset, block_text, state, state_machine):
    if not content:
        warning = state_machine.reporter.warning(
            'Content block expected for the "%s" directive; none found.'
            % name, nodes.literal_block(block_text, block_text), line=lineno)
        return [warning]
    block = nodes.line_block(classes=options.get('class', []))
    node_list = [block]
    for line_text in content:
        text_nodes, messages = state.inline_text(line_text.strip(),
                                                 lineno + content_offset)
        line = nodes.line(line_text, '', *text_nodes)
        if line_text.strip():
            line.indent = len(line_text) - len(line_text.lstrip())
        block += line
        node_list.extend(messages)
        content_offset += 1
    state.nest_line_block_lines(block)
    return node_list

line_block.options = {'class': directives.class_option}
line_block.content = 1

def parsed_literal(name, arguments, options, content, lineno,
                   content_offset, block_text, state, state_machine):
    set_classes(options)
    return block(name, arguments, options, content, lineno,
                 content_offset, block_text, state, state_machine,
                 node_class=nodes.literal_block)

parsed_literal.options = {'class': directives.class_option}
parsed_literal.content = 1

def block(name, arguments, options, content, lineno,
          content_offset, block_text, state, state_machine, node_class):
    if not content:
        warning = state_machine.reporter.warning(
            'Content block expected for the "%s" directive; none found.'
            % name, nodes.literal_block(block_text, block_text), line=lineno)
        return [warning]
    text = '\n'.join(content)
    text_nodes, messages = state.inline_text(text, lineno)
    node = node_class(text, '', *text_nodes, **options)
    node.line = content_offset + 1
    return [node] + messages

def rubric(name, arguments, options, content, lineno,
             content_offset, block_text, state, state_machine):
    rubric_text = arguments[0]
    textnodes, messages = state.inline_text(rubric_text, lineno)
    rubric = nodes.rubric(rubric_text, '', *textnodes, **options)
    return [rubric] + messages

rubric.arguments = (1, 0, 1)
rubric.options = {'class': directives.class_option}

def epigraph(name, arguments, options, content, lineno,
             content_offset, block_text, state, state_machine):
    block_quote, messages = state.block_quote(content, content_offset)
    block_quote['classes'].append('epigraph')
    return [block_quote] + messages

epigraph.content = 1

def highlights(name, arguments, options, content, lineno,
             content_offset, block_text, state, state_machine):
    block_quote, messages = state.block_quote(content, content_offset)
    block_quote['classes'].append('highlights')
    return [block_quote] + messages

highlights.content = 1

def pull_quote(name, arguments, options, content, lineno,
             content_offset, block_text, state, state_machine):
    block_quote, messages = state.block_quote(content, content_offset)
    block_quote['classes'].append('pull-quote')
    return [block_quote] + messages

pull_quote.content = 1

def compound(name, arguments, options, content, lineno,
             content_offset, block_text, state, state_machine):
    text = '\n'.join(content)
    if not text:
        error = state_machine.reporter.error(
            'The "%s" directive is empty; content required.' % name,
            nodes.literal_block(block_text, block_text), line=lineno)
        return [error]
    node = nodes.compound(text)
    node['classes'] += options.get('class', [])
    state.nested_parse(content, content_offset, node)
    return [node]

compound.options = {'class': directives.class_option}
compound.content = 1

def container(name, arguments, options, content, lineno,
              content_offset, block_text, state, state_machine):
    text = '\n'.join(content)
    if not text:
        error = state_machine.reporter.error(
            'The "%s" directive is empty; content required.' % name,
            nodes.literal_block(block_text, block_text), line=lineno)
        return [error]
    try:
        if arguments:
            classes = directives.class_option(arguments[0])
        else:
            classes = []
    except ValueError:
        error = state_machine.reporter.error(
            'Invalid class attribute value for "%s" directive: "%s".'
            % (name, arguments[0]),
            nodes.literal_block(block_text, block_text), line=lineno)
        return [error]
    node = nodes.container(text)
    node['classes'].extend(classes)
    state.nested_parse(content, content_offset, node)
    return [node]

container.arguments = (0, 1, 1)
container.content = 1
