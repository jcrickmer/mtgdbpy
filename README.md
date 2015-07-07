mtgdbpy
=======

mtgdbpy

You will need to get the right schema into the Solr install. Just using the out-of-the-box example configuration for Solr:
./manage.py build_solr_schema > ../solr/solr-4.10.3/example/solr/collection1/conf/schema.xml 
./manage.py rebuild_index


For Better Battles, create a file with te format id in it called 'betterbattle_{id}.csv'. It should have 1 column of physicalcard.id numbers.

To get it from tournamentdecks in the database:

    echo "SELECT DISTINCT(dc.physicalcard_id) FROM deckcard dc JOIN tournamentdeck td ON td.deck_id = dc.deck_id JOIN tournament t ON t.id = td.tournament_id WHERE t.format_id = 21 AND t.start_date > '2014-12-20';" | mysql -u root -p mtgdbpy > /opt/mtgdb/betterbattle_21.csv

Or, create a file with card names and run this:

    ./manage.py getphysicalcardid < tinyleader_cards.txt | sort | uniq > betterbattle_19.csv
