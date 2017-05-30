#!/usr/bin/env python
# -*- coding: utf-8 -*-
# :Copyright: © 2011, 2017 Günter Milde.
# :License: Released under the terms of the `2-Clause BSD license`_, in short:
#
#    Copying and distribution of this file, with or without modification,
#    are permitted in any medium without royalty provided the copyright
#    notice and this notice are preserved.
#    This file is offered as-is, without any warranty.
#
# .. _2-Clause BSD license: http://www.spdx.org/licenses/BSD-2-Clause

# :Id: $Id$
#
# ::

"""(Re)generate the utils.punctuation_chars module."""

# (re)generate the utils.punctuation_chars module
# ===============================================
#
# The category of some characters can change with the development of the
# Unicode standard. This tool checks the patterns in `utils.punctuation_chars`
# against a re-calculation based on the "unicodedata" stdlib module
# which may give different results for different Python versions.
#
# Updating the module with changed `unicode_punctuation_categories` (due to
# a new Python or Unicode standard version is an API cange (may render valid
# rST documents invalid). It should only be done for "feature releases" and
# requires also updating the specification of `inline markup recognition
# rules`_ in ../../docs/ref/rst/restructuredtext.txt.
#
# .. _inline markup recognition rules:
#     ../../docs/ref/rst/restructuredtext.html#inline-markup


# Setup::

import sys, re
import unicodedata

if sys.version_info >= (3,):
    unichr = chr # unichr not available in Py3k
else:
    import codecs
    sys.stdout = codecs.getwriter('UTF-8')(sys.stdout)


# Template for utils.punctuation_chars
# ------------------------------------
#
# Problem: ``ur`` prefix fails with Py 3.5 ::

module_template = u'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
# :Id: $Id$
# :Copyright: © 2011, 2017 Günter Milde.
# :License: Released under the terms of the `2-Clause BSD license`_, in short:
#
#    Copying and distribution of this file, with or without modification,
#    are permitted in any medium without royalty provided the copyright
#    notice and this notice are preserved.
#    This file is offered as-is, without any warranty.
#
# .. _2-Clause BSD license: http://www.spdx.org/licenses/BSD-2-Clause
#
# This file is generated by
# ``docutils/tools/dev/generate_punctuation_chars.py``.
# ::

import sys, re
import unicodedata

"""Docutils character category patterns.

   Patterns for the implementation of the `inline markup recognition rules`_
   in the reStructuredText parser `docutils.parsers.rst.states.py` based
   on Unicode character categories.
   The patterns are used inside ``[ ]`` in regular expressions.

   Rule (5) requires determination of matching open/close pairs. However, the
   pairing of open/close quotes is ambiguous due to  different typographic
   conventions in different languages. The ``quote_pairs`` function tests
   whether two characters form an open/close pair.

   The patterns are generated by
   ``docutils/tools/dev/generate_punctuation_chars.py`` to  prevent dependence
   on the Python version and avoid the time-consuming generation with every
   Docutils run. See there for motives and implementation details.

   The category of some characters changed with the development of the
   Unicode standard. The current lists are generated with the help of the
   "unicodedata" module of Python %(python_version)s (based on Unicode version %(unidata_version)s).

   .. _inline markup recognition rules:
      http://docutils.sf.net/docs/ref/rst/restructuredtext.html#inline-markup-recognition-rules
"""

%(openers)s
%(closers)s
%(delimiters)s
if sys.maxunicode >= 0x10FFFF: # "wide" build
%(delimiters_wide)s
closing_delimiters = u'\\\\\\\\.,;!?'


# Matching open/close quotes
# --------------------------

quote_pairs = {# open char: matching closing characters # usage example
               u'\\xbb':   u'\\xbb',         # » » Swedish
               u'\\u2018': u'\\u201a',       # ‘ ‚ Albanian/Greek/Turkish
               u'\\u2019': u'\\u2019',       # ’ ’ Swedish
               u'\\u201a': u'\\u2018\\u2019', # ‚ ‘ German ‚ ’ Polish
               u'\\u201c': u'\\u201e',       # “ „ Albanian/Greek/Turkish
               u'\\u201e': u'\\u201c\\u201d', # „ “ German „ ” Polish
               u'\\u201d': u'\\u201d',       # ” ” Swedish
               u'\\u203a': u'\\u203a',       # › › Swedish
              }
"""Additional open/close quote pairs."""

def match_chars(c1, c2):
    """Test whether `c1` and `c2` are a matching open/close character pair.

    Matching open/close pairs are at the same position in
    `punctuation_chars.openers` and `punctuation_chars.closers`.
    The pairing of open/close quotes is ambiguous due to  different
    typographic conventions in different languages,
    so we test for additional matches stored in `quote_pairs`.
    """
    try:
        i = openers.index(c1)
    except ValueError:  # c1 not in openers
        return False
    return c2 == closers[i] or c2 in quote_pairs.get(c1, u'')\
'''


# Generation of the  character category patterns
# ----------------------------------------------
#
# Unicode punctuation character categories
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# For details about Unicode categories, see
# http://www.unicode.org/Public/5.1.0/ucd/UCD.html#General_Category_Values
# ::

unicode_punctuation_categories = {
    # 'Pc': 'Connector', # not used in Docutils inline markup recognition
    'Pd': 'Dash',
    'Ps': 'Open',
    'Pe': 'Close',
    'Pi': 'Initial quote', # may behave like Ps or Pe depending on usage
    'Pf': 'Final quote', # may behave like Ps or Pe depending on usage
    'Po': 'Other'
    }
"""Unicode character categories for punctuation"""


# generate character pattern strings
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# ::

def unicode_charlists(categories, cp_min=0, cp_max=None):
    """Return dictionary of Unicode character lists.

    For each of the `categories`, an item contains a list with all Unicode
    characters with `cp_min` <= code-point <= `cp_max` that belong to
    the category.

    The default values check every code-point supported by Python
    (`sys.maxint` is 0x10FFFF in a "wide" build and 0xFFFF in a "narrow"
    build, i.e. ucs4 and ucs2 respectively).
    """
    # Determine highest code point with one of the given categories
    # (may shorten the search time considerably if there are many
    # categories with not too high characters):
    if cp_max is None:
        cp_max = max(x for x in range(sys.maxunicode+1)
                    if unicodedata.category(unichr(x)) in categories)
        # print(cp_max) # => 74867 for unicode_punctuation_categories
    charlists = {}
    for cat in categories:
        charlists[cat] = [unichr(x) for x in range(cp_min, cp_max+1)
                            if unicodedata.category(unichr(x)) == cat]
    return charlists


# Character categories in Docutils
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# ::

def character_category_patterns():

    """Docutils character category patterns.

    Return list of pattern strings for the categories "Open", "Close",
    "Delimiters" and "Closing-Delimiters" used in the `inline markup
    recognition rules`_.
    """

    cp_min = 160 # ASCII chars have special rules for backwards compatibility
    ucharlists = unicode_charlists(unicode_punctuation_categories, cp_min)
    """Strings of characters in Unicode punctuation character categories"""

    # match opening/closing characters
    # --------------------------------
    # Rearange the lists to ensure matching characters at the same
    # index position.

    # low quotation marks are also used as closers (e.g. in Greek)
    # move them to category Pi:
    ucharlists['Ps'].remove(u'‚') # 201A  SINGLE LOW-9 QUOTATION MARK
    ucharlists['Ps'].remove(u'„') # 201E  DOUBLE LOW-9 QUOTATION MARK
    ucharlists['Pi'] += [u'‚', u'„']

    ucharlists['Pi'].remove(u'‛') # 201B  SINGLE HIGH-REVERSED-9 QUOTATION MARK
    ucharlists['Pi'].remove(u'‟') # 201F  DOUBLE HIGH-REVERSED-9 QUOTATION MARK
    ucharlists['Pf'] += [u'‛', u'‟']

    # 301F  LOW DOUBLE PRIME QUOTATION MARK misses the opening pendant:
    ucharlists['Ps'].insert(ucharlists['Pe'].index(u'\u301f'), u'\u301d')

    # print(u''.join(ucharlists['Ps']).encode('utf8')
    # print(u''.join(ucharlists['Pe']).encode('utf8')
    # print(u''.join(ucharlists['Pi']).encode('utf8')
    # print(u''.join(ucharlists['Pf']).encode('utf8')

    # The Docutils character categories
    # ---------------------------------
    #
    # The categorization of ASCII chars is non-standard to reduce
    # both false positives and need for escaping. (see `inline markup
    # recognition rules`_)

    # allowed before markup if there is a matching closer
    openers = [u'"\'(<\\[{']
    for category in ('Ps', 'Pi', 'Pf'):
        openers.extend(ucharlists[category])

    # allowed after markup if there is a matching opener
    closers = [u'"\')>\\]}']
    for category in ('Pe', 'Pf', 'Pi'):
        closers.extend(ucharlists[category])

    # non-matching, allowed on both sides
    delimiters = [u'\\-/:']
    for category in ('Pd', 'Po'):
        delimiters.extend(ucharlists[category])

    # non-matching, after markup
    closing_delimiters = [r'\\.,;!?']

    return [u''.join(chars) for chars in (openers, closers, delimiters,
                                            closing_delimiters)]

def separate_wide_chars(s):
    """Return (s1,s2) with characters above 0xFFFF in s2"""
    maxunicode_narrow = 0xFFFF
    l1 = [ch for ch in s if ord(ch) <= maxunicode_narrow]
    l2 = [ch for ch in s if ord(ch) > maxunicode_narrow]
    return ''.join(l1), ''.join(l2)

def mark_intervals(s):
    """Return s with shortcut notation for runs of consecutive characters

    Sort string and replace 'cdef' by 'c-f' and similar.
    """
    l =[]
    s = [ord(ch) for ch in s]
    s.sort()
    for n in s:
        try:
            if l[-1][-1]+1 == n:
                l[-1].append(n)
            else:
                l.append([n])
        except IndexError:
            l.append([n])

    l2 = []
    for i in l:
        i = [unichr(n) for n in i]
        if len(i) > 2:
            i = i[0], u'-', i[-1]
        l2.extend(i)

    return ''.join(l2)

def wrap_string(s, startstring= "(u'",
                    endstring = "')", wrap=67):
    """Line-wrap a unicode string literal definition."""
    c = len(startstring)
    contstring = "'\n" + ' ' * (len(startstring)-2) + "u'"
    l = [startstring]
    for ch in s.replace("'", r"\'"):
        c += 1
        if ch == '\\' and c > wrap:
            c = len(startstring)
            ch = contstring + ch
        l.append(ch)
    l.append(endstring)
    return ''.join(l)


def print_differences(old, new, name):
    """List characters missing in old/new."""
    if old != new:
        print('new %s:' % name)
        for c in new:
            if c not in old:
                print('  %04x'%ord(c), unicodedata.name(c))
        print('removed %s:' % name)
        for c in old:
            if c not in new:
                print('  %04x'%ord(c), unicodedata.name(c))
    else:
        print('%s unchanged' % name)

def print_quote_pairs():
    pairs = [(o,c) for o,c in quote_pairs.items()]
    for o,c in sorted(pairs):
        print((u'%s %s' % (o,c)).encode('utf8'))

    # # Test open/close matching:
    # for i in range(min(len(openers),len(closers))):
    #     print('%4d    %s    %s' % (i, openers[i].encode('utf8'),
    #                                closers[i].encode('utf8'))


# Output
# ------
#
# ::

if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-t', '--test', action="store_true",
                        help='test for changed character categories')
    args = parser.parse_args()

# (Re)create character patterns
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# ::

    (o, c, d, cd) = character_category_patterns()

# Characters in the upper plane require a "wide" build::

    o, o_wide = separate_wide_chars(o)
    c, c_wide = separate_wide_chars(c)
    d, d_wide = separate_wide_chars(d)

# delimiters: sort and use shortcut for intervals (saves ~150 characters)
# (`openers` and `closers` must be verbose and keep order
# because they are also used in `match_chars()`)::

    d = d[:5] + mark_intervals(d[5:])
    d_wide = mark_intervals(d_wide)


# Test: compare module content with re-generated definitions
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ::

    if args.test:

# Import the punctuation_chars module from the source
# or Py3k build path for local Python modules::

        if sys.version_info < (3,):
            sys.path.insert(0, '../../docutils')
        else:
            sys.path.insert(0, '../../build/lib')

        from docutils.utils.punctuation_chars import (openers, closers,
                                          delimiters, closing_delimiters)

        print('Check for differences between the current `punctuation_chars`'
              ' module\n and a regeneration based on Unicode version %s:'
              % unicodedata.unidata_version)

        print_differences(openers, o, 'openers')
        if o_wide:
            print('+ openers-wide = ur"""%s"""' % o_wide.encode('utf8'))
        print_differences(closers, c, 'closers')
        if c_wide:
            print('+ closers-wide = ur"""%s"""' % c_wide.encode('utf8'))

        print_differences(delimiters, d + d_wide, 'delimiters')
        print_differences(closing_delimiters, cd, 'closing_delimiters')

        sys.exit()

# Print re-generation of the punctuation_chars module
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# The output can be copied to docutils/utils if an update is wanted
# (API change, see Intro).

# Replacements::

    substitutions = {
        'python_version': '.'.join(str(s) for s in sys.version_info[:3]),
        'unidata_version': unicodedata.unidata_version,
        'openers': wrap_string(o.encode('unicode-escape').decode(),
                               startstring="openers = (u'"),
        'closers': wrap_string(c.encode('unicode-escape').decode(),
                               startstring="closers = (u'"),
        'delimiters': wrap_string(d.encode('unicode-escape').decode(),
                                  startstring="delimiters = (u'"),
        'delimiters_wide': wrap_string(
                            d_wide.encode('unicode-escape').decode(),
                            startstring="    delimiters += (u'")
        }

    print(module_template % substitutions)


# test prints
# ~~~~~~~~~~~
#
# For interactive use in development you may uncomment the following
# definitions::

    # print "wide" Unicode characters:
    # ucharlists = unicode_charlists(unicode_punctuation_categories)
    # for key in ucharlists:
    #     if key.endswith('wide'):
    #         print key, ucharlists[key]

    # print 'openers = ', repr(openers)
    # print 'closers = ', repr(closers)
    # print 'delimiters = ', repr(delimiters)
    # print 'closing_delimiters = ', repr(closing_delimiters)

    # ucharlists = unicode_charlists(unicode_punctuation_categories)
    # for cat, chars in ucharlists.items():
    #     # print cat, chars
    #     # compact output (visible with a comprehensive font):
    #     print (u":%s: %s" % (cat, u''.join(chars))).encode('utf8')

# verbose print
#
# ::

    # print 'openers:'
    # for ch in openers:
    #     print ch.encode('utf8'), unicodedata.name(ch)
    # print 'closers:'
    # for ch in closers:
    #     print ch.encode('utf8'), unicodedata.name(ch)
    # print 'delimiters:'
    # for ch in delimiters:
    #     print ch.encode('utf8'), unicodedata.name(ch)
    # print 'closing_delimiters:'
    # for ch in closing_delimiters:
    #     print ch.encode('utf8'), unicodedata.name(ch)
