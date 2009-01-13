#!/usr/bin/env python

# $Id$
# Author: Dave Kuhlman <dkuhlman@rexx.com>
# Copyright: This module has been placed in the public domain.

"""
Tests for docutils odtwriter.

Instructions for adding a new test:

1. Add a new method to class DocutilsOdtTestCase (below) named
   test_odt_xxxx, where xxxx describes your new feature.  See
   test_odt_basic for an example.

2. Add a new input reST (.txt) file in test/functional/input. This
   file should contain the smallest amount of reST that tests your
   new feature.  Name this file odt_xxxx.txt.

3. Convert your input reST (.txt) file to an ODF (.odt) file using
   rst2odt.py.  Place this ODF (.odt) file in
   test/functional/expected.  Name this file odt_xxxx.odt.
   You can also pass parameter save_output_name='filename' to method
   process_test() in order to produce expected output.
   See and modify variable TEMP_FILE_PATH for destination.

4. Run your test.  Your new test should pass.

5. If any other tests fail, that's a possible regression.

"""

import sys
import os
import StringIO
import zipfile
from xml.dom import minidom
import tempfile

from __init__ import DocutilsTestSupport

import docutils
import docutils.core

#
# Globals
TEMP_FILE_PATH = '/tmp'
INPUT_PATH = 'functional/input/'
EXPECTED_PATH = 'functional/expected/'


class DocutilsOdtTestCase(DocutilsTestSupport.StandardTestCase):

    def process_test(self, input_filename, expected_filename, 
            save_output_name=None):
        # Test that xmlcharrefreplace is the default output encoding
        # error handler.
        input_file = open(INPUT_PATH + input_filename, 'r')
        expected_file = open(EXPECTED_PATH + expected_filename, 'r')
        input = input_file.read()
        expected = expected_file.read()
        input_file.close()
        expected_file.close()
        settings_overrides={
            }
        result = docutils.core.publish_string(
            source=input,
            reader_name='standalone',
            writer_name='odf_odt',
            settings_overrides=settings_overrides)
##         msg = 'file length not equal: expected length: %d  actual length: %d' % (
##             len(expected), len(result), )
##         self.assertEqual(str(len(result)), str(len(expected)))
        if save_output_name:
            filename = '%s%s%s' % (TEMP_FILE_PATH, os.sep, save_output_name,)
            outfile = open(filename, 'w')
            outfile.write(result)
            outfile.close()
        content1 = self.extract_file(result, 'content.xml')
        content2 = self.extract_file(expected, 'content.xml')
        msg = 'content.xml not equal: expected len: %d  actual len: %d' % (
            len(content2), len(content1), )
        self.assertEqual(content1, content2, msg)

    def extract_file(self, payload, filename):
        payloadfile = StringIO.StringIO()
        payloadfile.write(payload)
        payloadfile.seek(0)
        zfile = zipfile.ZipFile(payloadfile, 'r')
        content1 = zfile.read(filename)
        doc = minidom.parseString(content1)
        #content2 = doc.toprettyxml(indent='  ')
        content2 = doc.toxml()
        return content2

    def assertEqual(self, first, second, msg=None):
        if msg is None:
            msg2 = msg
        else:
            sep = '+' * 60
            msg1 = '\n%s\nresult:\n%s\n%s\nexpected:\n%s\n%s' % (
                sep, first, sep, second, sep, )
            #msg2 = '%s\n%s' % (msg1, msg, )
            msg2 = '%s' % (msg, )
        DocutilsTestSupport.StandardTestCase.failUnlessEqual(self,
            first, second, msg2)

    #
    # Unit test methods
    #
    # All test methods should be named "test_odt_xxxx", where
    #     xxxx is replaced with a name for the new test.
    # See instructions above in module doc-string.
    #

    def test_odt_basic(self):
        self.process_test('odt_basic.txt', 'odt_basic.odt',
            #save_output_name='odt_basic.odt'
            )

    def test_odt_tables1(self):
        self.process_test('odt_tables1.txt', 'odt_tables1.odt',
            #save_output_name='odt_tables1.odt'
            )

    #
    # Template for new tests.
    # Also add functional/input/odt_xxxx.txt and
    #   functional/expected/odt_xxxx.odt
    # Replace all xxxx with name of your test.
    #
##     def test_odt_xxxx(self):
##         self.process_test('odt_xxxx.txt', 'odt_xxxx.odt')


# -----------------------------------------------------------------


if __name__ == '__main__':
    import unittest
    unittest.main()
