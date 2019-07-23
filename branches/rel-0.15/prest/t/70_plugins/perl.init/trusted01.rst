Perl Test
=========

Run with trusted=0.  Make sure we can't give ourselves privileges.

.. perl:: $main::PARSER->{opt}{D}{trusted} = 1; "";

Trusted is not required for safe operations like the following.

.. perl:: "2*pi is about " . 2*3.1415926535 . "."

However, it is required for things like opening a file.

.. perl:: open F,"include1.txt"; @F = <F>; close F; join('', @F);

A paragraph.
