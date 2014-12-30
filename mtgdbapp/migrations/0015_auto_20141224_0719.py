# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


def load_types(apps, schema_editor):
    # Make sure that all of the foundational data for colors is in the
    # database.
    Type = apps.get_model('mtgdbapp', 'Type')
    for tt in [[1, 'Artifact'],
               [2, 'Basic'],
               [3, 'Creature'],
               [4, 'Enchantment'],
               [5, 'Instant'],
               [6, 'Land'],
               [7, 'Legendary'],
               [8, 'Ongoing'],
               [9, 'Phenomenon'],
               [10, 'Plane'],
               [11, 'Planeswalker'],
               [12, 'Scheme'],
               [13, 'Snow'],
               [14, 'Sorcery'],
               [15, 'Tribal'],
               [16, 'Vanguard'],
               [17, 'World'],
               [18, 'Conspiracy']]:
        curT = None
        try:
            curT = Type.objects.get(pk=tt[0])
        except Type.DoesNotExist:
            curT = Type(id=tt[0])
        curT.type = tt[1]
        curT.save()


def unload_types(apps, schema_editor):
    Type = apps.get_model('mtgdbapp', 'Type')
    # Let's actually not do anything here.


def load_formats(apps, schema_editor):
    # Make sure that all of the foundational data for formats is in the
    # database.
    Format = apps.get_model('mtgdbapp', 'Format')
    for ff in [[1, 'Modern', 'Modern_2014-09-26', datetime.datetime(2014, 9, 26), datetime.datetime(2015, 1, 23)],
               [2, 'Modern', 'Modern_2014-07-18', datetime.datetime(2014, 7, 18), datetime.datetime(2014, 9, 25)],
               [3, 'Modern', 'Modern_2014-05-02', datetime.datetime(2014, 5, 2), datetime.datetime(2014, 7, 17)],
               [4, 'Standard', 'Standard_2014-09-26', datetime.datetime(2014, 9, 26), datetime.datetime(2015, 1, 23)],
               [5, 'Standard', 'Standard_2014-07-18', datetime.datetime(2014, 7, 18), datetime.datetime(2014, 9, 25)],
               [6, 'Standard', 'Standard_2014-05-02', datetime.datetime(2014, 5, 2), datetime.datetime(2014, 7, 17)],
               [7, 'Standard', 'Standard_2014-02-07', datetime.datetime(2014, 2, 7), datetime.datetime(2014, 5, 1)],
               [8, 'Standard', 'Standard_2013-09-27', datetime.datetime(2013, 9, 27), datetime.datetime(2014, 2, 6)],
               [9, 'Standard', 'Standard_2013-07-19', datetime.datetime(2013, 7, 19), datetime.datetime(2013, 9, 26)],
               [10, 'Standard', 'Standard_2013-05-03', datetime.datetime(2013, 5, 3), datetime.datetime(2013, 7, 18)],
               [11, 'Standard', 'Standard_2013-02-01', datetime.datetime(2013, 2, 1), datetime.datetime(2013, 5, 2)],
               [12, 'Standard', 'Standard_2012-10-05', datetime.datetime(2012, 10, 5), datetime.datetime(2013, 1, 31)],
               [13, 'Commander', 'Commander_2014-11-07', datetime.datetime(2014, 11, 7), datetime.datetime(2015, 1, 23)],
               ]:
        curF = None
        try:
            curF = Format.objects.get(pk=ff[0])
        except Format.DoesNotExist:
            curF = Format(id=ff[0])
        curF.formatname = ff[1]
        curF.format = ff[2]
        curF.start_date = ff[3]
        curF.end_date = ff[4]
        curF.save()


def load_battletests(apps, schema_editor):
    # Make sure that all of the foundational data for formats is in the
    # database.
    BattleTest = apps.get_model('mtgdbapp', 'BattleTest')
    test = None
    try:
        test = BattleTest.objects.get(pk=1)
    except BattleTest.DoesNotExist:
        test = BattleTest(id=1)
    test.name = 'subjective'
    test.save()


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0014_auto_20141224_0440'),
    ]

    operations = [
        migrations.RunPython(load_types, unload_types),
        migrations.RunPython(load_formats),
        migrations.RunPython(load_battletests),
    ]
