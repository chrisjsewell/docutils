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

totest['outdenting'] = [
["""\
Anywhere a paragraph would have an effect on the current
indentation level, a comment or list item should also.

+ bullet

This paragraph ends the bullet list item before a block quote.

  Block quote.
""",
"""\
<document>
    <paragraph>
        Anywhere a paragraph would have an effect on the current
        indentation level, a comment or list item should also.
    <bullet_list bullet="+">
        <list_item>
            <paragraph>
                bullet
    <paragraph>
        This paragraph ends the bullet list item before a block quote.
    <block_quote>
        <paragraph>
            Block quote.
"""],
["""\
+ bullet

.. Comments swallow up all indented text following.

  (Therefore this is not a) block quote.

- bullet

  If we want a block quote after this bullet list item,
  we need to use an empty comment:

..

  Block quote.
""",
"""\
<document>
    <bullet_list bullet="+">
        <list_item>
            <paragraph>
                bullet
    <comment>
        Comments swallow up all indented text following.
        \n\
        (Therefore this is not a) block quote.
    <bullet_list bullet="-">
        <list_item>
            <paragraph>
                bullet
            <paragraph>
                If we want a block quote after this bullet list item,
                we need to use an empty comment:
    <comment>
    <block_quote>
        <paragraph>
            Block quote.
"""],
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
