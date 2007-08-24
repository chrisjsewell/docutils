#! /usr/bin/env python

# $Id$
# Author: Lea Wiemann <LeWiemann@gmail.com>
# Copyright: This module has been placed in the public domain.

"""
Tests for the "subdocs" and "docset-root" directives.
"""

import os.path

from __init__ import DocutilsTestSupport

from docutils import utils

def suite():
    s = DocutilsTestSupport.ParserTestSuite(suite_settings={
        # Make sure that the doctitle is still transformed in
        # sub-documents even if doctitle_xform is off.
        'doctitle_xform': False,
        })
    s.generateTests(totest)
    return s

# We have to use absolute paths throughout this test suite.  This is
# because no source_path is set for the test snippets, and therefore
# the docset-root directive will only accept absolute paths.  Since
# the docset-root is absolute, all resulting source attributes will be
# absolute, too.
paths = {}
paths['docset-root'] = utils.normalize_path(os.path.join(
    DocutilsTestSupport.testroot,
    'test_parsers/test_rst/test_directives/subdocs'))
for i in os.listdir(paths['docset-root']): # 'single-1.txt', ...
    paths[i] = utils.normalize_path(os.path.join(paths['docset-root'], i))
# Note that not all files are used in this test suite
# (test_subdocs.py); they are used in other test suites though.

totest = {}

totest['subdocs'] = [
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   * single-1.txt
   * single
     -2.txt
   * multi-3.txt
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <section ids="document-1" names="document\\ 1" source="%(single-1.txt)s">
        <title>
            Document 1
        <paragraph>
            Contents of document 1.
    <section ids="document-2" names="document\\ 2" source="%(single-2.txt)s">
        <title>
            Document 2
        <comment xml:space="preserve">
            Comments in front of the document title should be allowed.
    <section ids="document-3-section-a" names="document\\ 3,\\ section\\ a" source="%(multi-3.txt)s">
        <title>
            Document 3, section A
        <paragraph>
            Contents of document 3, section A.
    <section ids="document-3-section-b" names="document\\ 3,\\ section\\ b" source="%(multi-3.txt)s">
        <title>
            Document 3, section B
        <paragraph>
            Contents of document 3, section B.
        <section ids="subsection" names="subsection">
            <title>
                Subsection
            <paragraph>
                Subsection contents.
""" % paths],
["""\
.. docset-root:: %(docset-root)s
.. subdocuments:: 

   * single-1.txt
   * single-2.txt

     * single-1.txt
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <section ids="document-1" names="document\\ 1" source="%(single-1.txt)s">
        <title>
            Document 1
        <paragraph>
            Contents of document 1.
    <section ids="document-2" names="document\\ 2" source="%(single-2.txt)s">
        <title>
            Document 2
        <comment xml:space="preserve">
            Comments in front of the document title should be allowed.
        <section ids="id1" names="document\\ 1" source="%(single-1.txt)s">
            <title>
                Document 1
            <paragraph>
                Contents of document 1.
""" % paths],
["""\
.. docset-root:: %(docset-root)s//
.. subdocuments:: 

   * single-1.txt

     * single-2.txt

       * single-1.txt
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <section ids="document-1" names="document\\ 1" source="%(single-1.txt)s">
        <title>
            Document 1
        <paragraph>
            Contents of document 1.
        <section ids="document-2" names="document\\ 2" source="%(single-2.txt)s">
            <title>
                Document 2
            <comment xml:space="preserve">
                Comments in front of the document title should be allowed.
            <section ids="id1" names="document\\ 1" source="%(single-1.txt)s">
                <title>
                    Document 1
                <paragraph>
                    Contents of document 1.
""" % paths],
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   * funny_ filename.txt
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <section ids="document-with-a-funny-filename" names="document\\ with\\ a\\ funny\\ filename" source="%(funny_ filename.txt)s">
        <title>
            Document With a Funny Filename
        <paragraph>
            Document contents.
""" % paths],
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   * subtitle-test.txt
""" % paths,  # The "Document 1" title must not become a subtitle:
"""\
<document docset_root="%(docset-root)s" source="test data">
    <section ids="a-sub-document-with-a-title-only" names="a\\ sub-document\\ with\\ a\\ title\\ only" source="%(subtitle-test.txt)s">
        <title>
            A Sub-Document With a Title Only
        <section ids="document-1" names="document\\ 1" source="%(single-1.txt)s">
            <title>
                Document 1
            <paragraph>
                Contents of document 1.
""" % paths],
]

totest['subdocs-errors'] = [
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   * multi-3.txt

     * single-1.txt
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <system_message level="3" line="2" source="test data" type="ERROR">
        <paragraph>
            cannot have nested sub-documents since "multi-3.txt" contains more than one section
        <literal_block xml:space="preserve">
            .. subdocs::
            \n\
               * multi-3.txt
            \n\
                 * single-1.txt
""" % paths],
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   * empty.txt
   * single-1.txt
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <system_message level="3" line="2" source="test data" type="ERROR">
        <paragraph>
            Error with "subdocs" directive, file "%(empty.txt)s": a sub-document must either have a single document-title, or it must consist of one or more top-level sections and optionally transitions.
        <literal_block xml:space="preserve">
            .. subdocs::
            \n\
               * empty.txt
               * single-1.txt
""" % paths],
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   * nonexistent.txt
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <system_message level="3" line="2" source="test data" type="ERROR">
        <paragraph>
            Error with "subdocs" directive: could not read file "%(docset-root)s/nonexistent.txt": [Errno 2] No such file or directory: \'%(docset-root)s/nonexistent.txt\'
        <literal_block xml:space="preserve">
            .. subdocs::
            \n\
               * nonexistent.txt
""" % paths],
["""\
.. subdocs::

   * single-1.txt
""" % paths,
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            a doc-set root must be declared using the "docset-root" directive before referencing sub-documents
        <literal_block xml:space="preserve">
            .. subdocs::
            \n\
               * single-1.txt
""" % paths],
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   * recursive-1.txt
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <section ids="recursive-document-1" names="recursive\\ document\\ 1" source="%(recursive-1.txt)s">
        <title>
            Recursive Document 1
        <paragraph>
            Document contents.
        <section ids="recursive-document-2" names="recursive\\ document\\ 2" source="%(recursive-2.txt)s">
            <title>
                Recursive Document 2
            <paragraph>
                Document contents.
            <system_message level="3" line="9" source="%(recursive-2.txt)s" type="ERROR">
                <paragraph>
                    Error in "subdocs" directive: Recursive subdocument inclusion: "%(recursive-1.txt)s"
                <literal_block xml:space="preserve">
                    .. subdocs::
                    \n\
                       * recursive-1.txt
""" % paths],
]

totest['subdocs-syntax-errors'] = [
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   *

     * nested
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <system_message level="3" line="2" source="test data" type="ERROR">
        <paragraph>
            Error with "subdocs" directive, line 6: No bullet allowed here.
        <literal_block xml:space="preserve">
            .. subdocs::
            \n\
               *
            \n\
                 * nested
""" % paths],
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   Paragraph.
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <system_message level="3" line="2" source="test data" type="ERROR">
        <paragraph>
            Error with "subdocs" directive: must contain a bullet list.
        <literal_block xml:space="preserve">
            .. subdocs::
            \n\
               Paragraph.
""" % paths],
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   * single-1.txt

     Paragraph.
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <system_message level="3" line="2" source="test data" type="ERROR">
        <paragraph>
            Error with "subdocs" directive, line 6: Sub-document specification list items may only contain one nested bullet list
        <literal_block xml:space="preserve">
            .. subdocs::
            \n\
               * single-1.txt
            \n\
                 Paragraph.
""" % paths],
["""\
.. docset-root:: %(docset-root)s
.. subdocs::
   * single-1.txt
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <system_message level="3" line="2" source="test data" type="ERROR">
        <paragraph>
            Error in "subdocs" directive:
            no arguments permitted; blank line required before content block.
        <literal_block xml:space="preserve">
            .. subdocs::
               * single-1.txt
""" % paths],
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   *
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <system_message level="3" line="2" source="test data" type="ERROR">
        <paragraph>
            Error with "subdocs" directive, line 4: No empty list items allowed in sub-documents specification.
        <literal_block xml:space="preserve">
            .. subdocs::
            \n\
               *
""" % paths],
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   * :bad:-file.txt
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <system_message level="3" line="2" source="test data" type="ERROR">
        <paragraph>
            Error with "subdocs" directive, line 4: File names may not start with a colon.
        <literal_block xml:space="preserve">
            .. subdocs::
            \n\
               * :bad:-file.txt
""" % paths],
]

totest['docset-root'] = [
["""\
.. docset-root:: relative/path
""" % paths,
"""\
<document source="test data">
    <system_message level="3" line="1" source="test data" type="ERROR">
        <paragraph>
            relative doc-set roots are prohibited if the document source path (reader.source.source_path) cannot be determined
        <literal_block xml:space="preserve">
            .. docset-root:: relative/path
""" % paths],
["""\
.. docset-root:: %(docset-root)s
.. docset-root:: %(docset-root)s/different
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <system_message level="3" line="2" source="test data" type="ERROR">
        <paragraph>
            given doc-set root ("%(docset-root)s/different") conflicts with previously specified doc-set root ("%(docset-root)s")
        <literal_block xml:space="preserve">
            .. docset-root:: %(docset-root)s/different
""" % paths],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
