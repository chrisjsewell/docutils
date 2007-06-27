# $Id$
# Copyright (C) 2002-2005 Freescale Semiconductor, Inc.
# Distributed under terms of the Perl license, which is the disjunction of
# the GNU General Public License (GPL) and the Artistic License.

# This package implements the perl directive for the perl implementation
# of reStructuredText.

package Text::Restructured::Directive::perl;

($VERSION) = q$Revision$ =~ /(\d+)/g;

=pod
=begin reST
=begin Description
Executes perl code and interpolates the results.  The code can be
contained either in the arguments or the contents section (or
both). It has the following options:

``:lenient:``
  Causes the exit code for the subprocess to be ignored.
``:file: <filename>``
  Takes the perl code from file <filename>.
``:literal:``
  Interpret the returned value as a literal block.

If this option is not present, the return value is interpreted
based on its type.  If you return a text string, the text is
interpreted as reStructuredText and is parsed again.  If you
return an internal DOM object (or list of them), the object is
included directly into the parsed DOM structure.  (This latter
option requires knowledge of trip internals, but is the only way
to create a pending DOM object for execution at transformation
time rather than parse time.)

The perl directive makes the following global variables available for
use within the perl code:

``$SOURCE``
   The name of the source file containing the perl directive.
``$LINENO``
   The line number of the perl directive within $SOURCE.
``$DIRECTIVE``
   The literal text of the perl directive.
``@INCLUDES``
   Array of [filename, linenumber] pairs of files which have included this one.
``$opt_<x>``
   The ``<x>`` option from the command line.
``$PARSER``
   The Text::Restructured parser object to allow text parsing within a
   perl directive.
``$TOP_FILE``
   The name of the top-level file.
``$VERSION``
   The version of prest (${main::VERSION}).

The following defines are processed by the perl directive:

-D perl='perl-code'
                Specifies some perl code that is executed prior
                to evaluating the first perl directive.  This
                option can be used to specify variables on the
                command line; for example::

                  -D perl='$a=1; $b=2'

                defines constants ``$a`` and ``$b`` that can
                be used in a perl block.
-D trusted      Must be specified for perl directives to use any
                operators normally masked out in a Safe environment.
                This requirement is to prevent a perl directive in a
                file written elsewhere from doing destructive things
                on your computer.
=end Description
=end reST
=cut

BEGIN {
    Text::Restructured::Directive::handle_directive
	('perl', \&Text::Restructured::Directive::perl::main);
}

use vars qw($DOM);
BEGIN {
    *DOM = "Text::Restructured::DOM";
}

# Plug-in handler for perl directives.
# Arguments: directive name, parent, source, line number, directive text, 
#            literal text
# Returns: array of DOM objects
sub main {
    my($parser, $name, $parent, $source, $lineno, $dtext, $lit) = @_;
    print STDERR "Debug: $name: $source, $lineno\n" if $parser->{opt}{d} >= 3;
    my @optlist = qw(file lenient literal);
    my $dhash = Text::Restructured::Directive::parse_directive
	($parser, $dtext, $lit, $source, $lineno, \@optlist);
    return $dhash if ref($dhash) eq $DOM;
    my($args, $options, $content) = map($dhash->{$_}, qw(args options content));
    return Text::Restructured::Directive::system_msg
	($parser, $name, 3, $source, $lineno,
	 qq(Cannot have both argument and content.), $lit)
	if $args !~ /^$/ && $content !~ /^$/;
    my $code = "$args$content";
    if ($options->{file}) {
	return Text::Restructured::Directive::system_msg
	    ($parser, $name, 3, $source, $lineno,
	     qq(Cannot have both :file: and content.), $lit)
	    if $code ne '';
	open FILE, $options->{file} or
	    return Text::Restructured::Directive::system_msg
	    ($parser, $name, 3, $source, $lineno,
	     qq(Cannot open file "$options->{file}".), $lit);
	$code = join '', <FILE>;
	close FILE;
    }
    
    if (! $Perl::safe) {
	# Create a safe compartment for the Perl to run
	use Safe;
	$Perl::safe = new Safe "Perl::Safe";
	# Grant privileges to the safe if -D trusted specified
	$Perl::safe->mask(Safe::empty_opset()) if $parser->{opt}{D}{trusted};
	# Share $opt_ variables, $^A to $^Z, %ENV, STDIN, STDOUT, STDERR,
	# VERSION
	my @vars = grep(/^[\x00-\x1f]|^(ENV|STD(IN|OUT|ERR)|VERSION)\Z/,
			keys %main::);
	foreach (@vars) {
	    local *var = $main::{$_};
	    *{"Perl::Safe::$_"} = *var;
	}
	# Share $opt_ variables
 	foreach (keys %{$parser->{opt}}) {
	    my $opt = $parser->{opt}{$_};
	    if (ref $opt eq 'ARRAY') {
		*{"Perl::Safe::opt_$_"} = \@$opt;
	    }
	    elsif (ref $opt eq 'HASH') {
		*{"Perl::Safe::opt_$_"} = \%$opt;
	    }
	    else {
		*{"Perl::Safe::opt_$_"} = \$opt;
	    }
 	}
	# Share RST and DOM subroutines
	foreach (keys %Text::Restructured::) {
	    local *opt = $Text::Restructured::{$_};
	    no strict 'refs';
	    *{"Perl::Safe::Text::Restructured::$_"} = \*{"Text::Restructured::$_"};
	}
	foreach (keys %Text::Restructured::DOM::) {
	    local *opt = $Text::Restructured::DOM::{$_};
	    no strict 'refs';
	    *{"Perl::Safe::Text::Restructured::DOM::$_"} =
		\&{"Text::Restructured::DOM::$_"}
	    if defined &{"Text::Restructured::DOM::$_"};
	}
    }
    
    if (defined $parser->{opt}{D}{perl}) {
	my $exp = $parser->{opt}{D}{perl};
	$Perl::safe->reval($exp);
	delete $parser->{opt}{D}{perl};
	my $err = $@ =~ /trapped by/ ? "$@Run with -D trusted if you believe the code is safe" : $@;
	return $parser->system_message
	    (4, $source, $lineno,
	     qq(Error executing "-D perl" option: $err.), $exp)
	    if $@;
    }
    my @text;
    my $newsource = qq($name directive at $source, line $lineno);
    my $in_safe = 0;
    my $i=0;
    while (my ($subr) = (caller($i++))[3]) {
	if ($subr eq 'Safe::reval') {
	    $in_safe = 1;
	    last;
	}
    }
    if ($in_safe) {
	# We're already in the safe box: just eval
	local $main::SOURCE    = $source;
	local $main::LINENO    = $lineno;
	local $main::DIRECTIVE = $lit;
	local $main::PARSER    = $parser;
	@text = eval "package main; $code";
    }
    else {
	$Perl::Safe::SOURCE    = $source;
	$Perl::Safe::LINENO    = $lineno;
	$Perl::Safe::DIRECTIVE = $lit;
	$Perl::Safe::TOP_FILE  = $parser->{TOP_FILE};
	$Perl::Safe::PARSER    = $parser;
	@Perl::Safe::INCLUDES  = @Text::Restructured::INCLUDES;
	@text = $Perl::safe->reval($code);
    }
    my $err = $@ =~ /trapped by/ ?
	"$@Run with -D trusted if you believe the code is safe" : $@;
    return $parser->system_message
	(4, $source, $lineno,
	 qq(Error executing "$name" directive: $err.), $lit)
	if $@ && ! defined $options->{lenient};
    push @text, $@ if $@;
    if (defined $options->{literal}) {
	my $text = join('',@text);
	if ($text !~ /^$/) {
	    my $lb = $DOM->new('literal_block', %Text::Restructured::XML_SPACE,
			       source=>$newsource);
	    $lb->append($DOM->newPCDATA($text));
	    return $lb;
	}
    }
    else {
	my $text;
	if ($parent->{tag} eq 'substitution_definition') {
	    my @doms;
	    if (@text == 0) { }
	    elsif (@text == 1) {
		my $fake = $DOM->new('fake');
		$parser->Paragraphs($fake, $text[0], $newsource, 1);
		my $last = $fake->last();
		if (@{$fake->{content}} == 1 && $last->{tag} eq 'paragraph') {
		    # Devel::Cover branch 0 1 paragraph always has #PCDATA
		    chomp $last->{content}[-1]{text}
		    if defined $last->{content}[-1]{text};
		    return  @{$last->{content}};
		}
		push(@doms, grep($_->{tag} eq 'system_message' && do {
		    delete $_->{attr}{backrefs}; 1},
				 @{$fake->{content}}));
	    }
	    else {
		push @doms, $parser->system_message(3, $source, $lineno,
						    qq(Error in "$name" directive within substitution definition: may contain a single paragraph only.),
						    $lit);
	    }
	    return @doms;
	}
	else {
	    foreach $text (@text) {
		next unless defined $text;
		if (ref($text) =~ /$DOM$/o) {
		    # Convert any internal transform reference to point
		    # within the safe
		    $text->{internal}{'.transform'} =
			"Perl.Safe.$text->{internal}{'.transform'}"
			if (defined $text->{internal} &&
			    defined $text->{internal}{'.transform'});
		    $parent->append($text);
		}
		else {
		    $parser->Paragraphs($parent, "$text\n", $newsource, 1)
			if $text ne '';
		}
	    }
	}
    }

    return;
}

1;
