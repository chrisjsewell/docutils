;; Author: David Goodger <goodger@python.org>
;; Date: $Date$
;; Copyright: This module has been placed in the public domain.
;;
;; Support code for editing reStructuredText with Emacs indented-text mode.
;; The goal is to create an integrated reStructuredText editing mode.
;;
;; Updates
;; -------
;;
;; 2003-02-25 (blais): updated repeat-last-character function and added
;;                     a few routines for navigating between titles.

(defun replace-lines (fromchar tochar)
  ;; by David Goodger
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

(defun repeat-last-character ()
  ;; by Martin Blais
  "Fills the current line up to the length of the preceding line (if not empty),
using the last character on the current line.  If the preceding line is empty,
or if a prefix argument is provided, fill up to the fill-column.

If the current line is longer than the desired length, shave the characters off
the current line to fit the desired length.

As an added convenience, if the command is repeated immediately, the alternative
behaviour is performed."

;; TODO
;; ----
;; It would be useful if only these characters were repeated:
;; =-`:.'"~^_*+#<>!$%&(),/;?@[\]{|}
;; Especially, empty lines shouldn't be repeated.

  (interactive)
  (let* ((curcol (current-column))
	 (curline (+ (count-lines (point-min) (point)) (if (eq curcol 0) 1 0)))
	 (lbp (line-beginning-position 0))
	 (prevcol (if (= curline 1)
		      fill-column
		    (save-excursion
		      (forward-line -1)
		      (end-of-line)
		      (skip-chars-backward " \t" lbp)
		      (let ((cc (current-column)))
			(if (= cc 0) fill-column cc)))))
	 (rightmost-column
	  (cond (current-prefix-arg fill-column)
		((equal last-command 'repeat-last-character)
		 (if (= curcol fill-column) prevcol fill-column))
		(t (save-excursion
		     (if (= prevcol 0) fill-column prevcol))) )) )
    (end-of-line)
    (if (> (current-column) rightmost-column)
	;; shave characters off the end
	(delete-region (- (point)
			  (- (current-column) rightmost-column))
		       (point))
      ;; fill with last characters
      (insert-char (preceding-char)
		   (- rightmost-column (current-column)))) ))

(defun reST-title-char-p (c)
  ;; by Martin Blais
  "Returns true if the given character is a valid title char."
  (and (string-match "[-=`:\\.'\"~^_*+#<>!$%&(),/;?@\\\|]" 
		     (char-to-string c)) t))

(defun reST-forward-title ()
  ;; by Martin Blais
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

(defun reST-backward-title ()
  ;; by Martin Blais
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
