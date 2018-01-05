# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Max, Min, Count, Sum, Avg

from django.db import connection

import logging

from cards.models import PhysicalCard, Format, FormatBasecard, BaseCard
import json
import re
import sys

from django.core.cache import cache
from django.utils.functional import cached_property


import time


class Timer:

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, *args):
        self.end = time.time()
        self.interval = self.end - self.start


class Tournament(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    url = models.CharField(max_length=500)
    format = models.ForeignKey('cards.Format')
    start_date = models.DateField(null=False, blank=False)
    end_date = models.DateField(null=False, blank=False)
    updated_at = models.DateTimeField(
        auto_now=True,
        null=False)

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
    updated_at = models.DateTimeField(
        auto_now=True,
        null=False)

    # Returns the total number of cards in this deck.
    def get_card_count(self):
        dcs = DeckCard.objects.filter(deck=self)
        result = 0
        for dc in dcs:
            result = result + dc.cardcount
        return result

    def card_groups(self):
        result = None
        with Timer() as t:
            result = cache.get('dcg_' + str(self.id))
            if result is None:
                result = self.card_groups_i()
                cache.set('dcg_' + str(self.id), result, 300)
        safelog('card_groups took %.04f sec.' % t.interval)
        return result

    def card_groups_i(self):
        ''' Returns all of the cards in the deck broken up into groups
            that are common for display. This is an list, which each
            item in the array containing a 'title' text field, and
            then an array in 'deckcards'. '''
        tlist = [{'ctype': 'Instant', 'title': 'Instants', },
                 {'ctype': 'Sorcery', 'title': 'Sorceries', },
                 {'ctype': 'Creature', 'title': 'Creatures', },
                 {'ctype': 'Enchantment', 'title': 'Enchantments', },
                 {'ctype': 'Artifact', 'title': 'Artifacts', },
                 {'ctype': 'Planeswalker', 'title': 'Planeswalkers', },
                 {'ctype': 'Land', 'title': 'Lands', },
                 ]  # Sideboard!!
        result = list()
        handled = list()  # the deckcards that have already been handled
        dcs = self.deckcard_set.filter(board=DeckCard.MAIN)  # .order_by('
        # for ttt in range(0,0):
        for ttt in tlist:
            gres = dict()
            gres['title'] = ttt['title']
            gres['deckcards'] = list()
            for dc in dcs:
                basecard = None
                if True:  # slower way?
                    basecard = cache.get('bc_pc' + str(dc.physicalcard.id))
                    if basecard is None:
                        basecard = BaseCard.objects.filter(
                            physicalcard=dc.physicalcard,
                            cardposition__in=(
                                BaseCard.FRONT,
                                BaseCard.LEFT,
                                BaseCard.UP)).first()
                        cache.set('bc_pc' + str(dc.physicalcard.id), basecard, 300)
                    if dc.id not in handled and ttt['ctype'] in [qqq.type for qqq in basecard.types.all()]:
                        gres['deckcards'].append(dc)
                        handled.append(dc.id)
            if len(gres['deckcards']) > 0:
                result.append(gres)
        # dcssm = self.deckcard_set.filter(board=DeckCard.MAIN)#.order_by('
        #result.append({'title':'Mainboard', 'deckcards':dcssm,})
        dcss = self.deckcard_set.filter(board=DeckCard.SIDE)  # .order_by('
        result.append({'title': 'Sideboard', 'deckcards': dcss})
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

    # Note that when matching the card name here we are getting everything but
    # a "+" or a "/". This will give us the first card in a double card like
    # Wear // Tear
    req = re.compile(r'^([SsCc][BbZz]:\s*)?((\d+)x?\s+)?([^\+/]+)', re.UNICODE)

    def set_cards_from_text(self, cardlist):
        '''Go through each line and try to determine what the card is
        and how many should be present. If there are no errors, then
        delete/replace all of the existing DeckCards with these new
        DeckCards.'''

        new_deckcards = list()
        exceptions = list()
        for line in cardlist.splitlines():
            is_sb = False
            is_cz = False
            card_count = 1
            line = line.strip().lower()
            line_match = Deck.req.match(line)
            if line_match:
                is_sb = (line_match.group(1) and 'sb:' in line.lower()) or False
                is_cz = (line_match.group(1) and 'cz:' in line.lower()) or False
                card_count = line_match.group(3) or 1
                # getting close! Now let's see if it's a real card
                # Let's do some quick clean-up of the card name...
                card_name = line_match.group(4).strip()
                card_name = self._fix_bad_spelling(card_name)
                pc_cache_key = u'cardname_' + card_name.replace(' ', '_')
                pc = cache.get_or_set(pc_cache_key, PhysicalCard.objects.filter(basecard__name__iexact=card_name).first(), 60 * 60 * 24)
                if pc is not None:
                    # winner!
                    board_t = DeckCard.MAIN
                    if is_sb:
                        board_t = DeckCard.SIDE
                    elif is_cz:
                        board_t = DeckCard.COMMAND
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
        for sillyapos in [u'\u2019', r'\u2019', '\\' + 'u2019', u'’']:
            cardname = cardname.replace(sillyapos, u"'")
        for sillydash in [u'–', u'—', u'‒', u'-']:
            cardname = cardname.replace(sillydash, '-')

        if cardname.lower() in self._spelling_fixes:
            cardname = self._spelling_fixes[cardname]
        cardname = cardname.replace(u'\u00C6', 'Ae')
        cardname = cardname.replace(u'\u00E6', 'ae')
        return cardname

    _spelling_fixes = {'aetherize': 'Ætherize',
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
    COMMAND = 'command'
    BOARD_CHOICES = ((MAIN, MAIN), (SIDE, SIDE), (COMMAND, COMMAND))
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


def safelog(msg):
    try:
        sys.stderr.write('' + msg + "\n")
    except UnicodeEncodeError as uee:
        sys.stderr.write('cold not log because of stupid unicode error\n')
    return


class FormatStat(models.Model):
    # Number of decks that have to be in a tournament for it to qualify
    MIN_DECKS_IN_TOURNAMENT = 1

    id = models.AutoField(primary_key=True)
    format = models.ForeignKey('cards.Format')
    tournamentdeck_count = models.IntegerField(null=False, default=0)
    tournamentdeckcard_count = models.IntegerField(null=False, default=0)

    def __init__(self, *args, **kwargs):
        super(FormatStat, self).__init__(*args, **kwargs)
        self._qti = None

    @property
    def qualified_tourn_ids(self):
        if self._qti is None:
            self._qti = Tournament.objects.filter(
                format=self.format).annotate(
                deck_count=Count('tournamentdeck')).filter(
                deck_count__gte=FormatStat.MIN_DECKS_IN_TOURNAMENT).values('id').order_by('id')
        return self._qti

    def calc_tournamentdeck_count(self):
        ''' For this format, how many tournament decks are there
        '''
        self.tournamentdeck_count = TournamentDeck.objects.filter(
            tournament_id__in=self.qualified_tourn_ids).aggregate(
            Count('id'))['id__count'] or 0
        return self.tournamentdeck_count

    def calc_tournamentdeckcard_count(self):
        self.tournamentdeckcard_count = DeckCard.objects.filter(
            deck__tournaments__id__in=self.qualified_tourn_ids).aggregate(
            Sum('cardcount'))['cardcount__sum'] or 0
        return self.tournamentdeckcard_count

    @staticmethod
    def calc_all(new_only=False, start_date=None, end_date=None, only_formatname=None):
        safelog("FormatCardStat.calc_all start.")
        formats_db = Format.objects.all().values('formatname').distinct()
        for formatname in (x['formatname'] for x in formats_db):
            # If the caller wants only one of the formats, then skip
            # all of the others that are not the named format.
            if only_formatname is not None:
                if formatname != only_formatname:
                    continue

            latest_formats_qs = Format.objects.filter(formatname=formatname)
            if start_date is not None:
                latest_formats_qs = latest_formats_qs.filter(start_date__gte=start_date)
            if end_date is not None:
                latest_formats_qs = latest_formats_qs.filter(start_date__lte=end_date)
            # Always process in start_date order. This may actually
            # not matter to the result now (since staple is
            # calcualted at run-time), but this is how I started and
            # tested it.
            latest_formats_qs = latest_formats_qs.order_by('start_date')

            for fmt in latest_formats_qs:
                safelog("  FormatCardStat.calc_all format {}".format(fmt.format))
                fs = FormatStat.objects.filter(format=fmt).first()
                is_new = fs is None
                if is_new:
                    fs = FormatStat(format=fmt)
                    fs.save()
                    fs = FormatStat.objects.filter(format=fmt).first()
                if (new_only and is_new) or not new_only:
                    fs.calc_tournamentdeck_count()
                    fs.calc_tournamentdeckcard_count()
                    fs.save()
                    safelog("      {}".format(fs))

    def __unicode__(self):
        return 'FormatStat f="{}": dc={}, dcc={}'.format(str(self.format.format),
                                                         str(self.tournamentdeck_count),
                                                         str(self.tournamentdeckcard_count))

    class Meta:
        managed = True
        db_table = 'formatstat'


class FormatCardStat(models.Model):
    # For looking at Staples, look back and see how it performed in the previous 3 formats.
    STAPLE_LOOKBACK = 3

    # This is the threshold for how many times the card needs to show up in ALL of the decks in a given format. If there are 100 decks in
    # the format, then 0.0008 means that the card shows up 20*75 * 0.0008 = 6 times.
    STAPLE_THRESHOLD = 0.0008

    id = models.AutoField(primary_key=True)
    format = models.ForeignKey('cards.Format')
    physicalcard = models.ForeignKey('cards.PhysicalCard')

    # the number of times that this card shows up in all decks in this format
    occurence_count = models.IntegerField(null=False, default=0)

    # the number of decks in this format that have this card
    deck_count = models.IntegerField(null=False, default=0)

    # the average card count when this card is included in a deck
    average_card_count_in_deck = models.FloatField(null=False, default=0.0)

    # the percentage of all cards in the format that are this card
    percentage_of_all_cards = models.FloatField(null=False, default=0.0)

    def __init__(self, *args, **kwargs):
        super(FormatCardStat, self).__init__(*args, **kwargs)
        self._formatstat = None

    @property
    def formatstat(self):
        if self._formatstat is None:
            self._formatstat = FormatStat.objects.filter(format=self.format).first()
        return self._formatstat

    def in_decks_percentage(self):
        ''' Returns either None or the float percentage of the number of decks that have this physicalcard in this format.
        '''
        result = None
        if self.formatstat is not None and self.formatstat.tournamentdeck_count > 0:
            result = 100.0 * float(self.deck_count) / float(self.formatstat.tournamentdeck_count)
        return result

    def is_staple(self):
        latest_formats_qs = Format.objects.filter(formatname=self.format.formatname,
                                                  start_date__lte=self.format.start_date,
                                                  formatbasecard__basecard__physicalcard=self.physicalcard).order_by('-start_date')
        latest_formats = latest_formats_qs[0:FormatCardStat.STAPLE_LOOKBACK]
        #safelog("is_staple latest_formats = {}".format(latest_formats))
        result = True
        cntr = 1
        if result:
            for lformat in latest_formats:
                old_fcs = FormatCardStat.objects.filter(physicalcard=self.physicalcard, format=lformat).first()
                if old_fcs is not None:
                    #safelog("is_staple f={} old_fcs.percent = {}".format(lformat.format, old_fcs.percentage_of_all_cards))
                    pass
                else:
                    #safelog("is_staple f={} old_fcs is None".format(lformat.format))
                    pass
                result = result and old_fcs is not None and old_fcs.percentage_of_all_cards > FormatCardStat.STAPLE_THRESHOLD
                cntr = cntr + 1
        result = result and cntr >= FormatCardStat.STAPLE_LOOKBACK
        return result

    def calc_deck_count(self):
        if self.formatstat is not None and self.formatstat.tournamentdeck_count > 0:
            self.deck_count = DeckCard.objects.filter(deck__tournaments__id__in=self.formatstat.qualified_tourn_ids,
                                                      physicalcard=self.physicalcard).aggregate(
                Count('deck', distinct=True))['deck__count'] or 0
        return self.deck_count

    def calc_combined(self):
        self.deck_count = 0
        self.occurence_count = 0
        self.average_card_count_in_deck = 0.0
        if self.formatstat is not None and self.formatstat.tournamentdeck_count > 0:
            cstats = DeckCard.objects.filter(deck__tournaments__id__in=self.formatstat.qualified_tourn_ids,
                                             physicalcard=self.physicalcard).aggregate(Count('deck', distinct=True),
                                                                                       Sum('cardcount'),
                                                                                       Avg('cardcount'))
            self.deck_count = cstats['deck__count'] or 0
            self.occurence_count = cstats['cardcount__sum'] or 0
            self.average_card_count_in_deck = cstats['cardcount__avg'] or 0.0
            self.percentage_of_all_cards = float(self.occurence_count) / float(self.formatstat.tournamentdeckcard_count)
        return

    def calc_average_card_count_in_deck(self):
        # return the average card count when this card is included in a deck
        result = 0.0
        if self.formatstat is not None and self.formatstat.tournamentdeck_count > 0:
            result = DeckCard.objects.filter(deck__tournaments__id__in=self.formatstat.qualified_tourn_ids,
                                             physicalcard=self.physicalcard).aggregate(
                Avg('cardcount'))['cardcount__avg'] or 0.0
        self.average_card_count_in_deck = result
        return result

    def calc_percentage_of_all_cards(self):
        # get all of the tournaments in lformat that have at least MIN_DECKS_IN_TOURNAMENT in them
        self.percentage_of_all_cards = 0.0
        if self.formatstat is not None and self.formatstat.tournamentdeck_count > 0:
            if self.formatstat.tournamentdeckcard_count != 0:
                self.percentage_of_all_cards = float(self.calc_occurence_count()) / float(self.formatstat.tournamentdeckcard_count)
        return self.percentage_of_all_cards

    def calc_occurence_count(self):
        self.occurence_count = 0
        if self.formatstat is not None and self.formatstat.tournamentdeck_count > 0:
            self.occurence_count = DeckCard.objects.filter(deck__tournaments__id__in=self.formatstat.qualified_tourn_ids,
                                                           physicalcard=self.physicalcard).aggregate(
                Sum('cardcount'))['cardcount__sum'] or 0
        return self.occurence_count

    @staticmethod
    def calc_all(new_only=False, start_date=None, end_date=None, only_formatname=None):
        safelog("FormatCardStat.calc_all start.")
        formatstats_qs = FormatStat.objects.all()
        if only_formatname is not None:
            formatstats_qs = formatstats_qs.filter(format__formatname__iexact=only_formatname)
        if start_date is not None:
            formatstats_qs = formatstats_qs.filter(format__start_date__gte=start_date)
        if end_date is not None:
            formatstats_qs = formatstats_qs.filter(format__start_date__lte=end_date)

        # Always process in start_date order. This may actually not
        # matter to the result now (since staple is calcualted at
        # run-time), but this is how I started and tested it.
        formatstats_qs = formatstats_qs.order_by('format__start_date')

        for fstat in formatstats_qs:
            safelog("  FormatCardStat.calc_all: format {}".format(fstat.format.format))
            fcards = FormatBasecard.objects.filter(format=fstat.format)
            for fcard in fcards:
                fcs = None
                fcs = FormatCardStat.objects.filter(format=fstat.format, physicalcard=fcard.basecard.physicalcard).first()
                if fcs is None:
                    fcs = FormatCardStat(format=fstat.format, physicalcard=fcard.basecard.physicalcard)
                    fcs.save()
                    fcs = FormatCardStat.objects.filter(format=fstat.format, physicalcard=fcard.basecard.physicalcard).first()
                elif new_only:
                    # If we are calculating new only, then we better skip this one
                    continue
                safelog("    FormatCardStat.calc_all: card {}".format(fcs.physicalcard.get_card_name()))
                with Timer() as t:
                    fcs.calc_combined()
                safelog('        calc_combined took %.03f sec.' % t.interval)
                # with Timer() as t:
                #    fcs.calc_deck_count()
                #safelog('calc_deck_count took %.03f sec.' % t.interval)
                # with Timer() as t:
                #    fcs.calc_occurence_count()
                #safelog('calc_occurence_count took %.03f sec.' % t.interval)
                # with Timer() as t:
                #    fcs.calc_average_card_count_in_deck()
                #safelog('        calc_average_card_count_in_deck took %.03f sec.' % t.interval)
                # with Timer() as t:
                #    fcs.calc_percentage_of_all_cards()
                #safelog('        calc_percentage_of_all_cards took %.03f sec.' % t.interval)
                # with Timer() as t:
                fcs.save()
                #safelog('        save took %.03f sec.' % t.interval)
                # with Timer() as t:
                safelog("      {}".format(fcs))
                #safelog('        str took %.03f sec.' % t.interval)

    def __unicode__(self):
        return 'FormatCardStat f="{}" c="{}": dc={}, oc={}'.format(
            self.format.format, self.physicalcard.get_card_name(), str(
                self.deck_count), str(
                self.occurence_count))

    class Meta:
        managed = True
        db_table = 'formatcardstat'
        unique_together = ('format', 'physicalcard')


class DeckClusterDeck(models.Model):
    deckcluster = models.ForeignKey('DeckCluster')
    #deck = models.ForeignKey('Deck', unique=True)
    deck = models.OneToOneField(Deck)
    distance = models.FloatField(default=1000.0, null=False)

    class Meta:
        managed = True
        db_table = 'deckclusterdeck'


class DeckCluster(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False)
    clusterkey = models.IntegerField(null=False, default=-1)
    formatname = models.CharField(max_length=100, null=False)

    def get_stats_json(self):
        return json.dumps(self.get_stats())

    def get_stats(self):
        # All decks per month
        all_sql = '''SELECT DATE_FORMAT(t.start_date, '%%Y-%%m'), count(dcd.id), MIN(dcd.distance), MAX(dcd.distance), AVG(dcd.distance) FROM deckcluster dc JOIN deckclusterdeck dcd ON dc.id = dcd.deckcluster_id LEFT JOIN deck ON deck.id = dcd.deck_id LEFT JOIN tournamentdeck td ON td.deck_id = deck.id LEFT JOIN tournament t ON td.tournament_id = t.id LEFT JOIN format f ON t.format_id = f.id WHERE f.formatname = 'Modern' GROUP BY DATE_FORMAT(t.start_date, '%%Y%%m')'''

        # Just decks in a specific cluster per month
        cluster_sql = '''SELECT DATE_FORMAT(t.start_date, '%%Y-%%m'), count(dcd.id), MIN(dcd.distance), MAX(dcd.distance), AVG(dcd.distance) FROM deckcluster dc JOIN deckclusterdeck dcd ON dc.id = dcd.deckcluster_id LEFT JOIN deck ON deck.id = dcd.deck_id LEFT JOIN tournamentdeck td ON td.deck_id = deck.id LEFT JOIN tournament t ON td.tournament_id = t.id LEFT JOIN format f ON t.format_id = f.id WHERE f.formatname = 'Modern' AND dc.id = %s GROUP BY DATE_FORMAT(t.start_date, '%%Y%%m')'''

        cursor = connection.cursor()

        cursor.execute(all_sql, [])
        all_res = cursor.fetchall()

        cursor.execute(cluster_sql, [self.id])
        cluster_res = cursor.fetchall()
        result = dict()
        result['histogram'] = list()

        # setup all of the months that we want to look at
        all_dates = list()
        now = time.localtime()
        mon_delay = 1
        if now.tm_mday > 18:
            mon_delay = 0
        end_m = time.localtime(time.mktime((now.tm_year, now.tm_mon - mon_delay, 1, 0, 0, 0, 0, 0, 0)))[:2]
        start_month = 9
        start_year = 2013
        date_m = time.localtime(time.mktime((2013, 9, 1, 0, 0, 0, 0, 0, 0)))[:2]
        while date_m != end_m:
            date_m = time.localtime(time.mktime((start_year, start_month, 1, 0, 0, 0, 0, 0, 0)))[:2]
            all_dates.append(date_m)
            start_month = start_month + 1

        # create 0-objects for all of those dates and add them to a temporary dict
        temp_dict = dict()
        for rmonth in all_dates:
            record = dict()
            record['month'] = '{0:04d}-{1:02d}'.format(rmonth[0], rmonth[1])
            record['decks'] = 0
            record['distance_min'] = 0
            record['distance_max'] = 0
            record['distance_avg'] = 0
            record['all_decks'] = 0
            record['all_distance_min'] = 0
            record['all_distance_max'] = 0
            record['all_distance_avg'] = 0
            record['deck_percent_of_all'] = 0
            temp_dict[record['month']] = record

        for line in cluster_res:
            record = dict()
            record['month'] = line[0]
            record['decks'] = line[1]
            record['distance_min'] = line[2]
            record['distance_max'] = line[3]
            record['distance_avg'] = line[4]
            for allline in all_res:
                if allline[0] == record['month']:
                    record['all_decks'] = allline[1]
                    record['all_distance_min'] = allline[2]
                    record['all_distance_max'] = allline[3]
                    record['all_distance_avg'] = allline[4]
                    record['deck_percent_of_all'] = None
                    if record['all_decks'] > 0:
                        record['deck_percent_of_all'] = float(record['decks']) / float(record['all_decks'])
            temp_dict[record['month']] = record

        for rrkey in sorted(temp_dict.iterkeys()):
            result['histogram'].append(temp_dict[rrkey])

        count_sql = '''SELECT count(id), min(distance), max(distance), avg(distance) FROM deckclusterdeck WHERE deckcluster_id = %s'''
        cursor.execute(count_sql, [self.id])
        count_res = cursor.fetchone()
        result['cluster'] = dict()
        result['cluster']['size'] = count_res[0]
        result['cluster']['min_distance'] = count_res[1]
        result['cluster']['max_distance'] = count_res[2]
        result['cluster']['avg_distance'] = count_res[3]

        perc_sql = '''SELECT distance FROM deckclusterdeck WHERE deckcluster_id = %s ORDER BY distance'''
        cursor.execute(perc_sql, [self.id])
        perc_res = cursor.fetchall()
        result['cluster']['percentile'] = dict()
        for sample in range(1, 9):
            idx = len(perc_res) * sample / 10
            result['cluster']['percentile'][sample * 10] = perc_res[idx][0]
        result['cluster']['median_distance'] = result['cluster']['percentile'][50]

        return result

    def __unicode__(self):
        return 'DeckCluster {} ({}) [{}]'.format(str(self.name), str(self.formatname), str(self.id))

    class Meta:
        managed = True
        db_table = 'deckcluster'
