# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0008_auto_20141208_0431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battle',
            name='session_key',
            field=models.CharField(max_length=40),
            preserve_default=True,
        ),
    ]
