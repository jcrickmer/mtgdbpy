# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0017_auto_20141224_1539'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='card',
            unique_together=set([('expansionset', 'card_number', 'multiverseid')]),
        ),
    ]
