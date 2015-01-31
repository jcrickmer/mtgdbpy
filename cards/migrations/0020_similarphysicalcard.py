# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0019_cardkeyword'),
    ]

    operations = [
        migrations.CreateModel(
            name='SimilarPhysicalCard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.FloatField()),
                ('physicalcard', models.ForeignKey(related_name='physicalcard', to='mtgdbapp.PhysicalCard')),
                ('sim_physicalcard', models.ForeignKey(related_name='simphysicalcard', to='mtgdbapp.PhysicalCard')),
            ],
            options={
                'managed': True,
            },
            bases=(models.Model,),
        ),
    ]
