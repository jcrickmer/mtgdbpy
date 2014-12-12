# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0012_auto_20141211_0233'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cardrating',
            name='physicalcard',
            field=models.ForeignKey(to='mtgdbapp.PhysicalCard'),
            preserve_default=True,
        ),
    ]
