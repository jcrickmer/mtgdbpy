# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0016_auto_20141224_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='basecard',
            name='filing_name',
            field=models.CharField(max_length=128),
            preserve_default=True,
        ),
    ]
