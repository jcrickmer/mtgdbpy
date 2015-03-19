# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='rule',
            name='sortsection',
            field=models.CharField(default='100', unique=True, max_length=10),
            preserve_default=False,
        ),
    ]
