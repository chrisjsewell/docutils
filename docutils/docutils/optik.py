# This is *not* the official distribution of Optik.  See
# http://optik.sourceforge.net/ for the official distro.
#
# This combined module was converted from the "optik" package for Docutils use
# by David Goodger (2002-06-12).  Optik is slated for inclusion in the Python
# standard library as OptionParser.py.  Once Optik itself becomes a single
# module, Docutils will include the official module and kill off this
# temporary fork.

"""optik

A powerful, extensible, and easy-to-use command-line parser for Python.

By Greg Ward <gward@python.net>

See http://optik.sourceforge.net/
"""

# Copyright (c) 2001 Gregory P. Ward.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#   * Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#   * Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in the
#     documentation and/or other materials provided with the distribution.
#
#   * Neither the name of the author nor the names of its
#     contributors may be used to endorse or promote products derived from
#     this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS
# IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
# TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
# PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE REGENTS OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


__revision__ = "$Id$"

__version__ = "1.3+"


import sys
import os
import types
from types import TupleType, DictType
from distutils.fancy_getopt import wrap_text


SUPPRESS_HELP = "SUPPRESS"+"HELP"
SUPPRESS_USAGE = "SUPPRESS"+"USAGE"
# Not supplying a default is different from a default of None,
# so we need an explicit "not supplied" value.
NO_DEFAULT = "NO"+"DEFAULT"


class OptikError (Exception):
    def __init__ (self, msg):
        self.msg = msg

    def __str__ (self):
        return self.msg


class OptionError (OptikError):
    """
    Raised if an Option instance is created with invalid or
    inconsistent arguments.
    """

    def __init__ (self, msg, option):
        self.msg = msg
        self.option_id = str(option)

    def __str__ (self):
        if self.option_id:
            return "option %s: %s" % (self.option_id, self.msg)
        else:
            return self.msg

class OptionConflictError (OptionError):
    """
    Raised if conflicting options are added to an OptionParser.
    """

class OptionValueError (OptikError):
    """
    Raised if an invalid option value is encountered on the command
    line.
    """

class BadOptionError (OptikError):
    """
    Raised if an invalid or ambiguous option is seen on the command-line.
    """


_builtin_cvt = { "int" : (int, "integer"),
                 "long" : (long, "long integer"),
                 "float" : (float, "floating-point"),
                 "complex" : (complex, "complex") }

def check_builtin (option, opt, value):
    (cvt, what) = _builtin_cvt[option.type]
    try:
        return cvt(value)
    except ValueError:
        raise OptionValueError(
            #"%s: invalid %s argument %r" % (opt, what, value))
            "option %s: invalid %s value: %r" % (opt, what, value))


class Option:
    """
    Instance attributes:
      _short_opts : [string]
      _long_opts : [string]

      action : string
      type : string
      dest : string
      default : any
      nargs : int
      const : any
      callback : function
      callback_args : (any*)
      callback_kwargs : { string : any }
      help : string
      metavar : string
    """

    # The list of instance attributes that may be set through
    # keyword args to the constructor.
    ATTRS = ['action',
             'type',
             'dest',
             'default',
             'nargs',
             'const',
             'callback',
             'callback_args',
             'callback_kwargs',
             'help',
             'metavar']

    # The set of actions allowed by option parsers.  Explicitly listed
    # here so the constructor can validate its arguments.
    ACTIONS = ("store",
               "store_const",
               "store_true",
               "store_false",
               "append",
               "count",
               "callback",
               "help",
               "version")

    # The set of actions that involve storing a value somewhere;
    # also listed just for constructor argument validation.  (If
    # the action is one of these, there must be a destination.)
    STORE_ACTIONS = ("store",
                     "store_const",
                     "store_true",
                     "store_false",
                     "append",
                     "count")

    # The set of actions for which it makes sense to supply a value
    # type, ie. where we expect an argument to this option.
    TYPED_ACTIONS = ("store",
                     "append",
                     "callback")

    # The set of known types for option parsers.  Again, listed here for
    # constructor argument validation.
    TYPES = ("string", "int", "long", "float", "complex")

    # Dictionary of argument checking functions, which convert and
    # validate option arguments according to the option type.
    #
    # Signature of checking functions is:
    #   check(option : Option, opt : string, value : string) -> any
    # where
    #   option is the Option instance calling the checker
    #   opt is the actual option seen on the command-line
    #     (eg. "-a", "--file")
    #   value is the option argument seen on the command-line
    #
    # The return value should be in the appropriate Python type
    # for option.type -- eg. an integer if option.type == "int".
    #
    # If no checker is defined for a type, arguments will be
    # unchecked and remain strings.
    TYPE_CHECKER = { "int"    : check_builtin,
                     "long"   : check_builtin,
                     "float"  : check_builtin,
                     "complex"  : check_builtin,
                   }


    # CHECK_METHODS is a list of unbound method objects; they are called
    # by the constructor, in order, after all attributes are
    # initialized.  The list is created and filled in later, after all
    # the methods are actually defined.  (I just put it here because I
    # like to define and document all class attributes in the same
    # place.)  Subclasses that add another _check_*() method should
    # define their own CHECK_METHODS list that adds their check method
    # to those from this class.
    CHECK_METHODS = None


    # -- Constructor/initialization methods ----------------------------

    def __init__ (self, *opts, **attrs):
        # Set _short_opts, _long_opts attrs from 'opts' tuple
        opts = self._check_opt_strings(opts)
        self._set_opt_strings(opts)

        # Set all other attrs (action, type, etc.) from 'attrs' dict
        self._set_attrs(attrs)

        # Check all the attributes we just set.  There are lots of
        # complicated interdependencies, but luckily they can be farmed
        # out to the _check_*() methods listed in CHECK_METHODS -- which
        # could be handy for subclasses!  The one thing these all share
        # is that they raise OptionError if they discover a problem.
        for checker in self.CHECK_METHODS:
            checker(self)

    def _check_opt_strings (self, opts):
        # Filter out None because early versions of Optik had exactly
        # one short option and one long option, either of which
        # could be None.
        opts = filter(None, opts)
        if not opts:
            raise OptionError("at least one option string must be supplied",
                              self)
        return opts

    def _set_opt_strings (self, opts):
        self._short_opts = []
        self._long_opts = []
        for opt in opts:
            if len(opt) < 2:
                raise OptionError(
                    "invalid option string %r: "
                    "must be at least two characters long" % opt, self)
            elif len(opt) == 2:
                if not (opt[0] == "-" and opt[1] != "-"):
                    raise OptionError(
                        "invalid short option string %r: "
                        "must be of the form -x, (x any non-dash char)" % opt,
                        self)
                self._short_opts.append(opt)
            else:
                if not (opt[0:2] == "--" and opt[2] != "-"):
                    raise OptionError(
                        "invalid long option string %r: "
                        "must start with --, followed by non-dash" % opt,
                        self)
                self._long_opts.append(opt)

    def _set_attrs (self, attrs):
        for attr in self.ATTRS:
            if attrs.has_key(attr):
                setattr(self, attr, attrs[attr])
                del attrs[attr]
            else:
                if attr == 'default':
                    setattr(self, attr, NO_DEFAULT)
                else:
                    setattr(self, attr, None)
        if attrs:
            raise OptionError(
                "invalid keyword arguments: %s" % ", ".join(attrs.keys()),
                self)


    # -- Constructor validation methods --------------------------------

    def _check_action (self):
        if self.action is None:
            self.action = "store"
        elif self.action not in self.ACTIONS:
            raise OptionError("invalid action: %r" % self.action, self)

    def _check_type (self):
        if self.type is None:
            # XXX should factor out another class attr here: list of
            # actions that *require* a type
            if self.action in ("store", "append"):
                # No type given?  "string" is the most sensible default.
                self.type = "string"
        else:
            if self.type not in self.TYPES:
                raise OptionError("invalid option type: %r" % self.type, self)
            if self.action not in self.TYPED_ACTIONS:
                raise OptionError(
                    "must not supply a type for action %r" % self.action, self)

    def _check_dest (self):
        if self.action in self.STORE_ACTIONS and self.dest is None:
            # No destination given, and we need one for this action.
            # Glean a destination from the first long option string,
            # or from the first short option string if no long options.
            if self._long_opts:
                # eg. "--foo-bar" -> "foo_bar"
                self.dest = self._long_opts[0][2:].replace('-', '_')
            else:
                self.dest = self._short_opts[0][1]

    def _check_const (self):
        if self.action != "store_const" and self.const is not None:
            raise OptionError(
                "'const' must not be supplied for action %r" % self.action,
                self)

    def _check_nargs (self):
        if self.action in self.TYPED_ACTIONS:
            if self.nargs is None:
                self.nargs = 1
        elif self.nargs is not None:
            raise OptionError(
                "'nargs' must not be supplied for action %r" % self.action,
                self)

    def _check_callback (self):
        if self.action == "callback":
            if not callable(self.callback):
                raise OptionError(
                    "callback not callable: %r" % self.callback, self)
            if (self.callback_args is not None and
                type(self.callback_args) is not TupleType):
                raise OptionError(
                    "callback_args, if supplied, must be a tuple: not %r"
                    % self.callback_args, self)
            if (self.callback_kwargs is not None and
                type(self.callback_kwargs) is not DictType):
                raise OptionError(
                    "callback_kwargs, if supplied, must be a dict: not %r"
                    % self.callback_kwargs, self)
        else:
            if self.callback is not None:
                raise OptionError(
                    "callback supplied (%r) for non-callback option"
                    % self.callback, self)
            if self.callback_args is not None:
                raise OptionError(
                    "callback_args supplied for non-callback option", self)
            if self.callback_kwargs is not None:
                raise OptionError(
                    "callback_kwargs supplied for non-callback option", self)


    CHECK_METHODS = [_check_action,
                     _check_type,
                     _check_dest,
                     _check_const,
                     _check_nargs,
                     _check_callback]


    # -- Miscellaneous methods -----------------------------------------

    def __str__ (self):
        if self._short_opts or self._long_opts:
            return "/".join(self._short_opts + self._long_opts)
        else:
            raise RuntimeError, "short_opts and long_opts both empty!"

    def takes_value (self):
        return self.type is not None


    # -- Processing methods --------------------------------------------

    def check_value (self, opt, value):
        checker = self.TYPE_CHECKER.get(self.type)
        if checker is None:
            return value
        else:
            return checker(self, opt, value)

    def process (self, opt, value, values, parser):

        # First, convert the value(s) to the right type.  Howl if any
        # value(s) are bogus.
        if value is not None:
            if self.nargs == 1:
                value = self.check_value(opt, value)
            else:
                value = tuple([self.check_value(opt, v) for v in value])

        # And then take whatever action is expected of us.
        # This is a separate method to make life easier for
        # subclasses to add new actions.
        return self.take_action(
            self.action, self.dest, opt, value, values, parser)

    def take_action (self, action, dest, opt, value, values, parser):
        if action == "store":
            setattr(values, dest, value)
        elif action == "store_const":
            setattr(values, dest, self.const)
        elif action == "store_true":
            setattr(values, dest, 1)
        elif action == "store_false":
            setattr(values, dest, 0)
        elif action == "append":
            values.ensure_value(dest, []).append(value)
        elif action == "count":
            setattr(values, dest, values.ensure_value(dest, 0) + 1)
        elif action == "callback":
            args = self.callback_args or ()
            kwargs = self.callback_kwargs or {}
            self.callback(self, opt, value, parser, *args, **kwargs)
        elif action == "help":
            parser.print_help()
            sys.exit(0)
        elif action == "version":
            parser.print_version()
            sys.exit(0)
        else:
            raise RuntimeError, "unknown action %r" % self.action

        return 1

# class Option


# Some day, there might be many Option classes.  As of Optik 1.3, the
# preferred way to instantiate Options is indirectly, via make_option(),
# which will become a factory function when there are many Option
# classes.
make_option = Option


STD_HELP_OPTION = Option("-h", "--help",
                         action="help",
                         help="show this help message and exit")
STD_VERSION_OPTION = Option("--version",
                            action="version",
                            help="show program's version number and exit")


class OptionContainer:

    """
    Abstract base class.

    Class attributes:
      standard_option_list : [Option]
        List of standard options that will be accepted by all instances
        of this parser class (intended to be overridden by subclasses).

    Instance attributes:
      option_list : [Option]
        The list of Option objects contained by this OptionContainer.
      _short_opt : { string : Option }
        Dictionary mapping short option strings, eg. "-f" or "-X",
        to the Option instances that implement them.  If an Option
        has multiple short option strings, it will appears in this
        dictionary multiple times. [1]
      _long_opt : { string : Option }
        Dictionary mapping long option strings, eg. "--file" or
        "--exclude", to the Option instances that implement them.
        Again, a given Option can occur multiple times in this
        dictionary. [1]
      defaults : { string : any }
        Dictionary mapping option destination names to default
        values for each destination. [1]

    [1] These mappings are common to (shared by) all components of the
        controlling OptionParser, where they are initially created.

    """

    standard_option_list = []

    def __init__(self, parser, description=None, option_list=None):
        # List of Options is local to this OptionContainer.
        self.option_list = []
        # The shared mappings are stored in the parser.
        self._short_opt = parser._short_opt
        self._long_opt = parser._long_opt
        self.defaults = parser.defaults
        #
        self.format = parser.format
        self.option_class = parser.option_class
        self.conflict_handler = parser.conflict_handler
        self.set_description(description)
        self._populate_option_list(option_list)

    def set_description(self, description):
        self.description = description

    def _populate_option_list(self, option_list, version=None, help=None):
        if self.standard_option_list:
            self.add_options(self.standard_option_list)
        if option_list:
            self.add_options(option_list)
        if version:
            self.add_option(STD_VERSION_OPTION)
        if help:
            self.add_option(STD_HELP_OPTION)


    # -- Option-adding methods -----------------------------------------

    def _check_conflict (self, option):
        conflict_opts = []
        for opt in option._short_opts:
            if self._short_opt.has_key(opt):
                conflict_opts.append((opt, self._short_opt[opt]))
        for opt in option._long_opts:
            if self._long_opt.has_key(opt):
                conflict_opts.append((opt, self._long_opt[opt]))

        if conflict_opts:
            handler = self.conflict_handler
            if handler == "ignore":     # behaviour for Optik 1.0, 1.1
                pass
            elif handler == "error":    # new in 1.2
                raise OptionConflictError(
                    "conflicting option string(s): %s"
                    % ", ".join([co[0] for co in conflict_opts]),
                    option)
            elif handler == "resolve":  # new in 1.2
                for (opt, c_option) in conflict_opts:
                    if opt.startswith("--"):
                        c_option._long_opts.remove(opt)
                        del self._long_opt[opt]
                    else:
                        c_option._short_opts.remove(opt)
                        del self._short_opt[opt]
                    if not (c_option._short_opts or c_option._long_opts):
                        c_option.container.option_list.remove(c_option)

    def add_option (self, *args, **kwargs):
        """add_option(Option)
           add_option(opt_str, ..., kwarg=val, ...)
        """
        if type(args[0]) is types.StringType:
            option = self.option_class(*args, **kwargs)
        elif len(args) == 1 and not kwargs:
            option = args[0]
            if not isinstance(option, Option):
                raise TypeError, "not an Option instance: %r" % option
        else:
            raise TypeError, "invalid arguments"

        self._check_conflict(option)

        self.option_list.append(option)
        option.container = self
        for opt in option._short_opts:
            self._short_opt[opt] = option
        for opt in option._long_opts:
            self._long_opt[opt] = option

        if option.dest is not None:     # option has a dest, we need a default
            if option.default is not NO_DEFAULT:
                self.defaults[option.dest] = option.default
            elif not self.defaults.has_key(option.dest):
                self.defaults[option.dest] = None

    def add_options (self, option_list):
        for option in option_list:
            self.add_option(option)

    # -- Option query/removal methods ----------------------------------

    def get_option (self, opt_str):
        return (self._short_opt.get(opt_str) or
                self._long_opt.get(opt_str))

    def has_option (self, opt_str):
        return (self._short_opt.has_key(opt_str) or
                self._long_opt.has_key(opt_str))

    def remove_option (self, opt_str):
        option = self._short_opt.get(opt_str)
        if option is None:
            option = self._long_opt.get(opt_str)
        if option is None:
            raise ValueError("no such option %r" % opt_str)

        for opt in option._short_opts:
            del self._short_opt[opt]
        for opt in option._long_opts:
            del self._long_opt[opt]
        option.container.option_list.remove(option)


    # -- Feedback methods ----------------------------------------------

    def get_options(self):
        if not self.option_list:
            return ""
        result = []                     # list of strings to "".join() later
        for option in self.option_list:
            if not option.help is SUPPRESS_HELP:
                result.append(self.format.format_option(option))
        return "".join(result)

    def get_description(self):
        if self.description:
            return self.format.format_description(self.description)
        else:
            return ""

    def get_help(self):
        result = ""
        if self.description:
            result = self.get_description() + "\n"
        return result + self.get_options()


class OptionGroup(OptionContainer):

    def __init__(self, parser, title, description=None):
        OptionContainer.__init__(self, parser, description)
        self.parser = parser
        self.title = title
        self.description = description

    def set_title(self, title):
        self.title = title

    def get_help(self):
        result = self.format.format_heading(self.title)
        self.format.increase_nesting()
        result += OptionContainer.get_help(self)
        self.format.decrease_nesting()
        return result


class Values:

    def __init__ (self, defaults=None):
        if defaults:
            for (attr, val) in defaults.items():
                setattr(self, attr, val)


    def _update_careful (self, dict):
        """
        Update the option values from an arbitrary dictionary, but only
        use keys from dict that already have a corresponding attribute
        in self.  Any keys in dict without a corresponding attribute
        are silently ignored.
        """
        for attr in dir(self):
            if dict.has_key(attr):
                dval = dict[attr]
                if dval is not None:
                    setattr(self, attr, dval)

    def _update_loose (self, dict):
        """
        Update the option values from an arbitrary dictionary,
        using all keys from the dictionary regardless of whether
        they have a corresponding attribute in self or not.
        """
        self.__dict__.update(dict)

    def _update (self, dict, mode):
        if mode == "careful":
            self._update_careful(dict)
        elif mode == "loose":
            self._update_loose(dict)
        else:
            raise ValueError, "invalid update mode: %r" % mode

    def read_module (self, modname, mode="careful"):
        __import__(modname)
        mod = sys.modules[modname]
        self._update(vars(mod), mode)

    def read_file (self, filename, mode="careful"):
        vars = {}
        execfile(filename, vars)
        self._update(vars, mode)

    def ensure_value (self, attr, value):
        if not hasattr(self, attr) or getattr(self, attr) is None:
            setattr(self, attr, value)
        return getattr(self, attr)


class OptionParser(OptionContainer):

    """
    Instance attributes:
      usage : string
        a usage string for your program.  Before it is displayed
        to the user, "%prog" will be expanded to the name of
        your program (os.path.basename(sys.argv[0])).

      allow_interspersed_args : boolean = true
        If true, positional arguments may be interspersed with options.
        Assuming -a and -b each take a single argument, the command-line
          -ablah foo bar -bboo baz
        will be interpreted the same as
          -ablah -bboo -- foo bar baz
        If this flag were false, that command line would be interpreted as
          -ablah -- foo bar -bboo baz
        -- ie. we stop processing options as soon as we see the first
        non-option argument.  (This is the tradition followed by
        Python's getopt module, Perl's Getopt::Std, and other argument-
        parsing libraries, but it is generally annoying to users.)

      rargs : [string]
        the argument list currently being parsed.  Only set when
        parse_args() is active, and continually trimmed down as
        we consume arguments.  Mainly there for the benefit of
        callback options.
      largs : [string]
        the list of leftover arguments that we have skipped while
        parsing options.  If allow_interspersed_args is false, this
        list is always empty.
      values : Values
        the set of option values currently being accumulated.  Only
        set when parse_args() is active.  Also mainly for callbacks.

    Because of the 'rargs', 'largs', and 'values' attributes,
    OptionParser is not thread-safe.  If, for some perverse reason, you
    need to parse command-line arguments simultaneously in different
    threads, use different OptionParser instances.

    """

    def __init__ (self,
                  usage=None,
                  description=None,
                  option_list=None,
                  option_class=Option,
                  version=None,
                  help=1,
                  conflict_handler="error",
                  format=None):
        """Override OptionContainer.__init__."""
        self.set_usage(usage)
        self.set_description(description)
        self.option_class = option_class
        self.version = version
        self.set_conflict_handler(conflict_handler)
        self.allow_interspersed_args = 1
        if not format:
            format = Indented()
        self.format = format

        # Create the various lists and dicts that constitute the
        # "option list".  See class docstring for details about
        # each attribute.
        self._create_option_list()

        # Populate the option list; initial sources are the
        # standard_option_list class attribute, the 'option_list' argument,
        # and the STD_VERSION_OPTION and STD_HELP_OPTION globals (if 'version'
        # and/or 'help' supplied).
        self._populate_option_list(option_list, version=version, help=help)

        self._init_parsing_state()

    # -- Private methods -----------------------------------------------
    # (used by the constructor)

    def _create_option_list (self):
        self.option_list = []
        self.option_groups = []
        self._short_opt = {}            # single letter -> Option instance
        self._long_opt = {}             # long option -> Option instance
        self.defaults = {}              # maps option dest -> default value

    def _init_parsing_state (self):
        # These are set in parse_args() for the convenience of callbacks.
        self.rargs = None
        self.largs = None
        self.values = None


    # -- Simple modifier methods ---------------------------------------

    def set_usage (self, usage):
        if usage is None:
            self.usage = "%prog [options]"
        elif usage is SUPPRESS_USAGE:
            self.usage = None
        else:
            self.usage = usage

    def enable_interspersed_args (self):
        self.allow_interspersed_args = 1

    def disable_interspersed_args (self):
        self.allow_interspersed_args = 0

    def set_conflict_handler (self, handler):
        if handler not in ("ignore", "error", "resolve"):
            raise ValueError, "invalid conflict_resolution value %r" % handler
        self.conflict_handler = handler

    def set_default (self, dest, value):
        self.defaults[dest] = value

    def set_defaults (self, **kwargs):
        self.defaults.update(kwargs)

    def get_default_values(self):
        return Values(self.defaults)


    # -- OptionGroup methods -------------------------------------------

    def add_option_group(self, group):
        self.option_groups.append(group)

    def get_option_group(self, opt_str):
        option = (self._short_opt.get(opt_str) or
                  self._long_opt.get(opt_str))
        if option and option.container is not self:
            return option.container
        return None


    # -- Option-parsing methods ----------------------------------------

    def _get_args (self, args):
        if args is None:
            return sys.argv[1:]
        else:
            return args[:]              # don't modify caller's list

    def parse_args (self, args=None, values=None):
        """
        parse_args(args : [string] = sys.argv[1:],
                   values : Values = None)
        -> (values : Values, args : [string])

        Parse the command-line options found in 'args' (default:
        sys.argv[1:]).  Any errors result in a call to 'error()', which
        by default prints the usage message to stderr and calls
        sys.exit() with an error message.  On success returns a pair
        (values, args) where 'values' is an Values instance (with all
        your option values) and 'args' is the list of arguments left
        over after parsing options.
        """
        rargs = self._get_args(args)
        if values is None:
            values = self.get_default_values()

        # Store the halves of the argument list as attributes for the
        # convenience of callbacks:
        #   rargs
        #     the rest of the command-line (the "r" stands for
        #     "remaining" or "right-hand")
        #   largs
        #     the leftover arguments -- ie. what's left after removing
        #     options and their arguments (the "l" stands for "leftover"
        #     or "left-hand")
        self.rargs = rargs
        self.largs = largs = []
        self.values = values

        try:
            stop = self._process_args(largs, rargs, values)
        except (BadOptionError, OptionValueError), err:
            self.error(err.msg)

        args = largs + rargs
        return self.check_values(values, args)

    def check_values (self, values, args):
        """
        check_values(values : Values, args : [string])
        -> (values : Values, args : [string])

        Check that the supplied option values and leftover arguments are
        valid.  Returns the option values and leftover arguments
        (possibly adjusted, possibly completely new -- whatever you
        like).  Default implementation just returns the passed-in
        values; subclasses may override as desired.
        """
        return (values, args)

    def _process_args (self, largs, rargs, values):
        """_process_args(largs : [string],
                         rargs : [string],
                         values : Values)

        Process command-line arguments and populate 'values', consuming
        options and arguments from 'rargs'.  If 'allow_interspersed_args' is
        false, stop at the first non-option argument.  If true, accumulate any
        interspersed non-option arguments in 'largs'.
        """
        while rargs:
            arg = rargs[0]
            # We handle bare "--" explicitly, and bare "-" is handled by the
            # standard arg handler since the short arg case ensures that the
            # len of the opt string is greater than 1.
            if arg == "--":
                del rargs[0]
                return
            elif arg[0:2] == "--":
                # process a single long option (possibly with value(s))
                self._process_long_opt(rargs, values)
            elif arg[:1] == "-" and len(arg) > 1:
                # process a cluster of short options (possibly with
                # value(s) for the last one only)
                self._process_short_opts(rargs, values)
            elif self.allow_interspersed_args:
                largs.append(arg)
                del rargs[0]
            else:
                return                  # stop now, leave this arg in rargs

        # Say this is the original argument list:
        # [arg0, arg1, ..., arg(i-1), arg(i), arg(i+1), ..., arg(N-1)]
        #                            ^
        # (we are about to process arg(i)).
        #
        # Then rargs is [arg(i), ..., arg(N-1)] and largs is a *subset* of
        # [arg0, ..., arg(i-1)] (any options and their arguments will have
        # been removed from largs).
        #
        # _process_arg() will usually consume 1 or more arguments.
        # If it consumes 1 (eg. arg is an option that takes no arguments),
        # then after _process_arg() is done the situation is:
        #
        #   largs = subset of [arg0, ..., arg(i)]
        #   rargs = [arg(i+1), ..., arg(N-1)]
        #
        # If allow_interspersed_args is false, largs will always be
        # *empty* -- still a subset of [arg0, ..., arg(i-1)], but
        # not a very interesting subset!

    def _match_long_opt (self, opt):
        """_match_long_opt(opt : string) -> string

        Determine which long option string 'opt' matches, ie. which one
        it is an unambiguous abbrevation for.  Raises BadOptionError if
        'opt' doesn't unambiguously match any long option string.
        """
        return _match_abbrev(opt, self._long_opt)

    def _process_long_opt (self, rargs, values):
        arg = rargs.pop(0)

        # Value explicitly attached to arg?  Pretend it's the next
        # argument.
        if "=" in arg:
            (opt, next_arg) = arg.split("=", 1)
            rargs.insert(0, next_arg)
            had_explicit_value = 1
        else:
            opt = arg
            had_explicit_value = 0

        opt = self._match_long_opt(opt)
        option = self._long_opt[opt]
        if option.takes_value():
            nargs = option.nargs
            if len(rargs) < nargs:
                if nargs == 1:
                    self.error("%s option requires a value" % opt)
                else:
                    self.error("%s option requires %d values"
                               % (opt, nargs))
            elif nargs == 1:
                value = rargs.pop(0)
            else:
                value = tuple(rargs[0:nargs])
                del rargs[0:nargs]

        elif had_explicit_value:
            self.error("%s option does not take a value" % opt)

        else:
            value = None

        option.process(opt, value, values, self)

    def _process_short_opts (self, rargs, values):
        arg = rargs.pop(0)
        stop = 0
        i = 1
        for ch in arg[1:]:
            opt = "-" + ch
            option = self._short_opt.get(opt)
            i += 1                      # we have consumed a character

            if not option:
                self.error("no such option: %s" % opt)
            if option.takes_value():
                # Any characters left in arg?  Pretend they're the
                # next arg, and stop consuming characters of arg.
                if i < len(arg):
                    rargs.insert(0, arg[i:])
                    stop = 1

                nargs = option.nargs
                if len(rargs) < nargs:
                    if nargs == 1:
                        self.error("%s option requires a value" % opt)
                    else:
                        self.error("%s option requires %s values"
                                   % (opt, nargs))
                elif nargs == 1:
                    value = rargs.pop(0)
                else:
                    value = tuple(rargs[0:nargs])
                    del rargs[0:nargs]

            else:                       # option doesn't take a value
                value = None

            option.process(opt, value, values, self)

            if stop:
                break


    # -- Feedback methods ----------------------------------------------

    def error (self, msg):
        """error(msg : string)

        Print a usage message incorporating 'msg' to stderr and exit.
        If you override this in a subclass, it should not return -- it
        should either exit or raise an exception.
        """
        self.print_usage(sys.stderr)
        sys.exit("%s: error: %s" % (get_prog_name(), msg))

    def get_usage(self):
        if self.usage:
            return self.format.format_usage(
                self.usage.replace("%prog", get_prog_name()))
        else:
            return ""

    def print_usage (self, file=None):
        """print_usage(file : file = stdout)

        Print the usage message for the current program (self.usage) to
        'file' (default stdout).  Any occurence of the string "%prog" in
        self.usage is replaced with the name of the current program
        (basename of sys.argv[0]).  Does nothing if self.usage is empty
        or not defined.
        """
        if self.usage:
            print >>file, self.get_usage()

    def get_version(self):
        if self.version:
            return self.version.replace("%prog", get_prog_name())
        else:
            return ""

    def print_version (self, file=None):
        """print_version(file : file = stdout)

        Print the version message for this program (self.version) to
        'file' (default stdout).  As with print_usage(), any occurence
        of "%prog" in self.version is replaced by the current program's
        name.  Does nothing if self.version is empty or undefined.
        """
        if self.version:
            print >>file, self.get_version()

    def get_options(self):
        result = []
        result.append(self.format.format_heading("Options"))
        self.format.increase_nesting()
        if self.option_list:
            result.append(OptionContainer.get_options(self))
            result.append("\n")
        for group in self.option_groups:
            result.append(group.get_help())
            result.append("\n")
        self.format.decrease_nesting()
        # Drop the last "\n", or the header if no options or option groups:
        return "".join(result[:-1])

    def get_help(self):
        result = []
        if self.usage:
            result.append(self.get_usage() + "\n")
        if self.description:
            result.append(self.get_description() + "\n")
        result.append(self.get_options())
        return "".join(result)

    def print_help (self, file=None):
        """print_help(file : file = stdout)

        Print an extended help message, listing all options and any
        help text provided with them, to 'file' (default stdout).
        """
        if file is None:
            file = sys.stdout
        file.write(self.get_help())

# class OptionParser


class HelpFormat:

    """
    "--help" output format; abstract base class (Strategy design pattern).

    Instance attributes:
      indent_increment : int
        number of columns to indent per nesting level
      help_indent : int
        the starting column for option help text
      width : int
        the overall width (in columns) for output
      current_indent : int
        in columns, calculated
      level : int
        increased for each additional nesting level
      help_width : int
        number of columns available for option help text
    """

    def __init__(self, indent_increment, help_indent, width, short_first):
        self.indent_increment = indent_increment
        self.help_indent = help_indent
        self.width = width
        self.current_indent = 0
        self.level = 0
        self.help_width = self.width - self.help_indent
        if short_first:
            self.format_option_list = self.format_option_list_short_first
        else:
            self.format_option_list = self.format_option_list_long_first

    def increase_nesting(self):
        self.current_indent += self.indent_increment
        self.level += 1

    def decrease_nesting(self):
        self.current_indent -= self.indent_increment
        assert self.current_indent >= 0, "Indent decreased below 0."
        self.level -= 1

    def format_usage(self, usage):
        raise NotImplementedError

    def format_heading(self, heading):
        raise NotImplementedError

    def format_description(self, description):
        desc_width = self.width - self.current_indent
        desc_lines = wrap_text(description, desc_width)
        result = ["%*s%s\n" % (self.current_indent, "", line)
                  for line in desc_lines]
        return "".join(result)

    def format_option(self, option):
        # The help for each option consists of two parts:
        #   * the opt strings and metavars
        #     eg. ("-x", or "-fFILENAME, --file=FILENAME")
        #   * the user-supplied help string
        #     eg. ("turn on expert mode", "read data from FILENAME")
        #
        # If possible, we write both of these on the same line:
        #   -x      turn on expert mode
        #
        # But if the opt string list is too long, we put the help
        # string on a second line, indented to the same column it would
        # start in if it fit on the first line.
        #   -fFILENAME, --file=FILENAME
        #           read data from FILENAME
        result = []
        opts = self.format_option_list(option)
        opt_width = self.help_indent - self.current_indent - 2
        if len(opts) > opt_width:
            opts = "%*s%s\n" % (self.current_indent, "", opts)
            indent_first = self.help_indent
        else:                       # start help on same line as opts
            opts = "%*s%-*s  " % (self.current_indent, "", opt_width, opts)
            indent_first = 0
        result.append(opts)
        if option.help:
            help_lines = wrap_text(option.help, self.help_width)
            result.append("%*s%s\n" % (indent_first, "", help_lines[0]))
            result.extend(["%*s%s\n" % (self.help_indent, "", line)
                           for line in help_lines[1:]])
        elif opts[-1] != "\n":
            result.append("\n")
        return "".join(result)

    def format_option_list(self, option):
        """Return a comma-separated list of option strigs & metavariables."""
        raise NotImplementedError(
            "Virtual method; use format_option_list_short_first or "
            "format_option_list_long_first instead.")

    def format_option_list_short_first(self, option):
        opts = []                       # list of "-a" or "--foo=FILE" strings
        takes_value = option.takes_value()
        if takes_value:
            metavar = option.metavar or option.dest.upper()
            for sopt in option._short_opts:
                opts.append(sopt + metavar)
            for lopt in option._long_opts:
                opts.append(lopt + "=" + metavar)
        else:
            for opt in option._short_opts + option._long_opts:
                opts.append(opt)
        return ", ".join(opts)

    def format_option_list_long_first(self, option):
        opts = []                       # list of "-a" or "--foo=FILE" strings
        takes_value = option.takes_value()
        if takes_value:
            metavar = option.metavar or option.dest.upper()
            for lopt in option._long_opts:
                opts.append(lopt + "=" + metavar)
            for sopt in option._short_opts:
                opts.append(sopt + metavar)
        else:
            for opt in option._long_opts + option._short_opts:
                opts.append(opt)
        return ", ".join(opts)


class Indented(HelpFormat):

    """Formats help with indented section bodies."""

    def __init__(self, indent_increment=2, help_indent=24, width=78,
                 short_first=1):
        HelpFormat.__init__(self, indent_increment, help_indent, width,
                            short_first)

    def format_usage(self, usage):
        return "Usage: %s\n" % usage

    def format_heading(self, heading):
        return "%*s%s:\n" % (self.current_indent, "", heading)


class Titled(HelpFormat):

    """Formats help with underlined section headers."""

    def __init__(self, indent_increment=0, help_indent=24, width=78,
                 short_first=None):
        HelpFormat.__init__(self, indent_increment, help_indent, width,
                            short_first)

    def format_usage(self, usage):
        return "%s  %s\n" % (self.format_heading("Usage"), usage)

    def format_heading(self, heading):
        return "%s\n%s\n" % (heading, "=-"[self.level] * len(heading))


def _match_abbrev (s, wordmap):
    """_match_abbrev(s : string, wordmap : {string : Option}) -> string

    Return the string key in 'wordmap' for which 's' is an unambiguous
    abbreviation.  If 's' is found to be ambiguous or doesn't match any of
    'words', raise BadOptionError.
    """
    # Is there an exact match?
    if wordmap.has_key(s):
        return s
    else:
        # Isolate all words with s as a prefix.
        possibilities = [word for word in wordmap.keys()
                         if word.startswith(s)]
        # No exact match, so there had better be just one possibility.
        if len(possibilities) == 1:
            return possibilities[0]
        elif not possibilities:
            raise BadOptionError("no such option: %s" % s)
        else:
            # More than one possible completion: ambiguous prefix.
            raise BadOptionError("ambiguous option: %s (%s?)"
                                 % (s, ", ".join(possibilities)))

def get_prog_name ():
    return os.path.basename(sys.argv[0])
