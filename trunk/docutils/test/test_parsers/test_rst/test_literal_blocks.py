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

totest['literal_blocks'] = [
["""\
A paragraph::

    A literal block.
""",
"""\
<document source="test data">
    <paragraph>
        A paragraph:
    <literal_block xml:space="1">
        A literal block.
"""],
["""\
A paragraph with a space after the colons:: \n\

    A literal block.
""",
"""\
<document source="test data">
    <paragraph>
        A paragraph with a space after the colons:
    <literal_block xml:space="1">
        A literal block.
"""],
["""\
A paragraph::

    A literal block.

Another paragraph::

    Another literal block.
    With two blank lines following.


A final paragraph.
""",
"""\
<document source="test data">
    <paragraph>
        A paragraph:
    <literal_block xml:space="1">
        A literal block.
    <paragraph>
        Another paragraph:
    <literal_block xml:space="1">
        Another literal block.
        With two blank lines following.
    <paragraph>
        A final paragraph.
"""],
["""\
A paragraph
on more than
one line::

    A literal block.
""",
"""\
<document source="test data">
    <paragraph>
        A paragraph
        on more than
        one line:
    <literal_block xml:space="1">
        A literal block.
"""],
["""\
A paragraph
on more than
one line::
    A literal block
    with no blank line above.
""",
"""\
<document source="test data">
    <paragraph>
        A paragraph
        on more than
        one line:
    <system_message level="3" line="4" source="test data" type="ERROR">
        <paragraph>
            Unexpected indentation.
    <literal_block xml:space="1">
        A literal block
        with no blank line above.
"""],
["""\
A paragraph::

    A literal block.
no blank line
""",
"""\
<document source="test data">
    <paragraph>
        A paragraph:
    <literal_block xml:space="1">
        A literal block.
    <system_message level="2" line="4" source="test data" type="WARNING">
        <paragraph>
            Literal block ends without a blank line; unexpected unindent.
    <paragraph>
        no blank line
"""],
["""\
A paragraph: ::

    A literal block.
""",
"""\
<document source="test data">
    <paragraph>
        A paragraph:
    <literal_block xml:space="1">
        A literal block.
"""],
["""\
A paragraph:

::

    A literal block.
""",
"""\
<document source="test data">
    <paragraph>
        A paragraph:
    <literal_block xml:space="1">
        A literal block.
"""],
["""\
A paragraph:
::

    A literal block.
""",
"""\
<document source="test data">
    <paragraph>
        A paragraph:
    <literal_block xml:space="1">
        A literal block.
"""],
["""\
A paragraph::

Not a literal block.
""",
"""\
<document source="test data">
    <paragraph>
        A paragraph:
    <system_message level="2" line="2" source="test data" type="WARNING">
        <paragraph>
            Literal block expected; none found.
    <paragraph>
        Not a literal block.
"""],
["""\
A paragraph::

    A wonky literal block.
  Literal line 2.

    Literal line 3.
""",
"""\
<document source="test data">
    <paragraph>
        A paragraph:
    <literal_block xml:space="1">
          A wonky literal block.
        Literal line 2.
        \n\
          Literal line 3.
"""],
["""\
EOF, even though a literal block is indicated::
""",
"""\
<document source="test data">
    <paragraph>
        EOF, even though a literal block is indicated:
    <system_message level="2" line="2" source="test data" type="WARNING">
        <paragraph>
            Literal block expected; none found.
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
