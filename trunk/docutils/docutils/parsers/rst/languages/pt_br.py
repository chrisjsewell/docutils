# -*- coding: iso-8859-1 -*-
# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

# New language mappings are welcome.  Before doing a new translation, please
# read <http://docutils.sf.net/docs/howto/i18n.html>.  Two files must be
# translated for each language: one in docutils/languages, the other in
# docutils/parsers/rst/languages.

"""
Brazilian Portuguese-language mappings for language-dependent features of
reStructuredText.
"""

__docformat__ = 'reStructuredText'


directives = {
      # language-dependent: fixed
      u'aten��o': 'attention',
      'cuidado': 'caution',
      'perigo': 'danger',
      'erro': 'error',
      u'sugest�o': 'hint',
      'importante': 'important',
      'nota': 'note',
      'dica': 'tip',
      'aviso': 'warning',
      u'exorta��o': 'admonition',
      'barra-lateral': 'sidebar',
      u't�pico': 'topic',
      'bloco-de-linhas': 'line-block',
      'literal-interpretado': 'parsed-literal',
      'rubrica': 'rubric',
      u'ep�grafo': 'epigraph',
      'destaques': 'highlights',
      u'cita��o-destacada': 'pull-quote',
      u'table (translation required)': 'table',
      #'perguntas': 'questions',
      #'qa': 'questions',
      #'faq': 'questions',
      'meta': 'meta',
      #'imagemap': 'imagemap',
      'imagem': 'image',
      'figura': 'figure',
      u'inclus�o': 'include',
      'cru': 'raw',
      u'substitui��o': 'replace',
      'unicode': 'unicode',
      'classe': 'class',
      'role (translation required)': 'role',
      u'�ndice': 'contents',
      'numsec': 'sectnum',
      u'numera��o-de-se��es': 'sectnum',
      #u'notas-de-rorap�': 'footnotes',
      #u'cita��es': 'citations',
      u'links-no-rodap�': 'target-notes',
      'restructuredtext-test-directive': 'restructuredtext-test-directive'}
"""English name to registered (in directives/__init__.py) directive name
mapping."""

roles = {
    # language-dependent: fixed
    u'abbrevia��o': 'abbreviation',
    'ab': 'abbreviation',
    u'acr�nimo': 'acronym',
    'ac': 'acronym',
    u'�ndice-remissivo': 'index',
    'i': 'index',
    'subscrito': 'subscript',
    'sub': 'subscript',
    'sobrescrito': 'superscript',
    'sob': 'superscript',
    u'refer�ncia-a-t�tulo': 'title-reference',
    u't�tulo': 'title-reference',
    't': 'title-reference',
    u'refer�ncia-a-pep': 'pep-reference',
    'pep': 'pep-reference',
    u'refer�ncia-a-rfc': 'rfc-reference',
    'rfc': 'rfc-reference',
    u'�nfase': 'emphasis',
    'forte': 'strong',
    'literal': 'literal',
    u'refer�ncia-por-nome': 'named-reference',
    u'refer�ncia-an�nima': 'anonymous-reference',
    u'refer�ncia-a-nota-de-rodap�': 'footnote-reference',
    u'refer�ncia-a-cita��o': 'citation-reference',
    u'refer�ncia-a-substitui��o': 'substitution-reference',
    'alvo': 'target',
    u'refer�ncia-a-uri': 'uri-reference',
    'uri': 'uri-reference',
    'url': 'uri-reference',}
"""Mapping of English role names to canonical role names for interpreted text.
"""
