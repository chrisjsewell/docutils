# $Id$
# Authors: David Goodger <goodger@python.org>; Dmitry Jemerov
# Copyright: This module has been placed in the public domain.

"""
Directives for document parts.
"""

__docformat__ = 'reStructuredText'

from docutils import nodes, languages
from docutils.transforms import parts
from docutils.parsers.rst import Directive
from docutils.parsers.rst import directives, states


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


class Subdocuments(Directive):

    """Include sub-documents at the current position."""

    has_content = True
    option_spec = {'inherit': directives.flag}

    def run(self):
        if self.reader is None:
            raise self.warning('No document reader has been specified; '
                               'therefore, the "%s" directive is unavailable.'
                               % self.name) 
        self.assert_has_content()
        if 'inherit' in self.options:
            raise self.error('Error in "%s" directive: :inherit: option not'
                             'yet implemented.' % self.name)
        bullets = states.Body.patterns['bullet']
        bullet = self.content[0][0]
        # Not necessary. REMOVEME.
#         print bullet, bullets
#         if not bullet in bullets:
#             raise self.content_error(
#                 'directive must contain exactly one bullet list')
        bullet_list = nodes.bullet_list('\n'.join(self.content),
                                        bullet=bullet)
        newline_offset, blank_finish = self.state.nested_list_parse(
            self.content, self.content_offset, bullet_list,
            initial_state='SubdocumentsSpec', blank_finish=True)
        # XXX this does not work. Why?
#         if newline_offset != len(self.block_text.splitlines()):
#             raise self.content_error(
#                 'directive must contain exactly one bullet list')
        return self.interpret_bullet_list(bullet_list)

    def content_error(self, message):  # , node
        return self.error(
            'Error with %s directive: %s.' % (self.name, message))
        # XXX How do we report an error with the particular node it
        # occurred at, not with the whole directive?
        #msg_node = self.state.reporter.system_message(3, message_text)
        #source_line = self.state_machine.input_lines[node.LINE_NUMBER?]
        #msg_node += nodes.literal_block(node.rawsource, node.rawsource) # does not work
        #return msg_node

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
            # Expect field lists -- implement later:
#             # Parse field list.
#             sections += self.interpret_field_list(item[0])
#             # Parse nested bullet list.
#             assert len(item) != 2, 'nested sub-documents not yet implemented'
            sections += self.read_subdocument({'file': file_name})
            assert len(sections)
            if len(item) > 1:
                assert len(item) == 2 and isinstance(item[1],
                                                     nodes.bullet_list)
                if len(sections) > 1:
                    raise self.error('cannot have nested sub-documents '
                                     'since "%s" contains more than one '
                                     'section' % file_name)
                sections[0] += self.interpret_bullet_list(item[1])
        return sections

#     def interpret_field_list(self, field_list):
#         """
#         Parse the field list, read the sub-document specified, and
#         return a list of sections.
#         """
#         assert isinstance(field_list, nodes.field_list)
#         options = {}
#         allowed_options = ('file',)
#         required_options = ('file',)
#         for field in field_list:
#             field_name, field_body = field
#             option = field_name.astext()
#             # XXX HACK -- field bodies should be left unparsed instead
#             # (how do we do this?)
#             assert isinstance(field_body[0], nodes.paragraph)
#             value = field_body[0].rawsource
#             if not option in allowed_options:
#                 raise self.content_error(
#                     '"%s" is not a valid option; must be one of %s'
#                     % (option,
#                        ', '.join(['"%s"' % o for o in allowed_options])))
#             if option in options:
#                 raise self.content_error('duplicate option: "%s"' % option)
#             if not value:
#                 raise self.content_error(
#                     'value expected for "%s" option' % option)
#             options[option] = value
#         return self.read_subdocument(options)

    def read_subdocument(self, options):
        # Perhaps this should be moved into the reader.
        from docutils.readers import standalone
        from docutils.io import FileInput
        reader = standalone.Reader(parser_name='rst')
        file_name = options['file']
        try:
            # TODO make paths relative to document root
            source = FileInput(source_path=file_name,
                               handle_io_errors=False,
                               encoding=self.reader.source.encoding)
        except IOError, error:
            raise self.content_error('could not read file "%s": %s'
                                     % (file_name, error))
        subdocument = reader.read(source=source, parser=None,
                                  settings=self.state.document.settings)
        if len(subdocument) >= 1 and isinstance(subdocument[0], nodes.title):
            # Single document title.
            section = nodes.section(
                subdocument.rawsource, *subdocument.children,
                **subdocument.attributes)
            return [section]
        elif (len(subdocument) >= 1
              # at least one section:
              and [n for n in subdocument if isinstance(n, nodes.section)]
              # only sections and transitions:
              and not [n for n in subdocument if
                       not isinstance(n, (nodes.section, nodes.transition))]):
            return subdocument.children
        else:
            raise self.content_error(
                'problem with file "%s": a sub-document must either '
                'have a single document-title, or it must consist of one '
                'or more top-level sections and optionally transitions'
                % file_name)
