#!/usr/bin/perl -CS

use strict;
use utf8;
#use diagnostics;
use JSON::XS;
use DBI;
use Data::Dumper;
#use MTG::Util qw(makeFilingName);

my $dbh = DBI->connect('DBI:mysql:mtgdb','root','godzilla', {RaiseError=>1, PrintError=>0}) || die "Could not connect to database: $DBI::errstr";
$dbh->{'mysql_enable_utf8'} = 1;
$dbh->do(qq{SET NAMES 'utf8';});

my $prefix = 'http://spellbook.patsgames.com/cards/';

my $color_slang = {'white'=>['white'],
		   'blue'=>['blue'],
		   'black'=>['black'],
		   'red'=>['red'],
		   'green'=>['green'],
		   'azorius'=>['white','blue'],
		   'orzhov'=>['white','black'],
		   'boros'=>['white','red'],
		   'selesnya'=>['white','green'],
		   'dimir'=>['blue','black'],
		   'izzet'=>['blue','red'],
		   'simic'=>['blue','green'],
		   'rakdos'=>['black','red'],
		   'golgari'=>['black','green'],
		   'gruul'=>['red','green'],
		   'esper'=>['white','blue','black'],
		   'jeskai'=>['white','blue','red'],
		   'bant'=>['white','blue','green'],
		   'grixis'=>['blue','black','red'],
		   'sultai'=>['blue','black','green'],
		   'jund'=>['black','red','green'],
		   'mardu'=>['black','red','white'],
		   'naya'=>['red','green','white'],
		   'temur'=>['red','green','blue'],
		   'abzan'=>['green','white','black'],
           'artifice'=>['white','blue','black','red'],
           'chaos'=>['blue','black','red','green'],
           'aggression'=>['black','red','greem','white'],
           'altruism'=>['red','green','white','blue'],
           'growth'=>['green','white','blue','black'],
           'fivecolor'=>['white','blue','black','red','green'],
		  };

my $result;
eval {
        my $selectSQL = "SELECT MIN(c.multiverseid), bc.filing_name FROM card AS c JOIN basecard AS bc ON c.basecard_id = bc.id WHERE bc.cardposition IN ('F','L','U') GROUP BY bc.physicalcard_id ORDER BY c.multiverseid DESC";
	#my $selectSQL = 'SELECT c.multiverseid, bc.filing_name FROM card AS c JOIN basecard AS bc ON c.basecard_id = bc.id ORDER BY c.multiverseid DESC';
	my $sth = $dbh->prepare($selectSQL);
	$sth->execute();
	$result = $sth->fetchall_arrayref();
};
if ($@) {
	die("Unable to load types: " . $@);
}

print '<?xml version="1.0" encoding="UTF-8"?>',"\n",
      '<?xml-stylesheet type="text/xsl" href="http://card.ninja/wp-content/plugins/google-sitemap-generator/sitemap.xsl"?><!-- sitemap-generator-url="http://www.arnebrachhold.de" sitemap-generator-version="4.0.8" -->',"\n",
      '<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',"\n";

foreach my $formatname (qw/commander standard legacy modern/) {
    print '  <url>',"\n";
    print '    <loc>',$prefix,'stats/' . $formatname . '/', '</loc>',"\n";
    print '    <changefreq>weekly</changefreq>',"\n";
    print '    <priority>0.9</priority>',"\n";
    print '  </url>',"\n";
}
foreach my $type (qw/commanders planeswalkers/) {
    foreach my $key (keys %$color_slang) {
	print '  <url>',"\n";
	print '    <loc>',$prefix,'search/' . join('-',@{$color_slang->{$key}}) . '-' . $type . '/', '</loc>',"\n";
	print '    <changefreq>monthly</changefreq>',"\n";
	print '    <priority>0.9</priority>',"\n";
	print '  </url>',"\n";
    }
}
foreach my $pair (@$result) {
	my $slug = $pair->[1];
	$slug =~ s/\s/-/gi;
	$slug =~ s/&/&amp;/gi;
	print '  <url>',"\n";
	print '    <loc>',$prefix,$pair->[0] . '-' . $slug . '/', '</loc>',"\n";
	print '    <changefreq>monthly</changefreq>',"\n";
	print '    <priority>0.9</priority>',"\n";
	print '  </url>',"\n";
}
print '</urlset>',"\n";
