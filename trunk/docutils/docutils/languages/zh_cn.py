# -*- coding: utf-8 -*-
# Author: Pan Junyong
# Contact: panjy@zopechina.com
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

# New language mappings are welcome.  Before doing a new translation, please
# read <http://docutils.sf.net/docs/howto/i18n.html>.  Two files must be
# translated for each language: one in docutils/languages, the other in
# docutils/parsers/rst/languages.

"""
Simplified Chinese language mappings for language-dependent features
of Docutils.
"""

__docformat__ = 'reStructuredText'

labels = {
      # fixed: language-dependent
      'author': '作者',
      'authors': '作者群',
      'organization': '组织',
      'address': '地址',
      'contact': '联系',
      'version': '版本',
      'revision': '修订',
      'status': '状态',
      'date': '日期',
      'copyright': '版权',
      'dedication': '献辞',
      'abstract': '摘要',
      'attention': '注意',
      'caution': '小心',
      'danger': '危险',
      'error': '错误',
      'hint': '提示',
      'important': '重要',
      'note': '注解',
      'tip': '技巧',
      'warning': '警告',
      'contents': '目录',
} 
"""Mapping of node class name to label text."""

bibliographic_fields = {
      # language-dependent: fixed
      '作者': 'author',
      '作者群': 'authors',
      '组织': 'organization',
      '地址': 'address',
      '联系': 'contact',
      '版本': 'version',
      '修订': 'revision',
      '状态': 'status',
      '时间': 'date',
      '版权': 'copyright',
      '献辞': 'dedication',
      '摘要': 'abstract'}
"""Simplified Chinese to canonical name mapping for bibliographic fields."""

author_separators = [';', ',',
                     u'\uff1b', # '；'
                     u'\uff0c', # '，'
                     u'\u3001', # '、'
                    ]
"""List of separator strings for the 'Authors' bibliographic field. Tried in
order."""

# Decode UTF-8 strings.  (We cannot use unicode literals directly for
# Python 2.1 compatibility.)
for mapping in labels, bibliographic_fields:
    for key, value in mapping.items():
        del mapping[key]
        mapping[unicode(key, 'utf8')] = unicode(value, 'utf8')
