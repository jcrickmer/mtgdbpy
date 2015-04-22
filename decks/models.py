# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

from django.db import connection

import logging

from cards.models import PhysicalCard, Format
import re
import sys


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
