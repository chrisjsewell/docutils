# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Miscellaneous utilities for the documentation utilities.
"""

__docformat__ = 'reStructuredText'

import sys
import os
import os.path
from types import StringType, UnicodeType
from docutils import ApplicationError, DataError
from docutils import frontend, nodes


class SystemMessage(ApplicationError):

    def __init__(self, system_message):
        Exception.__init__(self, system_message.astext())


class Reporter:

    """
    Info/warning/error reporter and ``system_message`` element generator.

    Five levels of system messages are defined, along with corresponding
    methods: `debug()`, `info()`, `warning()`, `error()`, and `severe()`.

    There is typically one Reporter object per process.  A Reporter object is
    instantiated with thresholds for reporting (generating warnings) and
    halting processing (raising exceptions), a switch to turn debug output on
    or off, and an I/O stream for warnings.  These are stored in the default
    reporting category, '' (zero-length string).

    Multiple reporting categories [#]_ may be set, each with its own reporting
    and halting thresholds, debugging switch, and warning stream
    (collectively a `ConditionSet`).  Categories are hierarchical dotted-name
    strings that look like attribute references: 'spam', 'spam.eggs',
    'neeeow.wum.ping'.  The 'spam' category is the ancestor of
    'spam.bacon.eggs'.  Unset categories inherit stored conditions from their
    closest ancestor category that has been set.

    When a system message is generated, the stored conditions from its
    category (or ancestor if unset) are retrieved.  The system message level
    is compared to the thresholds stored in the category, and a warning or
    error is generated as appropriate.  Debug messages are produced iff the
    stored debug switch is on.  Message output is sent to the stored warning
    stream.

    The default category is '' (empty string).  By convention, Writers should
    retrieve reporting conditions from the 'writer' category (which, unless
    explicitly set, defaults to the conditions of the default category).

    The Reporter class also employs a modified form of the "Observer" pattern
    [GoF95]_ to track system messages generated.  The `attach_observer` method
    should be called before parsing, with a bound method or function which
    accepts system messages.  The observer can be removed with
    `detach_observer`, and another added in its place.

    .. [#] The concept of "categories" was inspired by the log4j project:
       http://jakarta.apache.org/log4j/.

    .. [GoF95] Gamma, Helm, Johnson, Vlissides. *Design Patterns: Elements of
       Reusable Object-Oriented Software*. Addison-Wesley, Reading, MA, USA,
       1995.
    """

    levels = 'DEBUG INFO WARNING ERROR SEVERE'.split()
    """List of names for system message levels, indexed by level."""

    def __init__(self, source, report_level, halt_level, stream=None,
                 debug=0):
        """
        Initialize the `ConditionSet` forthe `Reporter`'s default category.

        :Parameters:

            - `source`: The path to or description of the source data.
            - `report_level`: The level at or above which warning output will
              be sent to `stream`.
            - `halt_level`: The level at or above which `SystemMessage`
              exceptions will be raised, halting execution.
            - `debug`: Show debug (level=0) system messages?
            - `stream`: Where warning output is sent.  Can be file-like (has a
              ``.write`` method), a string (file name, opened for writing), or
              `None` (implies `sys.stderr`; default).
        """
        self.source = source
        """The path to or description of the source data."""
        
        if stream is None:
            stream = sys.stderr
        elif type(stream) in (StringType, UnicodeType):
            raise NotImplementedError('This should open a file for writing.')

        self.categories = {'': ConditionSet(debug, report_level, halt_level,
                                            stream)}
        """Mapping of category names to conditions. Default category is ''."""

        self.observers = []
        """List of bound methods or functions to call with each system_message
        created."""

    def set_conditions(self, category, report_level, halt_level,
                       stream=None, debug=0):
        if stream is None:
            stream = sys.stderr
        self.categories[category] = ConditionSet(debug, report_level,
                                                 halt_level, stream)

    def unset_conditions(self, category):
        if category and self.categories.has_key(category):
            del self.categories[category]

    __delitem__ = unset_conditions

    def get_conditions(self, category):
        while not self.categories.has_key(category):
            category = category[:category.rfind('.') + 1][:-1]
        return self.categories[category]

    __getitem__ = get_conditions

    def attach_observer(self, observer):
        """
        The `observer` parameter is a function or bound method which takes one
        argument, a `nodes.system_message` instance.
        """
        self.observers.append(observer)

    def detach_observer(self, observer):
        self.observers.remove(observer)

    def notify_observers(self, message):
        for observer in self.observers:
            observer(message)

    def system_message(self, level, message, *children, **kwargs):
        """
        Return a system_message object.

        Raise an exception or generate a warning if appropriate.
        """
        attributes = kwargs.copy()
        category = kwargs.get('category', '')
        if kwargs.has_key('category'):
            del attributes['category']
        if kwargs.has_key('base_node'):
            source, line = get_source_line(kwargs['base_node'])
            del attributes['base_node']
            if source is not None:
                attributes.setdefault('source', source)
            if line is not None:
                attributes.setdefault('line', line)
        attributes.setdefault('source', self.source)
        msg = nodes.system_message(message, level=level,
                                   type=self.levels[level],
                                   *children, **attributes)
        debug, report_level, halt_level, stream = self[category].astuple()
        if level >= report_level or debug and level == 0:
            if category:
                print >>stream, msg.astext(), '[%s]' % category
            else:
                print >>stream, msg.astext()
        if level >= halt_level:
            raise SystemMessage(msg)
        if level > 0 or debug:
            self.notify_observers(msg)
        return msg

    def debug(self, *args, **kwargs):
        """
        Level-0, "DEBUG": an internal reporting issue. Typically, there is no
        effect on the processing. Level-0 system messages are handled
        separately from the others.
        """
        return self.system_message(0, *args, **kwargs)

    def info(self, *args, **kwargs):
        """
        Level-1, "INFO": a minor issue that can be ignored. Typically there is
        no effect on processing, and level-1 system messages are not reported.
        """
        return self.system_message(1, *args, **kwargs)

    def warning(self, *args, **kwargs):
        """
        Level-2, "WARNING": an issue that should be addressed. If ignored,
        there may be unpredictable problems with the output.
        """
        return self.system_message(2, *args, **kwargs)

    def error(self, *args, **kwargs):
        """
        Level-3, "ERROR": an error that should be addressed. If ignored, the
        output will contain errors.
        """
        return self.system_message(3, *args, **kwargs)

    def severe(self, *args, **kwargs):
        """
        Level-4, "SEVERE": a severe error that must be addressed. If ignored,
        the output will contain severe errors. Typically level-4 system
        messages are turned into exceptions which halt processing.
        """
        return self.system_message(4, *args, **kwargs)


class ConditionSet:

    """
    A set of two thresholds (`report_level` & `halt_level`), a switch
    (`debug`), and an I/O stream (`stream`), corresponding to one `Reporter`
    category.
    """

    def __init__(self, debug, report_level, halt_level, stream):
        self.debug = debug
        self.report_level = report_level
        self.halt_level = halt_level
        self.stream = stream

    def astuple(self):
        return (self.debug, self.report_level, self.halt_level,
                self.stream)


class ExtensionOptionError(DataError): pass
class BadOptionError(ExtensionOptionError): pass
class BadOptionDataError(ExtensionOptionError): pass
class DuplicateOptionError(ExtensionOptionError): pass


def extract_extension_options(field_list, option_spec):
    """
    Return a dictionary mapping extension option names to converted values.

    :Parameters:
        - `field_list`: A flat field list without field arguments, where each
          field body consists of a single paragraph only.
        - `option_spec`: Dictionary mapping known option names to a
          conversion function such as `int` or `float`.

    :Exceptions:
        - `KeyError` for unknown option names.
        - `ValueError` for invalid option values (raised by the conversion
           function).
        - `DuplicateOptionError` for duplicate options.
        - `BadOptionError` for invalid fields.
        - `BadOptionDataError` for invalid option data (missing name,
          missing data, bad quotes, etc.).
    """
    option_list = extract_options(field_list)
    option_dict = assemble_option_dict(option_list, option_spec)
    return option_dict

def extract_options(field_list):
    """
    Return a list of option (name, value) pairs from field names & bodies.

    :Parameter:
        `field_list`: A flat field list, where each field name is a single
        word and each field body consists of a single paragraph only.

    :Exceptions:
        - `BadOptionError` for invalid fields.
        - `BadOptionDataError` for invalid option data (missing name,
          missing data, bad quotes, etc.).
    """
    option_list = []
    for field in field_list:
        if len(field[0].astext().split()) != 1:
            raise BadOptionError(
                'extension option field name may not contain multiple words')
        name = str(field[0].astext().lower())
        body = field[1]
        if len(body) == 0:
            data = None
        elif len(body) > 1 or not isinstance(body[0], nodes.paragraph) \
              or len(body[0]) != 1 or not isinstance(body[0][0], nodes.Text):
            raise BadOptionDataError(
                  'extension option field body may contain\n'
                  'a single paragraph only (option "%s")' % name)
        else:
            data = body[0][0].astext()
        option_list.append((name, data))
    return option_list

def assemble_option_dict(option_list, option_spec):
    """
    Return a mapping of option names to values.

    :Parameters:
        - `option_list`: A list of (name, value) pairs (the output of
          `extract_options()`).
        - `option_spec`: Dictionary mapping known option names to a
          conversion function such as `int` or `float`.

    :Exceptions:
        - `KeyError` for unknown option names.
        - `DuplicateOptionError` for duplicate options.
        - `ValueError` for invalid option values (raised by conversion
           function).
    """
    options = {}
    for name, value in option_list:
        convertor = option_spec[name]       # raises KeyError if unknown
        if options.has_key(name):
            raise DuplicateOptionError('duplicate option "%s"' % name)
        try:
            options[name] = convertor(value)
        except (ValueError, TypeError), detail:
            raise detail.__class__('(option: "%s"; value: %r)\n%s'
                                   % (name, value, detail))
    return options


class NameValueError(DataError): pass


def extract_name_value(line):
    """
    Return a list of (name, value) from a line of the form "name=value ...".

    :Exception:
        `NameValueError` for invalid input (missing name, missing data, bad
        quotes, etc.).
    """
    attlist = []
    while line:
        equals = line.find('=')
        if equals == -1:
            raise NameValueError('missing "="')
        attname = line[:equals].strip()
        if equals == 0 or not attname:
            raise NameValueError(
                  'missing attribute name before "="')
        line = line[equals+1:].lstrip()
        if not line:
            raise NameValueError(
                  'missing value after "%s="' % attname)
        if line[0] in '\'"':
            endquote = line.find(line[0], 1)
            if endquote == -1:
                raise NameValueError(
                      'attribute "%s" missing end quote (%s)'
                      % (attname, line[0]))
            if len(line) > endquote + 1 and line[endquote + 1].strip():
                raise NameValueError(
                      'attribute "%s" end quote (%s) not followed by '
                      'whitespace' % (attname, line[0]))
            data = line[1:endquote]
            line = line[endquote+1:].lstrip()
        else:
            space = line.find(' ')
            if space == -1:
                data = line
                line = ''
            else:
                data = line[:space]
                line = line[space+1:].lstrip()
        attlist.append((attname.lower(), data))
    return attlist

def normalize_name(name):
    """Return a case- and whitespace-normalized name."""
    return ' '.join(name.lower().split())

def new_document(source, options=None):
    if options is None:
        options = frontend.OptionParser().get_default_values()
    reporter = Reporter(source, options.report_level, options.halt_level,
                        options.warning_stream, options.debug)
    document = nodes.document(options, reporter, source=source)
    document.note_source(source)
    return document

def clean_rcs_keywords(paragraph, keyword_substitutions):
    if len(paragraph) == 1 and isinstance(paragraph[0], nodes.Text):
        textnode = paragraph[0]
        for pattern, substitution in keyword_substitutions:
            match = pattern.match(textnode.data)
            if match:
                textnode.data = pattern.sub(substitution, textnode.data)
                return

def relative_path(source, target):
    """
    Build and return a path to `target`, relative to `source`.

    If there is no common prefix, return the absolute path to `target`.
    """
    source_parts = os.path.abspath(source or '').split(os.sep)
    target_parts = os.path.abspath(target).split(os.sep)
    if source_parts[:1] != target_parts[:1]:
        # Nothing in common between paths.  Return absolute path.
        return '/'.join(target_parts)
    source_parts.reverse()
    target_parts.reverse()
    while (source_parts and target_parts
           and source_parts[-1] == target_parts[-1]):
        # Remove path components in common:
        source_parts.pop()
        target_parts.pop()
    target_parts.reverse()
    parts = ['..'] * (len(source_parts) - 1) + target_parts
    return '/'.join(parts)

def get_source_line(node):
    """
    Return the "source" and "line" attributes from the `node` given or from
    it's closest ancestor.
    """
    while node:
        if node.source or node.line:
            return node.source, node.line
        node = node.parent
    return None, None
