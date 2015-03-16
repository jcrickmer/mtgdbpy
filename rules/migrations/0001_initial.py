# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Example',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('position', models.IntegerField(default=0)),
                ('example_text', models.TextField()),
            ],
            options={
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('section', models.CharField(unique=True, max_length=9)),
                ('rule_text', models.TextField()),
                ('parent', models.ForeignKey(to='rules.Rule', null=True)),
            ],
            options={
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RulesMeta',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('source_url', models.CharField(max_length=200)),
                ('effective_date', models.DateField()),
                ('import_date', models.DateTimeField()),
            ],
            options={
                'managed': True,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='example',
            name='rule',
            field=models.ForeignKey(to='rules.Rule'),
            preserve_default=True,
        ),
    ]
