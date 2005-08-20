# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Docutils component-related transforms.
"""

__docformat__ = 'reStructuredText'

import sys
import os
import re
import time
from docutils import nodes, utils
from docutils import ApplicationError, DataError
from docutils.transforms import Transform, TransformError


class WriterFilter(Transform):

    """
    Remove elements which are specific to a format not supported by
    the current writer.
    """

    default_priority = 780

    def apply(self):
        writer = self.document.transformer.components['writer']
        for node in self.document.traverse(nodes.FormatSpecific):
            for format in node.requires_formats():
                if writer.supports(format):
                    break
            else:
                node.parent.remove(node)
