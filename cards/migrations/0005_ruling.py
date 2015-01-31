# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0004_physicalcard_layout'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ruling',
            fields=[
                ('id',
                 models.AutoField(
                     verbose_name='ID',
                     serialize=False,
                     auto_created=True,
                     primary_key=True)),
                ('ruling_text',
                 models.TextField()),
                ('ruling_date',
                 models.DateField()),
                ('basecard',
                 models.ForeignKey(
                     to='mtgdbapp.BaseCard')),
            ],
            options={
                'verbose_name_plural': 'Rulings',
            },
            bases=(
                models.Model,
            ),
        ),
    ]
