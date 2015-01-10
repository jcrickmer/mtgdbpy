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

from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

from mtgdbapp.view_utils import convertSymbolsToHTML
from django.utils.safestring import mark_safe

from django.db.models import Max, Min, Count
from django.db import connection


class Color(models.Model):
    id = models.CharField(primary_key=True, max_length=1)
    color = models.CharField(max_length=9)

    class Meta:
        managed = True
        db_table = 'colors'

    def __unicode__(self):
        return self.color


class Rarity(models.Model):
    id = models.CharField(primary_key=True, max_length=1)
    rarity = models.CharField(max_length=11)
    sortorder = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'rarities'
        verbose_name_plural = 'Rarities'

    def __unicode__(self):
        return self.rarity


class Type(models.Model):
    #id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=128, unique=True)

    class Meta:
        managed = True
        db_table = 'types'

    def __unicode__(self):
        return self.type


class Subtype(models.Model):
    #id = models.IntegerField(primary_key=True)
    subtype = models.CharField(max_length=128, unique=True)

    class Meta:
        managed = True
        db_table = 'subtypes'

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

    def get_cardrating_safe(self, format_id, test_id):
        try:
            return self.get_cardrating(format_id, test_id)
        except CardRating.DoesNotExist:
            # , format=Format.objects.get(pk=format_id), test=BattleTest.objects.get(pk=test_id))
            return CardRating(physicalcard=self)

    pass

    class Meta:
        managed = True
        db_table = 'physicalcards'
        verbose_name_plural = 'Physical Cards'

    def __unicode__(self):
        return "[PhysicalCard " + str(self.id) + "]"


class BaseCard(models.Model):
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
        default=timezone.now,
        null=False,
        auto_now_add=True)
    updated_at = models.DateTimeField(
        default=timezone.now,
        null=False,
        auto_now=True)
    cardposition = models.CharField(max_length=1, null=False, default='F')
    types = models.ManyToManyField(Type, through='CardType')
    subtypes = models.ManyToManyField(Subtype, through='CardSubtype')
    colors = models.ManyToManyField(Color, through='CardColor')

    def __setattr__(self, attrname, val):
        super(BaseCard, self).__setattr__(attrname, val)

        if attrname == 'name':
            self.filing_name = self.make_filing_name(val)

        if attrname == 'mana_cost':
            # REVISIT!
            self.cmc = 1

    def get_rulings(self):
        return Ruling.objects.filter(basecard=self.id).order_by('ruling_date')

    def make_filing_name(self, name):
        # REVISIT- Currently filing name logic is in Perl. See
        # MTG::Util::makeFilingName in the mtgstats project. We need
        # to get that moved to Python
        return name.lower()

    class Meta:
        managed = True
        db_table = 'basecards'
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

    def __unicode__(self):
        return "Ruling " + str(self.id) + " for " + self.basecard.name


class ExpansionSet(models.Model):
    #id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=128)
    abbr = models.CharField(unique=False, max_length=6)

    class Meta:
        managed = True
        db_table = 'expansionsets'
        verbose_name_plural = 'Expansion Sets'

    def __unicode__(self):
        return self.name + " (" + self.abbr + ")"


class Mark(models.Model):
    #id = models.IntegerField(primary_key=True)
    mark = models.CharField(max_length=128)

    class Meta:
        managed = True
        db_table = 'marks'

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
        #sql = 'SELECT bc.name, max(c.multiverseid), pc.id, cr.mu FROM physicalcards pc JOIN basecards bc ON pc.id = bc.physicalcard_id JOIN cards c ON bc.id = c.basecard_id JOIN mtgdbapp_cardrating cr ON cr.physicalcard_id = pc.id WHERE cr.format_id = ' + str(format_id) + ' AND cr.test_id = ' + str(test_id) + ' GROUP BY pc.id ORDER BY cr.mu'
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
            'SELECT c.id FROM physicalcards pc JOIN basecards bc ON pc.id = bc.physicalcard_id JOIN cards c ON bc.id = c.basecard_id JOIN mtgdbapp_cardrating cr ON cr.physicalcard_id = pc.id WHERE cr.format_id = ' +
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
        test_id = 1

        pre_where_clause = ''
        sql_s = '''SELECT c.id, c.basecard_id FROM physicalcards AS pc JOIN basecards AS bc ON pc.id = bc.physicalcard_id JOIN cards AS c ON c.basecard_id = bc.id JOIN cardtypes AS ct ON ct.basecard_id = bc.id LEFT JOIN cardsubtypes cst ON cst.basecard_id = bc.id LEFT JOIN cardcolors AS cc ON cc.basecard_id = bc.id LEFT JOIN mtgdbapp_formatbasecard AS f ON f.basecard_id = bc.id LEFT JOIN mtgdbapp_cardrating AS cr ON cr.physicalcard_id = pc.id AND cr.test_id = 1 '''

        terms = []
        not_terms = []
        sortds = []
        specified_format = None

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
                    sql_p = ' f.format_id = ' + str(arg.value) + ' '
                    terms.append(sql_p)

        if len(sortds) == 0:
            namesort = SortDirective()
            namesort.term = 'name'
            sortds.append(namesort)
        else:
            # go through the sort directives and andle card rating sorting, if needed
            for sd in sortds:
                # If we are sorting for card rating, we need to inject into the search criteria the format that we care about.
                if sd.term == 'cardrating':
                    pre_where_clause = ' LEFT JOIN mtgdbapp_cardrating AS crs ON crs.physicalcard_id = pc.id AND crs.test_id = 1 AND crs.format_id = ' + str(sd.crs_format_id)

        # Now we can process all of the other terms
        for arg in all_args:
            if isinstance(arg, SearchPredicate):
                if (arg.term == 'name'):
                    orc = []
                    for fieldname in ['bc.name', 'bc.filing_name']:
                        sql_p = fieldname
                        sql_p = sql_p + arg.text_sql_operator_and_value()
                        orc.append(sql_p)
                    if arg.negative:
                        terms.append('(' + ' AND '.join(orc) + ')')
                    else:
                        terms.append('(' + ' OR '.join(orc) + ')')
                elif arg.term == 'rules':
                    sql_p = ' bc.rules_text '
                    sql_p = sql_p + arg.text_sql_operator_and_value()
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
                    sql_p = sql_p + arg.text_sql_operator_and_value()
                    terms.append(sql_p)
                elif arg.term == 'color':
                    if arg.negative:
                        not_terms.append(arg)
                    else:
                        sql_p = ' cc.color_id '
                        sql_p = sql_p + arg.text_sql_operator_and_value()
                        terms.append(sql_p)
                elif arg.term == 'type':
                    if arg.negative:
                        not_terms.append(arg)
                    else:
                        sql_p = ' ct.type_id = ' + str(arg.value)
                        terms.append(sql_p)
                elif arg.term == 'subtype':
                    if arg.negative:
                        not_terms.append(arg)
                    else:
                        sql_p = ' cst.subtype_id = ' + str(arg.value)
                        terms.append(sql_p)
                elif arg.term == 'layout':
                    sql_p = ' pc.layout ' + arg.text_sql_operator_and_value()
                    terms.append(sql_p)

        sql_s = sql_s + pre_where_clause
        if len(terms) > 0:
            sql_s = sql_s + ' WHERE ' + ' AND '.join(terms)

        sql_s = sql_s + ' GROUP BY pc.id'

        if len(not_terms) > 0:  # If we have to pull out some types and subtypes, we better do it now.
            # Let's execute the SQL we have (sql_s) but do it with cursor so that we do not instantiate any objects
            cursor = connection.cursor()
            cursor.execute(sql_s)
            card_ids = cursor.fetchall()
            bc_ids = [row[1] for row in card_ids]

            sql_s = 'SELECT c.id FROM physicalcards AS pc JOIN basecards AS bc ON pc.id = bc.physicalcard_id JOIN cards AS c ON c.basecard_id = bc.id JOIN cardtypes AS ct ON ct.basecard_id = bc.id LEFT JOIN cardsubtypes cst ON cst.basecard_id = bc.id LEFT JOIN cardcolors AS cc ON cc.basecard_id = bc.id LEFT JOIN mtgdbapp_formatbasecard AS f ON f.basecard_id = bc.id LEFT JOIN mtgdbapp_cardrating AS cr ON cr.physicalcard_id = pc.id AND cr.test_id = 1 ' + \
                pre_where_clause + ' WHERE bc.id IN (' + ','.join(str(i) for i in bc_ids) + ') '
            for arg in not_terms:
                # Now that we have all of these ids, let's use them to filter out those types that we do not want.
                if arg.term == 'color':
                    sql_not = 'SELECT cc.basecard_id FROM cardcolors AS cc WHERE cc.color_id = \'' + \
                        str(arg.value) + '\' AND cc.basecard_id IN (' + ','.join(str(i) for i in bc_ids) + ')'
                    cursor.execute(sql_not)
                    not_basecard_ids = cursor.fetchall()
                    if len(not_basecard_ids) > 0:
                        sql_s = sql_s + ' AND bc.id NOT IN (' + ','.join(str(n[0]) for n in not_basecard_ids) + ') '
                elif arg.term == 'type':
                    sql_not = 'SELECT ct.basecard_id FROM cardtypes AS ct WHERE ct.type_id = ' + \
                        str(arg.value) + ' AND ct.basecard_id IN (' + ','.join(str(i) for i in bc_ids) + ')'
                    cursor.execute(sql_not)
                    not_basecard_ids = cursor.fetchall()
                    if len(not_basecard_ids) > 0:
                        sql_s = sql_s + ' AND bc.id NOT IN (' + ','.join(str(n[0]) for n in not_basecard_ids) + ') '
                elif arg.term == 'subtype':
                    sql_not = 'SELECT cst.basecard_id FROM cardsubtypes AS cst WHERE cst.subtype_id = ' + \
                        str(arg.value) + ' AND cst.basecard_id IN (' + ','.join(str(i) for i in bc_ids) + ')'
                    cursor.execute(sql_not)
                    not_basecard_ids = cursor.fetchall()
                    if len(not_basecard_ids) > 0:
                        sql_s = sql_s + ' AND bc.id NOT IN (' + ','.join(str(n[0]) for n in not_basecard_ids) + ') '

            sql_s = sql_s + ' GROUP BY bc.id HAVING max(c.multiverseid)'

        sql_s = sql_s + ' ORDER BY '
        sql_s = sql_s + ', '.join(str(str(arg.sqlname()) + ' ' + arg.direction) for arg in sortds)

        cards = self.raw(sql_s)

        return cards

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

    def text_sql_operator_and_value(self):
        res_s = ''
        # assume equals
        if self.value is None:
            if self.negative:
                res_s = res_s + ' IS NOT NULL '
            else:
                res_s = res_s + ' IS NULL '
        else:
            if self.operator == self.CONTAINS:
                if self.negative:
                    res_s = res_s + ' NOT LIKE '
                else:
                    res_s = res_s + ' LIKE '
                res_s = res_s + " '%%" + self.value + "%%' "
            else:  # equality
                if self.negative:
                    res_s = res_s + ' != '
                else:
                    res_s = res_s + ' = '
                res_s = res_s + " '" + self.value + "' "
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
        default=timezone.now,
        null=False,
        auto_now_add=True)
    updated_at = models.DateTimeField(
        default=timezone.now,
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
        db_table = 'cards'
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
        db_table = 'cardcolors'
        unique_together = ('basecard', 'color',)


class CardSubtype(models.Model):
    #id = models.IntegerField(primary_key=True)
    basecard = models.ForeignKey(BaseCard)
    subtype = models.ForeignKey('Subtype')
    position = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cardsubtypes'
        unique_together = ('basecard', 'position',)


class CardType(models.Model):
    #id = models.IntegerField(primary_key=True)
    basecard = models.ForeignKey(BaseCard)
    type = models.ForeignKey('Type')
    position = models.IntegerField()

    class Meta:
        managed = True
        db_table = 'cardtypes'
        unique_together = ('basecard', 'position',)

    def __unicode__(self):
        return str(
            self.id) + " [Card: " + str(
            self.basecard.id) + " (" + self.basecard.name + "), Type: " + str(
            self.type.id) + " (" + self.type.type + "), Position: " + str(
                self.position) + "]"


class Format(models.Model):
    id = models.IntegerField(primary_key=True)
    formatname = models.CharField(max_length=60, null=False)
    format = models.CharField(max_length=60, unique=True, null=False)
    start_date = models.DateField(
        auto_now=False,
        auto_now_add=False,
        null=True)
    end_date = models.DateField(auto_now=False, auto_now_add=False, null=True)

    def __unicode__(self):
        return str(
            self.id) + " [Format: " + str(self.formatname) + " (" + self.format + ")]"


class FormatBasecard(models.Model):
    format = models.ForeignKey(Format)
    basecard = models.ForeignKey(BaseCard)

    class Meta:
        verbose_name_plural = 'Format Base Cards'
        unique_together = ('format', 'basecard',)

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
        auto_now=True,
        auto_now_add=True,
        null=False)
    session_key = models.CharField(null=False, max_length=40)

    class Meta:
        verbose_name_plural = 'Battles'
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


class CardRating(models.Model):
    id = models.AutoField(primary_key=True)
    physicalcard = models.ForeignKey('PhysicalCard')
    mu = models.FloatField(default=25.0, null=False)
    sigma = models.FloatField(default=25.0 / 3.0, null=False)
    test = models.ForeignKey('BattleTest')
    format = models.ForeignKey('Format')
    updated_at = models.DateTimeField(
        default=timezone.now,
        auto_now=True,
        null=False)

    def cardninjaRating(self):
        return self.mu * 20.0

    def confidence(self):
        return 100.0 * ((25.0 / 3.0) - self.sigma) / (25.0 / 3.0)

    class Meta:
        verbose_name_plural = 'Card Ratings'
        unique_together = ('physicalcard', 'format', 'test')

    def __unicode__(self):
        return "[CardRating " + str(self.id) + ": " + str(self.physicalcard.id) + " mu=" + str(self.mu) + " sigma=" + str(
            self.sigma) + " for format \"" + str(self.format.format) + ", test \"" + str(self.test.name) + "\"]"
