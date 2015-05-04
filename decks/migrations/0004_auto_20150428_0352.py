# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('decks', '0003_auto_20150407_1240'),
    ]

    operations = [
        migrations.CreateModel(
            name='DeckCluster',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('clusterkey', models.IntegerField(default=-1)),
                ('formatname', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'deckcluster',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeckClusterDeck',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('distance', models.FloatField(default=1000.0)),
                ('deck', models.ForeignKey(to='decks.Deck', unique=True)),
                ('deckcluster', models.ForeignKey(to='decks.DeckCluster')),
            ],
            options={
                'db_table': 'deckclusterdeck',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='deck',
            name='tournaments',
            field=models.ManyToManyField(to='decks.Tournament', through='decks.TournamentDeck'),
            preserve_default=True,
        ),
    ]
