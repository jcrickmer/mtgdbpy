# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Max, Min, Count, Sum, Avg

from django.db import connection

import logging

from cards.models import PhysicalCard, Format
import re
import sys


class Tournament(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    url = models.CharField(max_length=500)
    format = models.ForeignKey('cards.Format')
    start_date = models.DateField(null=False, blank=False)

    def __unicode__(self):
        return 'Tournament {} ({}, {}) [{}]'.format(str(self.name), str(self.format.formatname), str(self.start_date), str(self.id))

    class Meta:
        managed = True
        db_table = 'tournament'


class Deck(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    url = models.CharField(max_length=500)
    VISIBLE = 'visible'
    HIDDEN = 'hidden'
    VISIBILITY_CHOICES = ((VISIBLE, 'visible'), (HIDDEN, 'hidden'))
    visibility = models.CharField(max_length=12, choices=VISIBILITY_CHOICES, default=VISIBLE)
    authorname = models.CharField(max_length=100)
    format = models.ForeignKey('cards.Format')
    cards = models.ManyToManyField(PhysicalCard, through='DeckCard')
    tournaments = models.ManyToManyField(Tournament, through='TournamentDeck', through_fields=('deck', 'tournament'))

    # Returns the total number of caxrds in this deck.
    def get_card_count(self):
        dcs = DeckCard.objects.filter(deck=self)
        result = 0
        for dc in dcs:
            result = result + dc.cardcount
        return result

    def is_legal(self):
        return True

    class CardNotFoundException():

        def __init__(self, text):
            self.text = text

        def __unicode__(self):
            return 'CardNotFoundException: "{}"'.format(str(self.text))

    class CardsNotFoundException():

        def __init__(self, cnfes):
            # a list of CardNotFoundExceptions
            self.cnfes = cnfes

        def __unicode__(self):
            return 'CardsNotFoundException: "{}"'.format(','.join(str(c) for c in self.cnfes))

    def set_cards_from_text(self, cardlist):
        '''Go through each line and try to determine what the card is
        and how many should be present. If there are no errors, then
        delete/replace all of the existing DeckCards with these new
        DeckCards.'''

        # Note that when matching the card name here we are getting everything but
        # a "+" or a "/". This will give us the first card in a double card like
        # Wear // Tear
        req = re.compile(r'^([Ss][Bb]:\s*)?((\d+)x?\s+)?([^\+/]+)', re.UNICODE)
        new_deckcards = list()
        exceptions = list()
        for line in cardlist.splitlines():
            is_sb = False
            card_count = 1
            line = line.strip().lower()
            line_match = req.match(line)
            if line_match:
                is_sb = line_match.group(1) or False
                card_count = line_match.group(3) or 1
                # getting close! Now let's see if it's a real card
                # Let's do some quick clean-up of the card name...
                card_name = line_match.group(4).strip()
                for sillyapos in [u'\u2019', r'\u2019', '\\' + 'u2019', u'’']:
                    card_name = card_name.replace(sillyapos, u"'")
                for sillydash in [u'–', u'—', u'‒', u'-']:
                    card_name = card_name.replace(sillydash, '-')
                card_name = self._fix_bad_spelling(card_name)
                pc = PhysicalCard.objects.filter(basecard__name__iexact=card_name).first()
                if pc is not None:
                    # winner!
                    board_t = DeckCard.MAIN
                    if is_sb:
                        board_t = DeckCard.SIDE
                    dc = DeckCard(deck=self, cardcount=card_count, physicalcard=pc, board=board_t)
                    new_deckcards.append(dc)
                else:
                    # throw an exception if we don't know it
                    ex = Deck.CardNotFoundException(line_match.group(4))
                    exceptions.append(ex)

        # if no exceptions, then clear current DeckCards and set the ones that we just parsed
        if len(exceptions) > 0:
            raise Deck.CardsNotFoundException(exceptions)
        else:
            DeckCard.objects.filter(deck=self).delete()
            for dc in new_deckcards:
                #sys.stderr.write("dc save: " + str(dc) + "\n")
                dc.save()

    def _fix_bad_spelling(self, cardname):
        fixes = {'aetherize': 'Ætherize',
                 'aetherling': 'Ætherling',
                 'aether spellbomb': 'Æther Spellbomb',
                 'aetherspouts': 'Ætherspouts',
                 'aether vial': 'Æther Vial',
                 'ajani, mentor of theros': 'Ajani, Mentor of Heroes',
                 'ajani, mentor to heroes': 'Ajani, Mentor of Heroes',
                 'arc lighting': 'Arc Lightning',
                 'back of nature': 'Back to Nature',
                 'blood mon': 'Blood Moon',
                 'bloodstained champion': 'Bloodsoaked Champion',
                 'brandle shot': 'Brindle Shoat',
                 'brimax, king of oreskos': 'Brimaz, King of Oreskos',
                 'brindle shoal': 'Brindle Shoat',
                 'brindlespout': 'Brindle Shoat',
                 'cascade bluff': 'Cascade Bluffs',
                 'chandra, pyromancer': 'Chandra, Pyromaster',
                 'chandra pyromaster': 'Chandra, Pyromaster',
                 'course of kruphix': 'Courser of Kruphix',
                 'coves of koilos': 'Caves of Koilos',
                 'crater\'s claw': 'Crater\'s Claws',
                 'dauthi merceneary': 'Dauthi Mercenary',
                 'death-head buzzard': 'Death\'s-Head Buzzard',
                 'destructive reverly': 'Destructive Revelry',
                 'disdainful stoke': 'Disdainful Stroke',
                 'disdainful strike': 'Disdainful Stroke',
                 'distinctive revelry': 'Destructive Revelry',
                 'dromoka\'scommand': 'Dromoka\'s Command',
                 'drowned in sorrow': 'Drown in Sorrow',
                 'drown in silence': 'Drown in Sorrow',
                 'drown on sorrow': 'Drown in Sorrow',
                 'elpseth, sun\'s champion': 'Elspeth, Sun\'s Champion',
                 'elspeth, knight errant': 'Elspeth, Knight-Errant',
                 'elspeth sun\'s champion': 'Elspeth, Sun\'s Champion',
                 'end hostility': 'End Hostilities',
                 'entomber exach': 'Entomber Exarch',
                 'erase in ice': 'Encase in Ice',
                 'fatal conflagration': 'Fated Conflagration',
                 'firedrinkner satyr': 'Firedrinker Satyr',
                 'flames of the bloodhand': 'Flames of the Blood Hand',
                 'fledling djinn': 'Fledgling Djinn',
                 'flowstown hellion': 'Flowstone Hellion',
                 'garruk, apex hunter': 'Garruk, Apex Predator',
                 'gideon jury': 'Gideon Jura',
                 'glare of heresey': 'Glare of Heresy',
                 'god\'s willing': 'Gods Willing',
                 'hornet\'s nest': 'Hornet Nest',
                 'inferno itan': 'Inferno Titan',
                 'jorubai, murk lurker': 'Jorubai Murk Lurker',
                 'karn, liberated': 'Karn Liberated',
                 'keranos, god of storm': 'Keranos, God of Storms',
                 'keranos, god of the storms': 'Keranos, God of Storms',
                 'laquatas\'s champion': 'Laquatus\'s Champion',
                 'lighting bolt': 'Lightning Bolt',
                 'lighting helix': 'Lightning Helix',
                 'liliana, vess': 'Liliana Vess',
                 'lilianna vess': 'Liliana Vess',
                 'lingeroing souls': 'Lingering Souls',
                 'manastery swiftspear': 'Monastery Swiftspear',
                 'mirran crusade': 'Mirran Crusader',
                 'mountains': 'Mountain',
                 'moutain': 'Mountain',
                 'nature\'s claw': 'Nature\'s Claim',
                 'nihil spellsbomb': 'Nihil Spellbomb',
                 'nissa worldwaker': 'Nissa, Worldwaker',
                 'nissa, world waker': 'Nissa, Worldwaker',
                 'paralyse': 'Paralyze',
                 'phraika, god of affliction': 'Pharika, God of Affliction',
                 'polukranos, world easter': 'Polukranos, World Eater',
                 'read in bones': 'Read the Bones',
                 'realm razor': 'Realm Razer',
                 'reclamation angel': 'Restoration Angel',
                 'repaer of the wilds': 'Reaper of the Wilds',
                 'sadnsteppe citadel': 'Sandsteppe Citadel',
                 'sarkhan, dragonspeaker': 'Sarkhan, the Dragonspeaker',
                 'sarkhan, the dragonspear': 'Sarkhan, the Dragonspeaker',
                 'satyr firedrinker': 'Firedrinker Satyr',
                 'scaling tarn': 'Scalding Tarn',
                 'seismic assulat': 'Seismic Assault',
                 'self-inflected wound': 'Self-Inflicted Wound',
                 'serum vision': 'Serum Visions',
                 'setessan tectics': 'Setessan Tactics',
                 'shief of the scale': 'Chief of the Scale',
                 'sidisi, blood tyrant': 'Sidisi, Brood Tyrant',
                 'simian grunt': 'Simian Grunts',
                 'soldier of pantheon': 'Soldier of the Pantheon',
                 'sorin, solemn visiot': 'Sorin, Solemn Visitor',
                 'sorin, solemn visistor': 'Sorin, Solemn Visitor',
                 'sorin solemn visitor': 'Sorin, Solemn Visitor',
                 'stirring wildwoods': 'Stirring Wildwood',
                 'swansong': 'Swan Song',
                 'tassigur, the golden fang': 'Tasigur, the Golden Fang',
                 'thoughseize': 'Thoughtseize',
                 'thoughtsieze': 'Thoughtseize',
                 'thoughtsize': 'Thoughtseize',
                 'titan\'s strenght': 'Titan\'s Strength',
                 'twinbolt': 'Twin Bolt',
                 'unknown card': 'Unknown Card',
                 'unravel the aether': 'Unravel the Æther',
                 'urborg, tomb of yawghmoth': 'Urborg, Tomb of Yawgmoth',
                 'valrous stance': 'Valorous Stance',
                 'warden of he first tree': 'Warden of the First Tree',
                 'wear &amp; tear': 'Wear',
                 'xenagos, the reveelr': 'Xenagos, the Reveler',
                 'young piromancer': 'Young Pyromancer',
                 }

        if cardname.lower() in fixes:
            cardname = fixes[cardname]

        return cardname

    def cards_as_text(self):
        result = ''
        cards = DeckCard.objects.filter(deck=self).order_by('board')
        for card in cards:
            sb = ''
            if card.board == DeckCard.SIDE:
                sb = 'SB: '
            result = '{}{}{} {}\n'.format(result, sb, card.cardcount, card.physicalcard.get_card_name())
        return result

    class Meta:
        managed = True
        db_table = 'deck'

    def __unicode__(self):
        return '{} [{}]'.format(str(self.name), str(self.id))


class DeckCard(models.Model):
    id = models.AutoField(primary_key=True)
    deck = models.ForeignKey('Deck', null=False)
    cardcount = models.IntegerField(null=False, default=1)
    physicalcard = models.ForeignKey('cards.PhysicalCard', null=False)
    MAIN = 'main'
    SIDE = 'side'
    BOARD_CHOICES = ((MAIN, MAIN), (SIDE, SIDE))
    board = models.CharField(max_length=8, null=False, choices=BOARD_CHOICES, default=MAIN)

    class Meta:
        managed = True
        db_table = 'deckcard'
        unique_together = ('deck', 'physicalcard', 'board')

    def __unicode__(self):
        return '[' + str(self.deck.name) + ' (' + str(self.deck.id) + '): ' + str(self.cardcount) + \
            ' ' + str(self.physicalcard.id) + ' ' + str(self.board) + ']'


class TournamentDeck(models.Model):
    id = models.AutoField(primary_key=True)
    deck = models.ForeignKey('Deck', null=False)
    tournament = models.ForeignKey('Tournament', null=False)
    place = models.IntegerField(null=False, default=1)

    class Meta:
        managed = True
        db_table = 'tournamentdeck'
        unique_together = ('deck', 'tournament')

    def __unicode__(self):
        return 'TournamentDeck ({}, {}, {}) [{}]'.format(str(self.tournament), str(self.deck), str(self.place), str(self.id))


class FormatCardStat():
    # For looking at Staples, look back and see how it performed in the previous 3 formats.
    STAPLE_LOOKBACK = 3

    # This is the threshold for how many times the card needs to show up in ALL of the decks in a given format. If there are 100 decks in
    # the format, then 0.0008 means that the card shows up 20*75 * 0.0008 = 6 times.
    STAPLE_THRESHOLD = 0.0008

    def __init__(self, physicalcard, format):
        # Shouldn't I throw a TypeError here if the user gave me crap
        self.format = format
        self.physicalcard = physicalcard

    def tournamentdecks_in_format_count(self):
        # For this format, how many tournament decks are there
        count = TournamentDeck.objects.filter(tournament__format=self.format).aggregate(Count('id'))['id__count'] or 0
        return count

    def deck_count(self):
        # return the card count in the current format
        count = DeckCard.objects.filter(
            deck__tournaments__format=self.format,
            physicalcard=self.physicalcard).aggregate(
            Count('deck', distinct=True))['deck__count'] or 0
        return count

    def decks_in_format_percentage(self):
        # Returns either None or the float percentage of the number of decks that have this physicalcard in this format.
        result = None
        tdifc = self.tournamentdecks_in_format_count()
        if tdifc > 0:
            result = 100.0 * float(self.deck_count()) / float(tdifc)
        return result

    def average_card_count_in_deck(self):
        # return the average card count when this card is included in a deck
        result = DeckCard.objects.filter(
            deck__tournaments__format=self.format,
            physicalcard=self.physicalcard).aggregate(
            Avg('cardcount'))['cardcount__avg'] or 0.0
        return result

    def is_staple(self):
        logger = logging.getLogger(__name__)
        # return true if this card is a "staple" in this format.
        # Let's get the last three iterations of this format
        result = True
        latest_formats = Format.objects.filter(formatname=self.format.formatname, start_date__lte=self.format.start_date).order_by(
            '-start_date')[0:FormatCardStat.STAPLE_LOOKBACK]
        for lformat in latest_formats:
            if result:
                tfcc = DeckCard.objects.filter(deck__tournaments__format=lformat).aggregate(Sum('cardcount'))['cardcount__sum'] or 0
                this_card_cc = DeckCard.objects.filter(
                    deck__tournaments__format=lformat,
                    physicalcard=self.physicalcard).aggregate(
                    Sum('cardcount'))['cardcount__sum'] or 0
                if tfcc == 0:
                    # no div by zero
                    logger.info('is_staple {} bailing on div by 0.'.format(str(self.physicalcard)))
                    result = False
                else:
                    pcalc = float(this_card_cc) / float(tfcc)
                    # logger.info('is_staple {} pcalc is {} from {} occurences in {} cards in {}.'.format(
                    #    str(self.physicalcard), str(pcalc), str(this_card_cc), str(tfcc), str(lformat)))
                    result = result and pcalc >= FormatCardStat.STAPLE_THRESHOLD
        return result

    def __unicode__(self):
        return 'FormatCardStat ({}, {})'.format(str(self.format), str(self.physicalcard))


class DeckClusterDeck(models.Model):
    deckcluster = models.ForeignKey('DeckCluster')
    deck = models.ForeignKey('Deck', unique=True)
    distance = models.FloatField(default=1000.0, null=False)

    class Meta:
        managed = True
        db_table = 'deckclusterdeck'


class DeckCluster(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    clusterkey = models.IntegerField(null=False, default=-1)
    formatname = models.CharField(max_length=100, null=False)

    def __unicode__(self):
        return 'DeckCluster {} ({}) [{}]'.format(str(self.name), str(self.formatname), str(self.id))

    class Meta:
        managed = True
        db_table = 'deckcluster'
