#! /usr/bin/env python

"""
:Author: David Goodger
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

Tests for docutils.transforms.universal.Messages.
"""

from __init__ import DocutilsTestSupport
from docutils.transforms.universal import Messages
from docutils.transforms.references import Substitutions
from docutils.parsers.rst import Parser


def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s

totest = {}

totest['system_message_sections'] = ((Substitutions, Messages,), [
["""\
This |unknown substitution| will generate a system message, thanks to
the ``Substitutions`` transform. The ``Messages`` transform will
generate a "System Messages" section.

(A second copy of the system message is tacked on to the end of the
doctree by the test framework.)
""",
"""\
<document>
    <paragraph>
        This \n\
        <problematic id="id2" refid="id1">
            |unknown substitution|
         will generate a system message, thanks to
        the \n\
        <literal>
            Substitutions
         transform. The \n\
        <literal>
            Messages
         transform will
        generate a "System Messages" section.
    <paragraph>
        (A second copy of the system message is tacked on to the end of the
        doctree by the test framework.)
    <section class="system-messages">
        <title>
            Docutils System Messages
        <system_message backrefs="id2" id="id1" level="3" type="ERROR">
            <paragraph>
                Undefined substitution referenced: "unknown substitution".
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
