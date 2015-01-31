# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0007_auto_20141208_0219'),
    ]

    operations = [
        migrations.CreateModel(
            name='BattleTest',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='battle',
            name='test',
            field=models.ForeignKey(default=0, to='mtgdbapp.BattleTest'),
            preserve_default=False,
        ),
    ]
