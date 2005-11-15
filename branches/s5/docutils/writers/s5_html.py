# Author: Chris Liechti
# Contact: cliechti@gmx.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
S5/HTML Slideshow Writer.
"""

__docformat__ = 'reStructuredText'


import sys
import os
import shutil
import docutils
from docutils import frontend, nodes, utils, writers
from docutils.writers import html4css1
from docutils.parsers.rst import directives

support_path = utils.relative_path(
    os.path.join(os.getcwd(), 'dummy'),
    os.path.join(writers.support_path, 's5_html'))

def find_theme(name):
    # Where else to look for a theme?
    # Check working dir?  Destination dir?  Config dir?  Plugins dir?
    path = os.path.join(support_path, name)
    if not os.path.isdir(path):
        raise docutils.ApplicationError('Theme directory not found: %r' % name)
    return path

def copy_file(name, source_dir, dest_dir, settings):
    """
    Copy file `name` (from `source_dir` to `dest_dir`) without overwriting.
    Return 1 if the file exists in either `source_dir` or `dest_dir`.
    """
    source = os.path.join(source_dir, name)
    dest = os.path.join(dest_dir, name)
    if os.path.isfile(source):
        if os.path.exists(dest):
            settings.record_dependencies.add(dest)
        else:
            shutil.copyfile(source, dest)
            settings.record_dependencies.add(source)
        return 1
    if os.path.isfile(dest):
        return 1


class Writer(html4css1.Writer):

    settings_spec = html4css1.Writer.settings_spec + (
        'S5 Slideshow Specific Options',
        'The --compact-lists option (defined in HTML-Specific Options above) '
        'is disabled by default for the S5/HTML writer.',
        (('Specify an installed S5 theme by name.  Overrides --theme-url.  '
          'The default theme name is "default".  The theme files will be '
          'copied into a "ui/<theme>" subdirectory, beside the destination '
          'file (output HTML).  Note that existing theme files will not be '
          'overwritten; you must manually delete the theme directory first.',
          ['--theme'],
          {'default': 'default', 'metavar': '<name>',
           'overrides': 'theme_url'}),
         ('Specify an S5 theme URL.  The destination file (output HTML) will '
          'link to this theme; nothing will be copied.  Overrides --theme.',
          ['--theme-url'],
          {'metavar': '<URL>', 'overrides': 'theme'}),))

    settings_default_overrides = {'compact_lists': 0}

    config_section = 's5_html writer'
    config_section_dependencies = ('writers', 'html4css1 writer')

    def __init__(self):
        html4css1.Writer.__init__(self)
        self.translator_class = S5HTMLTranslator


class S5HTMLTranslator(html4css1.HTMLTranslator):

    doctype = (
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'
        ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n')

    s5_stylesheet_template = '''\
<!-- configuration parameters -->
<meta name="defaultView" content="slideshow" />
<meta name="controlVis" content="hidden" />
<!-- style sheet links -->
<link rel="stylesheet" href="%(path)s/slides.css"
      type="text/css" media="projection" id="slideProj" />
<link rel="stylesheet" href="%(path)s/outline.css"
      type="text/css" media="screen" id="outlineStyle" />
<link rel="stylesheet" href="%(path)s/print.css"
      type="text/css" media="print" id="slidePrint" />
<link rel="stylesheet" href="%(path)s/opera.css"
      type="text/css" media="projection" id="operaFix" />
<script src="%(path)s/slides.js" type="text/javascript"></script>\n'''

    layout_template = '''\
<div class="layout">
<div id="controls"></div>
<div id="currentSlide"></div>
<div id="header">
%(header)s
</div>
<div id="footer">
%(title)s%(footer)s
</div>
</div>\n'''
# <div class="topleft"></div>
# <div class="topright"></div>
# <div class="bottomleft"></div>
# <div class="bottomright"></div>

    default_theme = 'default'
    """Name of the default theme."""

    base_theme_file = '__base__'
    """Name of the file containing the name of the base theme."""

    direct_theme_files = (
        'slides.css', 'outline.css', 'print.css', 'opera.css', 'slides.js')
    """Names of theme files directly linked to in the output HTML"""

    indirect_theme_files = (
        's5-core.css', 'framing.css', 'pretty.css', 'blank.gif', 'iepngfix.htc')
    """Names of files used indirectly; imported or used by files in
    `direct_theme_files`."""

    required_theme_files = indirect_theme_files + direct_theme_files
    """Names of mandatory theme files."""

    def __init__(self, *args):
        html4css1.HTMLTranslator.__init__(self, *args)
        #insert S5-specific stylesheet and script stuff:
        self.theme_file_path = None
        self.setup_theme()
        self.stylesheet.append(self.s5_stylesheet_template
                               % {'path': self.theme_file_path})
        self.add_meta('<meta name="version" content="S5 1.1" />\n')
        self.s5_footer = []
        self.s5_header = []
        self.section_count = 0

    def setup_theme(self):
        if self.document.settings.theme:
            self.copy_theme()
        elif self.document.settings.theme_url:
            self.theme_file_path = self.document.settings.theme_url
        else:
            raise docutils.ApplicationError(
                'No theme specified for S5/HTML writer.')

    def copy_theme(self):
        """
        Locate & copy theme files.

        A theme may be explicitly based on another theme via a '__base__'
        file.  The default base theme is 'default'.  Files are accumulated
        from the specified theme, any base themes, and 'default'.
        """
        settings = self.document.settings
        path = find_theme(settings.theme)
        theme_paths = [path]
        copied = {}
        # This is a link (URL) in HTML, so we use "/", not os.sep:
        self.theme_file_path = '%s/%s' % ('ui', settings.theme)
        dest = os.path.join(
            os.path.dirname(settings._destination), 'ui', settings.theme)
        if not os.path.isdir(dest):
            os.makedirs(dest)
        default = 0
        while path:
            for f in os.listdir(path):  # copy all files from each theme
                if ( copy_file(f, path, dest, settings)
                     and f in self.required_theme_files):
                    copied[f] = 1
            if default:
                break                   # "default" theme has no base theme
            # Find __base__ file in theme directory:
            base_theme_file = os.path.join(path, self.base_theme_file)
            # If it exists, read it and record the theme path:
            if os.path.isfile(base_theme_file):
                lines = open(base_theme_file).readlines()
                for line in lines:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        path = find_theme(line)
                        if path in theme_paths: # check for duplicates (cycles)
                            path = None         # if found, use default base
                        else:
                            theme_paths.append(path)
                        break
                else:                   # no theme name found
                    path = None         # use default base
            else:                       # no base theme file found
                path = None             # use default base
            if not path:
                path = find_theme(self.default_theme)
                theme_paths.append(path)
                default = 1
        if len(copied) != len(self.required_theme_files):
            # Some all required files weren't found & couldn't be copied.
            required = list(self.required_theme_files)
            for f in copied.keys():
                required.remove(f)
            raise docutils.ApplicationError(
                'Theme files not found: %s'
                % ', '.join(['%r' % f for f in required]))


    def depart_document(self, node):
        header = ''.join(self.s5_header)
        footer = ''.join(self.s5_footer)
        title = ''.join(self.html_title).replace('<h1 class="title">', '<h1>')
        layout = self.layout_template % {'header': header,
                                         'title': title,
                                         'footer': footer}
        self.fragment.extend(self.body)
        self.body_prefix.extend(layout)
        self.body_prefix.append('<div class="presentation">\n')
        self.body_prefix.append(self.starttag(node, 'div', CLASS='slide'))
        self.body_suffix.insert(0, '</div>\n')
        # skip content-type meta tag with interpolated charset value:
        self.html_head.extend(self.head[1:])
        self.html_body.extend(self.body_prefix[1:] + self.body_pre_docinfo
                              + self.docinfo + self.body
                              + self.body_suffix[:-1])

    def depart_footer(self, node):
        start = self.context.pop()
        self.s5_footer.append('<h2>')
        self.s5_footer.extend(self.body[start:])
        self.s5_footer.append('</h2>')
        del self.body[start:]

    def depart_header(self, node):
        start = self.context.pop()
        header = ['<div id="header">\n']
        header.extend(self.body[start:])
        header.append('\n</div>\n')
        del self.body[start:]
        self.s5_header.extend(header)

    def visit_section(self, node):
        if not self.section_count:
            self.body.append('\n</div>\n')
        self.section_count += 1
        self.section_level += 1
        if self.section_level > 1:
            # dummy for matching div's
            self.body.append(self.start_tag_with_title(
                node, 'div', CLASS='section'))
        else:
            self.body.append(self.start_tag_with_title(
                node, 'div', CLASS='slide'))
