#! /usr/bin/env python

"""
:Author: David Goodger
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

Tests for states.py.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['doctest_blocks'] = [
["""\
Paragraph.

>>> print "Doctest block."
Doctest block.

Paragraph.
""",
"""\
<document>
    <paragraph>
        Paragraph.
    <doctest_block>
        >>> print "Doctest block."
        Doctest block.
    <paragraph>
        Paragraph.
"""],
["""\
Paragraph.

>>> print "    Indented output."
    Indented output.
""",
"""\
<document>
    <paragraph>
        Paragraph.
    <doctest_block>
        >>> print "    Indented output."
            Indented output.
"""],
["""\
Paragraph.

    >>> print "    Indented block & output."
        Indented block & output.
""",
"""\
<document>
    <paragraph>
        Paragraph.
    <block_quote>
        <doctest_block>
            >>> print "    Indented block & output."
                Indented block & output.
"""],
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
