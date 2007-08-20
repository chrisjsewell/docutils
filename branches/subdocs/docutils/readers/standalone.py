# $Id$
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
Standalone file Reader for the reStructuredText markup syntax.
"""

__docformat__ = 'reStructuredText'


import sys
from docutils import frontend, utils, readers
from docutils.transforms import frontmatter, references, misc


class Reader(readers.Reader):

    supported = ('standalone',)
    """Contexts this reader supports."""

    document = None
    """A single document tree."""

    settings_spec = (
        'Standalone Reader',
        None,
        (('Disable the promotion of a lone top-level section title to '
          'document title (and subsequent section title to document '
          'subtitle promotion; enabled by default).',
          ['--no-doc-title'],
          {'dest': 'doctitle_xform', 'action': 'store_false', 'default': 1,
           'validator': frontend.validate_boolean}),
         ('Disable the bibliographic field list transform (enabled by '
          'default).',
          ['--no-doc-info'],
          {'dest': 'docinfo_xform', 'action': 'store_false', 'default': 1,
           'validator': frontend.validate_boolean}),
         ('Activate the promotion of lone subsection titles to '
          'section subtitles (disabled by default).',
          ['--section-subtitles'],
          {'dest': 'sectsubtitle_xform', 'action': 'store_true', 'default': 0,
           'validator': frontend.validate_boolean}),
         ('Deactivate the promotion of lone subsection titles.',
          ['--no-section-subtitles'],
          {'dest': 'sectsubtitle_xform', 'action': 'store_false'}),
         ))

    config_section = 'standalone reader'
    config_section_dependencies = ('readers',)

    def get_transforms(self):
        return readers.Reader.get_transforms(self) + [
            references.Substitutions,
            references.PropagateTargets,
            frontmatter.DocTitle,
            frontmatter.SectionSubTitle,
            frontmatter.DocInfo,
            references.AnonymousHyperlinks,
            references.IndirectHyperlinks,
            references.Footnotes,
            references.ExternalTargets,
            references.InternalTargets,
            references.DanglingReferences,
            references.QualifiedReferences,
            misc.Transitions,
            misc.CheckDoctreeValidity,
            ]

    def __init__(self, parser=None, parser_name=None,
                 docset_root=None, reserved_ids=[], is_subdocument=False):
        self.docset_root = docset_root
        self.is_subdocument = is_subdocument
        self.reserved_ids = reserved_ids
        readers.Reader.__init__(self, parser=parser, parser_name=parser_name)

    def new_document(self):
        """Create and return a new empty document tree (root node)."""
        document = utils.new_document(self.source.source_path, self.settings)
        if self.docset_root is not None:
            document['docset_root'] = self.docset_root
        document.reserved_ids = self.reserved_ids
        document.is_subdocument = self.is_subdocument
        return document
