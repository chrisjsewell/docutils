"""
Implement latex directive.

"""
import os
import shutil
import sha
import tempfile
import subprocess

from docutils import nodes
from docutils.parsers.rst.directives import register_directive, flag
from docutils.parsers.rst.roles import register_canonical_role


def latex_math(tex):
    """ Process `tex` and produce image nodes. """
    image_names = latex_snippet_to_png(tex)

    the_nodes = []
    alt = tex
    for pageno, name in enumerate(image_names):
        
        the_nodes.append(nodes.image(uri=name, alt=alt))
        alt = ''
                         
    return the_nodes
    

def latex_directive(name, arguments, options, content, lineno,
                    content_offset, block_text, state, state_machine):
    """ Latex directive. """
    tex = '\n'.join(content)

    return latex_math(tex)

latex_directive.content = True


def latex_role(role, rawtext, text, lineno, inliner,
               options={}, content=[]):
    """ Latex role. """

    i = rawtext.find('`')
    tex = rawtext[i+1:-1]
    return latex_math(tex), []
    
def register():
    register_directive('latex', latex_directive)
    register_canonical_role('latex', latex_role)

    

def call_command_in_dir(app, args, targetdir):

    cwd = os.getcwd()
    try:
        os.chdir(targetdir)
        print args
        print ' '.join(args)
        p = subprocess.Popen(app + ' ' + ' '.join(args), shell=True)
        sts = os.waitpid(p.pid, 0)

        # FIXME -- should we raise an exception of status is non-zero?
        
    finally:
        # Restore working directory
        os.chdir(cwd)

latex_template = r'''
\documentclass[12pt]{article}
\pagestyle{empty}
%(prologue)s
\begin{document}
%(raw)s
\end{document}
'''
max_pages = 10
MAX_RUN_TIME = 5 # seconds
latex_name_template = 'latex2png_%s'
latex = "latex"
dvipng = "dvipng"
latex_args = ("--interaction=nonstopmode", "%s.tex")
dvipng_args = ("-bgTransparent", "-Ttight", "--noghostscript", "-l%s" % max_pages, "%s.dvi")

def latex_snippet_to_png(inputtex, prologue=''):
    """ Convert a latex snippet into a png. """
    
    tex = latex_template % { 'raw': inputtex, 'prologue': prologue }
    namebase = latex_name_template % sha.new(tex).hexdigest()
    dst = namebase + '%d.png'

    tmpdir = tempfile.mkdtemp()
    try:
        data = open("%s/%s.tex" % (tmpdir, namebase), "w")
        data.write(tex)
        data.close()
        args = list(latex_args)
        args[-1] = args[-1] % namebase
        res = call_command_in_dir(latex, args, tmpdir)
        if not res is None:
            # FIXME need to return some sort of error
            return []
        args = list(dvipng_args)
        args[-1] = args[-1] % namebase
        res = call_command_in_dir(dvipng, args, tmpdir)
        if not res is None:
            # FIXME need to return some sort of error
            return []

        page = 1
        pagenames = []
        while os.access("%s/%s%d.png" % (tmpdir, namebase, page), os.R_OK):
            pagename = dst % page
            shutil.copyfile("%s/%s%d.png" % (tmpdir, namebase, page), pagename)
            page += 1
            pagenames.append(pagename)
    finally:
        # FIXME do some tidy up here
        pass

    return pagenames
            
