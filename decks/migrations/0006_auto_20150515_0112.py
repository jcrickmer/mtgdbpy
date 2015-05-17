# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0003_auto_20150320_1910'),
        ('decks', '0005_tournament_end_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='FormatCardStat',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('occurence_count', models.IntegerField(default=0)),
                ('deck_count', models.IntegerField(default=0)),
                ('average_card_count_in_deck', models.FloatField(default=0.0)),
                ('percentage_of_all_cards', models.FloatField(default=0.0)),
                ('format', models.ForeignKey(to='cards.Format')),
                ('physicalcard', models.ForeignKey(to='cards.PhysicalCard')),
            ],
            options={
                'db_table': 'formatcardstat',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FormatStat',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('tournamentdeck_count', models.IntegerField(default=0)),
                ('tournamentdeckcard_count', models.IntegerField(default=0)),
                ('format', models.ForeignKey(to='cards.Format')),
            ],
            options={
                'db_table': 'formatstat',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='formatcardstat',
            unique_together=set([('format', 'physicalcard')]),
        ),
    ]
