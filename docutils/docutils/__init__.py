# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
This is the Docutils (Python Documentation Utilities) package.

Package Structure
=================

Modules:

- __init__.py: Contains component base classes, exception classes, and
  Docutils `__version__`.

- core.py: Contains the ``Publisher`` class and ``publish_*()`` convenience
  functions.

- frontend.py: Runtime settings (command-line interface, configuration files)
  processing, for Docutils front-ends.

- io.py: Provides a uniform API for low-level input and output.

- nodes.py: Docutils document tree (doctree) node class library.

- statemachine.py: A finite state machine specialized for
  regular-expression-based text filters.

- urischemes.py: Contains a complete mapping of known URI addressing
  scheme names to descriptions.

- utils.py: Contains the ``Reporter`` system warning class and miscellaneous
  utilities.

Subpackages:

- languages: Language-specific mappings of terms.

- parsers: Syntax-specific input parser modules or packages.

- readers: Context-specific input handlers which understand the data
  source and manage a parser.

- transforms: Modules used by readers and writers to modify DPS
  doctrees.

- writers: Format-specific output translators.
"""

__docformat__ = 'reStructuredText'

__version__ = '0.3.3'
"""``major.minor.micro`` version number.  The micro number is bumped
any time there's a change in the API incompatible with one of the
front ends or significant new functionality, and at any alpha or beta
release.  The minor number is bumped whenever there is a stable
project release.  The major number will be bumped when the project is
feature-complete, and perhaps if there is a major change in the
design."""


class ApplicationError(StandardError): pass
class DataError(ApplicationError): pass


class SettingsSpec:

    """
    Runtime setting specification base class.

    SettingsSpec subclass objects used by `docutils.frontend.OptionParser`.
    """

    settings_spec = ()
    """Runtime settings specification.  Override in subclasses.

    Specifies runtime settings and associated command-line options, as used by
    `docutils.frontend.OptionParser`.  This tuple contains one or more sets of
    option group title, description, and a list/tuple of tuples: ``('help
    text', [list of option strings], {keyword arguments})``.  Group title
    and/or description may be `None`; a group title of `None` implies no
    group, just a list of single options.  The "keyword arguments" dictionary
    contains arguments to the OptionParser/OptionGroup ``add_option`` method,
    with the addition of a "validator" keyword (see the
    `docutils.frontend.OptionParser.validators` instance attribute).  Runtime
    settings names are derived implicitly from long option names
    ("--a-setting" becomes ``settings.a_setting``) or explicitly from the
    "dest" keyword argument."""

    settings_defaults = None
    """A dictionary of defaults for internal or inaccessible (by command-line
    or config file) settings.  Override in subclasses."""

    settings_default_overrides = None
    """A dictionary of auxiliary defaults, to override defaults for settings
    defined in other components.  Override in subclasses."""

    relative_path_settings = ()
    """Settings containing filesystem paths.  Override in subclasses.
    Settings listed here are to be interpreted relative to the current working
    directory."""

    config_section = None
    """The name of the config file section specific to this component
    (lowercase, no brackets).  Override in subclasses."""

    config_section_dependencies = None
    """A list of names of config file sections that are to be applied before
    `config_section`, in order (from general to specific).  In other words,
    the settings in `config_section` are to be overlaid on top of the settings
    from these sections.  The "general" section is assumed implicitly.
    Override in subclasses."""


class TransformSpec:

    """
    Runtime transform specification base class.

    TransformSpec subclass objects used by `docutils.transforms.Transformer`.
    """

    default_transforms = ()
    """Transforms required by this class.  Override in subclasses."""
    
    unknown_reference_resolvers = ()
    """List of functions to try to resolve unknown references.  Called when
    FinalCheckVisitor is unable to find a correct target.  The list should
    contain functions which will try to resolve unknown references, with the
    following signature::

        def reference_resolver(node):
            '''Returns boolean: true if resolved, false if not.'''

    Each function must have a "priority" attribute which will affect the order
    the unknown_reference_resolvers are run::

        reference_resolver.priority = 100

    Override in subclasses."""


class Component(SettingsSpec, TransformSpec):

    """Base class for Docutils components."""

    component_type = None
    """Name of the component type ('reader', 'parser', 'writer').  Override in
    subclasses."""

    supported = ()
    """Names for this component.  Override in subclasses."""
    
    def supports(self, format):
        """
        Is `format` supported by this component?

        To be used by transforms to ask the dependent component if it supports
        a certain input context or output format.
        """
        return format in self.supported
