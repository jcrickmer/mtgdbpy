# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0018_auto_20141228_0323'),
    ]

    operations = [
        migrations.CreateModel(
            name='CardKeyword',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keyword', models.CharField(max_length=60)),
                ('kwscore', models.FloatField()),
                ('physicalcard', models.ForeignKey(to='mtgdbapp.PhysicalCard')),
            ],
            options={
                'managed': True,
            },
            bases=(models.Model,),
        ),
    ]
