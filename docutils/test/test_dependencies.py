#! /usr/bin/env python

# Author: Felix Wiemann
# Contact: Felix_Wiemann@ososo.de
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Test module for the --record-dependencies option.
"""

import os.path
import unittest
import sys
import docutils.core
import docutils.utils
import DocutilsTestSupport


class RecordDependenciesTests(unittest.TestCase):

    def setUp(self):
        os.chdir(os.path.join(DocutilsTestSupport.testroot, 'data'))

    def get_record(self, inputfile=None, **settings):

        recordfile = 'record.txt'
        settings.setdefault('source_path', 'dependencies.txt')
        settings.setdefault('settings_overrides', {})
        settings['settings_overrides'] = settings['settings_overrides'].copy()
        settings['settings_overrides']['_disable_config'] = 1
        settings['settings_overrides']['_stylesheet_required'] = 0
        if not settings['settings_overrides'].has_key('record_dependencies'):
            settings['settings_overrides']['record_dependencies'] = \
                docutils.utils.DependencyList(recordfile)
        docutils.core.publish_file(destination=DocutilsTestSupport.DevNull(),
                                   **settings)
        settings['settings_overrides']['record_dependencies'].close()
        return open(recordfile).read().splitlines()

    def test_dependencies(self):
        self.assertEqual(self.get_record(),
                         ['include.txt',
                          'raw.txt'])
        self.assertEqual(self.get_record(writer_name='latex'),
                         ['include.txt',
                          'raw.txt',
                          'some_image.png'])

    def test_csv_dependencies(self):
        try:
            import csv
            self.assertEqual(self.get_record(source_path='csv_dep.txt'),
                             ['csv_data.txt'])
        except ImportError:
            pass

    def test_stylesheet_dependencies(self):
        # Parameters to publish_file.
        s = {'settings_overrides': {}}
        so = s['settings_overrides']
        so['embed_stylesheet'] = 0
        so['stylesheet_path'] = 'stylesheet.txt'
        so['stylesheet'] = None
        s['writer_name'] = 'html'
        self.assert_('stylesheet.txt' not in
                     self.get_record(**s))
        so['embed_stylesheet'] = 1
        self.assert_('stylesheet.txt' in
                     self.get_record(**s))
        del so['embed_stylesheet']
        s['writer_name'] = 'latex'
        self.assert_('stylesheet.txt' in
                     self.get_record(**s))


if __name__ == '__main__':
    unittest.main()
