# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0005_ruling'),
    ]

    operations = [
        migrations.AlterField(
            model_name='physicalcard',
            name='layout',
            field=models.CharField(
                default='normal',
                max_length=12,
                choices=[
                    ('normal',
                     'normal'),
                    ('split',
                     'split'),
                    ('flip',
                     'flip'),
                    ('double-faced',
                     'double-faced'),
                    ('token',
                     'token'),
                    ('plane',
                     'plane'),
                    ('scheme',
                     'scheme'),
                    ('phenomenon',
                     'phenomenon'),
                    ('leveler',
                     'leveler'),
                    ('vanguard',
                     'vanguard')]),
            preserve_default=True,
        ),
    ]
