# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-08-21 05:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('decks', '0006_auto_20150515_0112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deckclusterdeck',
            name='deck',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='decks.Deck'),
        ),
    ]