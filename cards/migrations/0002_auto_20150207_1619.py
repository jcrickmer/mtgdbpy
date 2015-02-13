# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='format',
            name='max_cards_main',
            field=models.IntegerField(default=60),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='format',
            name='max_cards_side',
            field=models.IntegerField(default=15),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='format',
            name='max_nonbl_card_count',
            field=models.IntegerField(default=4),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='format',
            name='min_cards_main',
            field=models.IntegerField(default=60),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='format',
            name='min_cards_side',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='format',
            name='uses_command_zone',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='format',
            name='validator',
            field=models.CharField(max_length=100, null=True),
            preserve_default=True,
        ),
    ]
