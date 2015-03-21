# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0002_auto_20150207_1619'),
    ]

    operations = [
        migrations.AlterField(
            model_name='expansionset',
            name='abbr',
            field=models.CharField(max_length=10),
            preserve_default=True,
        ),
    ]
