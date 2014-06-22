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
	class Meta:
		managed = True
		db_table = 'physicalcards'
		verbose_name_plural = 'Physical Cards'
	def __unicode__(self):
		return self.name

class BaseCard(models.Model):
	#	 id = models.IntegerField(primary_key=True)
	physicalcard = models.ForeignKey(PhysicalCard)
	name = models.CharField(max_length=128, unique=True)
	rules_text = models.CharField(max_length=1000, blank=True)
	mana_cost = models.CharField(max_length=60, null=False)
	cmc = models.IntegerField(null=False, default=0)
	power = models.CharField(max_length=4, null=True, blank=True)
	toughness = models.CharField(max_length=4, null=True, blank=True)
	loyalty = models.CharField(max_length=4, null=True, blank=True)
	created_at = models.DateTimeField(default=datetime.now, null=False, blank=True)
	updated_at = models.DateTimeField(default=datetime.now, null=False, blank=True)
	cardposition = models.CharField(max_length=1, null=False, default='F')
	types = models.ManyToManyField(Type, through='CardType')
	subtypes = models.ManyToManyField(Subtype, through='CardSubtype')
	colors = models.ManyToManyField(Color, through='CardColor')
	class Meta:
		managed = True
		db_table = 'basecards'
		verbose_name_plural = 'Base Cards'
		unique_together = ('physicalcard', 'cardposition',)
	def __unicode__(self):
		return self.name
	def save(self):
		# We should always set the CMC to the value that is indicated mana_cost field
		self.cmc = 1;
		super(BaseCard, self).save()

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
	multiverseid = models.IntegerField(unique=True, blank=True, null=False)
	flavor_text = models.CharField(max_length=1000, blank=True, null=True)
	card_number = models.CharField(max_length=6, blank=True, null=True)
	mark = models.ForeignKey('Mark', blank=True, null=True)
	created_at = models.DateTimeField(default=datetime.now, null=False, blank=True)
	updated_at = models.DateTimeField(default=datetime.now, null=False, blank=True)
	class Meta:
		managed = True
		db_table = 'cards'
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

