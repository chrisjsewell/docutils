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

totest['comments'] = [
["""\
.. A comment

Paragraph.
""",
"""\
<document>
    <comment>
        A comment
    <paragraph>
        Paragraph.
"""],
["""\
.. A comment
   block.

Paragraph.
""",
"""\
<document>
    <comment>
        A comment
        block.
    <paragraph>
        Paragraph.
"""],
["""\
..
   A comment consisting of multiple lines
   starting on the line after the
   explicit markup start.
""",
"""\
<document>
    <comment>
        A comment consisting of multiple lines
        starting on the line after the
        explicit markup start.
"""],
["""\
.. A comment.
.. Another.

Paragraph.
""",
"""\
<document>
    <comment>
        A comment.
    <comment>
        Another.
    <paragraph>
        Paragraph.
"""],
["""\
.. A comment
no blank line

Paragraph.
""",
"""\
<document>
    <comment>
        A comment
    <system_message level="2" type="WARNING">
        <paragraph>
            Explicit markup ends without a blank line; unexpected unindent at line 2.
    <paragraph>
        no blank line
    <paragraph>
        Paragraph.
"""],
["""\
.. A comment.
.. Another.
no blank line

Paragraph.
""",
"""\
<document>
    <comment>
        A comment.
    <comment>
        Another.
    <system_message level="2" type="WARNING">
        <paragraph>
            Explicit markup ends without a blank line; unexpected unindent at line 3.
    <paragraph>
        no blank line
    <paragraph>
        Paragraph.
"""],
["""\
.. A comment::

Paragraph.
""",
"""\
<document>
    <comment>
        A comment::
    <paragraph>
        Paragraph.
"""],
["""\
..
   comment::

The extra newline before the comment text prevents
the parser from recognizing a directive.
""",
"""\
<document>
    <comment>
        comment::
    <paragraph>
        The extra newline before the comment text prevents
        the parser from recognizing a directive.
"""],
["""\
..
   _comment: http://example.org

The extra newline before the comment text prevents
the parser from recognizing a hyperlink target.
""",
"""\
<document>
    <comment>
        _comment: http://example.org
    <paragraph>
        The extra newline before the comment text prevents
        the parser from recognizing a hyperlink target.
"""],
["""\
..
   [comment] Not a citation.

The extra newline before the comment text prevents
the parser from recognizing a citation.
""",
"""\
<document>
    <comment>
        [comment] Not a citation.
    <paragraph>
        The extra newline before the comment text prevents
        the parser from recognizing a citation.
"""],
["""\
..
   |comment| image:: bogus.png

The extra newline before the comment text prevents
the parser from recognizing a substitution definition.
""",
"""\
<document>
    <comment>
        |comment| image:: bogus.png
    <paragraph>
        The extra newline before the comment text prevents
        the parser from recognizing a substitution definition.
"""],
["""\
.. Next is an empty comment, which serves to end this comment and
   prevents the following block quote being swallowed up.

..

    A block quote.
""",
"""\
<document>
    <comment>
        Next is an empty comment, which serves to end this comment and
        prevents the following block quote being swallowed up.
    <comment>
    <block_quote>
        <paragraph>
            A block quote.
"""],
["""\
term 1
  definition 1

  .. a comment

term 2
  definition 2
""",
"""\
<document>
    <definition_list>
        <definition_list_item>
            <term>
                term 1
            <definition>
                <paragraph>
                    definition 1
                <comment>
                    a comment
        <definition_list_item>
            <term>
                term 2
            <definition>
                <paragraph>
                    definition 2
"""],
["""\
term 1
  definition 1

.. a comment

term 2
  definition 2
""",
"""\
<document>
    <definition_list>
        <definition_list_item>
            <term>
                term 1
            <definition>
                <paragraph>
                    definition 1
    <comment>
        a comment
    <definition_list>
        <definition_list_item>
            <term>
                term 2
            <definition>
                <paragraph>
                    definition 2
"""],
["""\
+ bullet paragraph 1

  bullet paragraph 2

  .. comment between bullet paragraphs 2 and 3

  bullet paragraph 3
""",
"""\
<document>
    <bullet_list bullet="+">
        <list_item>
            <paragraph>
                bullet paragraph 1
            <paragraph>
                bullet paragraph 2
            <comment>
                comment between bullet paragraphs 2 and 3
            <paragraph>
                bullet paragraph 3
"""],
["""\
+ bullet paragraph 1

  .. comment between bullet paragraphs 1 (leader) and 2

  bullet paragraph 2
""",
"""\
<document>
    <bullet_list bullet="+">
        <list_item>
            <paragraph>
                bullet paragraph 1
            <comment>
                comment between bullet paragraphs 1 (leader) and 2
            <paragraph>
                bullet paragraph 2
"""],
["""\
+ bullet

  .. trailing comment
""",
"""\
<document>
    <bullet_list bullet="+">
        <list_item>
            <paragraph>
                bullet
            <comment>
                trailing comment
"""],
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
