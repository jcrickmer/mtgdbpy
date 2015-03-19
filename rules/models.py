# Create your models here.
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

from django.db import connection

import logging
import re
from cards.view_utils import convertSymbolsToHTML

#from cards.models import PhysicalCard, Format


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

    def children(self):
        return Rule.objects.filter(parent=self).order_by('sortsection')

    def examples(self):
        return Example.objects.filter(rule=self).order_by('position')

    def marked_up_text(self):
        # First, let's look for rule references
        ruleref_re = re.compile('((\d\d\d)\.(\d{1,3}[a-z]?))', re.U)
        result = ruleref_re.sub(r'<a href="\2#\1">\1</a>', self.rule_text)
        ruleref2_re = re.compile('([Rr]ule) (\d\d\d)', re.U)
        result = ruleref2_re.sub(r'\1 <a href="\2">\2</a>', result)
        result = convertSymbolsToHTML(result)
        return result

    class Meta:
        managed = True

    def __unicode__(self):
        return str(self.section)


class Example(models.Model):
    id = models.AutoField(primary_key=True)
    rule = models.ForeignKey('Rule', null=False)
    position = models.IntegerField(null=False, default=0)
    example_text = models.TextField()

    def marked_up_text(self):
        # First, let's look for rule references
        ruleref_re = re.compile('((\d\d\d)\.(\d{1,3}[a-z]?))', re.U)
        result = ruleref_re.sub(r'<a href="\2#\1">\1</a>', self.example_text)
        ruleref2_re = re.compile('([Rr]ule) (\d\d\d)', re.U)
        result = ruleref2_re.sub(r'\1 <a href="\2">\2</a>', result)
        result = convertSymbolsToHTML(result)
        return result

    class Meta:
        managed = True

    def __unicode__(self):
        return '[Example ' + str(self.rule.section) + ' ' + str(self.position) + ']'
