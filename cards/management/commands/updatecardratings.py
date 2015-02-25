from django.core.management.base import BaseCommand, CommandError
from cards.models import CardRating
from cards.models import Battle
from cards.models import BattleTest
from cards.models import Format
from cards.models import FormatBasecard
from cards.models import PhysicalCard
from cards.models import BaseCard

import logging

import datetime
from django.utils import timezone

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
                # Let's get all of the battles that have taken place. After the
                # initial run of this for a given format and test, this will be
                # the normal path.
                battles = Battle.objects.filter(
                    test__id__exact=test.id,
                    format__id__exact=format.id).order_by('battle_date')  # , winner_pcard__id__in=[1381, 933, 2059])

                # IN THE FUTURE... when we have more data than we know what to
                # do with, this is where we would probably want to load the
                # cards' existing ratings and work from there.

                card_battled = {}
                card_ratings = {}
                card_lmd = {}  # last modified dates of cards
                for battle in battles:
                    card_a = None
                    card_b = None
                    card_a_date = None
                    card_b_date = None
                    try:
                        card_a = card_ratings[str(battle.winner_pcard.id)]
                    except KeyError:
                        # let's try to get the rating from the database
                        crsdb = CardRating.objects.filter(
                            physicalcard__id__exact=battle.winner_pcard.id,
                            test__id__exact=test.id,
                            format__id__exact=format.id)
                        try:
                            crdb = crsdb[0]
                            card_a = Rating(mu=crdb.mu, sigma=crdb.sigma)
                            card_a_date = crdb.updated_at
                        except IndexError:
                            # ok, let's start fresh
                            card_a = Rating()

                        card_lmd[str(battle.winner_pcard.id)] = card_a_date
                        card_ratings[str(battle.winner_pcard.id)] = card_a

                    try:
                        card_b = card_ratings[str(battle.loser_pcard.id)]
                    except KeyError:
                        # let's try to get the rating from the database
                        crsdb = CardRating.objects.filter(
                            physicalcard__id__exact=battle.loser_pcard.id,
                            test__id__exact=test.id,
                            format__id__exact=format.id)
                        try:
                            crdb = crsdb[0]
                            card_b = Rating(mu=crdb.mu, sigma=crdb.sigma)
                            card_b_date = crdb.updated_at
                        except IndexError:
                            # ok, let's start fresh
                            card_b = Rating()

                        card_lmd[str(battle.loser_pcard.id)] = card_b_date
                        card_ratings[str(battle.loser_pcard.id)] = card_b

                    # calculate!
                    if card_lmd[str(battle.winner_pcard.id)] is None or card_lmd[
                            str(battle.winner_pcard.id)] < battle.battle_date:
                        self.stdout.write(
                            "format {}: updating battles for cards {} and {}".format(
                                str(
                                    format.id), str(
                                    battle.winner_pcard.id), str(
                                    battle.loser_pcard.id)))
                        card_ratings[str(battle.winner_pcard.id)], card_ratings[
                            str(battle.loser_pcard.id)] = rate_1vs1(card_a, card_b, env=ts)
                        card_battled[str(battle.winner_pcard.id)] = True
                        card_battled[str(battle.loser_pcard.id)] = True

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
                    cardratings_db = CardRating.objects.filter(
                        physicalcard__id__exact=pcard_id,
                        test__id__exact=test.id,
                        format__id__exact=format.id)
                    # this should be a singleton. get the first (and only
                    # row). If it isn't there then we need to create a new
                    # object.
                    cr_db = None
                    try:
                        cr_db = cardratings_db[0]
                    except IndexError:
                        # not in the db. Let's start fresh!
                        cr_db = CardRating()
                        cr_db.physicalcard = PhysicalCard.objects.get(
                            pk=int(pcard_id))
                        cr_db.test = test
                        cr_db.format = format
                        card_lmd[str(pcard_id)] = timezone.now()
                        card_battled[str(pcard_id)] = True

                    if str(pcard_id) in card_battled and card_battled[
                            str(pcard_id)]:
                        cr_db.mu = card_rating.mu
                        cr_db.sigma = card_rating.sigma
                        self.stdout.write("format {}: saving to db pcard_id {}".format(str(format.id), str(pcard_id)))
                        cr_db.save()
