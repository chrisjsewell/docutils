# Authors: Engelbert Gruber; Felix Wiemann
# Contact: grubert@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

# New language mappings are welcome.  Before doing a new translation, please
# read <http://docutils.sf.net/docs/howto/i18n.html>.  Two files must be
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
      'tipp': 'tip',
      'warnung': 'warning',
      'ermahnung': 'admonition',
      'kasten': 'sidebar',
      'seitenkasten': 'sidebar',
      'thema': 'topic',
      'zeilen-block': 'line-block',
      'parsed-literal (translation required)': 'parsed-literal',
      'rubrik': 'rubric',
      'epigraph': 'epigraph',
      'highlights (translation required)': 'highlights',
      'pull-quote (translation required)': 'pull-quote', # kasten too ?
      'compound (translation required)': 'compound',
      #'fragen': 'questions',
      'tabelle': 'table',
      'csv-tabelle': 'csv-table',
      'meta': 'meta',
      #'imagemap': 'imagemap',
      'bild': 'image',
      'abbildung': 'figure',
      u'unver\xe4ndert': 'raw',
      u'einf\xfcgen': 'include',
      'ersetzung': 'replace',
      'ersetzen': 'replace',
      'ersetze': 'replace',
      'unicode': 'unicode',
      'klasse': 'class',
      'rolle': 'role',
      'inhalt': 'contents',
      'kapitel-nummerierung': 'sectnum',
      'abschnitts-nummerierung': 'sectnum',
      u'linkziel-fu\xdfnoten': 'target-notes',
      #u'fu\xdfnoten': 'footnotes',
      #'zitate': 'citations',
      }
"""German name to registered (in directives/__init__.py) directive name
mapping."""

roles = {
      u'abk\xfcrzung': 'abbreviation',
      'akronym': 'acronym',
      'index': 'index',
      'tiefgestellt': 'subscript',
      'hochgestellt': 'superscript',
      'titel-referenz': 'title-reference',
      'pep-referenz': 'pep-reference',
      'rfc-referenz': 'rfc-reference',
      'betonung': 'emphasis',
      'fett': 'strong',
      'literal (translation required)': 'literal',
      'benannte-referenz': 'named-reference',
      'unbenannte-referenz': 'anonymous-reference',
      u'fu\xdfnoten-referenz': 'footnote-reference',
      'zitat-referenz': 'citation-reference',
      'ersetzungs-referenz': 'substitution-reference',
      'ziel': 'target',
      'uri-referenz': 'uri-reference',}
"""Mapping of German role names to canonical role names for interpreted text.
"""
