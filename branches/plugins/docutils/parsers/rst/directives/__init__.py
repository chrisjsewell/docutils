# $Id$
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
This package contains directive implementation modules.
"""

__docformat__ = 'reStructuredText'

import re
import codecs
import sys
from docutils import nodes, utils
from docutils.parsers.rst.languages import en as _fallback_language_module


def _deprecated(fn):
    print >>sys.stderr, \
          'Warning: docutils.parsers.rst.directives.%s is deprecated; ' \
          'see <http://docutils.sf.net/docs/howto/rst-directives.html>.' % fn

_directive_registry = {}
"""Mapping of directive name to (module name, class name).  The
directive name is canonical & must be lowercase.  Language-dependent
names are defined in the ``language`` subpackage.  This mapping is
deprecated; see <http://docutils.sf.net/docs/howto/rst-directives.html>."""

_directives = {}
"""Cache of imported directives."""

def directive(directive_name, language_module, document):
    """
    Locate and return a directive function from its language-dependent name.
    If not found in the current language, check English.  Return None if the
    named directive cannot be found.
    """
    normname = directive_name.lower()
    messages = []
    msg_text = []
    if _directives.has_key(normname):
        return _directives[normname], messages
    canonicalname = None
    try:
        canonicalname = language_module.directives[normname]
    except AttributeError, error:
        msg_text.append('Problem retrieving directive entry from language '
                        'module %r: %s.' % (language_module, error))
    except KeyError:
        msg_text.append('No directive entry for "%s" in module "%s".'
                        % (directive_name, language_module.__name__))
    if not canonicalname:
        try:
            canonicalname = _fallback_language_module.directives[normname]
            msg_text.append('Using English fallback for directive "%s".'
                            % directive_name)
        except KeyError:
            msg_text.append('Trying "%s" as canonical directive name.'
                            % directive_name)
            # The canonical name should be an English name, but just in case:
            canonicalname = normname
    if msg_text:
        message = document.reporter.info(
            '\n'.join(msg_text), line=document.current_line)
        messages.append(message)
    try:
        directive = utils.get_entry_point('docutils.parsers.rst.directives',
                                          canonicalname)
    except utils.EntryPointNotFoundError:
        # Retain backwards compatibility with _directive_registry mechanism.
        if _directive_registry.has_key(canonicalname):
            _deprecated('_directive_registry')
            modulename, classname = _directive_registry[canonicalname]
            try:
                module = __import__(modulename, globals(), locals())
            except ImportError, detail:
                messages.append(document.reporter.error(
                    'Error importing directive module "%s" (directive "%s"):\n%s'
                    % (modulename, directive_name, detail),
                    line=document.current_line))
                return None, messages
            try:
                directive = getattr(module, classname)
                _directives[normname] = directive
            except AttributeError:
                messages.append(document.reporter.error(
                    'No directive class "%s" in module "%s" (directive "%s").'
                    % (classname, modulename, directive_name),
                    line=document.current_line))
                return None, messages
            return directive, messages
        # Error handling done by caller.
        return None, messages
    _directives[normname] = directive
    return directive, messages

def register_directive(name, directive):
    """
    Register a nonstandard application-defined directive function.
    Language lookups are not needed for such functions.
    """
    _deprecated('register_directive()')
    _directives[name] = directive

def flag(argument):
    """
    Check for a valid flag option (no argument) and return ``None``.
    (Directive option conversion function.)

    Raise ``ValueError`` if an argument is found.
    """
    if argument and argument.strip():
        raise ValueError('no argument is allowed; "%s" supplied' % argument)
    else:
        return None

def unchanged_required(argument):
    """
    Return the argument text, unchanged.
    (Directive option conversion function.)

    Raise ``ValueError`` if no argument is found.
    """
    if argument is None:
        raise ValueError('argument required but none supplied')
    else:
        return argument  # unchanged!

def unchanged(argument):
    """
    Return the argument text, unchanged.
    (Directive option conversion function.)

    No argument implies empty string ("").
    """
    if argument is None:
        return u''
    else:
        return argument  # unchanged!

def path(argument):
    """
    Return the path argument unwrapped (with newlines removed).
    (Directive option conversion function.)

    Raise ``ValueError`` if no argument is found.
    """
    if argument is None:
        raise ValueError('argument required but none supplied')
    else:
        path = ''.join([s.strip() for s in argument.splitlines()])
        return path

def uri(argument):
    """
    Return the URI argument with whitespace removed.
    (Directive option conversion function.)

    Raise ``ValueError`` if no argument is found.
    """
    if argument is None:
        raise ValueError('argument required but none supplied')
    else:
        uri = ''.join(argument.split())
        return uri

def nonnegative_int(argument):
    """
    Check for a nonnegative integer argument; raise ``ValueError`` if not.
    (Directive option conversion function.)
    """
    value = int(argument)
    if value < 0:
        raise ValueError('negative value; must be positive or zero')
    return value

length_units = ['em', 'ex', 'px', 'in', 'cm', 'mm', 'pt', 'pc']

def get_measure(argument, units):
    """
    Check for a positive argument of one of the units and return a
    normalized string of the form "<value><unit>" (without space in
    between).
    
    To be called from directive option conversion functions.
    """
    match = re.match(r'^([0-9.]+) *(%s)$' % '|'.join(units), argument)
    try:
        assert match is not None
        float(match.group(1))
    except (AssertionError, ValueError):
        raise ValueError(
            'not a positive measure of one of the following units:\n%s'
            % ' '.join(['"%s"' % i for i in units]))
    return match.group(1) + match.group(2)

def length_or_unitless(argument):
    return get_measure(argument, length_units + [''])

def length_or_percentage_or_unitless(argument):
    return get_measure(argument, length_units + ['%', ''])

def class_option(argument):
    """
    Convert the argument into a list of ID-compatible strings and return it.
    (Directive option conversion function.)

    Raise ``ValueError`` if no argument is found.
    """
    if argument is None:
        raise ValueError('argument required but none supplied')
    names = argument.split()
    class_names = []
    for name in names:
        class_name = nodes.make_id(name)
        if not class_name:
            raise ValueError('cannot make "%s" into a class name' % name)
        class_names.append(class_name)
    return class_names

unicode_pattern = re.compile(
    r'(?:0x|x|\\x|U\+?|\\u)([0-9a-f]+)$|&#x([0-9a-f]+);$', re.IGNORECASE)

def unicode_code(code):
    r"""
    Convert a Unicode character code to a Unicode character.
    (Directive option conversion function.)

    Codes may be decimal numbers, hexadecimal numbers (prefixed by ``0x``,
    ``x``, ``\x``, ``U+``, ``u``, or ``\u``; e.g. ``U+262E``), or XML-style
    numeric character entities (e.g. ``&#x262E;``).  Other text remains as-is.

    Raise ValueError for illegal Unicode code values.
    """
    try:
        if code.isdigit():                  # decimal number
            return unichr(int(code))
        else:
            match = unicode_pattern.match(code)
            if match:                       # hex number
                value = match.group(1) or match.group(2)
                return unichr(int(value, 16))
            else:                           # other text
                return code
    except OverflowError, detail:
        raise ValueError('code too large (%s)' % detail)

def single_char_or_unicode(argument):
    """
    A single character is returned as-is.  Unicode characters codes are
    converted as in `unicode_code`.  (Directive option conversion function.)
    """
    char = unicode_code(argument)
    if len(char) > 1:
        raise ValueError('%r invalid; must be a single character or '
                         'a Unicode code' % char)
    return char

def single_char_or_whitespace_or_unicode(argument):
    """
    As with `single_char_or_unicode`, but "tab" and "space" are also supported.
    (Directive option conversion function.)
    """
    if argument == 'tab':
        char = '\t'
    elif argument == 'space':
        char = ' '
    else:
        char = single_char_or_unicode(argument)
    return char

def positive_int(argument):
    """
    Converts the argument into an integer.  Raises ValueError for negative,
    zero, or non-integer values.  (Directive option conversion function.)
    """
    value = int(argument)
    if value < 1:
        raise ValueError('negative or zero value; must be positive')
    return value

def positive_int_list(argument):
    """
    Converts a space- or comma-separated list of values into a Python list
    of integers.
    (Directive option conversion function.)

    Raises ValueError for non-positive-integer values.
    """
    if ',' in argument:
        entries = argument.split(',')
    else:
        entries = argument.split()
    return [positive_int(entry) for entry in entries]

def encoding(argument):
    """
    Verfies the encoding argument by lookup.
    (Directive option conversion function.)

    Raises ValueError for unknown encodings.
    """
    try:
        codecs.lookup(argument)
    except LookupError:
        raise ValueError('unknown encoding: "%s"' % argument)
    return argument

def choice(argument, values):
    """
    Directive option utility function, supplied to enable options whose
    argument must be a member of a finite set of possible values (must be
    lower case).  A custom conversion function must be written to use it.  For
    example::

        from docutils.parsers.rst import directives

        def yesno(argument):
            return directives.choice(argument, ('yes', 'no'))

    Raise ``ValueError`` if no argument is found or if the argument's value is
    not valid (not an entry in the supplied list).
    """
    try:
        value = argument.lower().strip()
    except AttributeError:
        raise ValueError('must supply an argument; choose from %s'
                         % format_values(values))
    if value in values:
        return value
    else:
        raise ValueError('"%s" unknown; choose from %s'
                         % (argument, format_values(values)))

def format_values(values):
    return '%s, or "%s"' % (', '.join(['"%s"' % s for s in values[:-1]]),
                            values[-1])