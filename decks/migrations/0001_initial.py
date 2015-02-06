# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Deck',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('url', models.CharField(max_length=500)),
                ('visibility', models.CharField(default='visible', max_length=12, choices=[('visible', 'visible'), ('hidden', 'hidden')])),
                ('authorname', models.CharField(max_length=100)),
                ('format', models.ForeignKey(to='cards.Format')),
            ],
            options={
                'db_table': 'deck',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeckCard',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('cardcount', models.IntegerField(default=1)),
                ('board', models.CharField(default='main', max_length=8, choices=[('main', 'main'), ('side', 'side')])),
                ('deck', models.ForeignKey(to='decks.Deck')),
                ('physicalcard', models.ForeignKey(to='cards.PhysicalCard')),
            ],
            options={
                'db_table': 'deckcard',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='deckcard',
            unique_together=set([('deck', 'physicalcard')]),
        ),
    ]
