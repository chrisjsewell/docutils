#! /usr/bin/env python

# Author: engelbert gruber
# Contact: grubert@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Tests for latex2e writer.
"""

from __init__ import DocutilsTestSupport

def suite():
    s = DocutilsTestSupport.LatexPublishTestSuite()
    s.generateTests(totest)
    return s


latex_head = """\
\\documentclass[10pt,english]{article}
\\usepackage{babel}
\\usepackage{shortvrb}
\\usepackage[latin1]{inputenc}
\\usepackage{tabularx}
\\usepackage{longtable}
\\setlength{\\extrarowheight}{2pt}
\\usepackage{amsmath}
\\usepackage{graphicx}
\\usepackage{color}
\\usepackage{multirow}
\\usepackage[colorlinks=true,linkcolor=blue,urlcolor=blue]{hyperref}
\\usepackage[a4paper,margin=2cm,nohead]{geometry}
%% generator Docutils: http://docutils.sourceforge.net/
\\newlength{\\admonitionwidth}
\\setlength{\\admonitionwidth}{0.9\\textwidth}
\\newlength{\\docinfowidth}
\\setlength{\\docinfowidth}{0.9\\textwidth}
\\newlength{\\locallinewidth}
\\newcommand{\\optionlistlabel}[1]{\\bf #1 \\hfill}
\\newenvironment{optionlist}[1]
{\\begin{list}{}
  {\\setlength{\\labelwidth}{#1}
   \\setlength{\\rightmargin}{1cm}
   \\setlength{\\leftmargin}{\\rightmargin}
   \\addtolength{\\leftmargin}{\\labelwidth}
   \\addtolength{\\leftmargin}{\\labelsep}
   \\renewcommand{\\makelabel}{\\optionlistlabel}}
}{\\end{list}}
% begin: floats for footnotes tweaking.
\\setlength{\\floatsep}{0.5em}
\\setlength{\\textfloatsep}{\\fill}
\\addtolength{\\textfloatsep}{3em}
\\renewcommand{\\textfraction}{0.5}
\\renewcommand{\\topfraction}{0.5}
\\renewcommand{\\bottomfraction}{0.5}
\\setcounter{totalnumber}{50}
\\setcounter{topnumber}{50}
\\setcounter{bottomnumber}{50}
% end floats for footnotes
% some commands, that could be overwritten in the style file.
\\newcommand{\\rubric}[1]{\\subsection*{~\\hfill {\\it #1} \\hfill ~}}
% end of "some commands"
"""

totest = {}

totest['table_of_contents'] = [
# input
["""\
.. contents:: Table of Contents

Title 1
=======
Paragraph 1.

Title 2
-------
Paragraph 2.
""",
# expected output
latex_head + """\
\\title{Title 1}
\\author{}
\\date{}
\\hypersetup{\npdftitle={Title 1}
}
\\raggedbottom
\\begin{document}
\\maketitle


\\setlength{\\locallinewidth}{\\linewidth}
\\hypertarget{table-of-contents}{}
\\pdfbookmark[0]{Table of Contents}{table-of-contents}
\\subsection*{~\\hfill Table of Contents\\hfill ~}
\\begin{list}{}{}
\\item \\href{#title-2}{Title 2}

\\end{list}


Paragraph 1.


%___________________________________________________________________________

\\hypertarget{title-2}{}
\\pdfbookmark[0]{Title 2}{title-2}
\\section*{Title 2}

Paragraph 2.

\\end{document}
"""],

]


totest['enumerated_lists'] = [
# input
["""\
1. Item 1.
2. Second to the previous item this one will explain

  a) nothing.
  b) or some other.

3. Third is 

  (I) having pre and postfixes
  (II) in roman numerals.
""",
# expected output
latex_head + """\
\\title{}
\\author{}
\\date{}
\\raggedbottom
\\begin{document}
\\maketitle


\\setlength{\\locallinewidth}{\\linewidth}
\\newcounter{listcnt1}
\\begin{list}{\\arabic{listcnt1}.}
{
\\usecounter{listcnt1}
\\setlength{\\rightmargin}{\\leftmargin}
}
\\item 
Item 1.

\\item 
Second to the previous item this one will explain

\\end{list}
\\begin{quote}
\\newcounter{listcnt2}
\\begin{list}{\\alph{listcnt2})}
{
\\usecounter{listcnt2}
\\setlength{\\rightmargin}{\\leftmargin}
}
\\item 
nothing.

\\item 
or some other.

\\end{list}
\\end{quote}
\\newcounter{listcnt3}
\\begin{list}{\\arabic{listcnt3}.}
{
\\usecounter{listcnt3}
\\addtocounter{listcnt3}{2}
\\setlength{\\rightmargin}{\\leftmargin}
}
\\item 
Third is

\\end{list}
\\begin{quote}
\\newcounter{listcnt4}
\\begin{list}{(\\Roman{listcnt4})}
{
\\usecounter{listcnt4}
\\setlength{\\rightmargin}{\\leftmargin}
}
\\item 
having pre and postfixes

\\item 
in roman numerals.

\\end{list}
\\end{quote}

\\end{document}
"""],
]

# BUG: need to test for quote replacing if language is de (ngerman).

totest['quote_mangling'] = [
# input
["""\
Depending on language quotes are converted for latex.
Expecting "en" here.

Inside literal blocks quotes should be left untouched
(use only two quotes in test code makes life easier for
the python interpreter running the test)::

    ""
    This is left "untouched" also *this*.
    ""

.. parsed-literal::

    should get "quotes" and *italics*.


Inline ``literal "quotes"`` should be kept.
""",
latex_head + """\
\\title{}
\\author{}
\\date{}
\\raggedbottom
\\begin{document}
\\maketitle


\\setlength{\\locallinewidth}{\\linewidth}

Depending on language quotes are converted for latex.
Expecting ``en'' here.

Inside literal blocks quotes should be left untouched
(use only two quotes in test code makes life easier for
the python interpreter running the test):
\\begin{ttfamily}\\begin{flushleft}
\\mbox{""}\\\\
\\mbox{This~is~left~"untouched"~also~*this*.}\\\\
\\mbox{""}
\\end{flushleft}\\end{ttfamily}
\\begin{ttfamily}\\begin{flushleft}
\\mbox{should~get~"quotes"~and~\\emph{italics}.}
\\end{flushleft}\\end{ttfamily}

Inline \\texttt{literal "quotes"} should be kept.

\\end{document}
"""],
]

if __name__ == '__main__':
    import unittest
    unittest.main(defaultTest='suite')
