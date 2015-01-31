# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0015_auto_20141224_0719'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subtype',
            name='subtype',
            field=models.CharField(unique=True, max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='type',
            name='type',
            field=models.CharField(unique=True, max_length=128),
            preserve_default=True,
        ),
    ]
