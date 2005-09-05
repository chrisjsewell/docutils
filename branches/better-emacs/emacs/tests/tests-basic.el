;; Authors: Martin Blais <blais@furius.ca>
;; Date: $Date: 2005/04/01 23:19:41 $
;; Copyright: This module has been placed in the public domain.
;;
;; Regression tests for rest-adjust-section-title.
;;
;; Run this with::
;;
;;    emacs --script tests-adjust-section.el
;;

;; Import the module from the file in the parent directory directly.
(add-to-list 'load-path ".")
(load "tests-runner.el")
(add-to-list 'load-path "..")
(load "restructuredtext.el")

;; (setq debug-on-error t)


(setq rest-line-homogeneous-p-tests
  '(
;;------------------------------------------------------------------------------
(simple "Blablabla bla@" nil)
(true "-----------@" ?-)
(indented "   -----------@" ?-)
(letter "   aaaa@aaa" ?a)
(true2 "uuuuuuuuuuuuuuuuu@" ?u)
(misleading "--=---------@" nil)
(notstrip " uuuuuuuuuuuuuuuuu@" ?u)
(notstrip2 " uuuuuuuuuuuuuuuuu @" ?u)
(position "-------@----" ?-)
(one-char "-@" nil)
))

(progn
  (regression-test-compare-expect-values
   "Tests for predicate for one char line."
   rest-line-homogeneous-p-tests 'rest-line-homogeneous-p nil))




(setq rest-normalize-cursor-position-tests
      '(
;;------------------------------------------------------------------------------
(under
"

Du bon vin tous les jours.
@
"
"

@Du bon vin tous les jours.

"
)

;;------------------------------------------------------------------------------
(over
"
@
Du bon vin tous les jours.

"
"

@Du bon vin tous les jours.

"
)

;;------------------------------------------------------------------------------
(underline
"

Du bon vin tous les jours.
------@-----
"
"

@Du bon vin tous les jours.
-----------

"
)

;;------------------------------------------------------------------------------
(overline
"
------@-----
Du bon vin tous les jours.

"
"
-----------
@Du bon vin tous les jours.

"
)

;;------------------------------------------------------------------------------
(both
"
@-----------
Du bon vin tous les jours.
-----------

"
"
-----------
@Du bon vin tous les jours.
-----------

"
)

;;------------------------------------------------------------------------------
(joint
"
Du bon vin tous les jours.
@-----------
Du bon vin tous les jours.
-----------

"
"
@Du bon vin tous les jours.
-----------
Du bon vin tous les jours.
-----------

"
)

;;------------------------------------------------------------------------------
(separator
"

@-----------

"
"

@-----------

"
)

;;------------------------------------------------------------------------------
(between
"
Line 1
@
Line 2

"
"
@Line 1

Line 2

"
)

;;------------------------------------------------------------------------------
(between-2
"
=====================================
   Project Idea: Panorama Stitcher
====================================

:Author: Martin Blais <blais@furius.ca>
@
Another Title
=============
"
"
=====================================
   Project Idea: Panorama Stitcher
====================================

@:Author: Martin Blais <blais@furius.ca>

Another Title
=============
"
)

))


(progn
  (regression-test-compare-expect-buffer
   "Test preparation of cursor position."
   rest-normalize-cursor-position-tests 'rest-normalize-cursor-position nil))







(setq rest-get-decoration-tests
      '(
;;------------------------------------------------------------------------------
(nodec-1
"

@Du bon vin tous les jours

"
(nil nil 0))

;;------------------------------------------------------------------------------
(nodec-2
"

@
Du bon vin tous les jours

"
(nil nil 0))

;;------------------------------------------------------------------------------
(nodec-indent
"

@  Du bon vin tous les jours

"
(nil nil 2))

;;------------------------------------------------------------------------------
(underline
"

@Du bon vin tous les jours
=========================

"
(?= simple 0))

;;------------------------------------------------------------------------------
(underline-incomplete
"

@Du bon vin tous les jours
====================

"
(?= simple 0))

;;------------------------------------------------------------------------------
(underline-indent
"

@     Du bon vin tous les jours
====================

"
(?= simple 5))

;;------------------------------------------------------------------------------
(underline-one-char
"

@Du bon vin tous les jours
-
"
(nil nil 0))

;;------------------------------------------------------------------------------
(underline-two-char
"

@Du bon vin tous les jours
--
"
(?- simple 0))

;;------------------------------------------------------------------------------
(over-and-under
"
~~~~~~~~~~~~~~~~~~~~~~~~~
@Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~~~~~~~

"
(?~ over-and-under 0))

;;------------------------------------------------------------------------------
(over-and-under-indent
"
~~~~~~~~~~~~~~~~~~~~~~~~~
@   Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~~~~~~~

"
(?~ over-and-under 3))

;;------------------------------------------------------------------------------
(over-and-under-incomplete
"
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
@Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~

"
(?~ over-and-under 0))

;;------------------------------------------------------------------------------
(over-and-under-different-chars
"
---------------------------
@Du bon vin tous les jours
~~~~~~~~~~~~~~~~~~~~~~~~~~~

"
(?~ over-and-under 0))




;;------------------------------------------------------------------------------
(not-beginning
"

Du bon vin to@us les jours
=========================

"
(?= simple 0))

))


(progn
  (regression-test-compare-expect-values
   "Test getting the decoration."
   rest-get-decoration-tests 'rest-get-decoration nil))














(setq text-1
"===============================
   Project Idea: My Document
===============================

:Author: Martin Blais

Introduction
============

This is the introduction.

Notes
-----

Some notes.

Main Points
===========

Yep.

Super Point
-----------

~~~~~~~~~~~
@ Sub Point
~~~~~~~~~~~

Isn't this fabulous?

Conclusion
==========

That's it, really.

")

;; ~~~~~~~~~~~~~~~~~~
;;  Buggy Decoration
;; ~~~~~~
;;
;; ~~~~~~~~~~~~
;;  Decoration
;;
;;
;; ==========

(setq rest-find-all-decorations-tests
      `(
 ;;------------------------------------------------------------------------------
	(basic-1 ,text-1
		 ((2 61 over-and-under 3)
		  (7 61 simple 0)
		  (12 45 simple 0)
		  (17 61 simple 0)
		  (22 45 simple 0)
		  (26 126 over-and-under 1)
		  (31 61 simple 0))
		 )
	))


(progn
  (regression-test-compare-expect-values
   "Test finding all the decorations in a file."
   rest-find-all-decorations-tests 'rest-find-all-decorations nil))




(setq rest-get-hierarchy-tests
      `(
 ;;------------------------------------------------------------------------------
	(basic-1 ,text-1
		 ((61 over-and-under 3)
		  (61 simple 0)
		  (45 simple 0)
		  (126 over-and-under 1))
		 )
	))

(progn
  (regression-test-compare-expect-values
   "Test finding the hierarchy of sections in a file."
   rest-get-hierarchy-tests 'rest-get-hierarchy nil))




(setq rest-get-hierarchy-ignore-tests
      `(
 ;;------------------------------------------------------------------------------
	(basic-1 ,text-1
		 ((61 over-and-under 3)
		  (61 simple 0)
		  (45 simple 0))
		 )
	))

(progn
  (regression-test-compare-expect-values
   "Test finding the hierarchy of sections in a file, ignoring lines."
   rest-get-hierarchy-ignore-tests
   (lambda () (rest-get-hierarchy (rest-current-line))) nil))







(setq rest-decoration-complete-p-tests
  '(
;;------------------------------------------------------------------------------
(complete
"
@Vaudou
======
" t (?= simple 0))
))

(progn
  (regression-test-compare-expect-values
   "Tests for predicate for one char line."
   rest-decoration-complete-p-tests 'rest-decoration-complete-p nil))


















(setq rest-find-last-section-char-tests
  '(
;;------------------------------------------------------------------------------
(simple "
Simple Title
------------
@
" ?-)
;;------------------------------------------------------------------------------
(simple2 "
Simple Title1
=============

Simple Title
------------
@
" ?-)
))

(progn
  (regression-test-compare-expect-values
   "Tests for predicate for one char line."
   rest-find-last-section-char-tests
   'rest-find-last-section-char)
   nil)




(setq rest-current-section-char-tests
  '(
;;------------------------------------------------------------------------------
(simple "
Simple Title
------------
@
" ?-)
;;------------------------------------------------------------------------------
(incomplete "
Simple Title
---------
@
" ?-)
;;------------------------------------------------------------------------------
(over-and-under "
================
  Simple Title
================
@
" ?=)
))

(progn
  (regression-test-compare-expect-values
   "Tests for predicate for one char line."
   rest-current-section-char-tests
   (lambda () (rest-current-section-char (point)))
   t))



;;; FIXME continue here, write more tests.

