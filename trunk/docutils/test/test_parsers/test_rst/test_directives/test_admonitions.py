#! /usr/bin/env python

"""
:Author: David Goodger
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

Tests for admonitions.py directives.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['admonitions'] = [
["""\
.. Attention:: Directives at large.

.. Note:: This is a note.

.. Tip:: 15% if the
   service is good.

.. Hint:: It's bigger than a bread box.

- .. WARNING:: Strong prose may provoke extreme mental exertion.
     Reader discretion is strongly advised.
- .. Error:: Does not compute.

.. Caution::

   Don't take any wooden nickels.

.. DANGER:: Mad scientist at work!

.. Important::
   - Wash behind your ears.
   - Clean up your room.
   - Call your mother.
   - Back up your data.
""",
"""\
<document source="test data">
    <attention>
        <paragraph>
            Directives at large.
    <note>
        <paragraph>
            This is a note.
    <tip>
        <paragraph>
            15% if the
            service is good.
    <hint>
        <paragraph>
            It's bigger than a bread box.
    <bullet_list bullet="-">
        <list_item>
            <warning>
                <paragraph>
                    Strong prose may provoke extreme mental exertion.
                    Reader discretion is strongly advised.
        <list_item>
            <error>
                <paragraph>
                    Does not compute.
    <caution>
        <paragraph>
            Don't take any wooden nickels.
    <danger>
        <paragraph>
            Mad scientist at work!
    <important>
        <bullet_list bullet="-">
            <list_item>
                <paragraph>
                    Wash behind your ears.
            <list_item>
                <paragraph>
                    Clean up your room.
            <list_item>
                <paragraph>
                    Call your mother.
            <list_item>
                <paragraph>
                    Back up your data.
"""],
["""\
.. note:: One-line notes.
.. note:: One after the other.
.. note:: No blank lines in-between.
""",
"""\
<document source="test data">
    <note>
        <paragraph>
            One-line notes.
    <note>
        <paragraph>
            One after the other.
    <note>
        <paragraph>
            No blank lines in-between.
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
