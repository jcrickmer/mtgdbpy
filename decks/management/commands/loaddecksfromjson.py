# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from decks.models import Deck
from decks.models import Tournament
from decks.models import TournamentDeck
from cards.models import Card
from cards.models import Format
from cards.models import PhysicalCard
#from decks.models import CardsNotFoundException
#from optparse import make_option

from datetime import datetime, timedelta

from cards.view_utils import convertSymbolsToHTML, make_links_to_cards

import codecs
import operator

import json
import re
import os
from os import listdir
from os.path import isfile, join

import sys
from kitchen.text.converters import getwriter
UTF8Writer = getwriter('utf8')
sys.stdout = UTF8Writer(sys.stdout)
UTF8Reader = codecs.getreader('utf8')
sys.stdin = UTF8Reader(sys.stdin)
import exceptions


class Command(BaseCommand):
    help = '''Load up some JSON and add it to the database, if needed.'''

    def handle(self, *args, **options):
        #logger = logging.getLogger(__name__)
        # the first (and only) arg should be a filename
        if len(args) < 1:
            sys.stderr.write("No directory name given.\n")
            return
        directory = args[0]
        if not os.access(directory, os.R_OK):
            sys.stderr.write("Cannot read directory '{}'.\n".format(filename))
            return

        onlyfiles = [f for f in listdir(directory) if isfile(join(directory, f))]
        for filename in onlyfiles:
            if filename.find('tournament_') > -1:  # and False: # REVISIT - commented out for the moment!
                filehandler = open(join(directory, filename))
                jblob = json.load(filehandler)
                #{"url": "/en/content/2011-great-britain-national-championship", "tournament_format": null, "name": "Great Britain National Championship", "tournament_date": "2011-08-19"}
                turl = jblob['url']
                if turl.find('http') < 0:
                    turl = 'http://magic.wizards.com' + turl
                format_string = jblob['tournament_format']
                if format_string is None:
                    format_string = 'Unknown'
                db_format = Format.objects.filter(
                    formatname=format_string,
                    start_date__lte=jblob['tournament_date'],
                    end_date__gte=jblob['tournament_date']).first()
                if db_format is not None:
                    db_tournament = Tournament.objects.filter(
                        format=db_format,
                        name=jblob['name'],
                        start_date=jblob['tournament_date']).first()
                    if db_tournament is None:
                        # let's make one!
                        db_tournament = Tournament(format=db_format, name=jblob['name'], start_date=jblob['tournament_date'], url=turl)
                        db_tournament.save()
                        sys.stdout.write("Tournament: created {}\n".format(jblob['name']))
                    else:
                        if turl.find('/node/') < 0:
                            db_tournament.url = turl
                            sys.stdout.write("Tournament: updated {}\n".format(jblob['name']))
                            db_tournament.save()
                        else:
                            sys.stdout.write("Tournament: skipped updated with node {}\n".format(jblob['name']))
                else:
                    sys.stdout.write("Tournament: skipped no format found in db {}\n".format(jblob['name']))

        tournament_url_re = re.compile('^(.+/coverage/([^/]+))/?')
        for filename in onlyfiles:
            if filename.find('deck_') > -1:
                filehandler = open(join(directory, filename))
                jblob = json.load(filehandler)

                # let's test if jblob is a set JSON
                if 'name' in jblob and 'mainboard_cards' in jblob:
                    # We are going to skip decks and tournaments that look like draft and sealed
                    if jblob['tournament_url'].find('draft') > 0 or jblob['tournament_url'].find('sealed') > 0:
                        # skip
                        sys.stdout.write("Deck: skipped limited {}\n".format(jblob['name']))
                        continue

                    # now find the tournament
                    tu_match = tournament_url_re.search(jblob['tournament_url'])
                    tournament_url = jblob['tournament_url']
                    tournament_name = ''
                    if tu_match:
                        tournament_url = tu_match.group(1)
                        tournament_name = tu_match.group(2)
                    # find a real tournament that we match to
                    tourna = Tournament.objects.filter(url=tournament_url).exclude(format__formatname='Unknown').first()
                    if tourna is not None:
                        # let's see if we already have a deck for this
                        deck = Deck.objects.filter(url=jblob['url']).first()
                        if deck is None:
                            # no deck, so let's add it!
                            deck = Deck(url=jblob['url'], visibility=Deck.HIDDEN)
                            deck.name = jblob['name']
                            deck.authorname = jblob['author']
                            deck.format = tourna.format
                            deck.save()
                            sys.stdout.write("Deck: created {}\n".format(jblob['name']))
                            deck = Deck.objects.filter(url=jblob['url']).first()  # reload
                        else:
                            # for kicks, let's update name and authorname, since it could be that the
                            # scrapy crawler gets better at figuring those things out
                            deck.name = jblob['name']
                            deck.authorname = jblob['author']
                            deck.save()
                            sys.stdout.write("Deck: updated {}\n".format(jblob['name']))

                        #sys.stdout.write("Deck: {} (db card count {})\n".format(jblob['name'], deck.get_card_count()))
                        #sys.stdout.write("  URL: {}\n".format(jblob['url']))

                        # now we have to add cards to the deck...
                        cardtext = '\n'.join(jblob['mainboard_cards'])
                        cardtext = cardtext + '\nSB:' + '\nSB: '.join(jblob['sideboard_cards'])
                        #sys.stdout.write(cardtext + "\n")
                        # REVISIT - just updating them all for now. Shouldn't hurt since
                        # set_cards_from_text deletes all of the current card associations, right?
                        if deck.get_card_count() == 0 or True:
                            try:
                                deck.set_cards_from_text(cardtext)
                            except Deck.CardsNotFoundException as cnfe:
                                for g in cnfe.cnfes:
                                    try:
                                        sys.stdout.write("ERROR: Could not find card " + str(g.text) + " in file {}\n".format(filename))
                                    except UnicodeEncodeError:
                                        sys.stdout.write(
                                            "ERROR: Could not find card BUT I CAN'T TELL YOU ABOUT IT BECAUSE UNICODE IN PYTHON SUCKS in {}\n".format(filename))
                        # Now we will associate the deck to a tournament
                        td = TournamentDeck.objects.filter(deck=deck, tournament=tourna).first()
                        place = 99999
                        if 'place' in jblob:
                            place = jblob['place']
                        if td is None:
                            td = TournamentDeck(deck=deck, tournament=tourna, place=place)
                            td.save()
                            sys.stdout.write("TournamentDeck: created for {}\n".format(jblob['name']))
                            td = TournamentDeck.objects.filter(deck=deck, tournament=tourna).first()  # RELOAD
                        else:
                            td.place = place
                            td.save()
                            sys.stdout.write("TournamentDeck: updated for {}\n".format(jblob['name']))
                    else:
                        sys.stdout.write("Deck: skipped no valid tournament {}\n".format(jblob['name']))
