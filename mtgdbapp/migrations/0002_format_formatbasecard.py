# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mtgdbapp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Format',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True)),
                ('formatname', models.CharField(max_length=60)),
                ('format', models.CharField(unique=True, max_length=60)),
                ('start_date', models.DateField(null=True)),
                ('end_date', models.DateField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FormatBasecard',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('basecard', models.ForeignKey(to='mtgdbapp.BaseCard')),
                ('format', models.ForeignKey(to='mtgdbapp.Format')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
