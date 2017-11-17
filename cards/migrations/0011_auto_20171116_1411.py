# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-16 14:11
from __future__ import unicode_literals

import cards.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0010_formatbannedcard_formatexpansionset'),
    ]

    operations = [
        migrations.AddField(
            model_name='expansionset',
            name='releasedate',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='format',
            name='expansionsets',
            field=models.ManyToManyField(through='cards.FormatExpansionSet', to='cards.ExpansionSet'),
        ),
        migrations.AlterField(
            model_name='format',
            name='start_date',
            field=models.DateField(null=True, validators=[cards.models.ddvalstart]),
        ),
        migrations.AlterField(
            model_name='format',
            name='validator',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
