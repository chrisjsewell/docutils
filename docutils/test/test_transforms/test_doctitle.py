#! /usr/bin/env python

# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Tests for docutils.transforms.frontmatter.DocTitle.
"""

from __init__ import DocutilsTestSupport
from docutils.transforms.frontmatter import DocTitle
from docutils.parsers.rst import Parser


def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s

totest = {}

totest['section_headers'] = ((DocTitle,), [
["""\
.. test title promotion

Title
=====

Paragraph.
""",
"""\
<document ids="title" names="title" source="test data">
    <title>
        Title
    <comment xml:space="preserve">
        test title promotion
    <paragraph>
        Paragraph.
"""],
["""\
Title
=====
Paragraph (no blank line).
""",
"""\
<document ids="title" names="title" source="test data">
    <title>
        Title
    <paragraph>
        Paragraph (no blank line).
"""],
["""\
Paragraph.

Title
=====

Paragraph.
""",
"""\
<document source="test data">
    <paragraph>
        Paragraph.
    <section ids="title" names="title">
        <title>
            Title
        <paragraph>
            Paragraph.
"""],
["""\
Title
=====

Subtitle
--------

Test title & subtitle.
""",
"""\
<document ids="title" names="title" source="test data">
    <title>
        Title
    <subtitle ids="subtitle" names="subtitle">
        Subtitle
    <paragraph>
        Test title & subtitle.
"""],
["""\
Title
====

Test short underline.
""",
"""\
<document ids="title" names="title" source="test data">
    <title>
        Title
    <system_message level="2" line="2" source="test data" type="WARNING">
        <paragraph>
            Title underline too short.
        <literal_block xml:space="preserve">
            Title
            ====
    <paragraph>
        Test short underline.
"""],
["""\
=======
 Long    Title
=======

Test long title and space normalization.
The system_message should move after the document title
(it was before the beginning of the section).
""",
"""\
<document ids="long-title" names="long title" source="test data">
    <title>
        Long    Title
    <system_message level="2" line="1" source="test data" type="WARNING">
        <paragraph>
            Title overline too short.
        <literal_block xml:space="preserve">
            =======
             Long    Title
            =======
    <paragraph>
        Test long title and space normalization.
        The system_message should move after the document title
        (it was before the beginning of the section).
"""],
["""\
.. Test multiple second-level titles.

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.

Title 3
-------
Paragraph 3.
""",
"""\
<document ids="title-1" names="title 1" source="test data">
    <title>
        Title 1
    <comment xml:space="preserve">
        Test multiple second-level titles.
    <paragraph>
        Paragraph 1.
    <section ids="title-2" names="title 2">
        <title>
            Title 2
        <paragraph>
            Paragraph 2.
    <section ids="title-3" names="title 3">
        <title>
            Title 3
        <paragraph>
            Paragraph 3.
"""],
["""\
.. |foo| replace:: bar

.. _invisible target:

Title
=====
This title should be the document title despite the
substitution_definition.
""",
"""\
<document ids="title" names="title" source="test data">
    <title>
        Title
    <substitution_definition names="foo">
        bar
    <target ids="invisible-target" names="invisible target">
    <paragraph>
        This title should be the document title despite the
        substitution_definition.
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
