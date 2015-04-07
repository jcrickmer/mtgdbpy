# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0003_auto_20150320_1910'),
        ('decks', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='deck',
            name='cards',
            field=models.ManyToManyField(to='cards.PhysicalCard', through='decks.DeckCard'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='deckcard',
            unique_together=set([('deck', 'physicalcard', 'board')]),
        ),
    ]
