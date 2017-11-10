#-*- coding: utf-8 -*-

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines for those models you wish to give write DB access
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin.py sqlcustom [appname]'
# into your database.
from __future__ import unicode_literals
import sys
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

from cards.view_utils import convertSymbolsToHTML
from cards.text_utils import filing_string
from django.utils.safestring import mark_safe

from django.db.models import Max, Min, Count
from django.db import connection, ProgrammingError

import logging
from operator import itemgetter

from django.core.cache import cache


class Color(models.Model):
    id = models.CharField(primary_key=True, max_length=1)
    color = models.CharField(max_length=9)

    class Meta:
        managed = True
        db_table = 'color'

    def __unicode__(self):
        return self.color


class Rarity(models.Model):
    id = models.CharField(primary_key=True, max_length=1)
    rarity = models.CharField(max_length=11)
    sortorder = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'rarity'
        verbose_name_plural = 'Rarities'

    def __unicode__(self):
        return self.rarity


class Type(models.Model):
    #id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=128, unique=True)
    sort_order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'type'

    def __unicode__(self):
        return self.type


class Supertype(models.Model):
    #id = models.IntegerField(primary_key=True)
    supertype = models.CharField(max_length=128, unique=True)

    class Meta:
        managed = True
        db_table = 'supertype'

    def __unicode__(self):
        return self.supertype


class Subtype(models.Model):
    #id = models.IntegerField(primary_key=True)
    subtype = models.CharField(max_length=128, unique=True)

    class Meta:
        managed = True
        db_table = 'subtype'

    def __unicode__(self):
        return self.subtype


class PhysicalCard(models.Model):
    #id = models.IntegerField(primary_key=True)
    NORMAL = 'normal'
    SPLIT = 'split'
    FLIP = 'flip'
    DOUBLE = 'double-faced'
    TOKEN = 'token'
    PLANE = 'plane'
    SCHEME = 'scheme'
    PHENOMENON = 'phenomenon'
    LEVELER = 'leveler'
    VANGUARD = 'vanguard'
    LAYOUT_CHOICES = (
        (NORMAL,
         'normal'),
        (SPLIT,
         'split'),
        (FLIP,
         'flip'),
        (DOUBLE,
         'double-faced'),
        (TOKEN,
         'token'),
        (PLANE,
         'plane'),
        (SCHEME,
         'scheme'),
        (PHENOMENON,
         'phenomenon'),
        (LEVELER,
         'leveler'),
        (VANGUARD,
         'vanguard'))
    layout = models.CharField(
        max_length=12,
        choices=LAYOUT_CHOICES,
        default=NORMAL)

    def get_cardrating(self, format_id, test_id):
        # shortcut to get the CardRating for a given format and test.
        # This is accessible in templates
        return self.cardrating_set.get(format__id=format_id, test__id=test_id)

    def get_cardrating_safe(self, format_id, test_id=1):
        try:
            return self.get_cardrating(format_id, test_id)
        except CardRating.DoesNotExist:
            # , format=Format.objects.get(pk=format_id), test=BattleTest.objects.get(pk=test_id))
            return CardRating(physicalcard=self)

    def get_last_updated(self):
        return max(bc.updated_at for bc in self.basecard_set.all())

    def get_card_name(self):
        first_card = None
        sec_card = None
        for bc in self.basecard_set.all():
            if bc.cardposition == BaseCard.BACK or bc.cardposition == BaseCard.RIGHT or bc.cardposition == BaseCard.DOWN:
                sec_card = bc
            else:
                first_card = bc
        if not first_card:
            result = "!FIRST_CARD MISSING!"
            sys.stderr.write("NO first_card for " + str(self.id) + "\n")
        else:
            result = first_card.name
        if sec_card:
            result = result + '/' + sec_card.name
        return result

    def get_card_filing_name(self):
        first_card = None
        sec_card = None
        for bc in self.basecard_set.all():
            if bc.cardposition == BaseCard.BACK or bc.cardposition == BaseCard.RIGHT or bc.cardposition == BaseCard.DOWN:
                sec_card = bc
            else:
                first_card = bc
        result = first_card.filing_name
        if sec_card:
            result = result + '/' + sec_card.filing_name
        return result

    def get_face_basecard(self):
        basecard = BaseCard.objects.filter(physicalcard_id=self.id, cardposition__in=[BaseCard.FRONT, BaseCard.LEFT, BaseCard.UP]).first()
        return basecard

    def get_latest_card(self):
        logger = logging.getLogger(__name__)
        #logger.error("PhysicalCard.get_latest_card: self is {}".format(str(self)))
        card = cache.get('c_pc' + str(self.id))
        if card is None:
            bc = self.basecard_set.filter(cardposition__in=[BaseCard.FRONT, BaseCard.LEFT, BaseCard.UP]).first()
            if bc is None:
                logger.error("PhysicalCard.get_latest_card: ouch. bc is None")
            card = bc.card_set.all().order_by('-multiverseid').first()
            cache.set('c_pc' + str(self.id), card, 300)
        return card

    def get_latest_url_part(self):
        card = self.get_latest_card()
        return str(card.multiverseid) + '-' + card.url_slug()

    def get_searchable_document(self, include_names=True):
        result = ''
        for basecard in self.basecard_set.all():
            rules = basecard.rules_text
            if rules is None or len(rules) == 0:
                if basecard.name == 'Plains':
                    rules = 'tap: add manawhite to your mana pool.'
                elif basecard.name == 'Island':
                    rules = 'tap: add manablue to your mana pool.'
                elif basecard.name == 'Swamp':
                    rules = 'tap: add manablack to your mana pool.'
                elif basecard.name == 'Mountain':
                    rules = 'tap: add manared to your mana pool.'
                elif basecard.name == 'Forest':
                    rules = 'tap: add managreen to your mana pool.'
            rules = rules.replace(basecard.name, 'cardselfreference')
            rules = rules.lower()
            rules = rules.replace('{c}', ' manacolorless ')
            rules = rules.replace('{t}', ' tap ')
            rules = rules.replace('{e}', ' energy ')
            rules = rules.replace('{q}', ' untap ')
            rules = rules.replace('{w}', ' manawhite ')
            rules = rules.replace('{u}', ' manablue ')
            rules = rules.replace('{b}', ' manablack ')
            rules = rules.replace('{r}', ' manared ')
            rules = rules.replace('{g}', ' managreen ')
            rules = rules.replace('{s}', ' snowsymbol ')
            rules = rules.replace('{x}', ' manax ')
            for numm in range(0, 20):
                rules = rules.replace('{' + str(numm) + '}', 'mana' + str(numm))
            rules = rules.replace("{wp}", ' manawhite manaphyrexian ')
            rules = rules.replace("{up}", ' manablue manaphyrexian ')
            rules = rules.replace("{bp}", ' manablack manaphyrexian ')
            rules = rules.replace("{rp}", ' manared manaphyrexian ')
            rules = rules.replace("{gp}", ' managreen manaphyrexian ')
            rules = rules.replace("{2w}", ' manaalt2 manawhite ')
            rules = rules.replace("{2u}", ' manaalt2 manablue ')
            rules = rules.replace("{2b}", ' manaalt2 manablack ')
            rules = rules.replace("{2r}", ' manaalt2 manared ')
            rules = rules.replace("{2g}", ' manaalt2 managreen ')
            rules = rules.replace("{wu}", ' manawhite manablue manahybrid ')
            rules = rules.replace("{wb}", ' manawhite manablack manahybrid ')
            rules = rules.replace("{ub}", ' manablue manablack manahybrid ')
            rules = rules.replace("{ur}", ' manablue manared manahybrid ')
            rules = rules.replace("{br}", ' manablack manared manahybrid ')
            rules = rules.replace("{bg}", ' manablack managreen manahybrid ')
            rules = rules.replace("{rg}", ' manared managreen manahybrid ')
            rules = rules.replace("{rw}", ' manared manawhite manahybrid ')
            rules = rules.replace("{gw}", ' managreen manawhite manahybrid ')
            rules = rules.replace("{gu}", ' managreen manablue manahybrid ')

            # need to add something that does a regexp match on hybrid mana in mana cost and rules text and adds a term for 'manahybrid'

            if include_names:
                #result = result + basecard.name + '\n'
                result = result + basecard.filing_name + '\n'
            result = result + rules + '\n'
            #result = result + basecard.mana_cost + '\n'
            # add the pips that are in the mana cost
            if len(basecard.mana_cost) > 0:
                costparts = basecard.mana_cost.lower().split('}')
                for pippart in costparts:
                    if pippart.find('w') > -1:
                        result = result + 'pipwhite '
                    if pippart.find('u') > -1:
                        result = result + 'pipblue '
                    if pippart.find('b') > -1:
                        result = result + 'pipblack '
                    if pippart.find('r') > -1:
                        result = result + 'pipred '
                    if pippart.find('g') > -1:
                        result = result + 'pipgreen '
                    if pippart.find('c') > -1:
                        result = result + 'pipcolorless '
                result = result + "\n"
            strippedcost = str(basecard.mana_cost).replace('{', '')
            strippedcost = strippedcost.replace('}', '')
            strippedcost = strippedcost.replace('/p', '')
            strippedcost = strippedcost.replace('2/', '')
            strippedcost = strippedcost.replace('/', '')
            result = result + strippedcost.lower() + '\n'
            uses_pmana = False
            try:
                basecard.rules_text.lower().index('/p}')
                uses_pmana = True
            except ValueError:
                pass
            try:
                basecard.mana_cost.lower().index('/p}')
                uses_pmana = True
            except ValueError:
                pass
            if uses_pmana:
                result = result + ' manaphyrexian\n'

            result = result + 'cmc' + str(basecard.cmc) + '\n'
            if basecard.power is not None:
                try:
                    result = result + 'power' + str(basecard.power) + "\n"
                except:
                    pass
            if basecard.toughness is not None:
                try:
                    result = result + 'toughness' + str(basecard.toughness) + "\n"
                except:
                    pass
            if basecard.loyalty is not None:
                try:
                    result = result + 'loyalty' + str(basecard.loyalty) + "\n"
                except:
                    pass
            colors = basecard.colors.all()
            if len(colors) > 1:
                result = result + 'multicolored\n'
            else:
                result = result + 'notmulticolored\n'
            allcolors = ['white', 'blue', 'black', 'red', 'green', 'colorless']
            for color in colors:
                result = result + 'cardcolor' + color.color.lower() + "\n"
                allcolors.remove(color.color.lower())
            for notcolor in allcolors:
                result = result + 'notcardcolor' + notcolor + "\n"

            result = result + ' '.join('supertype' + csptype.supertype for csptype in basecard.supertypes.all()) + "\n"
            result = result + ' '.join('type' + ctype.type for ctype in basecard.types.all()) + "\n"
            result = result + ' '.join('subtype' + cstype.subtype for cstype in basecard.subtypes.all()) + "\n"
            #result = result + ' '.join(ctype.type for ctype in basecard.types.all()) + "\n"
            #result = result + ' '.join(cstype.subtype for cstype in basecard.subtypes.all()) + "\n"

            result = result + '\n'

        if self.basecard_set.all().count() > 1:
            result = 'multicard\n' + result

        return result

    class Meta:
        managed = True
        db_table = 'physicalcard'
        verbose_name_plural = 'Physical Cards'

    def __unicode__(self):
        return '{} [PC:{}]'.format(self.get_card_name(), str(self.id))


class BaseCard(models.Model):
    FRONT = 'F'
    BACK = 'B'
    LEFT = 'L'
    RIGHT = 'R'
    UP = 'U'
    DOWN = 'D'
    #id = models.IntegerField(primary_key=True)
    physicalcard = models.ForeignKey(PhysicalCard)
    name = models.CharField(max_length=128, unique=True, blank=False)
    filing_name = models.CharField(max_length=128, blank=False)
    rules_text = models.CharField(max_length=1000, blank=True)
    mana_cost = models.CharField(max_length=60, null=False)
    cmc = models.IntegerField(null=False, default=0)
    power = models.CharField(max_length=4, null=True, blank=True)
    toughness = models.CharField(max_length=4, null=True, blank=True)
    loyalty = models.CharField(max_length=4, null=True, blank=True)
    created_at = models.DateTimeField(
        null=False,
        auto_now_add=True)
    updated_at = models.DateTimeField(
        null=False,
        auto_now=True)
    cardposition = models.CharField(max_length=1, null=False, default=FRONT)
    types = models.ManyToManyField(Type, through='CardType')
    supertypes = models.ManyToManyField(Supertype, through='CardSupertype')
    subtypes = models.ManyToManyField(Subtype, through='CardSubtype')
    colors = models.ManyToManyField(Color, through='CardColor')

    def __setattr__(self, attrname, val):
        super(BaseCard, self).__setattr__(attrname, val)

        if attrname == 'name':
            self.filing_name = self.make_filing_name(val)

        if attrname == 'mana_cost':
            super(BaseCard, self).__setattr__(attrname, str(val).lower())
            # REVISIT!
            self.cmc = 1

    def get_rulings(self):
        return Ruling.objects.filter(basecard=self.id).order_by('ruling_date')

    def is_land(self):
        ct = CardType.objects.filter(type__type='Land', basecard=self).first()
        return ct is not None

    def make_filing_name(self, name):
        return filing_string(name)

    class Meta:
        managed = True
        db_table = 'basecard'
        verbose_name_plural = 'Base Cards'
        unique_together = ('physicalcard', 'cardposition',)

    def __unicode__(self):
        return self.name + \
            ' (physicalcard.id=' + str(self.physicalcard.id) + ')'

    def clean(self):
        # A name is required.
        if self.name is None or self.name == '':
            raise ValidationError('BaseCard must have a name.')
        # A filing_name is required.
        if self.filing_name is None or self.filing_name == '':
            raise ValidationError(
                'BaseCard must have a filing_name. It should be set through the name attribute.')

    def save(self):
        super(BaseCard, self).save()


class Ruling(models.Model):
    #id = models.IntegerField(primary_key=True)
    basecard = models.ForeignKey(BaseCard)
    ruling_text = models.TextField(null=False)
    ruling_date = models.DateField(null=False, blank=False)

    class Meta:
        verbose_name_plural = 'Rulings'
        db_table = 'ruling'

    def __unicode__(self):
        return "Ruling " + str(self.id) + " for " + self.basecard.name


class ExpansionSet(models.Model):
    #id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=128)
    abbr = models.CharField(unique=False, max_length=10)

    class Meta:
        managed = True
        db_table = 'expansionset'
        verbose_name_plural = 'Expansion Sets'

    def __unicode__(self):
        return self.name + " (" + self.abbr + ")"


class Mark(models.Model):
    #id = models.IntegerField(primary_key=True)
    mark = models.CharField(max_length=128)

    class Meta:
        managed = True
        db_table = 'mark'

    def __unicode__(self):
        return self.mark


class CardManager(models.Manager):

    def get_queryset(self, *args, **kwargs):
        # Not sure of the performance in here. Basically, I needed to
        # do a GROUP BY to get the max multiverseid and only display
        # that card. The first query here is getting the max
        # multiverseid for the given query. The second query then uses
        # that "mid_max" value to get back a list of all of the cards.
        card_listP = super(CardManager, self).get_queryset(*args, **kwargs)
        card_listP = card_listP.values('basecard__id').annotate(
            mid_max=Max('multiverseid'))
        card_list = super(CardManager, self).get_queryset()
        card_list = card_list.filter(
            multiverseid__in=[
                g['mid_max'] for g in card_listP]).order_by('basecard__filing_name')

        # Filer out the non-playing cards for now
        queryset = card_list.filter(
            basecard__physicalcard__layout__in=(
                'normal',
                'double-faced',
                'split',
                'flip',
                'leveler'))

        return queryset

    def get_latest_printing(self, *args, **kwargs):
        return self.get_queryset(*args, **kwargs)

    def in_cardrating_order(
            self,
            queryset,
            format_id=1,
            test_id=1,
            sort_order=1):
        #cursor = connection.cursor()
        #sql = 'SELECT bc.name, max(c.multiverseid), pc.id, cr.mu FROM physicalcard pc JOIN basecard bc ON pc.id = bc.physicalcard_id JOIN card c ON bc.id = c.basecard_id JOIN cardrating cr ON cr.physicalcard_id = pc.id WHERE cr.format_id = ' + str(format_id) + ' AND cr.test_id = ' + str(test_id) + ' GROUP BY pc.id ORDER BY cr.mu'
        # cursor.execute(sql)
        #context['winners'] = cursor.fetchall()

        # Try 2
        #cr_qs = CardRating.objects.filter(format_id=format_id, test_id=test_id).order_by('mu')
        #result = {}
        #qs = self.get_queryset().filter(*args, **kwargs)
        # for card in qs:
        #	index = 0
        #	for cr in cr_qs:
        #		if cr.physicalcard.id == card.basecard.physicalcard.id:
        #			result[index] = card
        #		index = index + 1
        #list2 = [result[x] for x in result if x]
        # return reversed(list2)

        sql_ord = 'ASC'
        if sort_order <= 0:
            sql_ord = 'DESC'

        cards = self.raw(
            'SELECT c.id FROM physicalcard pc JOIN basecard bc ON pc.id = bc.physicalcard_id JOIN card c ON bc.id = c.basecard_id JOIN cardrating cr ON cr.physicalcard_id = pc.id WHERE cr.format_id = ' +
            str(format_id) +
            ' AND cr.test_id = ' +
            str(test_id) +
            ' AND c.id IN (' +
            ','.join(str(card.id) for card in queryset) +
            ') GROUP BY pc.id HAVING max(c.multiverseid) ORDER BY cr.mu ' +
            sql_ord +
            ', bc.filing_name')
        return cards

    def search(self, *args, **kwargs):
        logger = logging.getLogger(__name__)
        test_id = 1

        # use this to create unique table aliases as we add joins
        jcounter = 0

        pre_where_clause = ''
        # This version gets the one with the last multiverseid (ostinsibly, the latest one), but it is really, really slow. And take the HAVING clause out if you are using this one.
        #sql_s = '''SELECT c.id, c.basecard_id FROM physicalcard AS pc JOIN basecard AS bc ON pc.id = bc.physicalcard_id JOIN card AS c ON c.basecard_id = bc.id INNER JOIN (SELECT basecard_id, MAX(multiverseid) AS multiverseid FROM card GROUP BY basecard_id) AS cm ON cm.basecard_id = c.basecard_id AND cm.multiverseid = c.multiverseid LEFT JOIN formatbasecard AS f ON f.basecard_id = bc.id LEFT JOIN cardrating AS cr ON cr.physicalcard_id = pc.id AND cr.test_id = 1 '''
        sql_s = '''SELECT c.id, c.basecard_id FROM physicalcard AS pc JOIN basecard AS bc ON pc.id = bc.physicalcard_id JOIN card AS c ON c.basecard_id = bc.id LEFT JOIN formatbasecard AS f ON f.basecard_id = bc.id LEFT JOIN cardrating AS cr ON cr.physicalcard_id = pc.id AND cr.test_id = 1 '''

        terms = []
        not_terms = []
        sortds = []
        specified_format = None

        safelocker = dict()
        safelocker['_counter'] = 0

        all_args = []

        for restriction in [PhysicalCard.TOKEN, PhysicalCard.PLANE, PhysicalCard.SCHEME, PhysicalCard.PHENOMENON, PhysicalCard.VANGUARD]:
            no_s = SearchPredicate()
            no_s.term = 'layout'
            no_s.negative = True
            no_s.value = restriction
            all_args.append(no_s)

        for arg in args:
            if isinstance(arg, list):
                for subarg in arg:
                    all_args.append(subarg)
            else:
                all_args.append(arg)

        # We must grab the format first
        for arg in all_args:
            if isinstance(arg, SortDirective):
                sortds.append(arg)
            elif isinstance(arg, SearchPredicate):
                if arg.term == 'format':
                    specified_format = arg.value
                    sql_p = ' f.format_id = %(sarg' + str(safelocker['_counter']) + ')s '
                    safelocker['sarg' + str(safelocker['_counter'])] = specified_format
                    safelocker['_counter'] = safelocker['_counter'] + 1
                    terms.append(sql_p)

        if len(sortds) == 0:
            namesort = SortDirective()
            namesort.term = 'name'
            sortds.append(namesort)
        else:
            # go through the sort directives and handle card rating sorting, if needed
            for sd in sortds:
                # If we are sorting for card rating, we need to inject into the search criteria the format that we care about.
                if sd.term == 'cardrating':
                    pre_where_clause = ' LEFT JOIN cardrating AS crs ON crs.physicalcard_id = pc.id AND crs.test_id = 1 AND crs.format_id = ' + \
                        str(sd.crs_format_id)

        # Now we can process all of the other terms
        for arg in all_args:
            if isinstance(arg, SearchPredicate):
                if (arg.term == 'name'):
                    orc = []
                    for fieldname in ['bc.name', 'bc.filing_name']:
                        sql_p = fieldname
                        sql_p = sql_p + arg.text_sql_operator_and_value(safelocker)
                        orc.append(sql_p)
                    if arg.negative:
                        terms.append('(' + ' AND '.join(orc) + ')')
                    else:
                        terms.append('(' + ' OR '.join(orc) + ')')
                elif arg.term == 'rules':
                    sql_p = ' bc.rules_text '
                    sql_p = sql_p + arg.text_sql_operator_and_value(safelocker)
                    terms.append(sql_p)
                elif arg.term in ['cmc', 'toughness', 'power', 'loyalty']:
                    sql_p = ' bc.' + arg.term + ' '
                    sql_p = sql_p + arg.numeric_sql_operator()
                    sql_p = sql_p + str(arg.value) + ' '
                    terms.append(sql_p)
                elif arg.term == 'cardrating':
                    if specified_format is None:
                        raise self.FormatNotSpecifiedException()
                    # NOTE! A singular format must ALSO be provided!!
                    terms.append(' cr.format_id = ' + str(specified_format) + ' ')

                    sql_p = ' ROUND(cr.mu,5) '
                    sql_p = sql_p + arg.numeric_sql_operator()

                    # remember that the database stores it on a scale from 0 to 50, but it is presented to users as 0 to 1000
                    sql_p = sql_p + str(arg.value / 20.0) + ' '

                    terms.append(sql_p)
                elif arg.term == 'rarity':
                    sql_p = ' c.rarity '
                    sql_p = sql_p + arg.text_sql_operator_and_value(safelocker)
                    terms.append(sql_p)
                elif arg.term == 'color':
                    if arg.negative:
                        not_terms.append(arg)
                    else:
                        tab_alias = 'cc' + str(jcounter)
                        jcounter = jcounter + 1
                        pre_where_clause = pre_where_clause + ' JOIN cardcolor AS ' + \
                            tab_alias + ' ON bc.id = ' + tab_alias + '.basecard_id '
                        sql_p = ' ' + tab_alias + '.color_id ' + arg.text_sql_operator_and_value(safelocker)
                        terms.append(sql_p)
                elif arg.term == 'type':
                    if arg.negative:
                        not_terms.append(arg)
                    else:
                        tab_alias = 'ct' + str(jcounter)
                        jcounter = jcounter + 1
                        pre_where_clause = pre_where_clause + ' JOIN cardtype AS ' + \
                            tab_alias + ' ON bc.id = ' + tab_alias + '.basecard_id '
                        sql_p = ' ' + tab_alias + '.type_id = ' + str(arg.value)
                        terms.append(sql_p)
                elif arg.term == 'supertype':
                    if arg.negative:
                        not_terms.append(arg)
                    else:
                        tab_alias = 'cspt' + str(jcounter)
                        jcounter = jcounter + 1
                        pre_where_clause = pre_where_clause + ' JOIN cardsupertype AS ' + \
                            tab_alias + ' ON bc.id = ' + tab_alias + '.basecard_id '
                        sql_p = ' ' + tab_alias + '.supertype_id = ' + str(arg.value)
                        terms.append(sql_p)
                elif arg.term == 'subtype':
                    if arg.negative:
                        not_terms.append(arg)
                    else:
                        tab_alias = 'cst' + str(jcounter)
                        jcounter = jcounter + 1
                        pre_where_clause = pre_where_clause + ' JOIN cardsubtype AS ' + \
                            tab_alias + ' ON bc.id = ' + tab_alias + '.basecard_id '
                        sql_p = ' ' + tab_alias + '.subtype_id = ' + str(arg.value)
                        terms.append(sql_p)
                elif arg.term == 'layout':
                    sql_p = ' pc.layout ' + arg.text_sql_operator_and_value(safelocker)
                    terms.append(sql_p)

        sql_s = sql_s + pre_where_clause
        if len(terms) > 0:
            sql_s = sql_s + ' WHERE ' + ' AND '.join(terms)

        group_by_added = True
        sql_s = sql_s + ' GROUP BY pc.id '

        if len(not_terms) > 0:  # If we have to pull out some types and subtypes, we better do it now.
            # Let's execute the SQL we have (sql_s) but do it with cursor so that we do not instantiate any objects
            cursor = connection.cursor()
            cursor.execute(sql_s, params=safelocker)
            card_ids = cursor.fetchall()
            bc_ids = [row[1] for row in card_ids]
            if len(bc_ids) > 0:
                sql_s = 'SELECT c.id FROM physicalcard AS pc JOIN basecard AS bc ON pc.id = bc.physicalcard_id JOIN card AS c ON c.basecard_id = bc.id LEFT JOIN cardcolor AS cc ON cc.basecard_id = bc.id LEFT JOIN formatbasecard AS f ON f.basecard_id = bc.id LEFT JOIN cardrating AS cr ON cr.physicalcard_id = pc.id AND cr.test_id = 1 ' + \
                    pre_where_clause + ' WHERE bc.id IN (' + ','.join(str(i) for i in bc_ids) + ') '
                for arg in not_terms:
                    # Now that we have all of these ids, let's use them to filter out those types that we do not want.
                    try:
                        if arg.term == 'color':
                            sql_not = 'SELECT cc.basecard_id FROM cardcolor AS cc WHERE cc.color_id = \'' + \
                                str(arg.value) + '\' AND cc.basecard_id IN (' + ','.join(str(i) for i in bc_ids) + ')'
                            cursor.execute(sql_not)
                            not_basecard_ids = cursor.fetchall()
                            if len(not_basecard_ids) > 0:
                                sql_s = sql_s + ' AND bc.id NOT IN (' + ','.join(str(n[0]) for n in not_basecard_ids) + ') '
                        elif arg.term == 'type':
                            sql_not = 'SELECT ct.basecard_id FROM cardtype AS ct WHERE ct.type_id = ' + \
                                str(arg.value) + ' AND ct.basecard_id IN (' + ','.join(str(i) for i in bc_ids) + ')'
                            cursor.execute(sql_not)
                            not_basecard_ids = cursor.fetchall()
                            if len(not_basecard_ids) > 0:
                                sql_s = sql_s + ' AND bc.id NOT IN (' + ','.join(str(n[0]) for n in not_basecard_ids) + ') '
                        elif arg.term == 'subtype':
                            sql_not = 'SELECT cst.basecard_id FROM cardsubtype AS cst WHERE cst.subtype_id = ' + \
                                str(arg.value) + ' AND cst.basecard_id IN (' + ','.join(str(i) for i in bc_ids) + ')'
                            cursor.execute(sql_not)
                            not_basecard_ids = cursor.fetchall()
                            if len(not_basecard_ids) > 0:
                                sql_s = sql_s + ' AND bc.id NOT IN (' + ','.join(str(n[0]) for n in not_basecard_ids) + ') '
                    except ProgrammingError as pe:
                        logger.error("CardManager.search: SQL error in: {}".format(sql_not))
                        raise pe
                group_by_added = False

        if group_by_added:
            #sql_s = sql_s + ' , '
            pass
        else:
            sql_s = sql_s + ' GROUP BY ' + 'pc.id '
        #sql_s = sql_s + ' bc.id HAVING max(c.multiverseid) '
        #sql_s = sql_s + ' HAVING max(c.multiverseid) '

        sql_s = sql_s + ' ORDER BY '
        sql_s = sql_s + ', '.join(str(str(arg.sqlname()) + ' ' + arg.direction) for arg in sortds)

        logger = logging.getLogger(__name__)
        #logger.error("Card Search SQL: " + sql_s)

        cards = self.raw(sql_s, params=safelocker)

        return cards

    def get_simple_cards_list(self, card_names_to_skip=list()):
        result = list()
        #bcards = BaseCard.objects.filter(physicalcard_id__gt=7400, physicalcard_id__lt=7500).order_by('-filing_name')
        # These are cards that pretty much aren't going to be referenced - there are more false positives than actual hits.
        bcards = BaseCard.objects.exclude(name__in=card_names_to_skip).order_by('-filing_name')
        for basecard in bcards:
            card = basecard.physicalcard.get_latest_card()
            simple = {'name': basecard.name,
                      'cleanname': basecard.name,
                      'url_slug': card.url_slug(),
                      'name_len': len(basecard.name),
                      'multiverseid': card.multiverseid}
            result.append(simple)
            try:
                if basecard.name.index("'"):
                    simple = {'name': basecard.name.replace(u"'", u"’"),
                              'cleanname': basecard.name,
                              'url_slug': card.url_slug(),
                              'name_len': len(basecard.name),
                              'multiverseid': card.multiverseid}
                    result.append(simple)
            except ValueError:
                pass
            for sillydash in [u'–', u'—', u'‒', u'-']:
                try:
                    if basecard.name.index(sillydash):
                        simple = {'name': basecard.name.replace(sillydash, u'-'),
                                  'cleanname': basecard.name,
                                  'url_slug': card.url_slug(),
                                  'name_len': len(basecard.name),
                                  'multiverseid': card.multiverseid}
                        result.append(simple)
                except ValueError:
                    pass
                try:
                    if simple['name'].index('-'):
                        simple = {'name': basecard.name.replace('-', sillydash),
                                  'cleanname': basecard.name,
                                  'url_slug': card.url_slug(),
                                  'name_len': len(basecard.name),
                                  'multiverseid': card.multiverseid}
                        result.append(simple)
                except ValueError:
                    pass

        result = sorted(result, key=itemgetter('name_len'), reverse=True)
        return result

    class FormatNotSpecifiedException(Exception):
        pass


class SortDirective():
    ASC = 'ASC'
    DESC = 'DESC'
    term = None
    crs_format_id = None
    direction = ASC

    def sqlname(self):
        if self.term == 'name':
            return 'bc.filing_name'
        elif self.term == 'cmc':
            return 'bc.cmc'
        elif self.term == 'cardrating':
            return 'crs.mu'
        else:
            return self.term


class SearchPredicate():
    EQUALS = 0
    CONTAINS = 1
    LESS_THAN = 2
    GREATER_THAN = 3
    term = None
    negative = False
    operator = EQUALS
    value = None

    def numeric_sql_operator(self):
        res_s = ''
        if self.operator == self.LESS_THAN:
            if self.negative:
                res_s = res_s + ' >= '
            else:
                res_s = res_s + ' < '
        elif self.operator == self.GREATER_THAN:
            if self.negative:
                res_s = res_s + ' <= '
            else:
                res_s = res_s + ' > '
        else:  # assume equals
            if self.negative:
                res_s = res_s + ' <> '
            else:
                res_s = res_s + ' = '
        return res_s

    def text_sql_operator_and_value(self, param_bag):
        res_s = ''
        # assume equals
        if self.value is None:
            if self.negative:
                res_s = res_s + ' IS NOT NULL '
            else:
                res_s = res_s + ' IS NULL '
        else:
            ptoken = 'sarg' + str(param_bag['_counter'])
            if self.operator == self.CONTAINS:
                if self.negative:
                    res_s = res_s + ' NOT LIKE '
                else:
                    res_s = res_s + ' LIKE '
                #res_s = res_s + " '%%" + self.value + "%%' "
                param_bag[ptoken] = '%' + str(self.value) + '%'
            else:  # equality
                if self.negative:
                    res_s = res_s + ' != '
                else:
                    res_s = res_s + ' = '
                param_bag[ptoken] = str(self.value)
            res_s = res_s + ' %(' + ptoken + ')s '
            param_bag['_counter'] = param_bag['_counter'] + 1
        return res_s


class Card(models.Model):
    #id = models.IntegerField(primary_key=True)
    expansionset = models.ForeignKey('ExpansionSet')
    basecard = models.ForeignKey(BaseCard)
    rarity = models.ForeignKey(
        'Rarity',
        db_column='rarity',
        blank=True,
        null=True)
    multiverseid = models.IntegerField(unique=False, blank=True, null=False)
    flavor_text = models.CharField(max_length=1000, blank=True, null=True)
    card_number = models.CharField(max_length=6, blank=True, null=True)
    mark = models.ForeignKey('Mark', blank=True, null=True)
    created_at = models.DateTimeField(
        null=False,
        auto_now_add=True)
    updated_at = models.DateTimeField(
        null=False,
        auto_now=True)
    objects = models.Manager()
    playables = CardManager()

    def img_url(self):
        return '/img/' + str(self.multiverseid) + '.jpg'

    def mana_cost_html(self):
        return convertSymbolsToHTML(self.basecard.mana_cost)

    def rules_text_html(self):
        return convertSymbolsToHTML(self.basecard.rules_text)

    def flavor_text_html(self):
        return mark_safe(self.flavor_text)

    def url_slug(self):
        return self.basecard.filing_name.replace(' ', '-').lower()

    def get_double_faced_card(self):
        """
        Return the double-faced card for Innastrad (and similiar)
        cards. Returns None if there is no second side to the card. If
        it is double-faced, this will always return the other face
        (e.g., 'Delver of Secrerts' returns 'Insectile Aberation';
        'Insectile Aberation' returns 'Delver of Secrets').
        """
        result = None
        if self.basecard.physicalcard.layout != PhysicalCard.DOUBLE:
            return None
        face_needed = 'B'
        if self.basecard.cardposition == 'B':
            face_needed = 'F'
        qs = Card.objects.filter(
            basecard__cardposition=face_needed,
            basecard__physicalcard=self.basecard.physicalcard,
            expansionset_id=self.expansionset.id)
        try:
            result = qs[0]
        except KeyError:
            result = None
        return result

    class Meta:
        managed = True
        db_table = 'card'
        unique_together = ('expansionset', 'card_number', 'multiverseid')

    def __unicode__(self):
        return self.basecard.name + \
            "(" + self.expansionset.abbr + ") [" + str(self.multiverseid) + "]"


class CardColor(models.Model):
    #id = models.IntegerField(primary_key=True)
    basecard = models.ForeignKey(BaseCard)
    color = models.ForeignKey('Color')

    class Meta:
        managed = True
        db_table = 'cardcolor'
        unique_together = ('basecard', 'color',)


class CardSupertype(models.Model):
    #id = models.IntegerField(primary_key=True)
    basecard = models.ForeignKey(BaseCard)
    supertype = models.ForeignKey('Supertype')
    position = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cardsupertype'
        unique_together = ('basecard', 'position',)


class CardSubtype(models.Model):
    #id = models.IntegerField(primary_key=True)
    basecard = models.ForeignKey(BaseCard)
    subtype = models.ForeignKey('Subtype')
    position = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cardsubtype'
        unique_together = ('basecard', 'position',)


class CardType(models.Model):
    #id = models.IntegerField(primary_key=True)
    basecard = models.ForeignKey(BaseCard)
    type = models.ForeignKey('Type')
    position = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cardtype'
        unique_together = ('basecard', 'position',)

    def __unicode__(self):
        return str(
            self.id) + " [Card: " + str(
            self.basecard.id) + " (" + self.basecard.name + "), Type: " + str(
            self.type.id) + " (" + self.type.type + "), Position: " + str(
                self.position) + "]"


class FormatManager(models.Manager):

    def current_legal_formats(self, card):
        # Look up all of the formats where this card is currently legal.
        # formats = FormatBasecard.objects.filter(basecard__id=card.basecard.id,
        #                                        format__start_date__lte=datetime.today(),
        #                                        format__end_date__gte=datetime.today())
        formats = Format.objects.filter(formatbasecard__basecard_id=card.basecard.id,
                                        start_date__lte=datetime.today(),
                                        end_date__gte=datetime.today())
        return formats


class Format(models.Model):
    id = models.AutoField(primary_key=True)
    formatname = models.CharField(max_length=60, null=False)
    format = models.CharField(max_length=60, unique=True, null=False)
    abbr = models.CharField(max_length=6, unique=False, null=True)
    min_cards_main = models.IntegerField(null=False, default=60)
    max_cards_main = models.IntegerField(null=False, default=60)
    min_cards_side = models.IntegerField(null=False, default=0)
    max_cards_side = models.IntegerField(null=False, default=15)
    max_nonbl_card_count = models.IntegerField(null=False, default=4)
    uses_command_zone = models.BooleanField(default=False)
    validator = models.CharField(max_length=100, null=True)
    start_date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        null=True)
    end_date = models.DateField(auto_now=False, auto_now_add=False, null=True)

    objects = models.Manager()
    cards = FormatManager()

    class Meta:
        verbose_name_plural = 'Formats'
        db_table = 'format'

    def __unicode__(self):
        return str(
            self.id) + " [Format: " + str(self.formatname) + " (" + self.format + ")]"


class FormatBasecard(models.Model):
    format = models.ForeignKey(Format)
    basecard = models.ForeignKey(BaseCard)

    class Meta:
        verbose_name_plural = 'Format Base Cards'
        unique_together = ('format', 'basecard',)
        db_table = 'formatbasecard'

    def __unicode__(self):
        return "[Format: " + str(self.format.format) + " - " + \
            self.basecard.name + " (" + str(self.basecard.id) + ")]"


class Battle(models.Model):
    #id = models.IntegerField(primary_key=True)
    test = models.ForeignKey('BattleTest')
    format = models.ForeignKey('Format')
    winner_pcard = models.ForeignKey('PhysicalCard', related_name='winner')
    loser_pcard = models.ForeignKey('PhysicalCard', related_name='loser')
    battle_date = models.DateTimeField(
        auto_now_add=True,
        null=False)
    session_key = models.CharField(null=False, max_length=40)

    class Meta:
        verbose_name_plural = 'Battles'
        db_table = 'battle'
        unique_together = (
            'format',
            'winner_pcard',
            'loser_pcard',
            'session_key')

    def __unicode__(self):
        return "[Battle " + str(self.id) + ": " + str(self.winner_pcard.id) + \
            " > " + str(self.loser_pcard.id) + " in " + self.format.format + "]"


class BattleTest(models.Model):
    #id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = 'Battle Tests'
        db_table = 'battletest'


class CardRating(models.Model):
    id = models.AutoField(primary_key=True)
    physicalcard = models.ForeignKey('PhysicalCard')
    mu = models.FloatField(default=25.0, null=False)
    sigma = models.FloatField(default=25.0 / 3.0, null=False)
    test = models.ForeignKey('BattleTest')
    format = models.ForeignKey('Format')
    updated_at = models.DateTimeField(
        auto_now=True,
        null=False)

    def cardninjaRating(self):
        return self.mu * 20.0

    def confidence(self):
        return 100.0 * ((25.0 / 3.0) - self.sigma) / (25.0 / 3.0)

    class Meta:
        verbose_name_plural = 'Card Ratings'
        unique_together = ('physicalcard', 'format', 'test')
        db_table = 'cardrating'

    def __unicode__(self):
        return "[CardRating " + str(self.id) + ": " + str(self.physicalcard.id) + " mu=" + str(self.mu) + " sigma=" + str(
            self.sigma) + " for format \"" + str(self.format.format) + ", test \"" + str(self.test.name) + "\"]"


class CardKeyword(models.Model):
    #id = models.IntegerField(primary_key=True)
    physicalcard = models.ForeignKey(PhysicalCard)
    keyword = models.CharField(max_length=60, null=False)
    kwscore = models.FloatField(null=False)

    class Meta:
        managed = True
        db_table = 'cardkeyword'


class SimilarPhysicalCard(models.Model):
    #id = models.IntegerField(primary_key=True)
    score = models.FloatField(null=False)
    physicalcard = models.ForeignKey(PhysicalCard, related_name='physicalcard')
    sim_physicalcard = models.ForeignKey(PhysicalCard, related_name='simphysicalcard')

    class Meta:
        managed = True
        db_table = 'similarphysicalcard'
