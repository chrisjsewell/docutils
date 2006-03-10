#! /usr/bin/env python

# Author: Felix Wiemann
# Contact: Felix_Wiemann@ososo.de
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Tests for the "epigraph" directive.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['epigraphs'] = [
["""\
.. epigraph::

   This is an epigraph.

   -- Attribution
""",
"""\
<document source="test data">
    <block_quote classes="epigraph">
        <paragraph>
            This is an epigraph.
        <attribution>
            Attribution
"""],
# TODO: Add class option.
# BUG: No content required.
["""\
.. epigraph::
""",
"""\
<document source="test data">
    <block_quote classes="epigraph">
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
