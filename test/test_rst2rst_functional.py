#!/usr/bin/env python

# $Id$
# Author: Stefan Rank <strank(AT)strank(DOT)info>
# Copyright: This module has been placed in the public domain.

"""
Test the rst2rst transformation with all the data in the
functional/ directory.
"""

import sys
import os
import os.path
import shutil
import unittest
import difflib
import string

import DocutilsTestSupport              # must be imported before docutils
import docutils
import docutils.core

import test_functional
from test_functional import datadir, join_path

### use this to limit the tests run:
testsubset = (0,2,3,4,5, ) # 1 == dangerous.txt
#testsubset = (5, ) #(0,1,2,3,4,)


class FunctionalRst2RstTestSuite(test_functional.FunctionalTestSuite):
    """Test suite containing test cases for all files in functional.
    But instead of looking in tests, it walks 'input' and creates one
    test per .txt file. (input and expected are identical for rst2rst)
    """

    def __init__(self):
        """Process all config files in functional/tests/."""
        DocutilsTestSupport.CustomTestSuite.__init__(self)
        os.chdir(DocutilsTestSupport.testroot)
        self.clear_output_directory()
        self.added = 0
        os.path.walk(join_path(datadir, 'input'), self.walker, None)
        assert self.added, 'No functional tests found.'

    def walker(self, dummy, dirname, names):
        """
        Process all .txt files among `names` in `dirname`.

        This is a helper function for os.path.walk.  Any .txt file is
        used to generate a rst2rst test that should give an identical
        file as expected output.
        """
        for name in names:
            if name.endswith('.txt') and not name.startswith('_'):
                if self.added in testsubset:
                    txt_file_full_path = join_path(dirname, name)
                    self.addTestCase(FunctionalRst2RstTestCase, 'test', None, None,
                                     id=txt_file_full_path,
                                     textfile=txt_file_full_path)
                self.added += 1


class FunctionalRst2RstTestCase(DocutilsTestSupport.CustomTestCase):
    """Test case for one .txt file."""

    def __init__(self, *args, **kwargs):
        """Set self.textfile, pass arguments to parent __init__."""
        self.textfile = kwargs['textfile']
        del kwargs['textfile']
        DocutilsTestSupport.CustomTestCase.__init__(self, *args, **kwargs)

    def shortDescription(self):
        return 'test_rst2rst_functional.py: ' + self.textfile

    def test(self):
        """Test rst2rst on self.textfile."""
        os.chdir(DocutilsTestSupport.testroot)
        # Keyword parameters for publish_file:
        namespace = {}
        # Initialize 'settings_overrides' for test settings scripts,
        # and disable configuration files:
        namespace['settings_overrides'] = {
                '_disable_config': 1,
                'docinfo_xform': 0,
                }
        namespace['reader_name'] = "standalone"
        namespace['parser_name'] = "rst"
        namespace['writer_name'] = "rst"
        # Read the variables set in the default config file:
        execfile(join_path(datadir, 'tests', '_default.py'), namespace)
        # Set source_path and destination_path:
        textfile = self.textfile[self.textfile.index('input') + 6:]
        namespace.setdefault('source_path',
                             join_path(datadir, 'input', textfile))
        # Path for actual output:
        namespace.setdefault('destination_path',
                             join_path(datadir, 'output',
                             os.path.basename(textfile) + '.rst'))
        # Path for expected output: it's the input!
        expected_path = join_path(datadir, 'input', textfile)
        # shallow copy of namespace to minimize:
        params = namespace.copy()
        # Delete private stuff like params['__builtins__']:
        for key in params.keys():
            if key.startswith('_'):
                del params[key]
        # Get output (automatically written to the output/ directory
        # by publish_file):
        output = docutils.core.publish_file(**params)
        # Get the expected output *after* writing the actual output.
        self.assert_(os.access(expected_path, os.R_OK),\
                     'Cannot find expected output at\n' + expected_path)
        f = open(expected_path, 'rU')
        expected = f.read()
        f.close()
        diff = ('The expected and actual output differs.\n'
                'Please compare the expected and actual output files:\n'
                '  kdiff3 %s %s.DEBUG\n'
                '  (remove .DEBUG for the real diff, .DEBUG contains extra info)\n'
                'and update the rst-writer to remove the difference.'
                % (expected_path, params['destination_path']))
        try:
            self.assertEquals(output, expected, diff)
        except AssertionError:
            # first write a debug version of the output file:
            params['destination_path'] += '.DEBUG'
            params['settings_overrides']['_debug_rst_writer'] = True
            #params['settings_overrides']['expose_internals'] = [
            #        'rawsource', 'child_text_separator', 'data', 'line']
            docutils.core.publish_file(**params)
            if hasattr(difflib, 'unified_diff'):
                # Generate diff if unified_diff available:
                difflines = list(difflib.unified_diff(expected.splitlines(1),
                                         output.splitlines(1),
                                         expected_path,
                                         params['destination_path']))
                for ind, dil in enumerate(difflines):
                    if len(dil) > 2 and dil[-2] in string.whitespace:
                        difflines[ind] = dil[:-1] + u'[$]' + dil[-1]
                diff = ''.join(difflines)
            print >>sys.stderr, '\n%s:' % (self,)
            print >>sys.stderr, diff
            raise


def suite():
    return FunctionalRst2RstTestSuite()


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
