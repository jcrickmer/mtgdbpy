mtgdbpy
=======

mtgdbpy

You will need to get the right schema into the Solr install. Just using the out-of-the-box example configuration for Solr:
./manage.py build_solr_schema > ../solr/solr-4.10.3/example/solr/collection1/conf/schema.xml 
./manage.py rebuild_index
