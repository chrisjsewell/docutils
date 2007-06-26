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
from docutils.parsers.rst import directives


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
        node = nodes.Element()  # anonymous container for parsing
        self.state.nested_parse(self.content, self.content_offset, node)
        if len(node) != 1 or not isinstance(node[0], nodes.bullet_list):
            raise self.content_error(
                'directive must contain exactly one bullet list')
        return self.parse_bullet_list(node[0])

    def content_error(self, message):  # , node
        return self.error(
            'Error with %s directive: %s.' % (self.name, message))
        # XXX How do we report an error with the particular node it
        # occurred at, not with the whole directive?
        #msg_node = self.state.reporter.system_message(3, message_text)
        #source_line = self.state_machine.input_lines[node.LINE_NUMBER?]
        #msg_node += nodes.literal_block(node.rawsource, node.rawsource) # does not work
        #return msg_node

    def parse_bullet_list(self, bullet_list):
        """
        Parse the bullet list, read the sub-documents, and return a
        list of sections.
        """
        assert isinstance(bullet_list, nodes.bullet_list)
        sections = []
        for item in bullet_list:
            # Error checking.
            if len(item) == 0:
                raise self.content_error('bullet list item may not be empty')
            if not isinstance(item[0], nodes.field_list):
                raise self.content_error(
                    'bullet list item must start with a field list')
            if len(item) > 1 and not isinstance(item[1], nodes.bullet_list):
                raise self.content_error(
                    'there may only (optionally) be a nested bullet list '
                    'after the initial field list in a bullet list item')
            if len(item) > 2:
                raise self.content_error(
                    'there must not be any elements after a bullet list')
            assert isinstance(item[0], nodes.field_list) and (
                len(item) == 1 or (len(item) == 2 and
                                   isinstance(item[1], nodes.bullet_list))), \
                'problem with structure; this should have been caught before'
            # Parse field list.
            sections += self.parse_field_list(item[0])
            # Parse nested bullet list.
            assert len(item) != 2, 'nested sub-documents not yet implemented'
        return sections

    def parse_field_list(self, field_list):
        """
        Parse the field list, read the sub-document specified, and
        return a list of sections.
        """
        assert isinstance(field_list, nodes.field_list)
        options = {}
        allowed_options = ('file',)
        required_options = ('file',)
        for field in field_list:
            field_name, field_body = field
            option = field_name.astext()
            # XXX HACK -- field bodies should be left unparsed instead
            # (how do we do this?)
            assert isinstance(field_body[0], nodes.paragraph)
            value = field_body[0].rawsource
            if not option in allowed_options:
                raise self.content_error(
                    '"%s" is not a valid option; must be one of %s'
                    % (option,
                       ', '.join(['"%s"' % o for o in allowed_options])))
            if option in options:
                raise self.content_error('duplicate option: "%s"' % option)
            if not value:
                raise self.content_error(
                    'value expected for "%s" option' % option)
            options[option] = value
        return self.read_subdocument(options)

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
