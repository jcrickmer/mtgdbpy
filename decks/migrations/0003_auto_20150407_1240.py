# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0003_auto_20150320_1910'),
        ('decks', '0002_auto_20150407_0406'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tournament',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('url', models.CharField(max_length=500)),
                ('start_date', models.DateField()),
                ('format', models.ForeignKey(to='cards.Format')),
            ],
            options={
                'db_table': 'tournament',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TournamentDeck',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('place', models.IntegerField(default=1)),
                ('deck', models.ForeignKey(to='decks.Deck')),
                ('tournament', models.ForeignKey(to='decks.Tournament')),
            ],
            options={
                'db_table': 'tournamentdeck',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='tournamentdeck',
            unique_together=set([('deck', 'tournament')]),
        ),
    ]
