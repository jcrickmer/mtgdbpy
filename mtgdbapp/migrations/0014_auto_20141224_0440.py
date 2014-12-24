# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
#from mtgdbapp.models import Color

def load_colors(apps, schema_editor):
	# Make sure that all of the foundational data for colors is in the database.
	Color = apps.get_model('mtgdbapp','Color')
	for cc in [['W','White'],['U','Blue'],['B','Black'],['R','Red'],['G','Green'],['c','Colorless']]:
		curColor = None
		try:
			curColor = Color.objects.get(pk=cc[0])
		except Color.DoesNotExist:
			curColor = Color()
			curColor.id = cc[0]
		curColor.color = cc[1]
		curColor.save()

def load_colors2(apps, schema_editor):
	Color = apps.get_model('mtgdbapp','Color')
	db_alias = schema_editor.connection.alias
	Color.objects.using(db_alias).bulk_create([
		Color(id='W',color='White'),
		Color(id='U',color='Blue'),
		Color(id='B',color='Black'),
		Color(id='R',color='Red'),
		Color(id='G',color='Green'),
		Color(id='c',color='Colorless'),
    ])

def unload_colors(apps, schema_editor):
	Color = apps.get_model('mtgdbapp','Color')
	Color.objects.all().delete()


def load_rarities(apps, schema_editor):
	# Make sure that all of the foundational data for colors is in the database.
	Rarity = apps.get_model('mtgdbapp','Rarity')
	for rr in [['b','Basic Land', 0],['c','Common',1],['u','Uncommon',2],['r','Rare',3],['m','Mythic Rare',4],['s','Special',5]]:
		curR = None
		try:
			curR = Rarity.objects.get(pk=rr[0])
		except Rarity.DoesNotExist:
			curR = Rarity(id=rr[0])
		curR.rarity = rr[1]
		curR.sortorder = rr[2]
		curR.save()

def unload_rarities(apps, schema_editor):
	Rarity = apps.get_model('mtgdbapp','Rarity')
	Rarity.objects.all().delete()

class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0013_auto_20141212_0426'),
    ]

    operations = [
		migrations.RunPython(load_colors, unload_colors),
		migrations.RunPython(load_rarities, unload_rarities),
    ]
