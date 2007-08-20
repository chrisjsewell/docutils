#! /usr/bin/env python

# $Id$
# Author: Lea Wiemann <LeWiemann@gmail.com>
# Copyright: This module has been placed in the public domain.

"""
Tests for `docutils.transforms.misc.CheckDoctreeValidity`.
"""

from __init__ import DocutilsTestSupport
from docutils.transforms.misc import CheckDoctreeValidity
from docutils.parsers.rst import Parser


def suite():
    parser = Parser()
    s = DocutilsTestSupport.TransformTestSuite(parser)
    s.generateTests(totest)
    return s

from test_parsers.test_rst.test_directives.test_subdocs import paths

totest = {}

totest['check_doctree_validity'] = ((CheckDoctreeValidity,), [
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   * %(single-1.txt)s

More content.

----------

Even more content.

Section
=======
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <section ids="document-1" names="document\\ 1" source="%(single-1.txt)s">
        <title>
            Document 1
        <paragraph>
            Contents of document 1.
        <paragraph>
            More content.
        <transition>
        <paragraph>
            Even more content.
        <system_message level="2" source="test data" type="WARNING">
            <paragraph>
                Only transitions and sections are allowed after the "subdocs" directive.
    <section ids="section" names="section">
        <title>
            Section
""" % paths,
],
["""\
.. docset-root:: %(docset-root)s
.. subdocs::

   * %(single-1.txt)s

----------

Section
=======
""" % paths,
"""\
<document docset_root="%(docset-root)s" source="test data">
    <section ids="document-1" names="document\\ 1" source="%(single-1.txt)s">
        <title>
            Document 1
        <paragraph>
            Contents of document 1.
    <transition>
    <section ids="section" names="section">
        <title>
            Section
""" % paths,
],
])


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
