# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0006_auto_20141129_1400'),
    ]

    operations = [
        migrations.CreateModel(
            name='Battle',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('battle_date', models.DateField(auto_now=True, auto_now_add=True)),
                ('format', models.ForeignKey(to='mtgdbapp.Format')),
                ('loser_pcard', models.ForeignKey(related_name='loser', to='mtgdbapp.PhysicalCard')),
                ('session_key', models.ForeignKey(to='mtgdbapp.DjangoSession')),
                ('winner_pcard', models.ForeignKey(related_name='winner', to='mtgdbapp.PhysicalCard')),
            ],
            options={
                'verbose_name_plural': 'Battles',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='battle',
            unique_together=set([('format', 'winner_pcard', 'loser_pcard', 'session_key')]),
        ),
    ]
