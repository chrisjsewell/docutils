#!/usr/bin/env python

# Author: David Goodger
# Contact: goodger@python.org
# Revision:  $Revision$
# Date:      $Date$
# Copyright: This module has been placed in the public domain.

"""
Tests of runtime settings.
"""

import sys
import os
import difflib
import pprint
import warnings
import unittest
from docutils import frontend
from docutils.writers import html4css1
from docutils.writers import pep_html


warnings.filterwarnings(action='ignore',
                        category=frontend.ConfigDeprecationWarning)

def fixpath(path):
    return os.path.abspath(os.path.join(mydir, path))

mydir = os.path.dirname(fixpath.func_code.co_filename)


class ConfigFileTests(unittest.TestCase):

    config_files = {'old': fixpath('data/config_old.txt'),
                    'one': fixpath('data/config_1.txt'),
                    'two': fixpath('data/config_2.txt'),
                    'list': fixpath('data/config_list.txt'),
                    'error': fixpath('data/config_error_handler.txt')}

    settings = {
        'old': {'datestamp': '%Y-%m-%d %H:%M UTC',
                'generator': 1,
                'no_random': 1,
                'python_home': 'http://www.python.org',
                'source_link': 1,
                'stylesheet_path': fixpath('data/stylesheets/pep.css'),
                'template': fixpath('data/pep-html-template')},
        'one': {'datestamp': '%Y-%m-%d %H:%M UTC',
                'generator': 1,
                'no_random': 1,
                'python_home': 'http://www.python.org',
                'source_link': 1,
                'stylesheet_path': fixpath('data/stylesheets/pep.css'),
                'template': fixpath('data/pep-html-template')},
        'two': {'generator': 0,
                'stylesheet_path': fixpath('data/test.css')},
        'list': {'expose_internals': ['a', 'b', 'c', 'd', 'e']},
        'error': {'error_encoding': 'ascii',
                  'error_encoding_error_handler': 'strict'},
        }

    compare = difflib.Differ().compare
    """Comparison method shared by all tests."""

    def setUp(self):
        self.option_parser = frontend.OptionParser(
            components=(pep_html.Writer,), read_config_files=None)

    def files_settings(self, *names):
        settings = {}
        for name in names:
            settings.update(self.option_parser.get_config_file_settings(
                self.config_files[name]))
        return settings

    def expected_settings(self, *names):
        expected = {}
        for name in names:
            expected.update(self.settings[name])
        return expected

    def compare_output(self, result, expected):
        """`result` and `expected` should both be dicts."""
        result = pprint.pformat(result) + '\n'
        expected = pprint.pformat(expected) + '\n'
        try:
            self.assertEquals(result, expected)
        except AssertionError:
            print >>sys.stderr, '\n%s\n' % (self,)
            print >>sys.stderr, '+: result\n-: expected'
            print >>sys.stderr, ''.join(self.compare(expected.splitlines(1),
                                                     result.splitlines(1)))
            raise

    def test_nofiles(self):
        self.compare_output(self.files_settings(),
                            self.expected_settings())

    def test_old(self):
        self.compare_output(self.files_settings('old'),
                            self.expected_settings('old'))

    def test_one(self):
        self.compare_output(self.files_settings('one'),
                            self.expected_settings('one'))

    def test_multiple(self):
        self.compare_output(self.files_settings('one', 'two'),
                            self.expected_settings('one', 'two'))

    def test_old_and_new(self):
        self.compare_output(self.files_settings('old', 'two'),
                            self.expected_settings('old', 'two'))

    def test_list(self):
        self.compare_output(self.files_settings('list'),
                            self.expected_settings('list'))

    def test_error_handler(self):
        self.compare_output(self.files_settings('error'),
                            self.expected_settings('error'))


class ConfigEnvVarFileTests(ConfigFileTests):

    def setUp(self):
        ConfigFileTests.setUp(self)
        self.orig_environ = os.environ
        os.environ = dict(os.environ)

    def files_settings(self, *names):
        files = [self.config_files[name] for name in names]
        os.environ['DOCUTILSCONFIG'] = os.pathsep.join(files)
        return self.option_parser.get_standard_config_settings()

    def tearDown(self):
        os.environ = self.orig_environ
    

if __name__ == '__main__':
    unittest.main()
