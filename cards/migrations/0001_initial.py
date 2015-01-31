# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='BaseCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=128)),
                ('filing_name', models.CharField(max_length=128)),
                ('rules_text', models.CharField(max_length=1000, blank=True)),
                ('mana_cost', models.CharField(max_length=60)),
                ('cmc', models.IntegerField(default=0)),
                ('power', models.CharField(max_length=4, null=True, blank=True)),
                ('toughness', models.CharField(max_length=4, null=True, blank=True)),
                ('loyalty', models.CharField(max_length=4, null=True, blank=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('cardposition', models.CharField(default='F', max_length=1)),
            ],
            options={
                'db_table': 'basecard',
                'managed': True,
                'verbose_name_plural': 'Base Cards',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Battle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('battle_date', models.DateTimeField(auto_now=True, auto_now_add=True)),
                ('session_key', models.CharField(max_length=40)),
            ],
            options={
                'db_table': 'battle',
                'verbose_name_plural': 'Battles',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BattleTest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'battletest',
                'verbose_name_plural': 'Battle Tests',
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
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, auto_now_add=True)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
                ('basecard', models.ForeignKey(to='cards.BaseCard')),
            ],
            options={
                'db_table': 'card',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CardColor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('basecard', models.ForeignKey(to='cards.BaseCard')),
            ],
            options={
                'db_table': 'cardcolor',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CardKeyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(max_length=60)),
                ('kwscore', models.FloatField()),
            ],
            options={
                'db_table': 'cardkeyword',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CardRating',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('mu', models.FloatField(default=25.0)),
                ('sigma', models.FloatField(default=8.333333333333334)),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, auto_now=True)),
            ],
            options={
                'db_table': 'cardrating',
                'verbose_name_plural': 'Card Ratings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CardSubtype',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField()),
                ('basecard', models.ForeignKey(to='cards.BaseCard')),
            ],
            options={
                'db_table': 'cardsubtype',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CardType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('position', models.IntegerField()),
                ('basecard', models.ForeignKey(to='cards.BaseCard')),
            ],
            options={
                'db_table': 'cardtype',
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
                'db_table': 'color',
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
                'db_table': 'expansionset',
                'managed': True,
                'verbose_name_plural': 'Expansion Sets',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('formatname', models.CharField(max_length=60)),
                ('format', models.CharField(unique=True, max_length=60)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
            ],
            options={
                'db_table': 'format',
                'verbose_name_plural': 'Formats',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FormatBasecard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('basecard', models.ForeignKey(to='cards.BaseCard')),
                ('format', models.ForeignKey(to='cards.Format')),
            ],
            options={
                'db_table': 'formatbasecard',
                'verbose_name_plural': 'Format Base Cards',
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
                'db_table': 'mark',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PhysicalCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('layout', models.CharField(default='normal', max_length=12, choices=[('normal', 'normal'), ('split', 'split'), ('flip', 'flip'), ('double-faced', 'double-faced'), ('token', 'token'), ('plane', 'plane'), ('scheme', 'scheme'), ('phenomenon', 'phenomenon'), ('leveler', 'leveler'), ('vanguard', 'vanguard')])),
            ],
            options={
                'db_table': 'physicalcard',
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
                'db_table': 'rarity',
                'managed': True,
                'verbose_name_plural': 'Rarities',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Ruling',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ruling_text', models.TextField()),
                ('ruling_date', models.DateField()),
                ('basecard', models.ForeignKey(to='cards.BaseCard')),
            ],
            options={
                'db_table': 'ruling',
                'verbose_name_plural': 'Rulings',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SimilarPhysicalCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.FloatField()),
                ('physicalcard', models.ForeignKey(related_name='physicalcard', to='cards.PhysicalCard')),
                ('sim_physicalcard', models.ForeignKey(related_name='simphysicalcard', to='cards.PhysicalCard')),
            ],
            options={
                'db_table': 'similarphysicalcard',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Subtype',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('subtype', models.CharField(unique=True, max_length=128)),
            ],
            options={
                'db_table': 'subtype',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(unique=True, max_length=128)),
            ],
            options={
                'db_table': 'type',
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='formatbasecard',
            unique_together=set([('format', 'basecard')]),
        ),
        migrations.AddField(
            model_name='cardtype',
            name='type',
            field=models.ForeignKey(to='cards.Type'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='cardtype',
            unique_together=set([('basecard', 'position')]),
        ),
        migrations.AddField(
            model_name='cardsubtype',
            name='subtype',
            field=models.ForeignKey(to='cards.Subtype'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='cardsubtype',
            unique_together=set([('basecard', 'position')]),
        ),
        migrations.AddField(
            model_name='cardrating',
            name='format',
            field=models.ForeignKey(to='cards.Format'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cardrating',
            name='physicalcard',
            field=models.ForeignKey(to='cards.PhysicalCard'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cardrating',
            name='test',
            field=models.ForeignKey(to='cards.BattleTest'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='cardrating',
            unique_together=set([('physicalcard', 'format', 'test')]),
        ),
        migrations.AddField(
            model_name='cardkeyword',
            name='physicalcard',
            field=models.ForeignKey(to='cards.PhysicalCard'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cardcolor',
            name='color',
            field=models.ForeignKey(to='cards.Color'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='cardcolor',
            unique_together=set([('basecard', 'color')]),
        ),
        migrations.AddField(
            model_name='card',
            name='expansionset',
            field=models.ForeignKey(to='cards.ExpansionSet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='mark',
            field=models.ForeignKey(blank=True, to='cards.Mark', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='card',
            name='rarity',
            field=models.ForeignKey(db_column='rarity', blank=True, to='cards.Rarity', null=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='card',
            unique_together=set([('expansionset', 'card_number', 'multiverseid')]),
        ),
        migrations.AddField(
            model_name='battle',
            name='format',
            field=models.ForeignKey(to='cards.Format'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='battle',
            name='loser_pcard',
            field=models.ForeignKey(related_name='loser', to='cards.PhysicalCard'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='battle',
            name='test',
            field=models.ForeignKey(to='cards.BattleTest'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='battle',
            name='winner_pcard',
            field=models.ForeignKey(related_name='winner', to='cards.PhysicalCard'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='battle',
            unique_together=set([('format', 'winner_pcard', 'loser_pcard', 'session_key')]),
        ),
        migrations.AddField(
            model_name='basecard',
            name='colors',
            field=models.ManyToManyField(to='cards.Color', through='cards.CardColor'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basecard',
            name='physicalcard',
            field=models.ForeignKey(to='cards.PhysicalCard'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basecard',
            name='subtypes',
            field=models.ManyToManyField(to='cards.Subtype', through='cards.CardSubtype'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='basecard',
            name='types',
            field=models.ManyToManyField(to='cards.Type', through='cards.CardType'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='basecard',
            unique_together=set([('physicalcard', 'cardposition')]),
        ),
    ]
