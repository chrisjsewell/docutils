#! /usr/bin/env python
"""
:Author: David Goodger
:Contact: goodger@users.sourceforge.net
:Revision: $Revision$
:Date: $Date$
:Copyright: This module has been placed in the public domain.

Transforms for PEP processing.

- `Headers`: Used to transform a PEP's initial RFC-2822 header.  It remains a
  field list, but some entries get processed.
- `Contents`: Auto-inserts a table of contents.
- `PEPZero`: Special processing for PEP 0.
"""

__docformat__ = 'reStructuredText'

import sys
import os
import re
import time
from docutils import nodes, utils
from docutils import ApplicationError, DataError
from docutils.transforms import Transform, TransformError
from docutils.transforms import parts


class Headers(Transform):

    """
    Process fields in a PEP's initial RFC-2822 header.
    """

    pep_url = 'pep-%04d.html'
    pep_cvs_url = ('http://cvs.sourceforge.net/cgi-bin/viewcvs.cgi/python/'
                   'python/nondist/peps/pep-%04d.txt')
    rcs_keyword_substitutions = (
          (re.compile(r'\$' r'RCSfile: (.+),v \$$', re.IGNORECASE), r'\1'),
          (re.compile(r'\$[a-zA-Z]+: (.+) \$$'), r'\1'),)

    def transform(self):
        if not len(self.document):
            raise DataError('Document tree is empty.')
        header = self.document[0]
        if not isinstance(header, nodes.field_list) or \
              header.get('class') != 'rfc2822':
            raise DataError('Document does not begin with an RFC-2822 '
                            'header; it is not a PEP.')
        pep = title = None
        for field in header:
            if field[0].astext().lower() == 'pep': # should be the first field
                pep = int(field[1].astext())
                break
        if pep is None:
            raise DataError('Document does not contain an RFC-2822 "PEP" '
                            'header.')
        if pep == 0:
            # Special processing for PEP 0.
            pending = nodes.pending(PEPZero, 'last reader', {})
            self.document.insert(1, pending)
            self.document.note_pending(pending)
        for field in header:
            name = field[0].astext().lower()
            body = field[1]
            if len(body) > 1:
                raise DataError('PEP header field body contains multiple '
                                'elements:\n%s' % field.pformat(level=1))
            elif len(body) == 1:
                if not isinstance(body[0], nodes.paragraph):
                    raise DataError('PEP header field body may only contain '
                                    'a single paragraph:\n%s'
                                    % field.pformat(level=1))
            elif name == 'last-modified':
                date = time.strftime(
                      '%d-%b-%Y',
                      time.localtime(os.stat(self.document['source'])[8]))
                body += nodes.paragraph()
                uri = self.pep_cvs_url % int(pep)
                body[0][:] = [nodes.reference('', date, refuri=uri)]
            else:
                # empty
                continue
            para = body[0]
            if name == 'author':
                for node in para:
                    if isinstance(node, nodes.reference):
                        node.parent.replace(node, mask_email(node))
            elif name == 'discussions-to':
                for node in para:
                    if isinstance(node, nodes.reference):
                        node.parent.replace(node, mask_email(node, pep))
            elif name in ('replaces', 'replaced-by', 'requires'):
                newbody = []
                space = nodes.Text(' ')
                for refpep in re.split(',?\s+', body.astext()):
                    pepno = int(refpep)
                    newbody.append(nodes.reference(
                          refpep, refpep, refuri=self.pep_url % pepno))
                    newbody.append(space)
                para[:] = newbody[:-1] # drop trailing space
            elif name == 'last-modified':
                utils.clean_rcs_keywords(para, self.rcs_keyword_substitutions)
                date = para.astext()
                uri = self.pep_cvs_url % int(pep)
                para[:] = [nodes.reference('', date, refuri=uri)]
            elif name == 'content-type':
                pep_type = para.astext()
                uri = self.pep_url % 12
                para[:] = [nodes.reference('', pep_type, refuri=uri)]
            elif name == 'version' and len(body):
                utils.clean_rcs_keywords(para, self.rcs_keyword_substitutions)


class Contents(Transform):

    """
    Insert a table of contents into the document after the RFC 2822 header.
    """


    def transform(self):
        pending = nodes.pending(parts.Contents, 'first writer',
                                {'title': None})
        self.document.insert(1, pending)
        self.document.note_pending(pending)


class PEPZero(Transform):

    """
    Special processing for PEP 0.
    """

    def transform(self):
        visitor = PEPZeroSpecial(self.document)
        self.document.walk(visitor)
        self.startnode.parent.remove(self.startnode)


class PEPZeroSpecial(nodes.SparseNodeVisitor):

    """
    Perform the special processing needed by PEP 0:
    
    - Mask email addresses.

    - Link PEP numbers in the second column of 4-column tables to the PEPs
      themselves.
    """

    pep_url = Headers.pep_url

    def unknown_visit(self, node):
        pass

    def visit_reference(self, node):
        node.parent.replace(node, mask_email(node))

    def visit_field_list(self, node):
        if node.hasattr('class') and node['class'] == 'rfc2822':
            raise nodes.SkipNode

    def visit_tgroup(self, node):
        self.pep_table = node['cols'] == 4
        self.entry = 0

    def visit_colspec(self, node):
        self.entry += 1
        if self.pep_table and self.entry == 2:
            node['class'] = 'num'

    def visit_row(self, node):
        self.entry = 0

    def visit_entry(self, node):
        self.entry += 1
        if self.pep_table and self.entry == 2 and len(node) == 1:
            node['class'] = 'num'
            p = node[0]
            if isinstance(p, nodes.paragraph) and len(p) == 1:
                text = p.astext()
                try:
                    pep = int(text)
                    ref = self.pep_url % pep
                    p[0] = nodes.reference(text, text, refuri=ref)
                except ValueError:
                    pass


non_masked_addresses = ('peps@python.org',
                        'python-list@python.org',
                        'python-dev@python.org')

def mask_email(ref, pepno=None):
    """
    Mask the email address in `ref` and return a replacement node.

    `ref` is returned unchanged if it contains no email address.

    For email addresses such as "user@host", mask the address as "user at
    host" (text) to thwart simple email address harvesters (except for those
    listed in `non_masked_addresses`).  If a PEP number (`pepno`) is given,
    return a reference including a default email subject.
    """
    if ref.hasattr('refuri') and ref['refuri'].startswith('mailto:'):
        if ref['refuri'][8:] in non_masked_addresses:
            replacement = ref[0]
        else:
            replacement_text = ref.astext().replace('@', '&#32;&#97;t&#32;')
            replacement = nodes.raw('', replacement_text, format='html')
        if pepno is None:
            return replacement
        else:
            ref['refuri'] += '?subject=PEP%%20%s' % pepno
            ref[:] = [replacement]
            return ref
    else:
        return ref
