# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-05 04:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cards', '0012_format_bannedcards'),
    ]

    operations = [
        migrations.CreateModel(
            name='Association',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('classification', models.CharField(max_length=60, null=True)),
                ('description', models.TextField(null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Association',
                'db_table': 'association',
                'managed': True,
                'verbose_name_plural': 'Associations',
            },
        ),
        migrations.CreateModel(
            name='AssociationCard',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('association', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cards.Association')),
            ],
            options={
                'db_table': 'associationcard',
                'managed': True,
            },
        ),
        migrations.AlterModelOptions(
            name='physicalcard',
            options={'managed': True, 'verbose_name': 'Physical Card', 'verbose_name_plural': 'Physical Cards'},
        ),
        migrations.AddField(
            model_name='associationcard',
            name='physicalcard',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assocphysicalcard', to='cards.PhysicalCard'),
        ),
        migrations.AddField(
            model_name='association',
            name='associationcards',
            field=models.ManyToManyField(through='cards.AssociationCard', to='cards.PhysicalCard'),
        ),
    ]
