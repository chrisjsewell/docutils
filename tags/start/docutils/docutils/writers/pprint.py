#! /usr/bin/env python

"""
:Authors: David Goodger
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

Simple internal document tree Writer, writes indented pseudo-XML.
"""

__docformat__ = 'reStructuredText'


from docutils import writers


class Writer(writers.Writer):

    output = None
    """Final translated form of `document`."""

    def translate(self):
        self.output = self.document.pformat()

    def record(self):
        self.recordfile(self.output, self.destination)
