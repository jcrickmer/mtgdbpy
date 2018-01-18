# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-01-18 12:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0015_auto_20180115_1430'),
    ]

    operations = [
        migrations.AlterField(
            model_name='physicalcard',
            name='layout',
            field=models.CharField(choices=[('normal', 'normal'), ('split', 'split'), ('flip', 'flip'), ('aftermath', 'aftermath'), ('double-faced', 'double-faced'), ('token', 'token'), ('plane', 'plane'), ('scheme', 'scheme'), ('phenomenon', 'phenomenon'), ('leveler', 'leveler'), ('vanguard', 'vanguard')], default='normal', max_length=12),
        ),
    ]
