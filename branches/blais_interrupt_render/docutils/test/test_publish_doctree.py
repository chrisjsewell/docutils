#!/usr/bin/env python

# Author: Martin Blais
# Contact: blais@furius.ca
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Perform tests with publishing to a tree, and running a writer on that tree later.
"""

import unittest
import cPickle as pickle
import docutils.core
import docutils.nodes


datadir = 'publish_doctree'
"""The directory to store the data needed for the functional tests."""


test_document = """
========================
  Simple Test Document
========================

:Author: The Man

This is a silly test document to produce a document tree for.

Uncertainty
-----------

- yes
- no
- I'm sure.
"""

class PublishDoctreeTestCase(unittest.TestCase):

    """Simplistic test case for publishing as a document tree."""
    
    def test_document_pickle(self):
        """
        Produce document tree, pickle, unpickle, write.
        """

        # produce the document tree.
        doctree, parts = docutils.core.publish_doctree(
            source=test_document,
            reader_name='standalone',
            parser_name='restructuredtext')
        
        assert isinstance(doctree, docutils.nodes.document)
        assert isinstance(parts, dict)
        
        # pickle the document
        pickled_document = pickle.dumps(doctree)
        assert isinstance(pickled_document, str)
        del doctree
        
        # unpickle the document
        doctree2 = pickle.loads(pickled_document)
        assert isinstance(doctree2, docutils.nodes.document)

        # write out the document
        output = docutils.core.publish_from_doctree(doctree2,
                                                    writer_name='pseudoxml')
        assert isinstance(output, str)

if __name__ == '__main__':
    unittest.main()
