#! /usr/bin/env python

"""
:Author: David Goodger
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

Tests for `docutils.transforms.parts.Contents` (via
`docutils.transforms.universal.LastReaderPending`).
"""

from __init__ import DocutilsTestSupport
from docutils.transforms.universal import LastReaderPending
from docutils.transforms.references import Substitutions
from docutils.parsers.rst import Parser


def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s

totest = {}

totest['tables_of_contents'] = ((Substitutions, LastReaderPending,), [
["""\
.. contents::

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.

Title 3
```````
Paragraph 3.

Title 4
-------
Paragraph 4.
""",
"""\
<document>
    <topic class="contents" id="contents" name="contents">
        <title>
            Contents
        <bullet_list>
            <list_item id="id1">
                <paragraph>
                    <reference refid="title-1">
                        Title 1
                <bullet_list>
                    <list_item id="id2">
                        <paragraph>
                            <reference refid="title-2">
                                Title 2
                        <bullet_list>
                            <list_item id="id3">
                                <paragraph>
                                    <reference refid="title-3">
                                        Title 3
                    <list_item id="id4">
                        <paragraph>
                            <reference refid="title-4">
                                Title 4
    <section id="title-1" name="title 1">
        <title refid="id1">
            Title 1
        <paragraph>
            Paragraph 1.
        <section id="title-2" name="title 2">
            <title refid="id2">
                Title 2
            <paragraph>
                Paragraph 2.
            <section id="title-3" name="title 3">
                <title refid="id3">
                    Title 3
                <paragraph>
                    Paragraph 3.
        <section id="title-4" name="title 4">
            <title refid="id4">
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
.. contents:: Table of Contents

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.
""",
"""\
<document>
    <topic class="contents" id="table-of-contents" name="table of contents">
        <title>
            Table of Contents
        <bullet_list>
            <list_item id="id1">
                <paragraph>
                    <reference refid="title-1">
                        Title 1
                <bullet_list>
                    <list_item id="id2">
                        <paragraph>
                            <reference refid="title-2">
                                Title 2
    <section id="title-1" name="title 1">
        <title refid="id1">
            Title 1
        <paragraph>
            Paragraph 1.
        <section id="title-2" name="title 2">
            <title refid="id2">
                Title 2
            <paragraph>
                Paragraph 2.
"""],
["""\
.. contents:: There's an image in Title 2

Title 1
=======
Paragraph 1.

|Title 2|
=========
Paragraph 2.

.. |Title 2| image:: title2.png
""",
"""\
<document>
    <topic class="contents" id="there-s-an-image-in-title-2" name="there's an image in title 2">
        <title>
            There's an image in Title 2
        <bullet_list>
            <list_item id="id1">
                <paragraph>
                    <reference refid="title-1">
                        Title 1
            <list_item id="id2">
                <paragraph>
                    <reference refid="title-2">
                        Title 2
    <section id="title-1" name="title 1">
        <title refid="id1">
            Title 1
        <paragraph>
            Paragraph 1.
    <section id="title-2" name="title 2">
        <title refid="id2">
            <image alt="Title 2" uri="title2.png">
        <paragraph>
            Paragraph 2.
        <substitution_definition name="title 2">
            <image alt="Title 2" uri="title2.png">
"""],                                   # emacs cruft: "
["""\
.. contents::
   :depth: 2

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.

Title 3
```````
Paragraph 3.

Title 4
-------
Paragraph 4.
""",
"""\
<document>
    <topic class="contents" id="contents" name="contents">
        <title>
            Contents
        <bullet_list>
            <list_item id="id1">
                <paragraph>
                    <reference refid="title-1">
                        Title 1
                <bullet_list>
                    <list_item id="id2">
                        <paragraph>
                            <reference refid="title-2">
                                Title 2
                    <list_item id="id3">
                        <paragraph>
                            <reference refid="title-4">
                                Title 4
    <section id="title-1" name="title 1">
        <title refid="id1">
            Title 1
        <paragraph>
            Paragraph 1.
        <section id="title-2" name="title 2">
            <title refid="id2">
                Title 2
            <paragraph>
                Paragraph 2.
            <section id="title-3" name="title 3">
                <title>
                    Title 3
                <paragraph>
                    Paragraph 3.
        <section id="title-4" name="title 4">
            <title refid="id3">
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
Title 1
=======

.. contents::
   :local:

Paragraph 1.

Title 2
-------
Paragraph 2.

Title 3
```````
Paragraph 3.

Title 4
-------
Paragraph 4.
""",
"""\
<document>
    <section id="title-1" name="title 1">
        <title>
            Title 1
        <topic class="contents" id="contents" name="contents">
            <bullet_list>
                <list_item id="id1">
                    <paragraph>
                        <reference refid="title-2">
                            Title 2
                    <bullet_list>
                        <list_item id="id2">
                            <paragraph>
                                <reference refid="title-3">
                                    Title 3
                <list_item id="id3">
                    <paragraph>
                        <reference refid="title-4">
                            Title 4
        <paragraph>
            Paragraph 1.
        <section id="title-2" name="title 2">
            <title refid="id1">
                Title 2
            <paragraph>
                Paragraph 2.
            <section id="title-3" name="title 3">
                <title refid="id2">
                    Title 3
                <paragraph>
                    Paragraph 3.
        <section id="title-4" name="title 4">
            <title refid="id3">
                Title 4
            <paragraph>
                Paragraph 4.
"""],
["""\
.. contents::
   :local:

Test duplicate name "Contents".

Contents
--------
Paragraph.
""",
"""\
<document>
    <topic class="contents" id="id1">
        <bullet_list>
            <list_item id="id2">
                <paragraph>
                    <reference refid="contents">
                        Contents
    <paragraph>
        Test duplicate name "Contents".
    <section id="contents" name="contents">
        <title refid="id2">
            Contents
        <paragraph>
            Paragraph.
"""],
["""\
.. contents::
   :backlinks: top

Contents
--------
Paragraph.
""",
"""\
<document>
    <topic class="contents" id="id1">
        <title>
            Contents
        <bullet_list>
            <list_item id="id2">
                <paragraph>
                    <reference refid="contents">
                        Contents
    <section id="contents" name="contents">
        <title refid="id1">
            Contents
        <paragraph>
            Paragraph.
"""],
["""\
.. contents::
   :backlinks: none

Contents
--------
Paragraph.
""",
"""\
<document>
    <topic class="contents" id="id1">
        <title>
            Contents
        <bullet_list>
            <list_item id="id2">
                <paragraph>
                    <reference refid="contents">
                        Contents
    <section id="contents" name="contents">
        <title>
            Contents
        <paragraph>
            Paragraph.
"""],
["""\
.. contents::

Degenerate case, no table of contents generated.
""",
"""\
<document>
    <paragraph>
        Degenerate case, no table of contents generated.
"""],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
