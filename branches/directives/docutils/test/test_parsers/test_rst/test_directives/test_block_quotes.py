#! /usr/bin/env python

# Author: Felix Wiemann
# Contact: Felix_Wiemann@ososo.de
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Tests for the block quote directives "epigraph", "highlights", and
"pull-quote".
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

generic_tests = [
["""\
.. %s::

   This is a block quote.

   -- Attribution
""",
"""\
<document source="test data">
    <block_quote classes="%s">
        <paragraph>
            This is a block quote.
        <attribution>
            Attribution
"""],
# TODO: Add class option.
# BUG: No content required.
["""\
.. %s::
""",
"""\
<document source="test data">
    <block_quote classes="%s">
"""],
]

totest = {}
for block_quote_type in ('epigraph', 'highlights', 'pull-quote'):
   totest[block_quote_type] = [
       [text % block_quote_type for text in pair] for pair in generic_tests]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
