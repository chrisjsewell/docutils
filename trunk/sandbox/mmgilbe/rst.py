# -*- coding: iso-8859-1 -*-
"""
    MoinMoin - ReStructured Text Parser

    @copyright: 2004 by Matthew Gilbert <gilbert AT voxmea DOT net>
        and by Alexander Schremmer <alex AT alexanderweb DOT de>
    @license: GNU GPL, see COPYING for details.
    
    REQUIRES docutils 0.3.3 or later
"""

#############################################################################
### ReStructured Text Parser
#############################################################################

import re
import new
import StringIO
import __builtin__
import sys
import copy

# docutils imports are below
import MoinMoin.parser.wiki
from MoinMoin.Page import Page

Dependencies = [] # this parser just depends on the raw text

# --- make docutils safe by overriding all module-scoped names related to IO ---

# TODO: Add an error message to dummyOpen so that the user knows what they did
# requested an unsupported feature of docutils in MoinMoin.
def dummyOpen(x, y=None, z=None): return

class dummyIO(StringIO.StringIO):
    def __init__(self, destination=None, destination_path=None,
                 encoding=None, error_handler='', autoclose=1,
                 handle_io_errors=1, source_path=None):
        StringIO.StringIO.__init__(self)
        pass

class dummyUrllib2:
    def urlopen(a):
        return StringIO.StringIO()
    urlopen = staticmethod(urlopen)

# # # All docutils imports must be contained below here
import docutils
from docutils.core import publish_parts
from docutils.writers import html4css1
from docutils.nodes import fully_normalize_name, reference
from docutils.parsers import rst
from docutils.parsers.rst import directives, roles
# # # All docutils imports must be contained above here

def safe_import(name, globals = None, locals = None, fromlist = None):
    mod = __builtin__.__import__(name, globals, locals, fromlist)
    if mod:
        mod.open = dummyOpen
        mod.urllib2 = dummyUrllib2
    return mod

# Go through and change all docutils modules to use a dummyOpen and dummyUrllib2
# module. Also make sure that any docutils imported modules also get the dummy
# implementations.
for i in sys.modules.keys():
    if i.startswith('docutils') and sys.modules[i]:
        sys.modules[i].open = dummyOpen
        sys.modules[i].urllib2 = dummyUrllib2
        sys.modules[i].__import__ = safe_import

docutils.io.FileInput = dummyIO
docutils.io.FileOutput = dummyIO

# --- End of dummy-code --------------------------------------------------------

def html_escape_unicode(node):
    # Find Python function that does this for me. string.encode('ascii',
    # 'xmlcharrefreplace') only 2.3 and above.
    for i in node:
        if ord(i) > 127:
            node = node.replace(i, '&#%d;' % (ord(i)))
    return node

class MoinWriter(html4css1.Writer):
    
    config_section = 'MoinMoin writer'
    config_section_dependencies = ('writers',)

    #"""Final translated form of `document`."""
    output = None
    
    def wiki_resolver(self, node):
        """
            Normally an unknown reference would be an error in an reST document.
            However, this is how new documents are created in the wiki. This
            passes on unknown references to eventually be handled by the
            MoinMoin formatter.
        """
        # TODO: Need to better document the attributes here.
        if getattr(node, 'indirect_reference_name', None):
            node['refuri'] = node.indirect_reference_name
            return 1
        elif 'id' in node.attributes:
            # I'm pretty sure the first test should catch any targets or
            # references with the "id" attribute. Therefore, if we get to here
            # its probably an internal link that didn't work so we let it go
            # through as an error.
            return 0
        node['refuri'] = node['refname']
        del node['refname']
        self.nodes.append(node)
        return 1
    
    wiki_resolver.priority = 001
    
    def __init__(self, formatter, request):
        html4css1.Writer.__init__(self)
        self.formatter = formatter
        self.request = request
        # Add our wiki unknown_reference_resolver to our list of functions to
        # run when a target isn't found
        self.unknown_reference_resolvers = [self.wiki_resolver]
        # We create a new parser to process MoinMoin wiki style links in the 
        # reST.
        self.wikiparser = MoinMoin.parser.wiki.Parser('', self.request)
        self.wikiparser.formatter = self.formatter
        self.wikiparser.hilite_re = None
        self.nodes = []
        
        
    def translate(self):
        visitor = MoinTranslator(self.document, 
                                 self.formatter, 
                                 self.request,
                                 self.wikiparser,
                                 self)
        self.document.walkabout(visitor)
        self.visitor = visitor
        self.output = html_escape_unicode(visitor.astext())
        

class Parser:
    
    # allow caching - This should be turned off when testing.
    caching = 1
    
    def __init__(self, raw, request, **kw):
        self.raw = raw
        self.request = request
        self.form = request.form
        
    def format(self, formatter):
        # Create our simple parser
        parser = MoinDirectives(self.request)
        
        parts =  publish_parts(source = self.raw,
                               writer = MoinWriter(formatter, self.request))
        
        text = ''
        if parts['title']:
            text += '<h2>' + parts['title'] + '</h2>'
        # If there is only one subtitle then it is held in parts['subtitle'].
        # However, if there is more than one subtitle then this is empty and
        # fragment contains all of the subtitles.
        if parts['subtitle']:
            text += '<h3>' + parts['subtitle'] + '</h3>'
        if parts['docinfo']:
            text += parts['docinfo']
        text += parts['fragment']
        self.request.write(html_escape_unicode(text))
        

class MoinTranslator(html4css1.HTMLTranslator):

    def __init__(self, document, formatter, request, parser, writer):
        html4css1.HTMLTranslator.__init__(self, document)
        self.formatter = formatter
        self.request = request
        # MMG: Using our own writer when needed. Save the old one to restore
        # after the page has been processed by the html4css1 parser.
        self.original_write, self.request.write = self.request.write, self.capture_wiki_formatting
        self.wikiparser = parser
        self.wikiparser.request = request
        # MoinMoin likes to start the initial headers at level 3 and the title
        # gets level 2, so to comply with their styles, we do here also. 
        # TODO: Could this be fixed by passing this value in settings_overrides?
        self.initial_header_level = 3
        # Temporary place for wiki returned markup. This will be filled when
        # replacing the default writer with the capture_wiki_formatting
        # function (see visit_image for an example). 
        self.wiki_text = ''
        self.setup_wiki_handlers()

    def capture_wiki_formatting(self, text):
        """
            Captures MoinMoin generated markup to the instance variable
            wiki_text.
        """
        # For some reason getting empty strings here which of course overwrites 
        # what we really want (this is called multiple times per MoinMoin 
        # format call, which I don't understand).
        self.wiki_text += text
            
    def process_wiki_text(self, text):
        """
            This sequence is repeated numerous times, so its captured as a
            single call here. Its important that wiki_text is blanked before we
            make the format call. format will call request.write which we've
            hooked to capture_wiki_formatting. If wiki_text is not blanked
            before a call to request.write we will get the old markup as well as
            the newly generated markup. 
            
            TODO: Could implement this as a list so that it acts as a stack. I
            don't like having to remember to blank wiki_text.
        """
        self.wiki_text = ''
        self.wikiparser.raw = text
        self.wikiparser.format(self.formatter)

    def add_wiki_markup(self):
        """
            Place holder in case this becomes more elaborate someday. For now it
            only appends the MoinMoin generated markup to the html body and
            raises SkipNode.
        """
        self.body.append(self.wiki_text)
        self.wiki_text = ''
        raise docutils.nodes.SkipNode
        
    def astext(self):
        self.request.write = self.original_write
        return html4css1.HTMLTranslator.astext(self)
        
    def process_inline(self, node, uri_string):
        """
            Process the "inline:" link scheme. This can either ome from
            visit_reference or from visit_image. The uri_string changes
            depending on the caller. The uri is passed to MoinMoin to handle the
            inline link. If it is an image, the src line is extracted and passed
            to the html4css1 writer to allow the reST image attributes.
            Otherwise, the html from MoinMoin is inserted into the reST document
            and SkipNode is raised.
        """
        self.process_wiki_text(node[uri_string])
        # Only pass the src and alt parts to the writer. The reST writer 
        # inserts its own tags so we don't need the MoinMoin html markup.
        src = re.search('src="([^"]+)"', self.wiki_text)
        if src:
            node['uri'] = src.groups()[0]
            if not 'alt' in node.attributes:
                alt = re.search('alt="([^"]*)"', self.wiki_text)
                if alt:
                    node['alt'] = alt.groups()[0]
        else:
            # Image doesn't exist yet for the page so just use what's
            # returned from MoinMoin verbatim
            self.add_wiki_markup()
            
    def process_wiki_target(self, target):
        self.process_wiki_text(target)
        # MMG: May need a call to fixup_wiki_formatting here but I 
        # don't think so.
        self.add_wiki_markup()
        
    def fixup_wiki_formatting(self, text):
        replacement = {'<p>': '', '</p>': '', '\n': '', '> ': '>'}
        for src, dst in replacement.items():
            text = text.replace(src, dst)
        # Everything seems to have a space ending the text block. We want to
        # get rid of this
        if text and text[-1] == ' ':
            text = text[:-1]
        return text

    def visit_reference(self, node):
        """
            Pass links to MoinMoin to get the correct wiki space url. Extract
            the url and pass it on to the html4css1 writer to handle. Inline
            images are also handled by visit_image. Not sure what the "drawing:"
            link scheme is used for, so for now it is handled here.
            
            Also included here is a hack to allow MoinMoin macros. This routine
            checks for a link which starts with "[[". This link is passed to the
            MoinMoin formatter and the resulting markup is inserted into the
            document in the place of the original link reference. 
        """
        moin_link_schemes = ['wiki:', 'attachment:', 'drawing:', '[[',
                             'inline:']
                             
        if 'refuri' in node.attributes:
            target = None
            refuri = node['refuri']
            
            # MMG: Fix this line
            if [scheme for scheme in moin_link_schemes if 
                    refuri.lstrip().startswith(scheme)]:
                # For a macro, We want the actuall text from the user in target, 
                # not the fully normalized version that is contained in refuri.
                if refuri.startswith('[['):
                    target = node['name']
                else:
                    target = refuri
            # TODO: Figure out the following two elif's and comment
            # appropriately.
            # The node should have a whitespace normalized name if the docutlis 
            # reStructuredText parser would normally fully normalize the name.
            elif ('name' in node.attributes and 
                  fully_normalize_name(node['name']) == refuri):
                target = ':%s:' % (node['name'])
            # If its not a uri containing a ':' then its probably destined for
            # wiki space.
            elif ':' not in refuri:
                target = ':%s:' % (refuri)
            
            if target:
                if target.startswith('inline:'):
                    self.process_inline(node, 'refuri')
                elif target.startswith('[[') and target.endswith(']]'):
                    self.process_wiki_target(target)
                else:
                    # Not a macro or inline so hopefully its a link. Put the target in 
                    # brackets so that MoinMoin knows its a link. Extract the
                    # href, if it exists, and let docutils handle it from there.
                    # If there is no href just add whatever MoinMoin returned.
                    node_text = node.astext().replace('\n', ' ')
                    self.process_wiki_text('[%s %s]' % (target, node_text))
                    href = re.search('href="([^"]+)"', self.wiki_text)
                    if href:
                        # dirty hack in order to undo the HTML entity quoting
                        node['refuri'] = href.groups()[0].replace("&amp;", "&")
                    else:
                        self.wiki_text = self.fixup_wiki_formatting(self.wiki_text)
                        self.add_wiki_markup()
        html4css1.HTMLTranslator.visit_reference(self, node)
    
    def visit_image(self, node):
        """ 
            Need to intervene in the case of inline images. We need MoinMoin to
            give us the actual src line to the image and then we can feed this
            to the default html4css1 writer. NOTE: Since the writer can't "open"
            this image the scale attribute doesn't work without directly
            specifying the height or width (or both).
            
            TODO: Need to handle figures similarly. 
        """
        uri = node['uri'].lstrip()
        prefix = ''       # assume no prefix
        if ':' in uri:
            prefix = uri.split(':',1)[0]
        # if prefix isn't URL, try to display in page
        if not prefix.lower() in ('file', 'http', 'https', 'ftp'):
            # no prefix given, so fake "inline:"
            if not prefix:
                node['uri'] = 'inline:' + uri
            self.process_inline(node, 'uri')
        html4css1.HTMLTranslator.visit_image(self, node)
        
    def create_wiki_functor(self, moin_func):
        moin_callable = getattr(self.formatter, moin_func)
        def visit_func(self, node):
            self.wiki_text = ''
            self.request.write(moin_callable(1))
            self.body.append(self.wiki_text)
        def depart_func(self, node):
            self.wiki_text = ''
            self.request.write(moin_callable(0))
            self.body.append(self.wiki_text)
        return visit_func, depart_func

    def setup_wiki_handlers(self):
        """
            Have the MoinMoin formatter handle markup when it makes sense. These
            are portions of the document that do not contain reST specific
            markup. This allows these portions of the document to look
            consistent with other wiki pages.
            
            Setup dispatch routines to handle basic document markup. The
            hanlders dict is the html4css1 handler name followed by the wiki
            handler name.
        """
        handlers = {
            # Text Markup
            'emphasis': 'emphasis',
            'strong': 'strong',
            'literal': 'code',
            # Blocks
            'literal_block': 'preformatted',
            # Simple Lists
            'bullet_list': 'bullet_list',
            'list_item': 'listitem',
            # Definition List
            'definition_list': 'definition_list',
            # Admonitions
            'warning': 'highlight'}
        for rest_func, moin_func in handlers.items():
            visit_func, depart_func = self.create_wiki_functor(moin_func)
            visit_func = new.instancemethod(visit_func, self, MoinTranslator)
            depart_func = new.instancemethod(depart_func, self, MoinTranslator)
            setattr(self, 'visit_%s' % (rest_func), visit_func)
            setattr(self, 'depart_%s' % (rest_func), depart_func)
        
    # Enumerated list takes an extra paramter so we handle this differently
    def visit_enumerated_list(self, node):
        self.wiki_text = ''
        self.request.write(self.formatter.number_list(1, start=node.get('start', None)))
        self.body.append(self.wiki_text)

    def depart_enumerated_list(self, node):
        self.wiki_text = ''
        self.request.write(self.formatter.number_list(0))
        self.body.append(self.wiki_text)

        
class MoinDirectives:
    """
        Class to handle all custom directive handling. This code is called as
        part of the parsing stage.
    """
    
    def __init__(self, request):
        self.request = request

        # include MoinMoin pages
        directives.register_directive('include', self.include)

        # used for MoinMoin macros
        directives.register_directive('macro', self.macro)
        
        # disallow a few directives in order to prevent XSS
        # disallowed include because it suffers from these bugs:
        #  * recursive includes are possible

        # for directive in ('meta', 'include', 'raw'):
        for directive in ('meta', 'raw'):
            directives.register_directive(directive, None)
            
        # disable the raw role
        roles._roles['raw'] = None
        
        # As a quick fix to handle recursive includes we limit the times a
        # document can be included to one.
        self.included_documents = []
        
    # Handle the include directive rather than letting the default docutils
    # parser handle it. This allows the inclusion of MoinMoin pages instead of
    # something from the filesystem.
    def include(self, name, arguments, options, content, lineno,
                content_offset, block_text, state, state_machine):
        # content contains the included file name
        
        _ = self.request.getText
        
        if len(content):
            if content[0] in self.included_documents:
                lines = [_("**Duplicate included files are not permitted**")]
                state_machine.insert_input(lines, 'MoinDirectives')
                return
            self.included_documents.append(content[0])
            page = Page(page_name = content[0], request = self.request)
            if page.exists():
                text = page.get_raw_body()
                lines = text.split('\n')
                # Remove the "#format rst" line
                if lines[0].startswith("#format"):
                    del lines[0]
            else:
                lines = [_("**Could not find the referenced page: %s**") % (content[0],)]
            # Insert the text from the included document and then continue
            # parsing
            state_machine.insert_input(lines, 'MoinDirectives')
        return
        
    include.content = True
    
    # Add additional macro directive. 
    # This allows MoinMoin macros to be used either by using the directive
    # directly or by using the substitution syntax. Much cleaner than using the
    # reference hack (`[[SomeMacro]]`_). This however simply adds a node to the
    # document tree which is a reference, but through a much better user
    # interface.
    def macro(self, name, arguments, options, content, lineno,
                content_offset, block_text, state, state_machine):
        # content contains macro to be called
        if len(content):
            # Allow either with or without brackets
            if content[0].startswith('[['):
                macro = content[0]
            else:
                macro = '[[%s]]' % content[0]
            ref = reference(macro, refuri = macro)
            ref['name'] = macro
            return [ref]
        return

    macro.content = True
    