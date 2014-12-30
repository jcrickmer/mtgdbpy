# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0009_auto_20141208_0452'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battle',
            name='id',
            field=models.AutoField(
                verbose_name='ID',
                serialize=False,
                auto_created=True,
                primary_key=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='battletest',
            name='id',
            field=models.AutoField(
                verbose_name='ID',
                serialize=False,
                auto_created=True,
                primary_key=True),
            preserve_default=True,
        ),
    ]
