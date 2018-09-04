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

my $baseurl = 'http://spellbook.patsgames.com/';
my $prefix = $baseurl . 'cards/';

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

my $counter = 0;

my $result;
my @entries = ();

push @entries, [$prefix, 'monthly'];
push @entries, [$prefix . 'battle/standard/', 'always'];
push @entries, [$prefix . 'battle/modern/', 'always'];
push @entries, [$prefix . 'battle/commander/', 'always'];
push @entries, [$prefix . 'battle/legacy/', 'always'];
push @entries, [$baseurl . 'decks/crafter/', 'always'];

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

foreach my $formatname (qw/commander standard legacy modern/) {
    my $eurl = $prefix . 'stats/' . $formatname . '/';
    push @entries, [$eurl, 'weekly'];
}
foreach my $type (qw/commanders planeswalkers/) {
    foreach my $key (keys %$color_slang) {
        my $eurl = $prefix . 'search/' . join('-',@{$color_slang->{$key}}) . '-' . $type . '/';
        push @entries, [$eurl, 'monthly'];
    }
}
foreach my $pair (@$result) {
    my $slug = $pair->[1];
    $slug =~ s/\s/-/gi;
    $slug =~ s/&/&amp;/gi;
    my $eurl = $prefix . $pair->[0] . '-' . $slug . '/';
    push @entries, [$eurl, 'monthly'];

    # And let's see if this is legal in any formats...
    my $f_sql = "SELECT f.formatname FROM card AS c JOIN formatbasecard AS fbc ON c.basecard_id = fbc.basecard_id JOIN format AS f ON fbc.format_id = f.id WHERE c.multiverseid = " . $pair->[0] . " AND f.end_date > NOW() GROUP BY f.formatname HAVING MAX(f.start_date)";
    my $fsth = $dbh->prepare($f_sql);
    $fsth->execute();
    my $formats = $fsth->fetchall_arrayref();
    foreach my $format_aref (@$formats) {
        my $ceurl = $eurl . $format_aref->[0] . '-company/';
        push @entries, [$ceurl, 'weekly'];
    }
}

my $MAX_SIZE = 25000;

open(my $fh, '>', 'sitemap.xml');
print $fh '<?xml version="1.0" encoding="UTF-8"?>',"\n";
print $fh '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',"\n";
for (my $scounter = 0; $scounter <= int (scalar(@entries) / $MAX_SIZE); $scounter++) {
    print $fh '  <sitemap>', "\n";
    print $fh '    <loc>' . $baseurl . 'sitemap'. $scounter . '.xml</loc>', "\n";
    print $fh '  </sitemap>', "\n";
}
print $fh '</sitemapindex>', "\n";
close $fh;

my $ecounter = 0;
for (my $scounter = 0; $scounter <= int (scalar(@entries) / $MAX_SIZE); $scounter++) {
    open(my $fh, '>', 'sitemap' . $scounter . '.xml');
    print $fh '<?xml version="1.0" encoding="UTF-8"?>',"\n";
    print $fh '<urlset xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.sitemaps.org/schemas/sitemap/0.9 http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd" xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',"\n";
    for ( ; $ecounter < scalar(@entries) && $ecounter < ($scounter + 1) * $MAX_SIZE; $ecounter++) {
        print $fh '  <url>' . "\n";
        print $fh '    <loc>' . $entries[$ecounter][0] . '</loc>' . "\n";
        print $fh '    <changefreq>' . $entries[$ecounter][1] . '</changefreq>' . "\n";
        print $fh '    <priority>0.9</priority>' . "\n";
        print $fh '  </url>' . "\n";
    }
    close $fh;
}
