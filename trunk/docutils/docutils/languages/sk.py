"""
:Author: Miroslav Va�ko
:Contact: zemiak@zoznam.sk
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

Slovak-language mappings for language-dependent features of Docutils.
"""

__docformat__ = 'reStructuredText'


from docutils import nodes


labels = {
      'author': 'Autor',
      'authors': 'Autori',
      'organization': 'Organiz�cia',
      'address': 'Adresa',
      'contact': 'Kontakt',
      'version': 'Verzia',
      'revision': 'Rev�zia',
      'status': 'Stav',
      'date': 'D�tum',
      'copyright': 'Copyright',
      'dedication': 'Venovanie',
      'abstract': 'Abstraktne',
      'attention': 'Pozor!',
      'caution': 'Opatrne!',
      'danger': '!NEBEZPE�ENSTVO!',
      'error': 'Chyba',
      'hint': 'Rada',
      'important': 'D�le�it�',
      'note': 'Pozn�mka',
      'tip': 'Tip',
      'warning': 'Varovanie',
      'contents': 'Obsah'}
"""Mapping of node class name to label text."""

bibliographic_fields = {
      'author': nodes.author,
      'authors': nodes.authors,
      'organization': nodes.organization,
      'address': nodes.address,
      'contact': nodes.contact,
      'version': nodes.version,
      'revision': nodes.revision,
      'status': nodes.status,
      'date': nodes.date,
      'copyright': nodes.copyright,
      'dedication': nodes.topic,
      'abstract': nodes.topic}
"""Field name (lowcased) to node class name mapping for bibliographic fields
(field_list)."""

author_separators = [';', ',']
"""List of separator strings for the 'Authors' bibliographic field. Tried in
order."""
