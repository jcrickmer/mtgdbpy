from django.core.management.base import BaseCommand, CommandError
from mtgdbapp.models import CardRating
from mtgdbapp.models import Battle
from mtgdbapp.models import BattleTest
from mtgdbapp.models import Format
from mtgdbapp.models import FormatBasecard
from mtgdbapp.models import PhysicalCard
from mtgdbapp.models import BaseCard

import logging

from trueskill import TrueSkill, Rating, quality_1vs1, rate_1vs1

class Command(BaseCommand):
    #args = '<poll_id poll_id ...>'
    help = 'Updates all CardRatings based on all Battles.'

    def handle(self, *args, **options):
		#logger = logging.getLogger(__name__)

		ts = TrueSkill(backend='mpmath')

		# Get all of our tests.
		tests = BattleTest.objects.all()

		# iterate through each test
		for test in tests:
			# get all of the formats
			formats = Format.objects.all()

			# iterate through each format
			for format in formats:
				# REVISIT - forcing format 4
				if format.id != 4:
					continue

 				# Let's get all of the battles that have taken place. After the
				# initial run of this for a given format and test, this will be
				# the normal path.
				battles = Battle.objects.filter(test__id__exact=test.id, format__id__exact=format.id)#, winner_pcard__id__in=[1381, 933, 2059])

				# IN THE FUTURE... when we have more data than we know what to
				# do with, this is where we would probably want to load the
				# cards' existing ratings and work from there.
				
				card_ratings = {}
				for battle in battles:
					card_a = None
					card_b = None
					try:
						card_a = card_ratings[str(battle.winner_pcard.id)]
					except KeyError:
						card_a = Rating()
						card_ratings[str(battle.winner_pcard.id)] = card_a

					try:
						card_b = card_ratings[str(battle.loser_pcard.id)]
					except KeyError:
						card_b = Rating()
						card_ratings[str(battle.loser_pcard.id)] = card_b

					# calculate!
					card_ratings[str(battle.winner_pcard.id)], card_ratings[str(battle.loser_pcard.id)] = rate_1vs1(card_a, card_b, env=ts)

				#self.stdout.write("all " + str(card_ratings))

				# But wait? What about all of those cards not yet rated?!
				# iterate through all cards in that format
				fbcards = FormatBasecard.objects.filter(format=format.id)
				for fbcard in fbcards:
					pcard = fbcard.basecard.physicalcard
					try:
						card_rating = card_ratings[str(pcard.id)]
						# if we got here, then we already have a
						# rating for the card.
 					except KeyError:
						# Oops. No rating yet.
						card_ratings[str(pcard.id)] = Rating()

				# Ok, now all of the cards have a ratings object from
				# trueskill. So, let's get it update in the database!
				for pcard_id in card_ratings:
					card_rating = card_ratings[pcard_id]
					cardratings_db = CardRating.objects.filter(physicalcard__id__exact=pcard_id, test__id__exact=test.id, format__id__exact=format.id)
					# this should be a singleton. get the first (and only
					# row). If it isn't there then we need to create a new object.
					cr_db = None
					try:
						cr_db = cardratings_db[0]
					except IndexError:
						# not in the db. Let's start fresh!
						cr_db = CardRating()
						cr_db.physicalcard = PhysicalCard.objects.get(pk=int(pcard_id))
						cr_db.test = test
						cr_db.format = format

					cr_db.mu = card_rating.mu;
					cr_db.sigma = card_rating.sigma;
					cr_db.save()
						
			#self.stdout.write('Successfully closed poll "%s"' % poll_id)
