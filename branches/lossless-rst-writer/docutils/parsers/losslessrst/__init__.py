# $Id$
# Author: Stefan Rank <strank(AT)strank(DOT)info>
# Copyright: This module has been placed in the public domain.

"""
This is ``docutils.parsers.losslessrst`` package.
A subclass of the rst parser that retains additional information
during parsing to allow exact reconstruction of the input.
(See the ``docutils.parsers.rst`` parser for general documentation

The node structure created is fully compatible with the rst parser.
Additional information is stored in one attribute per node.
(named lossless?)

"""

__docformat__ = 'reStructuredText'


import docutils.parsers
import docutils.statemachine
from docutils.parsers.losslessrst import states
from docutils import frontend, nodes


class Parser(docutils.parsers.rst.Parser):

    """The lossless reStructuredText parser."""

    supported = ('losslessrst', 'lossless')
    """Aliases this parser supports."""

    def __init__(self, rfc2822=None, inliner=None):
        if rfc2822:
            self.initial_state = 'RFC2822Body'
        else:
            self.initial_state = 'Body'
        self.state_classes = states.state_classes
        self.inliner = inliner

    def parse(self, inputstring, document):
        """Parse `inputstring` and populate `document`, a document tree."""
        self.setup_parse(inputstring, document)
        self.statemachine = states.RSTStateMachine(
              state_classes=self.state_classes,
              initial_state=self.initial_state,
              debug=document.reporter.debug_flag)
        inputlines = docutils.statemachine.string2lines(
              inputstring, tab_width=document.settings.tab_width,
              convert_whitespace=1)
        self.statemachine.run(inputlines, document, inliner=self.inliner)
        self.finish_parse()


