# $Id$
# Authors: David Goodger <goodger@python.org>; Dmitry Jemerov
# Copyright: This module has been placed in the public domain.

"""
Directives for references and targets.
"""

__docformat__ = 'reStructuredText'

from docutils import nodes
from docutils.transforms import references
from docutils.parsers.rst import directives


def target_notes(name, arguments, options, content, lineno,
                 content_offset, block_text, state, state_machine):
    """Target footnote generation."""
    pending = nodes.pending(references.TargetNotes)
    pending.details.update(options)
    state_machine.document.note_pending(pending)
    nodelist = [pending]
    return nodelist

target_notes.options = {'class': directives.class_option}
