#! /usr/bin/env python

"""
:Author: David Goodger, Dmitry Jemerov
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

Directives for document parts.
"""

__docformat__ = 'reStructuredText'

from docutils import nodes
from docutils.transforms import parts
from docutils.parsers.rst import directives


backlinks_values = ('top', 'entry', 'none')

def backlinks(arg):
    value = directives.choice(arg, backlinks_values)
    if value == 'none':
        return None
    else:
        return value

contents_option_spec = {'depth': int,
                        'local': directives.flag,
                        'backlinks': backlinks}
                        #'qa': unchanged}

def contents(match, type_name, data, state, state_machine, option_presets):
    """Table of contents."""
    lineno = state_machine.abs_line_number()
    line_offset = state_machine.line_offset
    datablock, indent, offset, blank_finish = \
          state_machine.get_first_known_indented(match.end(), until_blank=1)
    blocktext = '\n'.join(state_machine.input_lines[
          line_offset : line_offset + len(datablock) + 1])
    for i in range(len(datablock)):
        if datablock[i][:1] == ':':
            attlines = datablock[i:]
            datablock = datablock[:i]
            break
    else:
        attlines = []
        i = 0
    titletext = ' '.join([line.strip() for line in datablock])
    if titletext:
        textnodes, messages = state.inline_text(titletext, lineno)
        title = nodes.title(titletext, '', *textnodes)
    else:
        messages = []
        title = None
    pending = nodes.pending(parts.Contents, 'first writer', {'title': title},
                            blocktext)
    if attlines:
        success, data, blank_finish = state.parse_extension_options(
              contents_option_spec, attlines, blank_finish)
        if success:                     # data is a dict of options
            pending.details.update(data)
        else:                           # data is an error string
            error = state_machine.reporter.error(
                  'Error in "%s" directive options:\n%s.'
                  % (match.group(1), data), '',
                  nodes.literal_block(blocktext, blocktext), line=lineno)
            return [error] + messages, blank_finish
    state_machine.document.note_pending(pending)
    return [pending] + messages, blank_finish

sectnum_option_spec = {'depth': int}

def sectnum(match, type_name, data, state, state_machine, option_presets):
    """Automatic section numbering."""
    lineno = state_machine.abs_line_number()
    line_offset = state_machine.line_offset
    datablock, indent, offset, blank_finish = \
          state_machine.get_first_known_indented(match.end(), until_blank=1)
    pending = nodes.pending(parts.SectNum, 'last reader', {})
    success, data, blank_finish = state.parse_extension_options(
          sectnum_option_spec, datablock, blank_finish)
    if success:                     # data is a dict of options
        pending.details.update(data)
    else:                           # data is an error string
        blocktext = '\n'.join(state_machine.input_lines[
            line_offset : line_offset + len(datablock) + 1])
        error = state_machine.reporter.error(
              'Error in "%s" directive options:\n%s.'
              % (match.group(1), data), '',
              nodes.literal_block(blocktext, blocktext), line=lineno)
        return [error], blank_finish
    state_machine.document.note_pending(pending)
    return [pending], blank_finish
