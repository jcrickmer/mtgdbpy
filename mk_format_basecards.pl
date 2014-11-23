#!/usr/bin/perl
use strict;
use Data::Dumper;

my $foo = [
	{id=>1, formatname=>'Modern', format=>'Modern_2014-09-26', start_date=>'2014-09-26',
	 set=>['8ED','9ED','10E','M10','M11','M12','M13','M14','M15','MRD','DST','5DN','CSP','CHK','BOK','SOK','RAV','GPT','DIS','TSP','TSB','PLC','FUT','LRW','MOR','SHM','EVE','ALA','CON','ARB','ZEN','WWK','ROE','SOM','MBS','NPH','ISD','DKA','AVR','RTR','GTC','DGM','THS','BNG','JOU','KTK'],
	 banned=>["Ancestral Vision", "Ancient Den","Blazing Shoal","Bloodbraid Elf","Chrome Mox","Cloudpost","Dark Depths","Deathrite Shaman","Dread Return","Glimpse of Nature","Golgari Grave-Troll","Great Furnace","Green Sun's Zenith","Hypergenesis","Jace, the Mind Sculptor","Mental Misstep","Ponder","Preordain","Punishing Fire","Rite of Flame","Seat of the Synod","Second Sunrise","Seething Song","Sensei's Divining Top","Stoneforge Mystic","Skullclamp","Sword of the Meek","Tree of Tales","Umezawa's Jitte","Vault of Whispers"]},

	{id=>2, formatname=>'Modern', format=>'Modern_2014-07-18', start_date=>'2014-07-18', end_date=>'2014-09-25',
	 set=>['8ED','9ED','10E','M10','M11','M12','M13','M14','M15','MRD','DST','5DN','CSP','CHK','BOK','SOK','RAV','GPT','DIS','TSP','TSB','PLC','FUT','LRW','MOR','SHM','EVE','ALA','CON','ARB','ZEN','WWK','ROE','SOM','MBS','NPH','ISD','DKA','AVR','RTR','GTC','DGM','THS','BNG','JOU',],
	 banned=>["Ancestral Vision", "Ancient Den","Blazing Shoal","Bloodbraid Elf","Chrome Mox","Cloudpost","Dark Depths","Deathrite Shaman","Dread Return","Glimpse of Nature","Golgari Grave-Troll","Great Furnace","Green Sun's Zenith","Hypergenesis","Jace, the Mind Sculptor","Mental Misstep","Ponder","Preordain","Punishing Fire","Rite of Flame","Seat of the Synod","Second Sunrise","Seething Song","Sensei's Divining Top","Stoneforge Mystic","Skullclamp","Sword of the Meek","Tree of Tales","Umezawa's Jitte","Vault of Whispers"]},

	{id=>3, formatname=>'Modern', format=>'Modern_2014-05-02', start_date=>'2014-05-02', end_date=>'2014-07-17',
     set=>['8ED','9ED','10E','M10','M11','M12','M13','M14',      'MRD','DST','5DN','CSP','CHK','BOK','SOK','RAV','GPT','DIS','TSP','TSB','PLC','FUT','LRW','MOR','SHM','EVE','ALA','CON','ARB','ZEN','WWK','ROE','SOM','MBS','NPH','ISD','DKA','AVR','RTR','GTC','DGM','THS','BNG','JOU',],
	 banned=>['Ancestral Vision','Ancient Den','Blazing Shoal','Bloodbraid Elf','Chrome Mox','Cloudpost','Dark Depths','Deathrite Shaman','Dread Return','Glimpse of Nature','Golgari Grave-Troll','Great Furnace',"Green Sun's Zenith",'Hypergenesis','Jace, the Mind Sculptor','Mental Misstep','Ponder','Preordain','Punishing Fire','Rite of Flame','Seat of the Synod','Second Sunrise','Seething Song',"Sensei's Divining Top",'Stoneforge Mystic','Skullclamp','Sword of the Meek','Tree of Tales',"Umezawa's Jitte",'Vault of Whispers']},

	{id=>4, formatname=>'Standard', format=>'Standard_2014-09-26', start_date=>'2014-09-26',
	 set=>['M15','THS','BNG','JOU','KTK'],
 },
	{id=>5, formatname=>'Standard', format=>'Standard_2014-07-18', start_date=>'2014-07-18', end_date=>'2014-09-25',
	 set=>['M14','M15','RTR','GTC','DGM','THS','BNG','JOU'],
 },
	{id=>6, formatname=>'Standard', format=>'Standard_2014-05-02', start_date=>'2014-05-02', end_date=>'2014-07-17',
	 set=>['M14','RTR','GTC','DGM','THS','BNG','JOU'],
 },
	{id=>7, formatname=>'Standard', format=>'Standard_2014-02-07', start_date=>'2014-02-07', end_date=>'2014-05-01',
	 set=>['M14','RTR','GTC','DGM','THS','BNG'],
 },
	{id=>8, formatname=>'Standard', format=>'Standard_2013-09-27', start_date=>'2013-09-27', end_date=>'2014-02-06',
	 set=>['M14','RTR','GTC','DGM','THS'],
 },
	{id=>9, formatname=>'Standard', format=>'Standard_2013-07-19', start_date=>'2013-07-19', end_date=>'2013-09-26',
	 set=>['M13','M14','ISD','DKA','AVR','RTR','GTC','DGM'],
 },
	{id=>10, formatname=>'Standard', format=>'Standard_2013-05-03', start_date=>'2013-05-03', end_date=>'2013-07-18',
	 set=>['M13','ISD','DKA','AVR','RTR','GTC','DGM'],
 },
	{id=>11, formatname=>'Standard', format=>'Standard_2013-02-01', start_date=>'2013-02-01', end_date=>'2013-05-02',
	 set=>['M13','ISD','DKA','AVR','RTR','GTC'],
 },
	{id=>12, formatname=>'Standard', format=>'Standard_2012-10-05', start_date=>'2012-10-05', end_date=>'2013-01-31',
	 set=>['M13','ISD','DKA','AVR','RTR'],
 },
#	{id=>13, formatname=>'Commander', format=>'Commander_2014-11-07', start_date=>'2014-11-07',
# },
];

for (my $counter = 0; $counter < @$foo; $counter++) {
	my $set = $foo->[$counter];
	my $format_id = $counter + 1;
	print "INSERT IGNORE INTO mtgdbapp_format (id, formatname, format, start_date, end_date) VALUES (" . $format_id . ", '" . $set->{formatname} . "', '" . $set->{format} . "',";
	print " '" . $set->{start_date} . "',";
	if (defined $set->{end_date}) {
		print " '" . $set->{end_date} . "'";
	} else {
		print " NULL";
	}
	print ");\n";

	for (my $t = 0; $t < scalar @{$set->{set}} ; $t++) {
		print "INSERT IGNORE INTO mtgdbapp_formatbasecard (mtgdbapp_formatbasecard.format_id, mtgdbapp_formatbasecard.basecard_id) SELECT " . $format_id . ", basecard_id FROM cards, expansionsets WHERE cards.expansionset_id = expansionsets.id AND expansionsets.abbr = '" . $set->{set}->[$t] . "';\n"
	}
	if (defined $set->{banned}) {
		for (my $b = 0; $b < scalar @{$set->{banned}} ; $b++) {
			print "DELETE FROM mtgdbapp_formatbasecard WHERE format_id = " . $format_id . " AND basecard_id = (SELECT id FROM basecards WHERE name = '" . &quote($set->{banned}->[$b]) . "');\n";
		}
	}
}

sub quote() {
	my $val = shift;
	$val =~ s/'/\\'/g;
	return $val;
}
