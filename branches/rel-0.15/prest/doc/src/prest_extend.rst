======================
How to Extend Prest
======================
:Author: Mark Nodine
:Contact: mnodine@alum.mit.edu
:Revision: $Revision: 762 $
:Date: $Date: 2006-01-27 11:47:47 -0600 (Fri, 27 Jan 2006) $
:Copyright: This document has been placed in the public domain.

.. perl::
   # Make path safe for -T
   my $perl_dir = $1 if $^X =~ m|^(.*)/|;
   $ENV{PATH} = "$perl_dir:/bin";

.. contents::

This document explains how to write new modules to extend prest.  There
are two principal mechanisms by which prest can be extended: adding new
plug-in directives/roles and adding new writers.  For either of these tasks,
the programmer should be familiar with the DOM_ data structure and the
`DOM.pm`_ subroutines.

.. _`DOM`: `Text::Restructured::DOM`_
.. _`DOM.pm`: prest_internals.html#dom-pm

Adding New Directives
---------------------

To add a plug-in directive, the programmer should be familiar with the
Text::Restructured::Directive:: routines.  The `parser`_ objects are
those of type `Text::Restructured`_.  Important routines are
`Text::Restructured::Directive::arg_check`_, as well as the
Text::Restructured:: routines `Text::Restructured::system_message`_
and `Text::Restructured::Paragraphs`_.

A plug-in directive can be added by creating a Perl module with the
same name as the directive (with a ".pm" extension, of course).  The
Perl module should have an ``init`` routine which registers the
routine to call to process the directive using
`Text::Restructured::Directive::handle_directive`_ (though this call
can also be in a BEGIN block).  The ``init`` routine is called with
the arguments ``($parser, $source, $lineno)``, where
``$parser`` is the ``Text::Restructured`` object, ``$source`` is the
name of the file containing the directive,, and ``$lineno`` is the
line number within ``$source``.

As an example from the ``if`` plug-in directive,

.. system:: perl -ne 'print if /^BEGIN/ .. /^\}/' .\./.\./blib/lib/Text/Restructured/Directive/if.pm
   :literal:

Whatever routine you designate will get called with the following
arguments:

  *``$parser``*:
    The `Text::Restructured`_ object holding the state of the current
    parser.
  *``$name``*:
    The directive name.  This argument is useful if you use the same
    routine to process more than one directive with different names.
  *``$parent``*:
    Pointer to the parent DOM object.  It is needed to add new DOM objects
    to the parent's contents.
  *``$source``*:
    A string indicating the source for the directive.  If you call
    `Text::Restructured::Paragraphs`_ to parse reStructuredText
    recursively, you should supply it a source like "$name directive
    at $source, line $lineno".
  *``$lineno``*:
    The line number indicating where in the source this directive
    appears. 
  *``$dtext``*:
    The directive text in a format suitable for parsing by
    `Text::Restructured::Directive::parse_directive`_.  It consists of
    only the arguments, options, and content sections.
  *``$lit``*:
    The complete literal text of the explicit markup containing the
    directive.  Used for generating error messages.

The directive's routine will return any DOM objects representing system
messages.  It will also likely produce side-effects by appending new
DOM objects to the parent object's contents, at least if there were no
errors detected by the directive.

The first thing the directive's routine will usually do is to call
`Text::Restructured::Directive::parse_directive`_ as follows:

.. system:: grep parse_directive .\./.\./blib/lib/Text/Restructured/Directive/if.pm
   :literal:

It is recommended that if the directive encounters any parse errors
(wrong number of arguments, does/does not contain content, etc.), that
it return a ``system_message`` DOM object formatted with
`Text::Restructured::Directive::system_msg`_ to label the message as
having come from the specific directive.

It is also up to the package to provide the documentation that appears
when the user runs ``prest -h``.  Any comment in the perl module within
a ``=begin Description`` .. ``=end Description`` section of a Perl POD
section is printed for the module's help.  For example, here is the
help documentation from the ``if`` directive:

.. system:: perl -ne 'print if /^=pod/ .. /^=cut/' .\./.\./blib/lib/Text/Restructured/Directive/if.pm
   :literal:

.. note::

   The help text should parse correctly as reStructuredText, since it
   is passed through prest to create the web documentation.

Adding New Roles
---------------------

A plug-in role can be added by creating a Perl module with the same
name as the role (with a ".pm" extension, of course).  The Perl module
should have an ``init`` routine which registers the role using the
parser's `Text::Restructured::DefineRole`_ method.  The ``init``
routine is called with the arguments ``($parser, $source, $lineno)``,
where ``$parser`` is the ``Text::Restructured`` object, ``$source`` is
the name of the file containing the directive,, and ``$lineno`` is the
line number within ``$source``.

Adding New Writers
------------------

The output from a writer is generated by traversing the DOM_ tree
recursively.  There can be multiple phases of traversal, and the value
produced by the top-level DOM object in the final phase is what
actually gets written to the output.

Each writer exists in a file that is the writer's name with the
extension ``.wrt``.  A ``.wrt`` file has a special write schema
format specifically designed to make development of writers easy.
Here is a BNF for the _`write schema` file format::

  parser := phase_list
  phase_list := phase_desc | phase_list phase_desc
  phase_desc := phase id eq '{' NL sub_list NL '}' NL
  phase := 'phase' |
  eq := '=' |
  sub_list := sub_desc | sub_list sub_desc
  sub_desc := sub id eq '{' NL perl_code NL '}' NL
  sub := 'sub' |

An ``id`` is any sequence of non-space characters.  ``NL`` is a newline.
``perl_code`` is the perl code for a subroutine.  Note that the words
"phase" and "sub" are optional, as is the equal sign ("=") between the
``id`` and the open brace. 

The id's associated with phases are arbitrary.  The phases are
executed in the order they appear in the file. [#]_ The names of the
subroutines are regular expressions to match the ``tag`` field in the
DOM_ structure.  The first subroutine in the phase whose regular
expression matches the ``tag`` field of the DOM object to be processed
is the one that is called, and is referred to as the handler for that
tag.  The handlers are called doing a post-order traversal of the
tree; in other words, once all of the children (members of the
``content`` field) of a DOM object have had their handler called,
the DOM's own handler is called.  The arguments of the subroutine are:

  ``$dom``:
    A reference to the DOM object being processed.
  ``$str``:
    The concatenation of the strings returned by the handlers of all
    the children of the DOM object being processed.

The subroutine needs to return a string that is the combined result of
processing all the layers from the DOM on down (assisted, of course,
by the ``$str`` argument).  The result returned by the subroutine gets
cached in the ``val`` field of the DOM object for future use, as well
as being propagated as part of the ``$str`` argument of the parent's
handler routine.

Options to the writer can be specified using a ``-W`` define, which has
the format ::

  -W var[=val]

If no value is supplied, then the value defaults to 1.  Any such
defines become available to the writer directly in a variable ``$var``
which should be declared in a ``use vars qw($var)`` statement.

As an example, here is the code for the dom writer:

.. system:: perl -ne 'print if /^phase/ .. 0' .\./.\./blib/lib/Text/Restructured/Writer/dom.wrt
   :literal:

This example is not typical, since it needs to call the internal
`Text::Restructured::Writer::ProcessDOMPhase`_ (via the writer object)
routine in order to process the DOM objects in the internal
``.details`` field of the DOM; most writers should have no need to do
so.

It is also up to the writer to provide the documentation that appears
when the user runs ``prest -h``.  Any comment in the writer appearing
in a POD (Perl's Plain-Old-Documentation) Description section is
printed for the writer's help.  For example, here is the help
documentation from the ``dom`` writer:

.. system:: perl -ne 'print if /^=pod/ .. /^=cut/' .\./.\./blib/lib/Text/Restructured/Writer/dom.wrt
   :literal:

.. note::

   The help text should parse correctly as reStructuredText, since it
   is passed through prest to create the web documentation.

Footnotes
---------

.. [#] If the same phase name is repeated later in the file, its
   subroutine definitions are appended to those of the phase and
   run at the earlier position.

.. include:: prest_internals.xref


..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
