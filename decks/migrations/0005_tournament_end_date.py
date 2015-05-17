# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('decks', '0004_auto_20150428_0352'),
    ]

    operations = [
        migrations.AddField(
            model_name='tournament',
            name='end_date',
            field=models.DateField(default=datetime.datetime(2015, 5, 14, 0, 36, 23, 90586, tzinfo=utc)),
            preserve_default=False,
        ),
    ]
