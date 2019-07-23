=========================================
 reStructuredText Interpreted Text Roles
=========================================
:Author: David Goodger
:Author: Mark Nodine (for prest-specific implementation)
:Contact: goodger@users.sourceforge.net (mnodine@alum.mit.edu)
:Revision: $Revision: 762 $
:Date: $Date: 2006-01-27 11:47:47 -0600 (Fri, 27 Jan 2006) $
:Copyright: This document has been placed in the public domain.

This document describes the interpreted text roles implemented in the
reference reStructuredText parser.

Interpreted text uses backquotes (`) around the text.  An explicit
role marker may optionally appear before or after the text, delimited
with colons.  For example::

    This is `interpreted text` using the default role.

    This is :title:`interpreted text` using an explicit role.

A default role may be defined by applications of reStructuredText; it
is used if no explicit ``:role:`` prefix or suffix is given.  The
"default default role" is `:title-reference:`_.  It can be changed
using the default-role_ directive.

See the `Interpreted Text`_ section in the `reStructuredText Markup
Specification`_ for syntax details.

.. _"role" directive: directives.html#role
.. _default-role: directives.html#default-role
.. _Interpreted Text: ./reStructuredText.html#interpreted-text
.. _reStructuredText Markup Specification: ./reStructuredText.html


.. contents::


---------------
 Customization
---------------

Custom interpreted text roles may be defined in a document with the
`"role" directive`_.  Customization details are listed with each role.

.. _class:

A ``class`` option is recognized by the "role" directive for most
interpreted text roles.  A description__ is provided in the `"role"
directive`_ documentation.

__ directives.html#role-class


----------------
 Standard Roles
----------------

``:emphasis:``
==============

:Aliases: None
:DTD Element: emphasis
:Customization:
    :Options: class_.
    :Content: None.

Implements emphasis.  These are equivalent::

    *text*
    :emphasis:`text`


``:literal:``
==============

:Aliases: None
:DTD Element: literal
:Customization:
    :Options: class_.
    :Content: None.

Implements inline literal text.  These are equivalent::

    ``text``
    :literal:`text`

Care must be taken with backslash-escapes though.  These are *not*
equivalent::

    ``text \ and \ backslashes``
    :literal:`text \ and \ backslashes`

The backslashes in the first line are preserved (and do nothing),
whereas the backslashes in the second line escape the following
spaces.


``:pep-reference:``
===================

:Aliases: ``:PEP:``
:DTD Element: reference
:Customization:
    :Options: class_.
    :Content: None.

The ``:pep-reference:`` role is used to create an HTTP reference to a
PEP (Python Enhancement Proposal).  The ``:PEP:`` alias is usually
used.  For example::

    See :PEP:`287` for more information about reStructuredText.

This is equivalent to::

    See `PEP 287`__ for more information about reStructuredText.

    __ http://www.python.org/peps/pep-0287.html


``:rfc-reference:``
===================

:Aliases: ``:RFC:``
:DTD Element: reference
:Customization:
    :Options: class_.
    :Content: None.

The ``:rfc-reference:`` role is used to create an HTTP reference to an
RFC (Internet Request for Comments).  The ``:RFC:`` alias is usually
used.  For example::

    See :RFC:`2822` for information about email headers.

This is equivalent to::

    See `RFC 2822`__ for information about email headers.

    __ http://www.faqs.org/rfcs/rfc2822.html


``:strong:``
============

:Aliases: None
:DTD Element: strong
:Customization:
    :Options: class_.
    :Content: None.

Implements strong emphasis.  These are equivalent::

    **text**
    :strong:`text`


``:subscript:``
===============

:Aliases: ``:sub:``
:DTD Element: subscript
:Customization:
    :Options: class_.
    :Content: None.

Implements subscripts.

.. Tip::

   Whitespace or punctuation is required around interpreted text, but
   often not desired with subscripts & superscripts.
   Backslash-escaped whitespace can be used; the whitespace will be
   removed from the processed document::

       H\ :sub:`2`\ O
       E = mc\ :sup:`2`

   In such cases, readability of the plain text can be greatly
   improved with substitutions::

       The chemical formula for pure water is |H2O|.

       .. |H2O| replace:: H\ :sub:`2`\ O

   See `the reStructuredText spec`__ for further information on
   `character-level markup`__ and `the substitution mechanism`__.

   __ ./reStructuredText.html
   __ ./reStructuredText.html#character-level-inline-markup
   __ ./reStructuredText.html#substitution-references


``:superscript:``
=================

:Aliases: ``:sup:``
:DTD Element: superscript
:Customization:
    :Options: class_.
    :Content: None.

Implements superscripts.  See the tip in `:subscript:`_ above.

``:title-reference:``
=====================

:Aliases: ``:title:``, ``:t:``.
:DTD Element: title_reference
:Customization:
    :Options: class_.
    :Content: None.

The ``:title-reference:`` role is used to describe the titles of
books, periodicals, and other materials.  It is the equivalent of the
HTML "cite" element, and it is expected that HTML writers will
typically render "title_reference" elements using "cite".

Since title references are typically rendered with italics, they are
often marked up using ``*emphasis*``, which is misleading and vague. 
The "title_reference" element provides accurate and unambiguous
descriptive markup.

Let's assume ``:title-reference:`` is the default interpreted text
role (see below) for this example::

    `Design Patterns` [GoF95]_ is an excellent read.

The following document fragment (pseudo-XML_) will result from
processing::

    <paragraph>
        <title_reference>
            Design Patterns

        <citation_reference refname="gof95">
            GoF95
         is an excellent read.

``:title-reference:`` is the default interpreted text role in the
standard reStructuredText parser.  This means that no explicit role is
required.  Applications of reStructuredText may designate a different
default role, in which case the explicit ``:title-reference:`` role
must be used to obtain a ``title_reference`` element.


.. _pseudo-XML: ../doctree.html#pseudo-xml


-------------------
 Specialized Roles
-------------------

``raw``
=======

:Aliases: None
:DTD Element: raw
:Customization:
    :Options: class_, format
    :Content: None

.. WARNING::

   The "raw" role is a stop-gap measure allowing the author to bypass
   reStructuredText's markup.  It is a "power-user" feature that
   should not be overused or abused.  The use of "raw" ties documents
   to specific output formats and makes them less portable.

   If you often need to use "raw"-derived interpreted text roles or
   the "raw" directive, that is a sign either of overuse/abuse or that
   functionality may be missing from reStructuredText.  Please
   describe your situation in an email to the Docutils-users_ mailing
   list.

   .. _Docutils-users: ../../user/mailing-lists.html#docutils-user

The "raw" role indicates non-reStructuredText data that is to be
passed untouched to the Writer.  It is the inline equivalent of the
`"raw" directive`_; see its documentation for details on the
semantics.

.. _"raw" directive: directives.html#raw

The "raw" role cannot be used directly.  The `"role" directive`_ must
first be used to build custom roles based on the "raw" role.  One or
more formats (Writer names) must be provided in a "format" option.

For example, the following creates an HTML-specific "raw-html" role::

    .. role:: raw-html(raw)
       :format: html

This role can now be used directly to pass data untouched to the HTML
Writer.  For example::

    If there just *has* to be a line break here,
    :raw-html:`<br />`
    it can be accomplished with a "raw"-derived role.
    But the line block syntax should be considered first.

.. Tip:: Roles based on "raw" should clearly indicate their origin, so
   they are not mistaken for reStructuredText markup.  Using a "raw-"
   prefix for role names is recommended.

In addition to "class_", the following option is recognized:

``format`` : text
    One or more space-separated output format names (Writer names).

``ascii-mathml``
================

:Aliases: ``:mathml:`` ``:mathml-display:`` ``:mathml-inline:``
:DTD Element: mathml
:Customization:
    :Options: class_
    :Content: None

The ``ascii-mathml`` role is used to provide markup for mathematical
notation.  It is currently supported only by the latex writer.  See
the `ascii-mathml`_ document for further details.

.. note:: In order for at least some browsers (e.g. Firefox) to render
   mathml markup, the file must be saved with an extension of ``.xhtml``
   or ``.xml``; the markup is not processed for files with extension
   ``.html`` or ``.htm``.

The ``:mathml-display:`` and ``:mathml-inline:`` roles force the
generated mathml to use inline and display styles, respectively.

``:target:``
============

:Aliases: None
:DTD Element: target
:Customization:
    :Options: class_.
    :Content: None.

The ``:target:`` role creates an inline target that does not get
entered into the symbol table of targets.  It uses the same "text
<target>" syntax that is supported for inline references.  It allows
the same text to be used as the anchor for multiple targets or even to
have invisible targets.  For example, ::

  Here is a :target:`target <abc>` that I can refer to as abc_.
  Here is an :target:`<def>`\ invisible target that I can refer to as def_.

  There is another :target:`target <ghi>` with the same physical text,
  but which I can refer to as ghi_.

``:substitution-reference:``
============================

:Aliases: None
:DTD Element: substitution_reference
:Customization:
    :Options: class_.
    :Content: None.

The ``:substitution-reference:`` role creates a reference to a
substitution definition, with which it is substituted.
entered into the symbol table of targets.  For example, ::

  .. |mydef| replace:: a substitution definition

  Now we can reference `mydef`:substitution-reference: using a
  substitution-reference role.

--------------
Plug-in Roles
--------------

It is possible for plug-ins to define code to do specialized roles.
The following roles are provided by the standard released plug-ins.
For more information on how to write plug-ins to define roles, see
|prest_extend.adding new roles|_.

``perl``
================

:Aliases: None
:DTD Element: varies: text gets re-parsed
:Customization:
    :Options: none
    :Content: None

The ``perl`` role evaluates its text as perl code and returns the
result, which gets re-parsed.  For example::

  Did you know that 12345*54321 is :perl:`12345*54321`?

comes out as

  Did you know that 12345*54321 is :perl:`12345*54321`?

.. include:: prest_extend.xref
