#!/usr/bin/perl

# This script looks at all of the basecards in the database, then it updates the filing_name. Using Library of Congress Filing standards - http://www.loc.gov/catdir/cpso/G100.pdf

use strict;
#use feature 'unicode_strings';
use DBI;
use Unicode::CharName qw(uname ublock);
#use charnames;
use Data::Dumper;

my $dbh = DBI->connect('DBI:mysql:mtgdbpy','mtgdb','password', {RaiseError=>1, PrintError=>0}) || die "Could not connect to database: $DBI::errstr";
$dbh->{'mysql_enable_utf8'} = 1;
$dbh->do(qq{SET NAMES 'utf8';});

# First, load in all of the basecards
my $basecards_hash;
{
    my $testSQL = "SELECT id, name FROM basecard;";# WHERE name LIKE '%therlin%' OR name LIKE '%Avenan% 'OR name LIKE '%0%' OR name LIKE '%1%' OR name LIKE '%.%' OR name LIKE '%''%' OR name LIKE '%,%';";
    my $sth = $dbh->prepare($testSQL);
    $sth->execute;
    $basecards_hash = $sth->fetchall_hashref('id');
}

#print Dumper($basecards_hash);

sub numFix() {
	my $q = shift;
	my $n = shift;
	$n =~ s/,//g;
	return sprintf($q . '%09s', $n);
}

my $aaa = \&numFix;
my @ignored_punctuation = ('!','"','#','$','%',"'",'(',')','*','+',',','-','.','/',':',';','<','=','>','?','[',']','\\','^','_','{','|','}','~');
for (my $u = 161; $u < 192; $u++) {
	push @ignored_punctuation, chr($u);
}

foreach my $id (keys %{$basecards_hash} ) {

	$basecards_hash->{$id}->{filing_name} = $basecards_hash->{$id}->{name};

	# Rule 1 - General Principle
	#
	# This is standard alphetical order, which computers are good at. But,
	# let's lowercase everything to make sure that we are playing in the same space.
	$basecards_hash->{$id}->{filing_name} = lc($basecards_hash->{$id}->{filing_name});

	# Rule 2 - Treat modified letters like their equivalents in the
	# English alphabet. Ignore diacritical marks and modifications of
	# recognizable English letters
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00c0}/a/gi; # LATIN CAPITAL LETTER A WITH GRAVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00c1}/a/gi; # LATIN CAPITAL LETTER A WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00c2}/a/gi; # LATIN CAPITAL LETTER A WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00c3}/a/gi; # LATIN CAPITAL LETTER A WITH TILDE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00c4}/a/gi; # LATIN CAPITAL LETTER A WITH DIAERESIS
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00c5}/a/gi; # LATIN CAPITAL LETTER A WITH RING ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00c6}/ae/gi; # LATIN CAPITAL LETTER AE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00c7}/c/gi; # LATIN CAPITAL LETTER C WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00c8}/e/gi; # LATIN CAPITAL LETTER E WITH GRAVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00c9}/e/gi; # LATIN CAPITAL LETTER E WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00ca}/e/gi; # LATIN CAPITAL LETTER E WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00cb}/e/gi; # LATIN CAPITAL LETTER E WITH DIAERESIS
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00cc}/i/gi; # LATIN CAPITAL LETTER I WITH GRAVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00cd}/i/gi; # LATIN CAPITAL LETTER I WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00ce}/i/gi; # LATIN CAPITAL LETTER I WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00cf}/i/gi; # LATIN CAPITAL LETTER I WITH DIAERESIS
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00d0}/d/gi; # LATIN CAPITAL LETTER ETH
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00d1}/n/gi; # LATIN CAPITAL LETTER N WITH TILDE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00d2}/o/gi; # LATIN CAPITAL LETTER O WITH GRAVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00d3}/o/gi; # LATIN CAPITAL LETTER O WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00d4}/o/gi; # LATIN CAPITAL LETTER O WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00d5}/o/gi; # LATIN CAPITAL LETTER O WITH TILDE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00d6}/o/gi; # LATIN CAPITAL LETTER O WITH DIAERESIS
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00d7}/ /gi; # MULTIPLICATION SIGN
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00d8}/o/gi; # LATIN CAPITAL LETTER O WITH STROKE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00d9}/u/gi; # LATIN CAPITAL LETTER U WITH GRAVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00da}/u/gi; # LATIN CAPITAL LETTER U WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00db}/u/gi; # LATIN CAPITAL LETTER U WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00dc}/u/gi; # LATIN CAPITAL LETTER U WITH DIAERESIS
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00dd}/y/gi; # LATIN CAPITAL LETTER Y WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00de}/th/gi; # LATIN CAPITAL LETTER THORN
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00df}/s/gi; # LATIN SMALL LETTER SHARP S
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00e0}/a/gi; # LATIN SMALL LETTER A WITH GRAVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00e1}/a/gi; # LATIN SMALL LETTER A WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00e2}/a/gi; # LATIN SMALL LETTER A WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00e3}/a/gi; # LATIN SMALL LETTER A WITH TILDE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00e4}/a/gi; # LATIN SMALL LETTER A WITH DIAERESIS
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00e5}/a/gi; # LATIN SMALL LETTER A WITH RING ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00e6}/ae/gi; # LATIN SMALL LETTER AE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00e7}/c/gi; # LATIN SMALL LETTER C WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00e8}/e/gi; # LATIN SMALL LETTER E WITH GRAVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00e9}/e/gi; # LATIN SMALL LETTER E WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00ea}/e/gi; # LATIN SMALL LETTER E WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00eb}/e/gi; # LATIN SMALL LETTER E WITH DIAERESIS
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00ec}/i/gi; # LATIN SMALL LETTER I WITH GRAVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00ed}/i/gi; # LATIN SMALL LETTER I WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00ee}/i/gi; # LATIN SMALL LETTER I WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00ef}/i/gi; # LATIN SMALL LETTER I WITH DIAERESIS
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00f0}/d/gi; # LATIN SMALL LETTER ETH
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00f1}/n/gi; # LATIN SMALL LETTER N WITH TILDE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00f2}/o/gi; # LATIN SMALL LETTER O WITH GRAVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00f3}/o/gi; # LATIN SMALL LETTER O WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00f4}/o/gi; # LATIN SMALL LETTER O WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00f5}/o/gi; # LATIN SMALL LETTER O WITH TILDE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00f6}/o/gi; # LATIN SMALL LETTER O WITH DIAERESIS
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00f7}/ /gi; # DIVISION SIGN
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00f8}/o/gi; # LATIN SMALL LETTER O WITH STROKE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00f9}/u/gi; # LATIN SMALL LETTER U WITH GRAVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00fa}/u/gi; # LATIN SMALL LETTER U WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00fb}/u/gi; # LATIN SMALL LETTER U WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00fc}/u/gi; # LATIN SMALL LETTER U WITH DIAERESIS
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00fd}/y/gi; # LATIN SMALL LETTER Y WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00fe}/th/gi; # LATIN SMALL LETTER THORN
    $basecards_hash->{$id}->{filing_name} =~ s/\x{00ff}/y/gi; # LATIN SMALL LETTER Y WITH DIAERESIS
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0100}/a/gi; # LATIN CAPITAL LETTER A WITH MACRON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0101}/a/gi; # LATIN SMALL LETTER A WITH MACRON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0102}/a/gi; # LATIN CAPITAL LETTER A WITH BREVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0103}/a/gi; # LATIN SMALL LETTER A WITH BREVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0104}/a/gi; # LATIN CAPITAL LETTER A WITH OGONEK
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0105}/a/gi; # LATIN SMALL LETTER A WITH OGONEK
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0106}/c/gi; # LATIN CAPITAL LETTER C WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0107}/c/gi; # LATIN SMALL LETTER C WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0108}/c/gi; # LATIN CAPITAL LETTER C WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0109}/c/gi; # LATIN SMALL LETTER C WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{010a}/c/gi; # LATIN CAPITAL LETTER C WITH DOT ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{010b}/c/gi; # LATIN SMALL LETTER C WITH DOT ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{010c}/c/gi; # LATIN CAPITAL LETTER C WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{010d}/c/gi; # LATIN SMALL LETTER C WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{010e}/d/gi; # LATIN CAPITAL LETTER D WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{010f}/d/gi; # LATIN SMALL LETTER D WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0110}/d/gi; # LATIN CAPITAL LETTER D WITH STROKE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0111}/d/gi; # LATIN SMALL LETTER D WITH STROKE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0112}/e/gi; # LATIN CAPITAL LETTER E WITH MACRON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0113}/e/gi; # LATIN SMALL LETTER E WITH MACRON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0114}/e/gi; # LATIN CAPITAL LETTER E WITH BREVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0115}/e/gi; # LATIN SMALL LETTER E WITH BREVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0116}/e/gi; # LATIN CAPITAL LETTER E WITH DOT ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0117}/e/gi; # LATIN SMALL LETTER E WITH DOT ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0118}/e/gi; # LATIN CAPITAL LETTER E WITH OGONEK
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0119}/e/gi; # LATIN SMALL LETTER E WITH OGONEK
    $basecards_hash->{$id}->{filing_name} =~ s/\x{011a}/e/gi; # LATIN CAPITAL LETTER E WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{011b}/e/gi; # LATIN SMALL LETTER E WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{011c}/g/gi; # LATIN CAPITAL LETTER G WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{011d}/g/gi; # LATIN SMALL LETTER G WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{011e}/g/gi; # LATIN CAPITAL LETTER G WITH BREVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{011f}/g/gi; # LATIN SMALL LETTER G WITH BREVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0120}/g/gi; # LATIN CAPITAL LETTER G WITH DOT ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0121}/g/gi; # LATIN SMALL LETTER G WITH DOT ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0122}/g/gi; # LATIN CAPITAL LETTER G WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0123}/g/gi; # LATIN SMALL LETTER G WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0124}/h/gi; # LATIN CAPITAL LETTER H WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0125}/h/gi; # LATIN SMALL LETTER H WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0126}/h/gi; # LATIN CAPITAL LETTER H WITH STROKE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0127}/h/gi; # LATIN SMALL LETTER H WITH STROKE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0128}/i/gi; # LATIN CAPITAL LETTER I WITH TILDE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0129}/i/gi; # LATIN SMALL LETTER I WITH TILDE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{012a}/i/gi; # LATIN CAPITAL LETTER I WITH MACRON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{012b}/i/gi; # LATIN SMALL LETTER I WITH MACRON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{012c}/i/gi; # LATIN CAPITAL LETTER I WITH BREVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{012d}/i/gi; # LATIN SMALL LETTER I WITH BREVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{012e}/i/gi; # LATIN CAPITAL LETTER I WITH OGONEK
    $basecards_hash->{$id}->{filing_name} =~ s/\x{012f}/i/gi; # LATIN SMALL LETTER I WITH OGONEK
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0130}/i/gi; # LATIN CAPITAL LETTER I WITH DOT ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0131}/i/gi; # LATIN SMALL LETTER DOTLESS I
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0132}/ij/gi; # LATIN CAPITAL LIGATURE IJ
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0133}/ij/gi; # LATIN SMALL LIGATURE IJ
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0134}/j/gi; # LATIN CAPITAL LETTER J WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0135}/j/gi; # LATIN SMALL LETTER J WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0136}/k/gi; # LATIN CAPITAL LETTER K WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0137}/k/gi; # LATIN SMALL LETTER K WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0138}/kr/gi; # LATIN SMALL LETTER KRA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0139}/l/gi; # LATIN CAPITAL LETTER L WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{013a}/l/gi; # LATIN SMALL LETTER L WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{013b}/l/gi; # LATIN CAPITAL LETTER L WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{013c}/l/gi; # LATIN SMALL LETTER L WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{013d}/l/gi; # LATIN CAPITAL LETTER L WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{013e}/l/gi; # LATIN SMALL LETTER L WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{013f}/l/gi; # LATIN CAPITAL LETTER L WITH MIDDLE DOT
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0140}/l/gi; # LATIN SMALL LETTER L WITH MIDDLE DOT
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0141}/l/gi; # LATIN CAPITAL LETTER L WITH STROKE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0142}/l/gi; # LATIN SMALL LETTER L WITH STROKE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0143}/n/gi; # LATIN CAPITAL LETTER N WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0144}/n/gi; # LATIN SMALL LETTER N WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0145}/n/gi; # LATIN CAPITAL LETTER N WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0146}/n/gi; # LATIN SMALL LETTER N WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0147}/n/gi; # LATIN CAPITAL LETTER N WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0148}/n/gi; # LATIN SMALL LETTER N WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0149}/n/gi; # LATIN SMALL LETTER N PRECEDED BY APOSTROPHE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{014a}/n/gi; # LATIN CAPITAL LETTER ENG
    $basecards_hash->{$id}->{filing_name} =~ s/\x{014b}/n/gi; # LATIN SMALL LETTER ENG
    $basecards_hash->{$id}->{filing_name} =~ s/\x{014c}/o/gi; # LATIN CAPITAL LETTER O WITH MACRON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{014d}/o/gi; # LATIN SMALL LETTER O WITH MACRON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{014e}/o/gi; # LATIN CAPITAL LETTER O WITH BREVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{014f}/o/gi; # LATIN SMALL LETTER O WITH BREVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0150}/o/gi; # LATIN CAPITAL LETTER O WITH DOUBLE ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0151}/o/gi; # LATIN SMALL LETTER O WITH DOUBLE ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0152}/oe/gi; # LATIN CAPITAL LIGATURE OE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0153}/oe/gi; # LATIN SMALL LIGATURE OE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0154}/r/gi; # LATIN CAPITAL LETTER R WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0155}/r/gi; # LATIN SMALL LETTER R WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0156}/r/gi; # LATIN CAPITAL LETTER R WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0157}/r/gi; # LATIN SMALL LETTER R WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0158}/r/gi; # LATIN CAPITAL LETTER R WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0159}/r/gi; # LATIN SMALL LETTER R WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{015a}/s/gi; # LATIN CAPITAL LETTER S WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{015b}/s/gi; # LATIN SMALL LETTER S WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{015c}/s/gi; # LATIN CAPITAL LETTER S WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{015d}/s/gi; # LATIN SMALL LETTER S WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{015e}/s/gi; # LATIN CAPITAL LETTER S WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{015f}/s/gi; # LATIN SMALL LETTER S WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0160}/s/gi; # LATIN CAPITAL LETTER S WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0161}/s/gi; # LATIN SMALL LETTER S WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0162}/t/gi; # LATIN CAPITAL LETTER T WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0163}/t/gi; # LATIN SMALL LETTER T WITH CEDILLA
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0164}/t/gi; # LATIN CAPITAL LETTER T WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0165}/t/gi; # LATIN SMALL LETTER T WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0166}/t/gi; # LATIN CAPITAL LETTER T WITH STROKE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0167}/t/gi; # LATIN SMALL LETTER T WITH STROKE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0168}/u/gi; # LATIN CAPITAL LETTER U WITH TILDE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0169}/u/gi; # LATIN SMALL LETTER U WITH TILDE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{016a}/u/gi; # LATIN CAPITAL LETTER U WITH MACRON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{016b}/u/gi; # LATIN SMALL LETTER U WITH MACRON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{016c}/u/gi; # LATIN CAPITAL LETTER U WITH BREVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{016d}/u/gi; # LATIN SMALL LETTER U WITH BREVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{016e}/u/gi; # LATIN CAPITAL LETTER U WITH RING ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{016f}/u/gi; # LATIN SMALL LETTER U WITH RING ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0170}/u/gi; # LATIN CAPITAL LETTER U WITH DOUBLE ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0171}/u/gi; # LATIN SMALL LETTER U WITH DOUBLE ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0172}/u/gi; # LATIN CAPITAL LETTER U WITH OGONEK
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0173}/u/gi; # LATIN SMALL LETTER U WITH OGONEK
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0174}/w/gi; # LATIN CAPITAL LETTER W WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0175}/w/gi; # LATIN SMALL LETTER W WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0176}/y/gi; # LATIN CAPITAL LETTER Y WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0177}/y/gi; # LATIN SMALL LETTER Y WITH CIRCUMFLEX
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0178}/y/gi; # LATIN CAPITAL LETTER Y WITH DIAERESIS
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0179}/z/gi; # LATIN CAPITAL LETTER Z WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{017a}/z/gi; # LATIN SMALL LETTER Z WITH ACUTE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{017b}/z/gi; # LATIN CAPITAL LETTER Z WITH DOT ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{017c}/z/gi; # LATIN SMALL LETTER Z WITH DOT ABOVE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{017d}/z/gi; # LATIN CAPITAL LETTER Z WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{017e}/z/gi; # LATIN SMALL LETTER Z WITH CARON
    $basecards_hash->{$id}->{filing_name} =~ s/\x{017f}/s/gi; # LATIN SMALL LETTER LONG S
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0180}/b/gi; # LATIN SMALL LETTER B WITH STROKE
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0181}/b/gi; # LATIN CAPITAL LETTER B WITH HOOK
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0182}/b/gi; # LATIN CAPITAL LETTER B WITH TOPBAR
    $basecards_hash->{$id}->{filing_name} =~ s/\x{0183}/b/gi; # LATIN SMALL LETTER B WITH TOPBAR
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0184}/_/gi; # LATIN CAPITAL LETTER TONE SIX
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0185}/_/gi; # LATIN SMALL LETTER TONE SIX
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0186}/_/gi; # LATIN CAPITAL LETTER OPEN O
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0187}/_/gi; # LATIN CAPITAL LETTER C WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0188}/_/gi; # LATIN SMALL LETTER C WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0189}/_/gi; # LATIN CAPITAL LETTER AFRICAN D
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{018a}/_/gi; # LATIN CAPITAL LETTER D WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{018b}/_/gi; # LATIN CAPITAL LETTER D WITH TOPBAR
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{018c}/_/gi; # LATIN SMALL LETTER D WITH TOPBAR
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{018d}/_/gi; # LATIN SMALL LETTER TURNED DELTA
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{018e}/_/gi; # LATIN CAPITAL LETTER REVERSED E
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{018f}/_/gi; # LATIN CAPITAL LETTER SCHWA
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0190}/_/gi; # LATIN CAPITAL LETTER OPEN E
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0191}/_/gi; # LATIN CAPITAL LETTER F WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0192}/_/gi; # LATIN SMALL LETTER F WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0193}/_/gi; # LATIN CAPITAL LETTER G WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0194}/_/gi; # LATIN CAPITAL LETTER GAMMA
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0195}/_/gi; # LATIN SMALL LETTER HV
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0196}/_/gi; # LATIN CAPITAL LETTER IOTA
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0197}/_/gi; # LATIN CAPITAL LETTER I WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0198}/_/gi; # LATIN CAPITAL LETTER K WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0199}/_/gi; # LATIN SMALL LETTER K WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{019a}/_/gi; # LATIN SMALL LETTER L WITH BAR
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{019b}/_/gi; # LATIN SMALL LETTER LAMBDA WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{019c}/_/gi; # LATIN CAPITAL LETTER TURNED M
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{019d}/_/gi; # LATIN CAPITAL LETTER N WITH LEFT HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{019e}/_/gi; # LATIN SMALL LETTER N WITH LONG RIGHT LEG
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{019f}/_/gi; # LATIN CAPITAL LETTER O WITH MIDDLE TILDE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01a0}/_/gi; # LATIN CAPITAL LETTER O WITH HORN
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01a1}/_/gi; # LATIN SMALL LETTER O WITH HORN
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01a2}/_/gi; # LATIN CAPITAL LETTER OI
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01a3}/_/gi; # LATIN SMALL LETTER OI
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01a4}/_/gi; # LATIN CAPITAL LETTER P WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01a5}/_/gi; # LATIN SMALL LETTER P WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01a6}/_/gi; # LATIN LETTER YR
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01a7}/_/gi; # LATIN CAPITAL LETTER TONE TWO
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01a8}/_/gi; # LATIN SMALL LETTER TONE TWO
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01a9}/_/gi; # LATIN CAPITAL LETTER ESH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01aa}/_/gi; # LATIN LETTER REVERSED ESH LOOP
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ab}/_/gi; # LATIN SMALL LETTER T WITH PALATAL HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ac}/_/gi; # LATIN CAPITAL LETTER T WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ad}/_/gi; # LATIN SMALL LETTER T WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ae}/_/gi; # LATIN CAPITAL LETTER T WITH RETROFLEX HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01af}/_/gi; # LATIN CAPITAL LETTER U WITH HORN
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01b0}/_/gi; # LATIN SMALL LETTER U WITH HORN
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01b1}/_/gi; # LATIN CAPITAL LETTER UPSILON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01b2}/_/gi; # LATIN CAPITAL LETTER V WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01b3}/_/gi; # LATIN CAPITAL LETTER Y WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01b4}/_/gi; # LATIN SMALL LETTER Y WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01b5}/_/gi; # LATIN CAPITAL LETTER Z WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01b6}/_/gi; # LATIN SMALL LETTER Z WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01b7}/_/gi; # LATIN CAPITAL LETTER EZH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01b8}/_/gi; # LATIN CAPITAL LETTER EZH REVERSED
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01b9}/_/gi; # LATIN SMALL LETTER EZH REVERSED
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ba}/_/gi; # LATIN SMALL LETTER EZH WITH TAIL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01bb}/_/gi; # LATIN LETTER TWO WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01bc}/_/gi; # LATIN CAPITAL LETTER TONE FIVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01bd}/_/gi; # LATIN SMALL LETTER TONE FIVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01be}/_/gi; # LATIN LETTER INVERTED GLOTTAL STOP WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01bf}/_/gi; # LATIN LETTER WYNN
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01c0}/_/gi; # LATIN LETTER DENTAL CLICK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01c1}/_/gi; # LATIN LETTER LATERAL CLICK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01c2}/_/gi; # LATIN LETTER ALVEOLAR CLICK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01c3}/_/gi; # LATIN LETTER RETROFLEX CLICK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01c4}/_/gi; # LATIN CAPITAL LETTER DZ WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01c5}/_/gi; # LATIN CAPITAL LETTER D WITH SMALL LETTER Z WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01c6}/_/gi; # LATIN SMALL LETTER DZ WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01c7}/_/gi; # LATIN CAPITAL LETTER LJ
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01c8}/_/gi; # LATIN CAPITAL LETTER L WITH SMALL LETTER J
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01c9}/_/gi; # LATIN SMALL LETTER LJ
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ca}/_/gi; # LATIN CAPITAL LETTER NJ
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01cb}/_/gi; # LATIN CAPITAL LETTER N WITH SMALL LETTER J
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01cc}/_/gi; # LATIN SMALL LETTER NJ
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01cd}/_/gi; # LATIN CAPITAL LETTER A WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ce}/_/gi; # LATIN SMALL LETTER A WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01cf}/_/gi; # LATIN CAPITAL LETTER I WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01d0}/_/gi; # LATIN SMALL LETTER I WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01d1}/_/gi; # LATIN CAPITAL LETTER O WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01d2}/_/gi; # LATIN SMALL LETTER O WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01d3}/_/gi; # LATIN CAPITAL LETTER U WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01d4}/_/gi; # LATIN SMALL LETTER U WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01d5}/_/gi; # LATIN CAPITAL LETTER U WITH DIAERESIS AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01d6}/_/gi; # LATIN SMALL LETTER U WITH DIAERESIS AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01d7}/_/gi; # LATIN CAPITAL LETTER U WITH DIAERESIS AND ACUTE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01d8}/_/gi; # LATIN SMALL LETTER U WITH DIAERESIS AND ACUTE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01d9}/_/gi; # LATIN CAPITAL LETTER U WITH DIAERESIS AND CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01da}/_/gi; # LATIN SMALL LETTER U WITH DIAERESIS AND CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01db}/_/gi; # LATIN CAPITAL LETTER U WITH DIAERESIS AND GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01dc}/_/gi; # LATIN SMALL LETTER U WITH DIAERESIS AND GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01dd}/_/gi; # LATIN SMALL LETTER TURNED E
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01de}/_/gi; # LATIN CAPITAL LETTER A WITH DIAERESIS AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01df}/_/gi; # LATIN SMALL LETTER A WITH DIAERESIS AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01e0}/_/gi; # LATIN CAPITAL LETTER A WITH DOT ABOVE AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01e1}/_/gi; # LATIN SMALL LETTER A WITH DOT ABOVE AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01e2}/_/gi; # LATIN CAPITAL LETTER AE WITH MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01e3}/_/gi; # LATIN SMALL LETTER AE WITH MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01e4}/_/gi; # LATIN CAPITAL LETTER G WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01e5}/_/gi; # LATIN SMALL LETTER G WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01e6}/_/gi; # LATIN CAPITAL LETTER G WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01e7}/_/gi; # LATIN SMALL LETTER G WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01e8}/_/gi; # LATIN CAPITAL LETTER K WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01e9}/_/gi; # LATIN SMALL LETTER K WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ea}/_/gi; # LATIN CAPITAL LETTER O WITH OGONEK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01eb}/_/gi; # LATIN SMALL LETTER O WITH OGONEK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ec}/_/gi; # LATIN CAPITAL LETTER O WITH OGONEK AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ed}/_/gi; # LATIN SMALL LETTER O WITH OGONEK AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ee}/_/gi; # LATIN CAPITAL LETTER EZH WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ef}/_/gi; # LATIN SMALL LETTER EZH WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01f0}/_/gi; # LATIN SMALL LETTER J WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01f1}/_/gi; # LATIN CAPITAL LETTER DZ
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01f2}/_/gi; # LATIN CAPITAL LETTER D WITH SMALL LETTER Z
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01f3}/_/gi; # LATIN SMALL LETTER DZ
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01f4}/_/gi; # LATIN CAPITAL LETTER G WITH ACUTE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01f5}/_/gi; # LATIN SMALL LETTER G WITH ACUTE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01f6}/_/gi; # LATIN CAPITAL LETTER HWAIR
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01f7}/_/gi; # LATIN CAPITAL LETTER WYNN
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01f8}/_/gi; # LATIN CAPITAL LETTER N WITH GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01f9}/_/gi; # LATIN SMALL LETTER N WITH GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01fa}/_/gi; # LATIN CAPITAL LETTER A WITH RING ABOVE AND ACUTE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01fb}/_/gi; # LATIN SMALL LETTER A WITH RING ABOVE AND ACUTE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01fc}/_/gi; # LATIN CAPITAL LETTER AE WITH ACUTE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01fd}/_/gi; # LATIN SMALL LETTER AE WITH ACUTE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01fe}/_/gi; # LATIN CAPITAL LETTER O WITH STROKE AND ACUTE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{01ff}/_/gi; # LATIN SMALL LETTER O WITH STROKE AND ACUTE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0200}/_/gi; # LATIN CAPITAL LETTER A WITH DOUBLE GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0201}/_/gi; # LATIN SMALL LETTER A WITH DOUBLE GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0202}/_/gi; # LATIN CAPITAL LETTER A WITH INVERTED BREVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0203}/_/gi; # LATIN SMALL LETTER A WITH INVERTED BREVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0204}/_/gi; # LATIN CAPITAL LETTER E WITH DOUBLE GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0205}/_/gi; # LATIN SMALL LETTER E WITH DOUBLE GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0206}/_/gi; # LATIN CAPITAL LETTER E WITH INVERTED BREVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0207}/_/gi; # LATIN SMALL LETTER E WITH INVERTED BREVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0208}/_/gi; # LATIN CAPITAL LETTER I WITH DOUBLE GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0209}/_/gi; # LATIN SMALL LETTER I WITH DOUBLE GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{020a}/_/gi; # LATIN CAPITAL LETTER I WITH INVERTED BREVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{020b}/_/gi; # LATIN SMALL LETTER I WITH INVERTED BREVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{020c}/_/gi; # LATIN CAPITAL LETTER O WITH DOUBLE GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{020d}/_/gi; # LATIN SMALL LETTER O WITH DOUBLE GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{020e}/_/gi; # LATIN CAPITAL LETTER O WITH INVERTED BREVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{020f}/_/gi; # LATIN SMALL LETTER O WITH INVERTED BREVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0210}/_/gi; # LATIN CAPITAL LETTER R WITH DOUBLE GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0211}/_/gi; # LATIN SMALL LETTER R WITH DOUBLE GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0212}/_/gi; # LATIN CAPITAL LETTER R WITH INVERTED BREVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0213}/_/gi; # LATIN SMALL LETTER R WITH INVERTED BREVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0214}/_/gi; # LATIN CAPITAL LETTER U WITH DOUBLE GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0215}/_/gi; # LATIN SMALL LETTER U WITH DOUBLE GRAVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0216}/_/gi; # LATIN CAPITAL LETTER U WITH INVERTED BREVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0217}/_/gi; # LATIN SMALL LETTER U WITH INVERTED BREVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0218}/_/gi; # LATIN CAPITAL LETTER S WITH COMMA BELOW
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0219}/_/gi; # LATIN SMALL LETTER S WITH COMMA BELOW
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{021a}/_/gi; # LATIN CAPITAL LETTER T WITH COMMA BELOW
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{021b}/_/gi; # LATIN SMALL LETTER T WITH COMMA BELOW
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{021c}/_/gi; # LATIN CAPITAL LETTER YOGH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{021d}/_/gi; # LATIN SMALL LETTER YOGH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{021e}/_/gi; # LATIN CAPITAL LETTER H WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{021f}/_/gi; # LATIN SMALL LETTER H WITH CARON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0220}/_/gi; # LATIN CAPITAL LETTER N WITH LONG RIGHT LEG
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0221}/_/gi; # LATIN SMALL LETTER D WITH CURL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0222}/_/gi; # LATIN CAPITAL LETTER OU
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0223}/_/gi; # LATIN SMALL LETTER OU
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0224}/_/gi; # LATIN CAPITAL LETTER Z WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0225}/_/gi; # LATIN SMALL LETTER Z WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0226}/_/gi; # LATIN CAPITAL LETTER A WITH DOT ABOVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0227}/_/gi; # LATIN SMALL LETTER A WITH DOT ABOVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0228}/_/gi; # LATIN CAPITAL LETTER E WITH CEDILLA
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0229}/_/gi; # LATIN SMALL LETTER E WITH CEDILLA
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{022a}/_/gi; # LATIN CAPITAL LETTER O WITH DIAERESIS AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{022b}/_/gi; # LATIN SMALL LETTER O WITH DIAERESIS AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{022c}/_/gi; # LATIN CAPITAL LETTER O WITH TILDE AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{022d}/_/gi; # LATIN SMALL LETTER O WITH TILDE AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{022e}/_/gi; # LATIN CAPITAL LETTER O WITH DOT ABOVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{022f}/_/gi; # LATIN SMALL LETTER O WITH DOT ABOVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0230}/_/gi; # LATIN CAPITAL LETTER O WITH DOT ABOVE AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0231}/_/gi; # LATIN SMALL LETTER O WITH DOT ABOVE AND MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0232}/_/gi; # LATIN CAPITAL LETTER Y WITH MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0233}/_/gi; # LATIN SMALL LETTER Y WITH MACRON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0234}/_/gi; # LATIN SMALL LETTER L WITH CURL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0235}/_/gi; # LATIN SMALL LETTER N WITH CURL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0236}/_/gi; # LATIN SMALL LETTER T WITH CURL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0237}/_/gi; # LATIN SMALL LETTER DOTLESS J
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0238}/_/gi; # LATIN SMALL LETTER DB DIGRAPH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0239}/_/gi; # LATIN SMALL LETTER QP DIGRAPH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{023a}/_/gi; # LATIN CAPITAL LETTER A WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{023b}/_/gi; # LATIN CAPITAL LETTER C WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{023c}/_/gi; # LATIN SMALL LETTER C WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{023d}/_/gi; # LATIN CAPITAL LETTER L WITH BAR
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{023e}/_/gi; # LATIN CAPITAL LETTER T WITH DIAGONAL STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{023f}/_/gi; # LATIN SMALL LETTER S WITH SWASH TAIL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0240}/_/gi; # LATIN SMALL LETTER Z WITH SWASH TAIL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0241}/_/gi; # LATIN CAPITAL LETTER GLOTTAL STOP
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0242}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0243}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0244}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0245}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0246}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0247}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0248}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0249}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{024a}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{024b}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{024c}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{024d}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{024e}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{024f}/_/gi; # 
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0250}/_/gi; # LATIN SMALL LETTER TURNED A
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0251}/_/gi; # LATIN SMALL LETTER ALPHA
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0252}/_/gi; # LATIN SMALL LETTER TURNED ALPHA
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0253}/_/gi; # LATIN SMALL LETTER B WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0254}/_/gi; # LATIN SMALL LETTER OPEN O
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0255}/_/gi; # LATIN SMALL LETTER C WITH CURL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0256}/_/gi; # LATIN SMALL LETTER D WITH TAIL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0257}/_/gi; # LATIN SMALL LETTER D WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0258}/_/gi; # LATIN SMALL LETTER REVERSED E
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0259}/_/gi; # LATIN SMALL LETTER SCHWA
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{025a}/_/gi; # LATIN SMALL LETTER SCHWA WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{025b}/_/gi; # LATIN SMALL LETTER OPEN E
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{025c}/_/gi; # LATIN SMALL LETTER REVERSED OPEN E
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{025d}/_/gi; # LATIN SMALL LETTER REVERSED OPEN E WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{025e}/_/gi; # LATIN SMALL LETTER CLOSED REVERSED OPEN E
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{025f}/_/gi; # LATIN SMALL LETTER DOTLESS J WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0260}/_/gi; # LATIN SMALL LETTER G WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0261}/_/gi; # LATIN SMALL LETTER SCRIPT G
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0262}/_/gi; # LATIN LETTER SMALL CAPITAL G
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0263}/_/gi; # LATIN SMALL LETTER GAMMA
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0264}/_/gi; # LATIN SMALL LETTER RAMS HORN
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0265}/_/gi; # LATIN SMALL LETTER TURNED H
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0266}/_/gi; # LATIN SMALL LETTER H WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0267}/_/gi; # LATIN SMALL LETTER HENG WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0268}/_/gi; # LATIN SMALL LETTER I WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0269}/_/gi; # LATIN SMALL LETTER IOTA
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{026a}/_/gi; # LATIN LETTER SMALL CAPITAL I
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{026b}/_/gi; # LATIN SMALL LETTER L WITH MIDDLE TILDE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{026c}/_/gi; # LATIN SMALL LETTER L WITH BELT
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{026d}/_/gi; # LATIN SMALL LETTER L WITH RETROFLEX HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{026e}/_/gi; # LATIN SMALL LETTER LEZH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{026f}/_/gi; # LATIN SMALL LETTER TURNED M
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0270}/_/gi; # LATIN SMALL LETTER TURNED M WITH LONG LEG
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0271}/_/gi; # LATIN SMALL LETTER M WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0272}/_/gi; # LATIN SMALL LETTER N WITH LEFT HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0273}/_/gi; # LATIN SMALL LETTER N WITH RETROFLEX HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0274}/_/gi; # LATIN LETTER SMALL CAPITAL N
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0275}/_/gi; # LATIN SMALL LETTER BARRED O
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0276}/_/gi; # LATIN LETTER SMALL CAPITAL OE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0277}/_/gi; # LATIN SMALL LETTER CLOSED OMEGA
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0278}/_/gi; # LATIN SMALL LETTER PHI
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0279}/_/gi; # LATIN SMALL LETTER TURNED R
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{027a}/_/gi; # LATIN SMALL LETTER TURNED R WITH LONG LEG
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{027b}/_/gi; # LATIN SMALL LETTER TURNED R WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{027c}/_/gi; # LATIN SMALL LETTER R WITH LONG LEG
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{027d}/_/gi; # LATIN SMALL LETTER R WITH TAIL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{027e}/_/gi; # LATIN SMALL LETTER R WITH FISHHOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{027f}/_/gi; # LATIN SMALL LETTER REVERSED R WITH FISHHOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0280}/_/gi; # LATIN LETTER SMALL CAPITAL R
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0281}/_/gi; # LATIN LETTER SMALL CAPITAL INVERTED R
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0282}/_/gi; # LATIN SMALL LETTER S WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0283}/_/gi; # LATIN SMALL LETTER ESH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0284}/_/gi; # LATIN SMALL LETTER DOTLESS J WITH STROKE AND HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0285}/_/gi; # LATIN SMALL LETTER SQUAT REVERSED ESH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0286}/_/gi; # LATIN SMALL LETTER ESH WITH CURL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0287}/_/gi; # LATIN SMALL LETTER TURNED T
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0288}/_/gi; # LATIN SMALL LETTER T WITH RETROFLEX HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0289}/_/gi; # LATIN SMALL LETTER U BAR
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{028a}/_/gi; # LATIN SMALL LETTER UPSILON
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{028b}/_/gi; # LATIN SMALL LETTER V WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{028c}/_/gi; # LATIN SMALL LETTER TURNED V
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{028d}/_/gi; # LATIN SMALL LETTER TURNED W
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{028e}/_/gi; # LATIN SMALL LETTER TURNED Y
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{028f}/_/gi; # LATIN LETTER SMALL CAPITAL Y
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0290}/_/gi; # LATIN SMALL LETTER Z WITH RETROFLEX HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0291}/_/gi; # LATIN SMALL LETTER Z WITH CURL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0292}/_/gi; # LATIN SMALL LETTER EZH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0293}/_/gi; # LATIN SMALL LETTER EZH WITH CURL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0294}/_/gi; # LATIN LETTER GLOTTAL STOP
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0295}/_/gi; # LATIN LETTER PHARYNGEAL VOICED FRICATIVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0296}/_/gi; # LATIN LETTER INVERTED GLOTTAL STOP
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0297}/_/gi; # LATIN LETTER STRETCHED C
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0298}/_/gi; # LATIN LETTER BILABIAL CLICK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{0299}/_/gi; # LATIN LETTER SMALL CAPITAL B
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{029a}/_/gi; # LATIN SMALL LETTER CLOSED OPEN E
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{029b}/_/gi; # LATIN LETTER SMALL CAPITAL G WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{029c}/_/gi; # LATIN LETTER SMALL CAPITAL H
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{029d}/_/gi; # LATIN SMALL LETTER J WITH CROSSED-TAIL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{029e}/_/gi; # LATIN SMALL LETTER TURNED K
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{029f}/_/gi; # LATIN LETTER SMALL CAPITAL L
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02a0}/_/gi; # LATIN SMALL LETTER Q WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02a1}/_/gi; # LATIN LETTER GLOTTAL STOP WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02a2}/_/gi; # LATIN LETTER REVERSED GLOTTAL STOP WITH STROKE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02a3}/_/gi; # LATIN SMALL LETTER DZ DIGRAPH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02a4}/_/gi; # LATIN SMALL LETTER DEZH DIGRAPH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02a5}/_/gi; # LATIN SMALL LETTER DZ DIGRAPH WITH CURL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02a6}/_/gi; # LATIN SMALL LETTER TS DIGRAPH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02a7}/_/gi; # LATIN SMALL LETTER TESH DIGRAPH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02a8}/_/gi; # LATIN SMALL LETTER TC DIGRAPH WITH CURL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02a9}/_/gi; # LATIN SMALL LETTER FENG DIGRAPH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02aa}/_/gi; # LATIN SMALL LETTER LS DIGRAPH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02ab}/_/gi; # LATIN SMALL LETTER LZ DIGRAPH
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02ac}/_/gi; # LATIN LETTER BILABIAL PERCUSSIVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02ad}/_/gi; # LATIN LETTER BIDENTAL PERCUSSIVE
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02ae}/_/gi; # LATIN SMALL LETTER TURNED H WITH FISHHOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02af}/_/gi; # LATIN SMALL LETTER TURNED H WITH FISHHOOK AND TAIL
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02b0}/_/gi; # MODIFIER LETTER SMALL H
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02b1}/_/gi; # MODIFIER LETTER SMALL H WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02b2}/_/gi; # MODIFIER LETTER SMALL J
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02b3}/_/gi; # MODIFIER LETTER SMALL R
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02b4}/_/gi; # MODIFIER LETTER SMALL TURNED R
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02b5}/_/gi; # MODIFIER LETTER SMALL TURNED R WITH HOOK
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02b6}/_/gi; # MODIFIER LETTER SMALL CAPITAL INVERTED R
    # $basecards_hash->{$id}->{filing_name} =~ s/\x{02b7}/_/gi; # MODIFIER LETTER SMALL W


	# Rule 3 - Order of fields with identical leading elements
	#
	# does not apply

	# Rule 4 - Place names
	#
	# does not apply

	# Rule 5 - Identical filing entries
	#
	# Interpretted as meaning do them in some other respectible order,
	# which I would use multiverse id for. However, since I am only
	# concerned with base cards at this time, muid does not exist. So
	# no-op.

	# Rule 6 - Abbreviations. File abbreviations exactly as written.
	#
	# No-op

	# Rule 7 - Trreat bracketed data as signifcant
	#
	# No-op

	# Rule 8 - Hyphenated words.
	# 
	# Treat words connected by a hyphen as separate words, regardless of
	# language.
	$basecards_hash->{$id}->{filing_name} =~ s/-/ /gi; # dash
	$basecards_hash->{$id}->{filing_name} =~ s/\x{2013}/ /gi; # endash
	$basecards_hash->{$id}->{filing_name} =~ s/\x{2014}/ /gi; # emdash

	# Rule 9 and 10 - Initial articles.
	#
	# Don't include them at the start of a title, unless it is a
	# person or place. We will assume that all Cards are of a
	# Person or Place (although this isn't quite true).
	#$basecards_hash->{$id}->{filing_name} =~ s/^a //gi;
	#$basecards_hash->{$id}->{filing_name} =~ s/^an //gi; # dash
	#$basecards_hash->{$id}->{filing_name} =~ s/^ye //gi; # dash
	#$basecards_hash->{$id}->{filing_name} =~ s/^de //gi; # dash
	#$basecards_hash->{$id}->{filing_name} =~ s/^d'//gi; # dash

	# Rule 11 - Initials and acronyms
	# 
	# Essentially, make periods and ellipses into spaces
	$basecards_hash->{$id}->{filing_name} =~ s/\./ /gi; # dash
	$basecards_hash->{$id}->{filing_name} =~ s/\x{2026}/ /gi; # emdash

	# Rule 12 - Names with a prefix. Treat a prefix that is part of a
	# name or place as a separate word unless it is joined to the rest
	# of the name directly or by an apostrophe without a space. File 
	# letter by letter. 
	$basecards_hash->{$id}->{filing_name} =~ s/([a-z])'([a-z])/\1\2/gi;

	# Rule 12
	#
	# No op

	# Rule 13
	#
	# Not taking action on roman numeral interpretation as arabic

	# Rule 16  - Ignore all symbols except for "&"
	# 
	# Putting this rule before Rule 14 since comma can be used in nmbers and it is easier to process this first.

	foreach my $symb (@ignored_punctuation) {
		$basecards_hash->{$id}->{filing_name} =~ s/\Q$symb//ge;
	}
	$basecards_hash->{$id}->{filing_name} =~ s/\s+/ /gi;

	# Rule 14 - Numerals
	# 
	# Complicated, since there could be unknown number of digits. Assuming 9 digits
	
	# if it starts with a number, let's fix that number.
	$basecards_hash->{$id}->{filing_name} =~ s/^([\d,]+)/$aaa->('',$1)/gie;
	# if there is a number in the middle, let's fix it
	$basecards_hash->{$id}->{filing_name} =~ s/([^\.\d])([\d,]+)/$aaa->($1,$2)/gie;
}


# Now that we have all of the names fixed, let's jam them back in.
#print Dumper($basecards_hash);
foreach my $id (keys %{$basecards_hash} ) {
	eval {
		my $updateSQL = 'UPDATE basecard SET filing_name = ? WHERE id = ?';
		my $sth = $dbh->prepare($updateSQL);
		$sth->execute(
			$basecards_hash->{$id}->{filing_name},
			$id
		);
	}
	#if ($@) {
	#	print "!!!!!! Database Error! Card follows...\n";
	#	print " Error is " . $@ . "\n";
	#	print Dumper($basecards_hash->{$id});
	#}
}



#for (my $g = 0x00c0; $g < 0x02b8; $g++) {
#	print '    $basecards_hash->{$id}->{filing_name} =~ s/\x{' . sprintf('%0.4x', $g) . '}/_/gi; # ' , uname($g), "\n";
#}
