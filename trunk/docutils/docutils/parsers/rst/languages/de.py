# -*- coding: iso-8859-1 -*-
# Author: Engelbert Gruber
# Contact: grubert@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

# New language mappings are welcome.  Before doing a new translation, please
# read <http://docutils.sf.net/spec/howto/i18n.html>.  Two files must be
# translated for each language: one in docutils/languages, the other in
# docutils/parsers/rst/languages.

"""
German-language mappings for language-dependent features of
reStructuredText.
"""

__docformat__ = 'reStructuredText'


directives = {
      'achtung': 'attention',
      'vorsicht': 'caution',
      'gefahr': 'danger',
      'fehler': 'error',
      'hinweis': 'hint',
      'wichtig': 'important',
      'notiz': 'note',
      'tip': 'tip',
      'warnung': 'warning',
      'ermahnung': 'admonition',
      'kasten': 'sidebar', # seitenkasten ?
      'thema': 'topic', 
      'line-block': 'line-block',
      'parsed-literal': 'parsed-literal',
      'rubrik': 'rubric',
      'epigraph (translation required)': 'epigraph',
      'highlights (translation required)': 'highlights',
      'pull-quote (translation required)': 'pull-quote', # kasten too ?
      #'questions': 'questions',
      #'qa': 'questions',
      #'faq': 'questions',
      'meta': 'meta',
      #'imagemap': 'imagemap',
      'bild': 'image',
      'abbildung': 'figure',
      'raw': 'raw',         # unbearbeitet
      'include': 'include', # einf�gen, "f�ge ein" would be more like a command.
                            # einf�gung would be the noun. 
      'ersetzung': 'replace', # ersetzen, ersetze
      'unicode': 'unicode',
      'klasse': 'class',    # offer class too ?
      'inhalt': 'contents',
      'sectnum': 'sectnum',
      'section-numbering': 'sectnum',
      'target-notes': 'target-notes',
      #'footnotes': 'footnotes',
      #'citations': 'citations',
      'restructuredtext-test-directive': 'restructuredtext-test-directive'}
"""English name to registered (in directives/__init__.py) directive name
mapping."""
