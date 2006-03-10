# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Admonition directives.
"""

__docformat__ = 'reStructuredText'


from docutils.parsers.rst import Directive, states, directives
from docutils import nodes


class GenericAdmonition(Directive):

    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = True

    options = {}
    has_content = True

    # Subclasses must set node_class to the appropriate admonition
    # node class.
    node_class = None

    def run(self):
        if not self.content:
            error = self.state_machine.reporter.error(
                'The "%s" admonition is empty; content required.' % self.name,
                nodes.literal_block(self.block_text, self.block_text),
                line=self.lineno)
            return [error]
        text = '\n'.join(self.content)
        admonition_node = self.node_class(text)
        if self.arguments:
            title_text = self.arguments[0]
            textnodes, messages = self.state.inline_text(title_text,
                                                         self.lineno)
            admonition_node += nodes.title(title_text, '', *textnodes)
            admonition_node += messages
            if self.options.has_key('class'):
                classes = self.options['class']
            else:
                classes = ['admonition-' + nodes.make_id(title_text)]
            admonition_node['classes'] += classes
        self.state.nested_parse(self.content, self.content_offset,
                                admonition_node)
        return [admonition_node]

class Admonition(GenericAdmonition):
    required_arguments = 1
    options = {'class': directives.class_option}
    node_class = nodes.admonition

class Attention(GenericAdmonition):
    node_class = nodes.attention

class Caution(GenericAdmonition):
    node_class = nodes.caution

class Danger(GenericAdmonition):
    node_class = nodes.danger

class Error(GenericAdmonition):
    node_class = nodes.error

class Hint(GenericAdmonition):
    node_class = nodes.hint

class Important(GenericAdmonition):
    node_class = nodes.important

class Note(GenericAdmonition):
    node_class = nodes.note

class Tip(GenericAdmonition):
    node_class = nodes.tip

class Warning(GenericAdmonition):
    node_class = nodes.warning
