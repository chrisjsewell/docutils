.. -*- coding: utf-8 -*-

=====================================
 Emacs Support for reStructuredText_
=====================================

:Date: $Date$

.. _reStructuredText: http://docutils.sourceforge.net/rst.html


Directory Contents
==================

This directory contains the following Emacs lisp package files:

* rst.el : Emacs support for ReStructuredText. This file contains

  * Section decoration/adornment creation and updating (M. Blais);
  * Table-of-contents mode and insertion (M. Blais);
  * Font-lock syntax highlighting (S. Merten);
  * Some handy editing functions (D. Goodger).
  * Some functions for converting documents from emacs (M. Blais).  

* tests subdirectory: automated tests for some of the features in rst.el.
  Please make sure the tests pass if you change the LISP code.  Just type "make"
  to run the tests.

To install the package, put a copy of the package file in a directory on your
``load-path`` (use ``C-h v load-path`` to check).
