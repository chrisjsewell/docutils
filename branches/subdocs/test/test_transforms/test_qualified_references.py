#! /usr/bin/env python

# $Id$
# Author: Lea Wiemann <LeWiemann@gmail.com>
# Copyright: This module has been placed in the public domain.

"""
Tests for `docutils.transforms.references.QualifiedReferences`.
"""

from __init__ import DocutilsTestSupport
from docutils.transforms.references import QualifiedReferences
from docutils.parsers.rst import Parser


def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s

from test_parsers.test_rst.test_directives.test_subdocs import paths

totest = {}

totest['qualified-references'] = ((QualifiedReferences,), [
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   * %(single-1.txt)s

`<single-1.txt> DocUMeNt  1`_
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <section ids="document-1" names="document\\ 1" source="%(single-1.txt)s">
        <title>
            Document 1
        <paragraph>
            Contents of document 1.
    <paragraph>
        <reference refid="document-1">
            DocUMeNt  1
""" % paths,
],
["""\
.. docset-root:: %(docset-root)s

.. _foo:

`<../../../../test data> foo`_
""" % paths,  # cruelly test that the document can reference its own namespace
"""\
<document docset_root="%(docset-root)s" source="test data">
    <target ids="foo" names="foo">
    <paragraph>
        <reference refid="foo">
            foo
""" % paths,
],
["""\
.. docset-root:: %(docset-root)s

.. subdocs::

   * references.txt

.. _foo:
""" % paths,  # references.txt references the foo target
"""\
<document docset_root="%(docset-root)s" source="test data">
    <section ids="section" names="section" source="%(references.txt)s">
        <title>
            Section
        <paragraph>
            <reference refid="foo">
                foo
    <target ids="foo" names="foo">
""" % paths,
],
])

totest['qualified-references-errors'] = ((QualifiedReferences,), [
["""\
.. docset-root:: %(docset-root)s

`<nonexistent> bar`_
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <paragraph>
        <problematic ids="id2" refid="id1">
            `<nonexistent> bar`_
    <system_message backrefs="id2" ids="id1" level="3" line="3" source="test data" type="ERROR">
        <paragraph>
            Invalid namespace: nonexistent
""" % paths,
],
["""\
.. docset-root:: %(docset-root)s

.. subdocs::

   * single-1.txt

`<single-1.txt> nonexistent`_
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <section ids="document-1" names="document\\ 1" source="%(single-1.txt)s">
        <title>
            Document 1
        <paragraph>
            Contents of document 1.
    <paragraph>
        <problematic ids="id2" refid="id1">
            `<single-1.txt> nonexistent`_
    <system_message backrefs="id2" ids="id1" level="3" line="7" source="test data" type="ERROR">
        <paragraph>
            No target "nonexistent" found in namespace "single-1.txt".
""" % paths,
],
["""\
.. docset-root:: %(docset-root)s

Section
=======
Section
=======

`<../../..\\..\\test data> Section`_
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <section dupnames="section" ids="section">
        <title>
            Section
    <section dupnames="section" ids="id1">
        <title>
            Section
        <system_message backrefs="id1" level="1" line="6" source="test data" type="INFO">
            <paragraph>
                Duplicate implicit target name: "section".
        <paragraph>
            <problematic ids="id3" refid="id2">
                `<../../..\\..\\test data> Section`_
    <system_message backrefs="id3" ids="id2" level="3" line="8" source="test data" type="ERROR">
        <paragraph>
            Duplicate target "section" in namespace "../../../../test data" cannot be referenced.
""" % paths,
],
])

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
