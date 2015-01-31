# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0002_format_formatbasecard'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='formatbasecard',
            options={'verbose_name_plural': 'Format Base Cards'},
        ),
        migrations.AddField(
            model_name='basecard',
            name='filing_name',
            field=models.CharField(default='', max_length=128),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='formatbasecard',
            unique_together=set([('format', 'basecard')]),
        ),
    ]
