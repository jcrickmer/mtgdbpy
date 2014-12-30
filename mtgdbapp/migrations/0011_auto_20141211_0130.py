# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0010_auto_20141209_0454'),
    ]

    operations = [
        migrations.CreateModel(
            name='CardRating', fields=[
                ('id', models.AutoField(
                    serialize=False, primary_key=True)), ('mu', models.FloatField(
                        default=25.0)), ('sigma', models.FloatField(
                            default=8.333333333333334)), ('last_update', models.DateField(
                                auto_now=True, auto_now_add=True)), ('format', models.ForeignKey(
                                    to='mtgdbapp.Format')), ('physicalcard', models.ForeignKey(
                                        related_name='physicalcard', to='mtgdbapp.PhysicalCard')), ('test', models.ForeignKey(
                                            to='mtgdbapp.BattleTest')), ], options={
                'verbose_name_plural': 'Card Ratings', }, bases=(
                                                models.Model,), ), migrations.AlterUniqueTogether(
                                                    name='cardrating', unique_together=set(
                                                        [
                                                            ('physicalcard', 'format', 'test')]), ), ]
