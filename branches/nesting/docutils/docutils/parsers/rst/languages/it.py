# Author: Nicola Larosa, Lele Gaifax
# Contact: docutils@tekNico.net, lele@seldati.it
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Italian-language mappings for language-dependent features of
reStructuredText.
"""

__docformat__ = 'reStructuredText'


directives = {
      'attenzione': 'attention',
      'cautela': 'caution',
      'pericolo': 'danger',
      'errore': 'error',
      'suggerimento': 'hint',
      'importante': 'important',
      'nota': 'note',
      'consiglio': 'tip',
      'avvertenza': 'warning',
      'ammonizione': 'admonition',
      'riquadro': 'sidebar',
      'argomento': 'topic',
      'blocco-di-righe': 'line-block',
      'blocco-interpretato': 'parsed-literal',
      'rubrica': 'rubric',
      'epigrafe': 'epigraph',
      'highlights (translation required)': 'highlights',
      'pull-quote (translation required)': 'pull-quote',
      u'table (translation required)': 'table',
      #'questions': 'questions',
      #'qa': 'questions',
      #'faq': 'questions',
      'meta': 'meta',
      #'imagemap': 'imagemap',
      'immagine': 'image',
      'figura': 'figure',
      'includi': 'include',
      'grezzo': 'raw',
      'sostituisci': 'replace',
      'unicode': 'unicode',
      'classe': 'class',
      'indice': 'contents',
      'seznum': 'sectnum',
      'sezioni-autonumerate': 'sectnum',
      'annota-riferimenti-esterni': 'target-notes',
      #'footnotes': 'footnotes',
      #'citations': 'citations',
      'restructuredtext-test-directive': 'restructuredtext-test-directive'}
"""Italian name to registered (in directives/__init__.py) directive name
mapping."""

roles = {
      'abbreviazione': 'abbreviation',
      'acronimo': 'acronym',
      'indice': 'index',
      'deponente': 'subscript',
      'esponente': 'superscript',
      'riferimento-titolo': 'title-reference',
      'riferimento-pep': 'pep-reference',
      'riferimento-rfc': 'rfc-reference',
      'enfasi': 'emphasis',
      'forte': 'strong',
      'letterale': 'literal',
      'riferimento-con-nome': 'named-reference',
      'riferimento-anonimo': 'anonymous-reference',
      'riferimento-nota': 'footnote-reference',
      'riferimento-citazione': 'citation-reference',
      'riferimento-sostituzione': 'substitution-reference',
      'destinazione': 'target',
      'riferimento-uri': 'uri-reference',}
"""Mapping of Italian role names to canonical role names for interpreted text.
"""
