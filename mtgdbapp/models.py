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

from mtgdbapp.view_utils import convertSymbolsToHTML
from django.utils.safestring import mark_safe

class AuthGroup(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    class Meta:
        managed = True
        db_table = 'auth_group'

class AuthGroupPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    group_id = models.IntegerField()
    permission_id = models.IntegerField()
    class Meta:
        managed = True
        db_table = 'auth_group_permissions'

class AuthPermission(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    content_type_id = models.IntegerField()
    codename = models.CharField(max_length=100)
    class Meta:
        managed = True
        db_table = 'auth_permission'

class AuthUser(models.Model):
    id = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField()
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=75)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    class Meta:
        managed = True
        db_table = 'auth_user'

class AuthUserGroups(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    group_id = models.IntegerField()
    class Meta:
        managed = True
        db_table = 'auth_user_groups'

class AuthUserUserPermissions(models.Model):
    id = models.IntegerField(primary_key=True)
    user_id = models.IntegerField()
    permission_id = models.IntegerField()
    class Meta:
        managed = True
        db_table = 'auth_user_user_permissions'

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
	#    id = models.IntegerField(primary_key=True)
    type = models.CharField(max_length=128)
    class Meta:
        managed = True
        db_table = 'types'
    def __unicode__(self):
        return self.type

class Subtype(models.Model):
	#    id = models.IntegerField(primary_key=True)
	subtype = models.CharField(max_length=128)
	class Meta:
		managed = True
		db_table = 'subtypes'
	def __unicode__(self):
		return self.subtype

class PhysicalCard(models.Model):
	#	 id = models.IntegerField(primary_key=True)
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
	LAYOUT_CHOICES = ((NORMAL , 'normal'), (SPLIT , 'split'), (FLIP , 'flip'), (DOUBLE , 'double-faced'), (TOKEN , 'token'), (PLANE , 'plane'), (SCHEME , 'scheme'), (PHENOMENON , 'phenomenon'), (LEVELER , 'leveler'), (VANGUARD , 'vanguard'))
	layout = models.CharField(max_length=12, choices=LAYOUT_CHOICES, default=NORMAL)

	def getCardRating(self, format_id, test_id):
		# shortcut to get the CardRating for a given format and test.
		# This is accessible in templates
		return self.cardrating_set.get(format__id=format_id, test__id=test_id)
	pass

	class Meta:
		managed = True
		db_table = 'physicalcards'
		verbose_name_plural = 'Physical Cards'
	def __unicode__(self):
		return "[PhysicalCard " + str(self.id) + "]"


class BaseCard(models.Model):
	#	 id = models.IntegerField(primary_key=True)
	physicalcard = models.ForeignKey(PhysicalCard)
	name = models.CharField(max_length=128, unique=True)
	filing_name = models.CharField(max_length=128, default='')
	rules_text = models.CharField(max_length=1000, blank=True)
	mana_cost = models.CharField(max_length=60, null=False)
	cmc = models.IntegerField(null=False, default=0)
	power = models.CharField(max_length=4, null=True, blank=True)
	toughness = models.CharField(max_length=4, null=True, blank=True)
	loyalty = models.CharField(max_length=4, null=True, blank=True)
	created_at = models.DateTimeField(default=timezone.now, null=False, blank=True, auto_now_add=True)
	updated_at = models.DateTimeField(default=timezone.now, null=False, blank=True, auto_now=True)
	cardposition = models.CharField(max_length=1, null=False, default='F')
	types = models.ManyToManyField(Type, through='CardType')
	subtypes = models.ManyToManyField(Subtype, through='CardSubtype')
	colors = models.ManyToManyField(Color, through='CardColor')
	def get_rulings(self):
		return Ruling.objects.filter(basecard=self.id).order_by('ruling_date')
	class Meta:
		managed = True
		db_table = 'basecards'
		verbose_name_plural = 'Base Cards'
		unique_together = ('physicalcard', 'cardposition',)
	def __unicode__(self):
		return self.name + ' (physicalcard.id=' + str(self.physicalcard.id) + ')'
	def save(self):
		# We should always set the CMC to the value that is indicated mana_cost field
		self.cmc = 1;
		super(BaseCard, self).save()


class Ruling(models.Model):
	#	 id = models.IntegerField(primary_key=True)
	basecard = models.ForeignKey(BaseCard)
	ruling_text = models.TextField(null=False)
	ruling_date = models.DateField(null=False, blank=False)
	class Meta:
		verbose_name_plural = 'Rulings'
	def __unicode__(self):
		return "Ruling " + str(self.id) + " for " + self.basecard.name


class ExpansionSet(models.Model):
	#	id = models.IntegerField(primary_key=True)
	name = models.CharField(unique=True, max_length=128)
	abbr = models.CharField(unique=False, max_length=6)
	class Meta:
		managed = True
		db_table = 'expansionsets'
		verbose_name_plural = 'Expansion Sets'
	def __unicode__(self):
		return self.name + " (" + self.abbr + ")" 

class Mark(models.Model):
	#	id = models.IntegerField(primary_key=True)
	mark = models.CharField(max_length=128)
	class Meta:
		managed = True
		db_table = 'marks'
	def __unicode__(self):
		return self.mark

class Card(models.Model):
	#	id = models.IntegerField(primary_key=True)
	expansionset = models.ForeignKey('ExpansionSet')
	basecard = models.ForeignKey(BaseCard)
	rarity = models.ForeignKey('Rarity', db_column='rarity', blank=True, null=True)
	multiverseid = models.IntegerField(unique=False, blank=True, null=False)
	flavor_text = models.CharField(max_length=1000, blank=True, null=True)
	card_number = models.CharField(max_length=6, blank=True, null=True)
	mark = models.ForeignKey('Mark', blank=True, null=True)
	created_at = models.DateTimeField(default=timezone.now, null=False, blank=True, auto_now_add=True)
	updated_at = models.DateTimeField(default=timezone.now, null=False, blank=True, auto_now=True)
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
	class Meta:
		managed = True
		db_table = 'cards'
		unique_together = ('expansionset', 'card_number',)
	def __unicode__(self):
		return self.basecard.name + "(" + self.expansionset.abbr + ") [" + str(self.multiverseid) + "]"

class CardColor(models.Model):
	#	id = models.IntegerField(primary_key=True)
	basecard = models.ForeignKey(BaseCard)
	color = models.ForeignKey('Color')
	class Meta:
		managed = True
		db_table = 'cardcolors'
		unique_together = ('basecard', 'color',)

class CardSubtype(models.Model):
	#	id = models.IntegerField(primary_key=True)
	basecard = models.ForeignKey(BaseCard)
	subtype = models.ForeignKey('Subtype')
	position = models.IntegerField()
	class Meta:
		managed = True
		db_table = 'cardsubtypes'
		unique_together = ('basecard', 'position',)

class CardType(models.Model):
	#	id = models.IntegerField(primary_key=True)
	basecard = models.ForeignKey(BaseCard)
	type = models.ForeignKey('Type')
	position = models.IntegerField()
	class Meta:
		managed = True
		db_table = 'cardtypes'
		unique_together = ('basecard', 'position',)
	def __unicode__(self):
		return str(self.id) + " [Card: " + str(self.basecard.id) + " (" + self.basecard.name + "), Type: " + str(self.type.id) + " (" + self.type.type + "), Position: " + str(self.position) + "]"

class Format(models.Model):
	id = models.IntegerField(primary_key=True)
	formatname = models.CharField(max_length=60, null=False)
	format = models.CharField(max_length=60, unique=True, null=False)
	start_date = models.DateField(auto_now=False, auto_now_add=False, null=True)
	end_date = models.DateField(auto_now=False, auto_now_add=False, null=True)
	def __unicode__(self):
		return str(self.id) + " [Format: " + str(self.formatname) + " (" + self.format + ")]"
	
class FormatBasecard(models.Model):
	format = models.ForeignKey(Format)
	basecard = models.ForeignKey(BaseCard)
	class Meta:
		verbose_name_plural = 'Format Base Cards'
		unique_together = ('format', 'basecard',)
	def __unicode__(self):
		return "[Format: " + str(self.format.format) + " - " + self.basecard.name + " (" + str(self.basecard.id) + ")]"

class Battle(models.Model):
	#id = models.IntegerField(primary_key=True)
	test = models.ForeignKey('BattleTest')
	format = models.ForeignKey('Format')
	winner_pcard = models.ForeignKey('PhysicalCard', related_name='winner')
	loser_pcard = models.ForeignKey('PhysicalCard', related_name='loser')
	battle_date = models.DateTimeField(auto_now=True, auto_now_add=True, null=False)
	session_key = models.CharField(null=False, max_length=40)
	class Meta:
		verbose_name_plural = 'Battles'
		unique_together = ('format', 'winner_pcard','loser_pcard','session_key')
	def __unicode__(self):
		return "[Battle " + str(self.id) + ": " + str(self.winner_pcard.id) + " > " + str(self.loser_pcard.id) + " in " + self.format.format + "]"

class BattleTest(models.Model):
	#id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=100)

class CardRating(models.Model):
	id = models.AutoField(primary_key=True)
	physicalcard = models.ForeignKey('PhysicalCard')
	mu = models.FloatField(default=25.0, null=False)
	sigma = models.FloatField(default=25.0/3.0, null=False)
	test = models.ForeignKey('BattleTest')
	format = models.ForeignKey('Format')
	updated_at = models.DateTimeField(default=timezone.now, auto_now=True, null=False)
	def cardninjaRating(self):
		return self.mu * 20.0
	def confidence(self):
		return 100.0 * ( (25.0/3.0) - self.sigma ) / (25.0/3.0)
	class Meta:
		verbose_name_plural = 'Card Ratings'
		unique_together = ('physicalcard', 'format', 'test')
	def __unicode__(self):
		return "[CardRating " + str(self.id) + ": " + str(self.physicalcard.id) + " mu=" + str(self.mu) + " sigma=" + str(self.sigma) + " for format \"" + str(self.format.format) + ", test \"" + str(self.test.name) + "\"]"
	
class DjangoAdminLog(models.Model):
	id = models.IntegerField(primary_key=True)
	action_time = models.DateTimeField()
	user_id = models.IntegerField()
	content_type_id = models.IntegerField(blank=True, null=True)
	object_id = models.TextField(blank=True)
	object_repr = models.CharField(max_length=200)
	action_flag = models.IntegerField()
	change_message = models.TextField()
	class Meta:
		managed = True
		db_table = 'django_admin_log'

class DjangoContentType(models.Model):
	id = models.IntegerField(primary_key=True)
	name = models.CharField(max_length=100)
	app_label = models.CharField(max_length=100)
	model = models.CharField(max_length=100)
	class Meta:
		managed = True
		db_table = 'django_content_type'

class DjangoSession(models.Model):
	session_key = models.CharField(primary_key=True, max_length=40)
	session_data = models.TextField()
	expire_date = models.DateTimeField()
	class Meta:
		managed = True
		db_table = 'django_session'

