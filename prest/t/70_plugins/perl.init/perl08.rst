Test of Perl dom option
=======================

.. perl::
   my $dom = new Text::Restructured::DOM('pending');
   $dom->{'source'} = $SOURCE;
   $dom->{'lineno'} = $LINENO;
   $dom->{'internal'}{'.transform'} = 'test.mytransform';
   return $dom;
   package test;
   sub mytransform {
       my($dom, $parser, $details) = @_;
       return newPCDATA Text::Restructured::DOM("This string contains the global variable \$Global::VAR: '$Global::VAR'")
   }

.. perl::
   $string = "\$Global::VAR = 'my string';";
   eval($string);
   $string;
