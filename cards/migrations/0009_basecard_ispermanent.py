# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-12 14:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0008_auto_20171107_0221'),
    ]

    operations = [
        migrations.AddField(
            model_name='basecard',
            name='ispermanent',
            field=models.BooleanField(default=False),
        ),
    ]