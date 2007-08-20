# $Id$
# Authors: David Goodger <goodger@python.org>;
#     Lea Wiemann <LeWiemann@gmail.com>; Dmitry Jemerov
# Copyright: This module has been placed in the public domain.

"""
Directives for document parts.
"""

__docformat__ = 'reStructuredText'

import os.path

from docutils import nodes, languages, utils
from docutils.io import FileInput
from docutils.transforms import parts
from docutils.parsers.rst import Directive, Parser
from docutils.parsers.rst import directives, states
from docutils.readers import standalone


class Contents(Directive):

    """
    Table of contents.

    The table of contents is generated in two passes: initial parse and
    transform.  During the initial parse, a 'pending' element is generated
    which acts as a placeholder, storing the TOC title and any options
    internally.  At a later stage in the processing, the 'pending' element is
    replaced by a 'topic' element, a title and the table of contents proper.
    """

    backlinks_values = ('top', 'entry', 'none')

    def backlinks(arg):
        value = directives.choice(arg, Contents.backlinks_values)
        if value == 'none':
            return None
        else:
            return value

    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {'depth': directives.nonnegative_int,
                   'local': directives.flag,
                   'backlinks': backlinks,
                   'class': directives.class_option}
    
    def run(self):
        if not (self.state_machine.match_titles
                or isinstance(self.state_machine.node, nodes.sidebar)):
            raise self.error('The "%s" directive may not be used within '
                             'topics or body elements.' % self.name)
        document = self.state_machine.document
        language = languages.get_language(document.settings.language_code)
        if self.arguments:
            title_text = self.arguments[0]
            text_nodes, messages = self.state.inline_text(title_text,
                                                          self.lineno)
            title = nodes.title(title_text, '', *text_nodes)
        else:
            messages = []
            if self.options.has_key('local'):
                title = None
            else:
                title = nodes.title('', language.labels['contents'])
        topic = nodes.topic(classes=['contents'])
        topic['classes'] += self.options.get('class', [])
        if self.options.has_key('local'):
            topic['classes'].append('local')
        if title:
            name = title.astext()
            topic += title
        else:
            name = language.labels['contents']
        name = nodes.fully_normalize_name(name)
        if not document.has_name(name):
            topic['names'].append(name)
        document.note_implicit_target(topic)
        pending = nodes.pending(parts.Contents, rawsource=self.block_text)
        pending.details.update(self.options)
        document.note_pending(pending)
        topic += pending
        return [topic] + messages


class Sectnum(Directive):

    """Automatic section numbering."""

    option_spec = {'depth': int,
                   'start': int,
                   'prefix': directives.unchanged_required,
                   'suffix': directives.unchanged_required}

    def run(self):
        pending = nodes.pending(parts.SectNum)
        pending.details.update(self.options)
        self.state_machine.document.note_pending(pending)
        return [pending]


class Header(Directive):

    """Contents of document header."""

    has_content = True

    def run(self):
        self.assert_has_content()
        header = self.state_machine.document.get_decoration().get_header()
        self.state.nested_parse(self.content, self.content_offset, header)
        return []


class Footer(Directive):

    """Contents of document footer."""

    has_content = True

    def run(self):
        self.assert_has_content()
        footer = self.state_machine.document.get_decoration().get_footer()
        self.state.nested_parse(self.content, self.content_offset, footer)
        return []


class Subdocs(Directive):

    """Include sub-documents at the current position."""

    has_content = True
    # Reserve space for future options.
    option_spec = {}

    def run(self):
        self.assert_has_content()
        bullets = states.Body.patterns['bullet']
        bullet = self.content[0][0]
        bullet_list = nodes.bullet_list('\n'.join(self.content),
                                        bullet=bullet)
        try:
            newline_offset, blank_finish = self.state.nested_list_parse(
                self.content, self.content_offset, bullet_list,
                initial_state='SubdocumentsSpec', blank_finish=True)
        except states.SubdocumentsSpecError, e:
            raise self.error('Error with "%s" directive, line %s: %s'
                             % (self.name, e.line, e.msg))
        if newline_offset != len(self.content) + self.content_offset:
            raise self.error('Error with "%s" directive: must contain a '
                             'bullet list.' % self.name)
        return self.interpret_bullet_list(bullet_list)

    def interpret_bullet_list(self, bullet_list):
        """
        Interpret the bullet list, read the sub-documents, and return a
        list of sections.
        """
        assert isinstance(bullet_list, nodes.bullet_list)
        sections = []
        for item in bullet_list:
            # Expect paragraph as first item:
            assert isinstance(item, nodes.list_item) and len(item) \
                   and isinstance(item[0], nodes.paragraph) \
                   and len(item[0]) == 1
            file_name = item[0].astext()
            subdocument, subdoc_sections = self.read_subdocument(file_name)
            assert len(subdoc_sections)
            sections += subdoc_sections
            if len(item) > 1:
                assert len(item) == 2 and isinstance(item[1],
                                                     nodes.bullet_list)
                if len(subdoc_sections) > 1:
                    raise self.error('cannot have nested sub-documents '
                                     'since "%s" contains more than one '
                                     'section' % file_name)
                subdoc_sections[0] += self.interpret_bullet_list(item[1])
        return sections

    def read_subdocument(self, file_name):
        """
        Read the document `file_name` and return a tuple (document,
        sections), where `document` is the parsed document node and
        `sections` are the sections to be inserted.
        """
        # Perhaps this should be moved into the reader.
        document = self.state_machine.document
        subdoc_reader = standalone.Reader(
            parser_name='rst', docset_root=document.get('docset_root'),
            reserved_ids=(document.ids.keys() + document.reserved_ids),
            is_subdocument=True)
        if not os.path.isabs(file_name):
            if not document.hasattr('docset_root'):
                raise self.error('a doc-set root must be declared using the '
                                 '"docset-root" directive before '
                                 'referencing sub-documents')
                # Not *quite* true; absolute paths are still allowed. ;->
            file_name = os.path.join(document['docset_root'], file_name)
        file_name = utils.normalize_path(file_name)
        # Test for recursion.
        subdoc_reader.subdoc_stack = (
            hasattr(self.reader, 'subdoc_stack')
            and self.reader.subdoc_stack or [])
        if self.reader and self.reader.source and \
               self.reader.source.source_path:
            subdoc_reader.subdoc_stack.append(os.path.normcase(
                os.path.abspath(self.reader.source.source_path)))
        if os.path.normcase(os.path.abspath(file_name)) in \
           subdoc_reader.subdoc_stack:
            raise self.error('Error in "%s" directive: Recursive subdocument '
                             'inclusion: "%s"' % (self.name, file_name))
        try:
            source = FileInput(source_path=file_name,
                               handle_io_errors=False,
                               # None or current encoding
                               encoding=(self.reader and self.reader.source
                                         and self.reader.source.encoding))
        except IOError, error:
            raise self.error(
                'Error with "%s" directive: could not read file "%s": %s'
                % (self.name, file_name, error))
        subdoc_settings = self.state.document.settings.copy()
        subdoc_settings.doctitle_xform = True
        subdocument = subdoc_reader.read(
            source=source, parser=Parser(subdoc_reader),
            settings=subdoc_settings)
        if len(subdocument) >= 1 and isinstance(subdocument[0], nodes.title):
            # Single document title.
            attributes = {}
            for att in 'ids', 'names', 'source':
                assert subdocument.hasattr(att)
                attributes[att] = subdocument[att]
            section = nodes.section(
                subdocument.rawsource, *subdocument.children,
                **attributes)
            for id in attributes['ids']:
                subdocument.ids[id] = section
            sections = [section]
        elif (# at least one section:
              [n for n in subdocument if isinstance(n, nodes.section)]
              # only sections and transitions:
              and not [n for n in subdocument if
                       not isinstance(n, (nodes.section, nodes.transition))]):
            # Filter out transitions.
            sections = [n for n in subdocument
                        if isinstance(n, nodes.section)]
            for section in sections:
                section['source'] = subdocument['source']
            for id in subdocument['ids']:
                sections[0]['ids'].append(id)
                subdocument.ids[id] = sections[0]
        else:
            raise self.error(
                'Error with "%s" directive, file "%s": a sub-document must '
                'either have a single document-title, or it must consist of '
                'one or more top-level sections and optionally transitions.'
                % (self.name, file_name))
        # Update the master document's ID's and name-to-id mapping.
        document.ids.update(subdocument.ids)
        document.global_nameids.update(subdocument.global_nameids)
        # Remove decoration (header and footer).
        for node in subdocument.traverse(nodes.decoration):
            node.parent.remove(node)
        return subdocument, sections


class DocsetRoot(Directive):

    """
    Specify the root of the doc-set (used by the subdocs directive).
    """

    required_arguments = 1
    final_argument_whitespace = True

    def run(self):
        path = self.arguments[0]
        if not os.path.isabs(path):
            if self.reader is None or self.reader.source is None or \
                   self.reader.source.source_path is None:
                # This could happen when called programmatically.
                raise self.error('relative doc-set roots are prohibited if '
                                 'the document source path '
                                 '(reader.source.source_path) cannot be '
                                 'determined')
            path = os.path.join(
                os.path.dirname(self.state_machine.input_lines.source(
                self.lineno - self.state_machine.input_offset - 1)), path)
        path = utils.normalize_path(path)
        document = self.state_machine.document
        if not document.hasattr('docset_root'):
            document['docset_root'] = path
        elif os.path.normcase(os.path.abspath(document['docset_root'])) != \
                 os.path.normcase(os.path.abspath(path)):
            raise self.error('given doc-set root ("%s") conflicts with '
                             'previously specified doc-set root ("%s")'
                             % (path, document['docset_root']))
        return []
