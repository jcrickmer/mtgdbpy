# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('rules', '0002_rule_sortsection'),
    ]

    operations = [
        migrations.AddField(
            model_name='example',
            name='example_text_html',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='rule',
            name='rule_text_html',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
