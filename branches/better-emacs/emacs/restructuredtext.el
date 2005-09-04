;; Authors: David Goodger <goodger@python.org>,
;;          Martin Blais <blais@furius.ca>
;; Date: $Date$
;; Copyright: This module has been placed in the public domain.
;;
;; Support code for editing reStructuredText with Emacs indented-text mode.
;; The goal is to create an integrated reStructuredText editing mode.
;;
;; Installation instructions
;; -------------------------
;;
;; Add this line to your .emacs file::
;;
;;   (require 'restructuredtext)
;;
;; You should bind the versatile sectioning command to some key in the text-mode
;; hook. Something like this::
;;
;;   (defun user-rst-mode-hook ()
;;     (local-set-key [(control ?=)] 'rest-adjust-section-title)
;;     )
;;   (add-hook 'text-mode-hook 'user-rst-mode-hook)
;;
;; Other specialized and more generic functions are also available.
;; Note that C-= is a good binding, since it allows you to specify a negative
;; arg easily with C-- C-= (easy to type), as well as ordinary prefix arg with
;; C-u C-=.

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Generic Filter function.

(if (not (fboundp 'filter))
    (defun filter (pred list)
      "Returns a list of all the elements fulfilling the pred requirement (that
is for which (pred elem) is true)"
      (if list
          (let ((head (car list))
                (tail (filter pred (cdr list))))
            (if (funcall pred head)
                (cons head tail)
              tail)))))

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; Generic text functions that are more convenient than the defaults.
;;

(defun replace-lines (fromchar tochar)
  "Replace flush-left lines, consisting of multiple FROMCHAR characters,
with equal-length lines of TOCHAR."
  (interactive "\
cSearch for flush-left lines of char:
cand replace with char: ")
  (save-excursion
    (let* ((fromstr (string fromchar))
	   (searchre (concat "^" (regexp-quote fromstr) "+ *$"))
	   (found 0))
      (condition-case err
	  (while t
	    (search-forward-regexp searchre)
	    (setq found (1+ found))
	    (search-backward fromstr)  ;; point will be *before* last char
	    (setq p (1+ (point)))
	    (beginning-of-line)
	    (setq l (- p (point)))
	    (kill-line)
	    (insert-char tochar l))
	(search-failed
	 (message (format "%d lines replaced." found)))))))

(defun join-paragraph ()
  "Join lines in current paragraph into one line, removing end-of-lines."
  (interactive)
  (let ((fill-column 65000)) ; some big number
    (call-interactively 'fill-paragraph)))

(defun force-fill-paragraph ()
  "Fill paragraph at point, first joining the paragraph's lines into one.
This is useful for filling list item paragraphs."
  (interactive)
  (join-paragraph)
  (fill-paragraph nil))


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; The following functions implement a smart automatic title sectioning feature.
;; The idea is that with the cursor sitting on a section title, we try to get as
;; much information from context and try to do the best thing automatically.
;; This function can be invoked many times and/or with prefix argument to rotate
;; between the various sectioning decorations.
;;
;; Definitions: the two forms of sectioning define semantically separate section
;; levels.  A sectioning DECORATION consists in:
;;
;;   - a CHARACTER
;;
;;   - a STYLE which can be either of 'simple' or 'over-and-under'.
;;
;;   - an INDENT (meaningful for the over-and-under style only) which determines
;;     how many characters and over-and-under style is hanging outside of the
;;     title at the beginning and ending.
;;
;; Here are two examples of decorations (| represents the window border, column
;; 0):
;;
;;                                  |
;; 1. char: '-'   e                 |Some Title
;;    style: simple                 |----------
;;                                  |
;; 2. char: '='                     |==============
;;    style: over-and-under         |  Some Title
;;    indent: 2                     |==============
;;                                  |
;;
;; Some notes:
;;
;; - The underlining character that is used depends on context. The file is
;;   scanned to find other sections and an appropriate character is selected.
;;   If the function is invoked on a section that is complete, the character is
;;   rotated among the existing section decorations.
;;
;;   Note that when rotating the characters, if we come to the end of the
;;   hierarchy of decorations, the variable rest-preferred-decorations is
;;   consulted to propose a new underline decoration, and if continued, we cycle
;;   the decorations all over again.  Set this variable to nil if you want to
;;   limit the underlining character propositions to the existing decorations in
;;   the file.
;;
;; - A prefix argument can be used to alternate the style.
;;
;; - An underline/overline that is not extended to the column at which it should
;;   be hanging is dubbed INCOMPLETE.  For example::
;;
;;      |Some Title
;;      |-------
;;
;; Examples of default invocation:
;;
;;   |Some Title       --->    |Some Title
;;   | 			       |----------
;;
;;   |Some Title       --->    |Some Title
;;   |----- 		       |----------
;;
;;   |                         |------------
;;   | Some Title      --->    | Some Title
;;   | 			       |------------
;;
;; In over-and-under style, when alternating the style, a variable is available
;; to select how much default indent to use (it can be zero).  Note that if the
;; current section decoration already has an indent, we don't adjust it to the
;; default, we rather use the current indent that is already there for
;; adjustment (unless we cycle, in which case we use the indent that has been
;; found previously).

(defun rest-line-homogeneous-p (&optional accept-special)
  "Predicate return the unique char if the current line is
  composed only of a single repeated non-whitespace
  character. This returns the char even if there is whitespace at
  the beginning of the line.

  If ACCEPT-SPECIAL is specified we do not ignore special sequences
  which normally we would ignore when doing a search on many lines.
  For example, normally we have cases to ignore commonly occuring
  patterns, such as :: or ...;  with the flag do not ignore them."
  (save-excursion
    (back-to-indentation)
    (if (not (looking-at "\n"))
	(let ((c (thing-at-point 'char)))
	  (if (and (looking-at (format "[%s]+[ \t]*$" c))
		   (or accept-special
		       (and
			;; Common patterns.
			(not (looking-at "::[ \t]*$"))
			(not (looking-at "\\.\\.\\.[ \t]*$"))
			;; Discard one char line
			(not (looking-at ".[ \t]*$"))
			)))
	      (string-to-char c))
	  ))
    ))

(defun rest-find-last-section-char ()
  "Looks backward in the file for the character from the last
decoration before point."
  (let (c)
    (save-excursion
      (while (and (not c) (not (bobp)))
	(forward-line -1)
	(setq c (rest-line-homogeneous-p))
	))
    c))

(defun rest-current-section-char (&optional point)
  "Gets the character from the decoration around the current
point."
  (save-excursion
    (if point (goto-char point))
    (let ((offlist '(0 1 -2))
	  loff
	  rval
	  c)
      (while offlist
	(forward-line (car offlist))
	(setq c (rest-line-homogeneous-p 1))
	(if c
	    (progn (setq offlist nil
			 rval c))
	  (setq offlist (cdr offlist)))
	)
      rval
      )))

(defun rest-initial-sectioning-style (&optional point)
  "Looks around point and attempts to determine the sectioning style,
  between simple and over-and-under.  If a decoration cannot be
  found, return nil."
  (save-excursion
    (if point (goto-char point))
    (let (ou)
      (save-excursion
	(setq ou (mapcar
		  (lambda (x)
		    (forward-line x)
		    (rest-line-homogeneous-p))
		  '(-1 2))))
      (beginning-of-line)
      (cond
       ((equal ou '(nil nil)) nil)
       ((car ou) 'over-and-under) ;; we only need check the overline
       (t 'simple)
       )
      )))

(defun rest-all-section-chars (&optional ignore-lines)
  ;; FIXME this is insufficient
  "Finds all the section characters in the entire file and orders
  them hierarchically, removing duplicates.  Basically, returns a
  list of the section underlining characters.

  Optional parameters IGNORE-AROUND can be a list of lines to
  ignore."

  (let (chars
	c
	(curline 1))
    (save-excursion
      (beginning-of-buffer)
      (while (< (point) (buffer-end 1))
	(if (not (memq curline ignore-lines))
	    (progn
	      (setq c (rest-line-homogeneous-p))
	      (if c
		  (progn
		    (add-to-list 'chars c t)
		    ))) )
	(forward-line 1) (setq curline (+ curline 1))
	))
    chars))


(defun rest-suggest-new-char (allchars)
;; FIXME this is insufficient too
  "Suggest a new, different character, different from all that
have been seen."
  (let ((potentials (copy-sequence rest-preferred-decorations)))
    (dolist (x allchars)
      (setq potentials (delq x potentials))
      )
    (car potentials)
    ))


(defun rest-update-section (char style &optional indent)
  "Unconditionally updates the style of a section decoration
  using the given character CHAR, with STYLE 'simple or
  'over-and-under, and with indent INDENT.  If the STYLE is
  'simple, whitespace before the title is removed (indent is
  always assume to be 0).

  If there are existing overline and/or underline from the
  existing decoration, they are removed before adding the
  requested decoration."

  (interactive)
  (let (marker
	len
	ec
	(c ?-))

      (end-of-line)
      (setq marker (point-marker))

      ;; Fixup whitespace at the beginning and end of the line
      (if (or (null indent) (eq style 'simple))
	  (setq indent 0))
      (beginning-of-line)
      (delete-horizontal-space)
      (insert (make-string indent ? ))

      (end-of-line)
      (delete-horizontal-space)

      ;; Set the current column, we're at the end of the title line
      (setq len (+ (current-column) indent))

      ;; Remove previous line if it consists only of a single repeated character
      (save-excursion
	(forward-line -1)
	(and (rest-line-homogeneous-p 1)
	     (kill-line 1)))

      ;; Remove following line if it consists only of a single repeated
      ;; character
      (save-excursion
	(forward-line +1)
	(and (rest-line-homogeneous-p 1)
	     (kill-line 1))
	;; Add a newline if we're at the end of the buffer, for the subsequence
	;; inserting of the underline
	(if (= (point) (buffer-end 1))
	    (newline 1)))

      ;; Insert overline
      (if (eq style 'over-and-under)
	  (save-excursion
	    (beginning-of-line)
	    (open-line 1)
	    (insert (make-string len char))))

      ;; Insert underline
      (forward-line +1)
      (open-line 1)
      (insert (make-string len char))

      (forward-line +1)
      (goto-char marker)
      ))





(defvar rest-preferred-decorations
  '( (?= 'over-and-under 1)
     (?= 'simple 0)
     (?- 'simple 0)
     (?~ 'simple 0)
     (?+ 'simple 0)
     (?` 'simple 0)
     (?# 'simple 0)
     (?@ 'simple 0) )
  "Preferred ordering of section title decorations.  This
  sequence is consulted to offer a new decoration suggestion when
  we rotate the underlines at the end of the existing hierarchy
  of characters, or when there is no existing section title in
  the file.")


(defvar rest-default-indent 1
  "Number of characters to indent the section title when toggling
  decoration styles.  This is used when switching from a simple
  decoration style to a over-and-under decoration style.")


(defun rest-adjust-section-decoration ()
  "Adjust/rotate the section decoration for the section title around point.

This function is the main focus of this module and is a bit of a
swiss knife.  It is meant as the single function to invoke to
adjust the decorations of a section title in restructuredtext.

General Behaviour
=================

The next action it takes depends on context around the point, and
it is meant to be invoked possibly more than once to rotate among
the various possibilities. Basically, this function deals with:

- adding a decoration if the title does not have one;

- adjusting the length of the underline characters to fit a
  modified title;

- rotating the decoration in the set of already existing
  sectioning decorations used in the file;

- switching between simple and over-and-under styles.

You should normally not have to read all the following, just
invoke the method and it will do the most obvious thing that you
would expect.


Decoration Definitions
======================

The decorations consist in

1. a CHARACTER

2. a STYLE which can be either of 'simple' or 'over-and-under'.

3. an INDENT (meaningful for the over-and-under style only)
   which determines how many characters and over-and-under
   style is hanging outside of the title at the beginning and
   ending.

See source code for mode details.


Prefix Arguments
================

The method can take either (but not both) of

a. a (non-negative) prefix argument, which generally means to
   toggle the decoration style.  Invoke with C-u prefix for
   example;

b. a negative numerical argument, which generally inverts the
   direction of search in the file or hierarchy.  Invoke with C--
   prefix for example.


Detailed Behaviour Description
==============================

Here are the gory details of the algorithm (it seems quite
complicated, but really, it does the most obvious thing in all
the particular cases):

Case 1: No Decoration
---------------------

If the current line has no decoration around it,

- search backwards for the last previous decoration, and apply
  the decoration to the current (or preceding, if current is
  empty) line.  If a negative prefix argument is specified, we
  search forward instead.

- if there is no decoration found in the given direction, we
  use the first of rest-preferred-decorations.

Special note (existing indent): if there is an existing indent
in front of the section title (without existing decoration),
the over-and-under style is forced (using that indent).  If a
prefix argument is used in the case, the simple style is
forced.

Otherwise, if there is no existing indent, the prefix argument
forces a toggle of the prescribed decoration style.

Case 2: Incomplete Decoration
-----------------------------

If the current line does have an existing decoration, but the
decoration is incomplete, that is, the underline/overline does
not extend to exactly the end of the title line (it is either too
short or too long), we simply extend the length of the
underlines/overlines to fit exactly the section title.

If the prefix argument is given, we toggle the style of the
decoration as well.

A negative argument has no effect in this case.

Case 3: Complete Existing Decoration
------------------------------------

If the decoration is complete (i.e. the underline (overline)
length is already adjusted to the end of the title line), we
search/parse the file to establish the hierarchy of all the
decorations (making sure not to include the decoration around
point), and we rotate the current title's decoration from within
that list (by default, going *down* the hierarchy that is present
in the file, i.e. to a lower section level).  This is meant to be
used potentially multiple times, until the desired decoration is
found around the title.

If we hit the boundary of the hierarchy, exactly one choice from
the list of preferred decorations is suggested/chosen, the first
of those decoration that has not been seen in the file yet (and
not including the decoration around point), and the next
invocation rolls over to the other end of the hierarchy (i.e. it
cycles).  This allows you to avoid having to set which character
to use by always using the

If a negative argument is specified, the effect is to change the
direction of rotation in the hierarchy of decorations, thus
instead going *up* the hierarchy.

However, if there is a non-negative prefix argument, we do not
rotate the decoration, but instead simply toggle the style of the
current decoration (this should be the most common way to toggle
the style of an existing complete decoration).


Point Location
==============

The invocation of this function can be carried out anywhere
within the section title line, on an existing underline or
overline, as well as on an empty line following a section title.
This is meant to be as convenient as possible.


Indented Sections
=================

Indented section titles such as ::

   My Title
   --------

are illegal in restructuredtext and thus not recognized by the
parser.  This code will thus not work in a way that would support
indented sections (it would be ambiguous anyway).


Joint Sections
==============

Section titles that are right next to each other may not be
treated well.  More work might be needed to support those, and
special conditions on the completeness of existing decorations
might be required to make it non-ambiguous.

For now we assume that the decorations are disjoint, that is,
there is at least a single line between the titles/decoration
lines.


Suggested Binding
=================

We suggest that you bind this function on C-=.  It is close to
C-- so a negative argument can be easily specified with a flick
of the right hand fingers and the binding is unused in text-mode.
"
;; FIXME: you need to re-implement the algorithm to match the new description
;; above

  (interactive)

  (let* (
	 ;; Check if we're on an underline around a section title, and move the
	 ;; cursor to the title if this is the case.
	 (moved (rest-normalize-cursor-position))

	 ;; Find the decoration and completeness around point.
	 )))
;; FIXME todo



(defun the-rest ()
  ((
	 ;; Find current sectioning character.
	 (curchar (rest-current-section-char))
	 ;; Find current sectioning style.
	 (init-style (rest-initial-sectioning-style))
	 ;; Find current indentation of title line.
	 (curindent (save-excursion
		      (back-to-indentation)
		      (current-column)))

	 ;; Ending column.
	 (endcol (- (save-excursion
		      (end-of-line)
		      (current-column))
		    (save-excursion
		      (back-to-indentation)
		      (current-column))))
	 )

    ;; If there is no current style found...
    (if (eq init-style nil)
	;; Select style based on the whitespace at the beginning of the line.
	(save-excursion
	  (beginning-of-line)
	  (setq init-style
		(if (looking-at "^\\s-+") 'over-and-under 'simple))))

    ;; If we're switching characters, we're going to simply change the
    ;; sectioning style.  this branch is also taken if there is no current
    ;; sectioning around the title.
    (if (or (and current-prefix-arg
		 (not (< (prefix-numeric-value current-prefix-arg) 0)))
	    (eq curchar nil))

	;; We're switching characters or there is currently no sectioning.
	(progn
	  (setq curchar
		(or curchar
		    (rest-find-last-section-char)
		    (car (rest-all-section-chars))
		    (car rest-preferred-decorations)
		    ?=))

	  ;; If there is a current indent, reuse it, otherwise use default.
	  (if (= curindent 0)
	      (setq curindent rest-default-indent))

	  (rest-update-section
	   curchar
	   (if (and current-prefix-arg
		    (not (< (prefix-numeric-value current-prefix-arg) 0)))
	       (if (eq init-style 'over-and-under) 'simple 'over-and-under)
	     init-style)
	   curindent)
	  )

      ;; Else we're not switching characters, and there is some sectioning
      ;; already present, so check if the current sectioning is complete and
      ;; correct.
      (let ((exps (concat "^"
			  (regexp-quote (make-string
					 (+ endcol curindent) curchar))
			  "$")))
	(if (or
	     (not (save-excursion (forward-line +1)
				  (beginning-of-line)
				  (looking-at exps)))
	     (and (eq init-style 'over-and-under)
		  (not (save-excursion (forward-line -1)
				       (beginning-of-line)
				       (looking-at exps)))))

	    ;; The current sectioning needs to be fixed/updated!
	    (rest-update-section curchar init-style curindent)

	  ;; The current sectioning is complete, rotate characters.
	  (let* ( (curline (+ (count-lines (point-min) (point))
			      (if (bolp) 1 0)))
		  (allchars (rest-all-section-chars
			     (list (- curline 1) curline (+ curline 1))))

		  (rotchars
		   (append allchars
			   (filter 'identity
				   (list
				    ;; suggest a new char
				    (rest-suggest-new-char allchars)
				    ;; rotate to first char
				    (car allchars)))))
		  (nextchar
		   (or (cadr (memq curchar
				   (if (< (prefix-numeric-value
					   current-prefix-arg) 0)
				       (reverse rotchars) rotchars)))
		       (car allchars)) ) )


	    (if nextchar
		(rest-update-section nextchar init-style curindent))
	    )))
      )



    ;; Correct the position of the cursor to more accurately reflect where it
    ;; was located when the function was invoked.
    (if (!= moved 0)
	(progn (forward-line (- moved)) 
	       (end-of-line)))

    ))


;; =============================================================================

(defun rest-normalize-cursor-position ()
  "If the cursor is on a decoration line or an empty line , place
  it on the section title line (at the end).  Returns the line
  offset by which the cursor was moved. This works both over or
  under a line."
  (if (or (rest-line-homogeneous-p 1)
	  (looking-at "^[ \t]*$"))
      (cond
       ((save-excursion (forward-line -1)
			(beginning-of-line)
			(looking-at "^[ \t]*\\w+"))
	(progn (forward-line -1) -1))
       ((save-excursion (forward-line +1)
			(beginning-of-line)
			(looking-at "^[ \t]*\\w+"))
	(progn (forward-line +1) +1))
       (t 0))
    ))


(defun rest-find-all-decorations ()
  "Finds all the decorations in the file, and returns a list of
  (line, decoration) pairs.  Each decoration consists in a (char,
  style, indent) triple."

  (let (positions
	(curline 1))
    ;; Iterate over all the section titles/decorations in the file.
    (save-excursion
      (beginning-of-buffer)
      (while (< (point) (buffer-end 1))
	(if (rest-line-homogeneous-p)
	    (progn
	      (setq curline (+ curline (rest-normalize-cursor-position)))

	      ;; Here we have found a potential site for a decoration,
	      ;; characterize it.
	      (let ((deco (rest-get-decoration)))
		(if (cadr deco) ;; Style is existing.
		    ;; Found a real decoration site.
		    (progn
		      (push (cons curline (list deco)) positions)
		      ;; Push beyond the underline.
		      (forward-line 1) 
		      (setq curline (+ curline 1))
		      )))
	      ))
	(forward-line 1)
	(setq curline (+ curline 1))
	))
    positions))

(defun rest-get-decoration (&optional point)
  "Looks around point and finds the characteristics of the
  decoration that is found there.  We assume that the cursor is
  already placed on the title line (and not on the overline or
  underline).

  This function returns a (char, style, indent) triple.  If the
  characters of overline and underline are different, we return
  the underline character.  The indent is always calculated.  A
  decoration can be said to exist if the style is not nil.

  A point can be specified to go to the given location before
  extracting the decoration."
 
  (let (char style indent)
    (save-excursion
      (if point (goto-char point))
      (let (ou)
	(save-excursion
	  (setq ou (mapcar
		    (lambda (x)
		      (forward-line x)
		      (rest-line-homogeneous-p))
		    '(-1 2))))
	(beginning-of-line)
	(cond
	 ;; No decoration found, leave all return values nil.
	 ((equal ou '(nil nil))) 

	 ;; Overline only, leave all return values nil.
	 ;;
	 ;; Note: we don't return the overline character, but it could perhaps
	 ;; in some cases be used to do something.
	 ((and (car ou) (eq (cadr ou) nil)))

	 ;; Underline only.
	 ((and (cadr ou) (eq (car ou) nil))
	  (setq char (cadr ou)
		style 'simple))

	 ;; Both overline and underline.
	 (t
	  (setq char (cadr ou)
		style 'over-and-under))
	 )
	)
      ;; Find indentation.
      (setq indent (save-excursion
		     (back-to-indentation)
		     (current-column)))
      )
    ;; Return values.
    (list char style indent)))





(global-set-key [(meta ?[)]
		 (lambda () (interactive)
		   (message (prin1-to-string 
;			     (rest-line-homogeneous-p)
;			     (rest-normalize-cursor-position)
;			     (rest-get-decoration)
			     (rest-find-all-decorations)
			     )))))


    chars))

  (let (chars
	c
	(curline 1))
    (save-excursion
      (beginning-of-buffer)
      (while (< (point) (buffer-end 1))
	(if (not (memq curline ignore-lines))
	    (progn
	      (setq c (rest-line-homogeneous-p))
	      (if c
		  (progn
		    (add-to-list 'chars c t)
		    ))) )
	(forward-line 1) (setq curline (+ curline 1))
	))
    chars))






;; (defun rest-adjust-section-decoration-old ()
;;   "Older version of rest-adjust-section-decoration with looser
;; semantic and some bugs."
;;
;;   (interactive)
;;
;;   (let* (
;; 	 ;; Check if we're on an underline under a title line, and move the
;; 	 ;; cursor up if it is so.
;; 	 (moved
;; 	  (if (and (or (rest-line-homogeneous-p 1)
;; 		       (looking-at "^\\s-*$"))
;; 		   (save-excursion
;; 		     (forward-line -1)
;; 		     (beginning-of-line)
;; 		     (looking-at "^.+$")))
;; 	      (progn (forward-line -1) t)
;; 	    ))
;;
;; 	 ;; Find current sectioning character.
;; 	 (curchar (rest-current-section-char))
;; 	 ;; Find current sectioning style.
;; 	 (init-style (rest-initial-sectioning-style))
;; 	 ;; Find current indentation of title line.
;; 	 (curindent (save-excursion
;; 		      (back-to-indentation)
;; 		      (current-column)))
;;
;; 	 ;; Ending column.
;; 	 (endcol (- (save-excursion
;; 		      (end-of-line)
;; 		      (current-column))
;; 		    (save-excursion
;; 		      (back-to-indentation)
;; 		      (current-column))))
;; 	 )
;;
;;     ;; If there is no current style found...
;;     (if (eq init-style nil)
;; 	;; Select style based on the whitespace at the beginning of the line.
;; 	(save-excursion
;; 	  (beginning-of-line)
;; 	  (setq init-style
;; 		(if (looking-at "^\\s-+") 'over-and-under 'simple))))
;;
;;     ;; If we're switching characters, we're going to simply change the
;;     ;; sectioning style.  this branch is also taken if there is no current
;;     ;; sectioning around the title.
;;     (if (or (and current-prefix-arg
;; 		 (not (< (prefix-numeric-value current-prefix-arg) 0)))
;; 	    (eq curchar nil))
;;
;; 	;; We're switching characters or there is currently no sectioning.
;; 	(progn
;; 	  (setq curchar
;; 		(or curchar
;; 		    (rest-find-last-section-char)
;; 		    (car (rest-all-section-chars))
;; 		    (car rest-preferred-decorations)
;; 		    ?=))
;;
;; 	  ;; If there is a current indent, reuse it, otherwise use default.
;; 	  (if (= curindent 0)
;; 	      (setq curindent rest-default-indent))
;;
;; 	  (rest-update-section
;; 	   curchar
;; 	   (if (and current-prefix-arg
;; 		    (not (< (prefix-numeric-value current-prefix-arg) 0)))
;; 	       (if (eq init-style 'over-and-under) 'simple 'over-and-under)
;; 	     init-style)
;; 	   curindent)
;; 	  )
;;
;;       ;; Else we're not switching characters, and there is some sectioning
;;       ;; already present, so check if the current sectioning is complete and
;;       ;; correct.
;;       (let ((exps (concat "^"
;; 			  (regexp-quote (make-string
;; 					 (+ endcol curindent) curchar))
;; 			  "$")))
;; 	(if (or
;; 	     (not (save-excursion (forward-line +1)
;; 				  (beginning-of-line)
;; 				  (looking-at exps)))
;; 	     (and (eq init-style 'over-and-under)
;; 		  (not (save-excursion (forward-line -1)
;; 				       (beginning-of-line)
;; 				       (looking-at exps)))))
;;
;; 	    ;; The current sectioning needs to be fixed/updated!
;; 	    (rest-update-section curchar init-style curindent)
;;
;; 	  ;; The current sectioning is complete, rotate characters.
;; 	  (let* ( (curline (+ (count-lines (point-min) (point))
;; 			      (if (bolp) 1 0)))
;; 		  (allchars (rest-all-section-chars
;; 			     (list (- curline 1) curline (+ curline 1))))
;;
;; 		  (rotchars
;; 		   (append allchars
;; 			   (filter 'identity
;; 				   (list
;; 				    ;; suggest a new char
;; 				    (rest-suggest-new-char allchars)
;; 				    ;; rotate to first char
;; 				    (car allchars)))))
;; 		  (nextchar
;; 		   (or (cadr (memq curchar
;; 				   (if (< (prefix-numeric-value
;; 					   current-prefix-arg) 0)
;; 				       (reverse rotchars) rotchars)))
;; 		       (car allchars)) ) )
;;
;;
;; 	    (if nextchar
;; 		(rest-update-section nextchar init-style curindent))
;; 	    )))
;;       )
;;
;;     (if moved
;; 	(progn (forward-line 1) (end-of-line)))
;;     ))

;; Maintain an alias for compatibility.
(defalias 'rest-adjust-section-title 'rest-adjust-section-decoration)


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; Generic character repeater function.
;;
;; For sections, better to use the specialized function above, but this can
;; be useful for creating separators.

(defun repeat-last-character (&optional tofill)
  "Fills the current line up to the length of the preceding line (if not
empty), using the last character on the current line.  If the preceding line is
empty, we use the fill-column.

If a prefix argument is provided, use the next line rather than the preceding
line.

If the current line is longer than the desired length, shave the characters off
the current line to fit the desired length.

As an added convenience, if the command is repeated immediately, the alternative
column is used (fill-column vs. end of previous/next line)."
  (interactive)
  (let* ((curcol (current-column))
	 (curline (+ (count-lines (point-min) (point))
		     (if (eq curcol 0) 1 0)))
	 (lbp (line-beginning-position 0))
	 (prevcol (if (and (= curline 1) (not current-prefix-arg))
		      fill-column
		    (save-excursion
		      (forward-line (if current-prefix-arg 1 -1))
		      (end-of-line)
		      (skip-chars-backward " \t" lbp)
		      (let ((cc (current-column)))
			(if (= cc 0) fill-column cc)))))
	 (rightmost-column
	  (cond (tofill fill-column)
		((equal last-command 'repeat-last-character)
		 (if (= curcol fill-column) prevcol fill-column))
		(t (save-excursion
		     (if (= prevcol 0) fill-column prevcol)))
		)) )
    (end-of-line)
    (if (> (current-column) rightmost-column)
	;; shave characters off the end
	(delete-region (- (point)
			  (- (current-column) rightmost-column))
		       (point))
      ;; fill with last characters
      (insert-char (preceding-char)
		   (- rightmost-column (current-column))))
    ))



;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;
;; Section movement commands.
;;

;; Note: this is not quite correct, the definition is any non alpha-numeric
;; character.
(defun rest-title-char-p (c)
  "Returns true if the given character is a valid title char."
  (and (string-match "[-=`:\\.'\"~^_*+#<>!$%&(),/;?@\\\|]"
		     (char-to-string c)) t))

(defun rest-forward-section ()
  "Skip to the next restructured text section title."
  (interactive)
  (let* ( (newpoint
	   (save-excursion
	     (forward-char) ;; in case we're right on a title
	     (while
	       (not
		(and (re-search-forward "^[A-Za-z0-9].*[ \t]*$" nil t)
		     (reST-title-char-p (char-after (+ (point) 1)))
		     (looking-at (format "\n%c\\{%d,\\}[ \t]*$"
					 (char-after (+ (point) 1))
					 (current-column))))))
	     (beginning-of-line)
	     (point))) )
    (if newpoint (goto-char newpoint)) ))

(defun rest-backward-section ()
  "Skip to the previous restructured text section title."
  (interactive)
  (let* ( (newpoint
	   (save-excursion
	     ;;(forward-char) ;; in case we're right on a title
	     (while
	       (not
		(and (or (backward-char) t)
		     (re-search-backward "^[A-Za-z0-9].*[ \t]*$" nil t)
		     (or (end-of-line) t)
		     (reST-title-char-p (char-after (+ (point) 1)))
		     (looking-at (format "\n%c\\{%d,\\}[ \t]*$"
					 (char-after (+ (point) 1))
					 (current-column))))))
	     (beginning-of-line)
	     (point))) )
    (if newpoint (goto-char newpoint)) ))


;;------------------------------------------------------------------------------
;; For backwards compatibility.  Remove at some point.
(defalias 'reST-title-char-p 'rest-title-char-p)
(defalias 'reST-forward-title 'rest-forward-section)
(defalias 'reST-backward-title 'rest-backward-section)


(provide 'restructuredtext)
