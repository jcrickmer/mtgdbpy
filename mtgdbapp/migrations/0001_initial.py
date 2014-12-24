# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils import timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('rules_text', models.CharField(max_length=1000, blank=True)),
                ('mana_cost', models.CharField(max_length=60)),
                ('cmc', models.IntegerField(default=0)),
                ('power', models.CharField(max_length=4, null=True, blank=True)),
                ('toughness', models.CharField(max_length=4, null=True, blank=True)),
                ('loyalty', models.CharField(max_length=4, null=True, blank=True)),
                ('created_at', models.DateTimeField(default=timezone.now, blank=True)),
                ('updated_at', models.DateTimeField(default=timezone.now, blank=True)),
                ('cardposition', models.CharField(default='F', max_length=1)),
            ],
            options={
                'db_table': 'basecards',
                'managed': True,
                'verbose_name_plural': 'Base Cards',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Card',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('multiverseid', models.IntegerField(blank=True)),
                ('flavor_text', models.CharField(max_length=1000, null=True, blank=True)),
                ('card_number', models.CharField(max_length=6, null=True, blank=True)),
                ('created_at', models.DateTimeField(default=timezone.now, blank=True)),
                ('updated_at', models.DateTimeField(default=timezone.now, blank=True)),
                ('basecard', models.ForeignKey(to='mtgdbapp.BaseCard')),
            ],
            options={
                'db_table': 'cards',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CardColor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('basecard', models.ForeignKey(to='mtgdbapp.BaseCard')),
            ],
            options={
                'db_table': 'cardcolors',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CardSubtype',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField()),
                ('basecard', models.ForeignKey(to='mtgdbapp.BaseCard')),
            ],
            options={
                'db_table': 'cardsubtypes',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CardType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField()),
                ('basecard', models.ForeignKey(to='mtgdbapp.BaseCard')),
            ],
            options={
                'db_table': 'cardtypes',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Color',
            fields=[
                ('id', models.CharField(max_length=1, serialize=False, primary_key=True)),
                ('color', models.CharField(max_length=9)),
            ],
            options={
                'db_table': 'colors',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DjangoSession',
            fields=[
                ('session_key', models.CharField(max_length=40, serialize=False, primary_key=True)),
                ('session_data', models.TextField()),
                ('expire_date', models.DateTimeField()),
            ],
            options={
                'db_table': 'django_session',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ExpansionSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('abbr', models.CharField(max_length=6)),
            ],
            options={
                'db_table': 'expansionsets',
                'managed': True,
                'verbose_name_plural': 'Expansion Sets',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Mark',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mark', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'marks',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PhysicalCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
            options={
                'db_table': 'physicalcards',
                'managed': True,
                'verbose_name_plural': 'Physical Cards',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rarity',
            fields=[
                ('id', models.CharField(max_length=1, serialize=False, primary_key=True)),
                ('rarity', models.CharField(max_length=11)),
                ('sortorder', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'rarities',
                'managed': True,
                'verbose_name_plural': 'Rarities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subtype',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subtype', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'subtypes',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'types',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='type',
            field=models.ForeignKey(to='mtgdbapp.Type'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='cardtype',
            unique_together=set([('basecard', 'position')]),
        ),
        migrations.AddField(
            model_name='cardsubtype',
            name='subtype',
            field=models.ForeignKey(to='mtgdbapp.Subtype'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='cardsubtype',
            unique_together=set([('basecard', 'position')]),
        ),
        migrations.AddField(
            model_name='cardcolor',
            name='color',
            field=models.ForeignKey(to='mtgdbapp.Color'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='cardcolor',
            unique_together=set([('basecard', 'color')]),
        ),
        migrations.AddField(
            model_name='card',
            name='expansionset',
            field=models.ForeignKey(to='mtgdbapp.ExpansionSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='mark',
            field=models.ForeignKey(blank=True, to='mtgdbapp.Mark', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rarity',
            field=models.ForeignKey(db_column='rarity', blank=True, to='mtgdbapp.Rarity', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='card',
            unique_together=set([('expansionset', 'card_number')]),
        ),
        migrations.AddField(
            model_name='basecard',
            name='colors',
            field=models.ManyToManyField(to='mtgdbapp.Color', through='mtgdbapp.CardColor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basecard',
            name='physicalcard',
            field=models.ForeignKey(to='mtgdbapp.PhysicalCard'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basecard',
            name='subtypes',
            field=models.ManyToManyField(to='mtgdbapp.Subtype', through='mtgdbapp.CardSubtype'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basecard',
            name='types',
            field=models.ManyToManyField(to='mtgdbapp.Type', through='mtgdbapp.CardType'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='basecard',
            unique_together=set([('physicalcard', 'cardposition')]),
        ),
    ]
