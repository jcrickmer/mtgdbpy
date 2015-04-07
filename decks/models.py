from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

from django.db import connection

import logging

from cards.models import PhysicalCard, Format
import re


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

    # Returns the total number of cards in this deck.
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
            return u'CardNotFoundException: "{}"'.format(self.text)

    class CardsNotFoundException():

        def __init__(self, cnfes):
            self.cnfes = cnfes

        def __unicode__(self):
            return u'CardsNotFoundException: "{}"'.format(self.cnfes)

    def set_cards_from_text(self, cardlist):
        '''Go through each line and try to determine what the card is
        and how many should be present. If there are no errors, then
        delete/replace all of the existing DeckCards with these new
        DeckCards.'''
        req = re.compile(r'^(sb:\s*)?((\d+)x?\s+)?(.+)$', re.UNICODE)
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
                # REVSIT - ADDRESS multi-basecard cards, like "Beck // Call"
                pc = PhysicalCard.objects.filter(basecard__name__iexact=line_match.group(4)).first()
                if pc is not None:
                    # winner!
                    dc = DeckCard(deck=self, cardcount=card_count, physicalcard=pc)
                    if is_sb:
                        dc.board = DeckCard.SIDE
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
                dc.save()

    class Meta:
        managed = True
        db_table = 'deck'

    def __unicode__(self):
        return str(self.name)


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
        unique_together = ('deck', 'physicalcard')

    def __unicode__(self):
        return '[' + str(self.deck.name) + ' (' + str(self.deck.id) + '): ' + str(self.cardcount) + ' ' + str(self.physicalcard.id) + ']'
