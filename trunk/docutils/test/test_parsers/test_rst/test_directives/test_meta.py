#! /usr/bin/env python

"""
:Author: David Goodger
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

Tests for html.py meta directives.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.ParserTestSuite()
    s.generateTests(totest)
    return s

totest = {}

totest['meta'] = [
["""\
.. meta::
   :description: The reStructuredText plaintext markup language
   :keywords: plaintext,markup language
""",
"""\
<document>
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.components.Filter
             .stage: 'first writer'
             .details:
               nodes:
                 <meta content="The reStructuredText plaintext markup language" name="description">
               writer: 'html'
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.components.Filter
             .stage: 'first writer'
             .details:
               nodes:
                 <meta content="plaintext,markup language" name="keywords">
               writer: 'html'
"""],
["""\
.. meta::
   :description lang=en: An amusing story
   :description lang=fr: Un histoire amusant
""",
"""\
<document>
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.components.Filter
             .stage: 'first writer'
             .details:
               nodes:
                 <meta content="An amusing story" lang="en" name="description">
               writer: 'html'
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.components.Filter
             .stage: 'first writer'
             .details:
               nodes:
                 <meta content="Un histoire amusant" lang="fr" name="description">
               writer: 'html'
"""],
["""\
.. meta::
   :http-equiv=Content-Type: text/html; charset=ISO-8859-1
""",
"""\
<document>
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.components.Filter
             .stage: 'first writer'
             .details:
               nodes:
                 <meta content="text/html; charset=ISO-8859-1" http-equiv="Content-Type">
               writer: 'html'
"""],
["""\
.. meta::
   :name: content
     over multiple lines
""",
"""\
<document>
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.components.Filter
             .stage: 'first writer'
             .details:
               nodes:
                 <meta content="content over multiple lines" name="name">
               writer: 'html'
"""],
["""\
Paragraph

.. meta::
   :name: content
""",
"""\
<document>
    <paragraph>
        Paragraph
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.components.Filter
             .stage: 'first writer'
             .details:
               nodes:
                 <meta content="content" name="name">
               writer: 'html'
"""],
["""\
.. meta::
""",
"""\
<document>
    <system_message level="3" type="ERROR">
        <paragraph>
            Empty meta directive at line 1.
"""],
["""\
.. meta::
   :empty:
""",
"""\
<document>
    <system_message level="1" type="INFO">
        <paragraph>
            No content for meta tag "empty" at line 2.
        <literal_block>
            :empty:
"""],
["""\
.. meta::
   not a field list
""",
"""\
<document>
    <system_message level="3" type="ERROR">
        <paragraph>
            Invalid meta directive at line 2.
        <literal_block>
            .. meta::
               not a field list
"""],
["""\
.. meta::
   :name: content
   not a field
""",
"""\
<document>
    <pending>
        .. internal attributes:
             .transform: docutils.transforms.components.Filter
             .stage: 'first writer'
             .details:
               nodes:
                 <meta content="content" name="name">
               writer: 'html'
    <system_message level="3" type="ERROR">
        <paragraph>
            Invalid meta directive at line 3.
        <literal_block>
            .. meta::
               :name: content
               not a field
"""],
["""\
.. meta::
   :name notattval: content
""",
"""\
<document>
    <system_message level="3" type="ERROR">
        <paragraph>
            Error parsing meta tag attribute "notattval" at line 2: missing "=".
        <literal_block>
            :name notattval: content
"""],
]


if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
