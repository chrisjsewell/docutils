# $Id$
# Author: Stefan Rank <strank@strank.info>
# Copyright: This module has been placed in the public domain.

"""
Document tree Writer, reproducing the original rst source.
Needs extensions in the parser to losslessly preserve all information.
"""

__docformat__ = 'reStructuredText'

import pprint

from docutils import writers, nodes


class Writer(writers.Writer):

    supported = ('restructuredtext', 'rst', 'rest', 'restx', 'rtxt', 'rstx')
    """Formats this writer supports."""

    config_section = 'rst writer'
    config_section_dependencies = ('writers',)

    output = None
    """Final translated form of `document`."""

    def __init__(self):
        writers.Writer.__init__(self)
        self.translator_class = RSTTranslator

    def translate(self):
        self.visitor = visitor = self.translator_class(self.document)
        self.document.walkabout(visitor)
        self.output = visitor.astext()
        if hasattr(self.document.settings, '_debug_rst_writer'):
            debugvisitor = self.translator_class(self.document)
            debugvisitor.debug = True
            self.document.walkabout(debugvisitor)
            self.output += debugvisitor.astext()
            #self.output += self.document.pformat().encode('raw_unicode_escape')

    def supports(self, format):
        """This writer supports all format-specific elements."""
        return 1


def getnodestring(node):
    '''Return a debug string with info about this node.'''
    extra = u''
    if hasattr(node, 'attributes'):
        atts = node.attributes
        atts = dict((key, val) for (key, val) in atts.items() if val)
        extra += u'\n  attributes: %r' % atts
    if hasattr(node, 'data'):
        if node.data == node.rawsource:
            extra += u'\n  data: == rawsource'
        else:
            extra += u'\n  data: %r' % node.data
    extra += u'\n  rawsource: %r' % node.rawsource
    return u'\n%s%s\n' % (str(node.__class__), extra)


sectionadornments = [u'=', u'-', u'~', u"'", ]


class RSTTranslator(nodes.GenericNodeVisitor):
    """
    This RST writer reconstructs the input source
    """

    def __init__(self, document):
        nodes.NodeVisitor.__init__(self, document)
        self.debug = False
        #self.debug = True
        self.body = []
        self.context = ContextStack(defaults={
                'bullet': u'',
                'indent': u'',
                'sectionadornment': u'',
                })

    def dispatch_visit(self, node):
        """Calls superclass but first print generic node info,
        if self.debug is set.
        """
        if self.debug:
            self.body.append(getnodestring(node))
        nodes.GenericNodeVisitor.dispatch_visit(self, node)

    def astext(self):
        return u''.join(self.body)

    def default_visit(self, node):
        """Override for generic, uniform traversals."""
        if not self.debug:
            self.body.append(getnodestring(node))

    def default_departure(self, node):
        """Override for generic, uniform traversals."""
        self.body.append(u'\ndepart %s' % str(node.__class__))

    def passvisit(self, node):
        """No-op, can be assigned to empty visit_ or depart_ methods."""
        pass

    def classdirective(self, classes):
        """Call with the first element that has a class assigned."""
        self.body.append(self.context.indent
                + u'.. class:: %s\n\n' % u', '.join(classes))

    def indentstring(self, thestring):
        return thestring.replace(u'\n', u'\n' + self.context.indent)

    # meta is a non-standard node type that's no covered by default_visit
    def visit_meta(self, node):
        """Meta node added by meta directive."""
        self.body.append('\n%s\n%s' % (node.__class__, node.rawsource))

    depart_meta = passvisit

    ### Below are further visit and depart methods, should be sorted

    def visit_bullet_list(self, node):
        #self.default_visit(node)
        classes = node.attributes['classes']
        if classes:
            self.classdirective(classes)
        self.context.bullet = node.attributes['bullet']

    def depart_bullet_list(self, node):
        del self.context.bullet

    visit_document = passvisit
    depart_document = passvisit

    visit_docinfo = passvisit
    depart_docinfo = passvisit

    def visit_field(self, node):
        pass

    def depart_field(self, node):
        self.body.append(u'\n')

    def visit_field_body(self, node):
        self.body.append(self.indentstring(node.rawsource))
        raise nodes.SkipChildren

    def depart_field_body(self, node):
        del self.context.indent # which was setattr by field_name

    def visit_field_list(self, node):
        pass

    def depart_field_list(self, node):
        pass

    def visit_field_name(self, node):
        source = u':%s: ' % node.rawsource
        self.body.append(source)
        # indent for field body
        self.context.indent = self.context.indent + u' ' * len(source)
        raise nodes.SkipChildren

    depart_field_name = passvisit

    def visit_footnote(self, node):
        if node.attributes['auto']:
            self.body.append(u'.. [#] ')
            self.context.indent = self.context.indent + u'   '
            self.context.parentrawsource = node.rawsource
            self.rawsourceindex = 0
            return
        self.default_visit(node) #TODO

    def depart_footnote(self, node):
        self.body.append(u'\n')

    def visit_label(self, node):
        raise nodes.SkipChildren # TODO: this might only apply to auto labels?

    depart_label = passvisit

    def visit_list_item(self, node):
        self.body.append(u'%s ' % self.context.bullet)
        self.context.indent = self.context.indent + u'  '
        self.context.parentrawsource = node.rawsource
        self.rawsourceindex = 0

    def depart_list_item(self, node):
        self.body.append(u'%s\n' %
                self.context.parentrawsource[self.rawsourceindex:])
        del self.rawsourceindex
        del self.context.parentrawsource
        del self.context.indent

    def visit_paragraph(self, node):
        source = node.rawsource
        try:
            parentsource = self.context.parentrawsource
            #print '\n%r\n%r\n%r\n' % (parentsource, source, self.rawsourceindex)
            newindex = parentsource.index(source, self.rawsourceindex)
            endsourceindex = newindex + len(source)
            source = parentsource[self.rawsourceindex:endsourceindex]
            self.rawsourceindex = endsourceindex
        except AttributeError:
            pass
        self.body.append(self.indentstring(source) + '\n')
        raise nodes.SkipChildren

    depart_paragraph = passvisit

    def visit_section(self, node):
        newindex = 0
        seca = self.context.sectionadornment
        if seca:
            newindex = sectionadornments.index(seca) + 1
        self.context.sectionadornment = sectionadornments[newindex]

    def depart_section(self, node):
        del self.context.sectionadornment

    def visit_target(self, node):
        self.body.append(u'\n\n%s\n\n' % node.rawsource)

    depart_target = passvisit

    def visit_title(self, node):
        self.body.append(u'\n\n%s\n%s\n\n' % (node.rawsource,
                self.context.sectionadornment * len(node.rawsource)))
        raise nodes.SkipChildren

    depart_title = passvisit

    def visit_transition(self, node):
        self.body.append(u'%s\n\n' %node.rawsource)

    depart_transition = passvisit


class ContextStack(object):
    """A stack of states. Setting an attribute overwrites the last
    value, but deleting the value reactivates the old one.
    Default values can be set on construction.
    
    This is used for important states during output of rst,
    e.g. indent level, last bullet type.
    """
    
    def __init__(self, defaults=None):
        '''Initialise _defaults and _stack, but avoid calling __setattr__'''
        if defaults is None:
            object.__setattr__(self, '_defaults', {})
        else:
            object.__setattr__(self, '_defaults', dict(defaults))
        object.__setattr__(self, '_stack', {})

    def __getattr__(self, name):
        '''Return last value of name in stack, or default.'''
        if name in self._stack:
            return self._stack[name][-1]
        if name in self._defaults:
            return self._defaults[name]
        raise AttributeError

    def __setattr__(self, name, value):
        '''Pushes a new value for name onto the stack.'''
        if name in self._stack:
            self._stack[name].append(value)
        else:
            self._stack[name] = [value]

    def __delattr__(self, name):
        '''Remove a value of name from the stack.'''
        if name not in self._stack:
            raise AttributeError
        del self._stack[name][-1]
        if not self._stack[name]:
            del self._stack[name]
