# Create your models here.
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

from django.db import connection

import logging
import re


class RulesMeta(models.Model):
    id = models.AutoField(primary_key=True)
    source_url = models.CharField(max_length=200, null=False)
    effective_date = models.DateField()
    import_date = models.DateTimeField()

    class Meta:
        managed = True


class Rule(models.Model):
    id = models.AutoField(primary_key=True)
    section = models.CharField(max_length=9, null=False, unique=True)
    sortsection = models.CharField(max_length=10, null=False, unique=True)
    parent = models.ForeignKey('self', null=True)
    rule_text = models.TextField()
    rule_text_html = models.TextField()

    def children(self):
        return Rule.objects.filter(parent=self).order_by('sortsection')

    def examples(self):
        return Example.objects.filter(rule=self).order_by('position')

    def marked_up_text(self):
        return self.rule_text_html

    class Meta:
        managed = True

    def __unicode__(self):
        return str(self.section)


class Example(models.Model):
    id = models.AutoField(primary_key=True)
    rule = models.ForeignKey('Rule', null=False)
    position = models.IntegerField(null=False, default=0)
    example_text = models.TextField()
    example_text_html = models.TextField()

    def marked_up_text(self):
        return self.example_text_html

    class Meta:
        managed = True

    def __unicode__(self):
        return '[Example ' + str(self.rule.section) + ' ' + str(self.position) + ']'
