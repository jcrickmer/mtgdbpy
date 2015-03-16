# Create your models here.
from __future__ import unicode_literals
from django.db import models
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

from django.db import connection

import logging

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
    parent = models.ForeignKey('self', null=True)
    rule_text = models.TextField()

    def children(self):
        return Rule.objects.filter(parent=self).order_by('section')

    def marked_up_text(self):
        return self.rule_text

    class Meta:
        managed = True

    def __unicode__(self):
        return str(self.section)


class Example(models.Model):
    id = models.AutoField(primary_key=True)
    rule = models.ForeignKey('Rule', null=False)
    position = models.IntegerField(null=False, default=0)
    example_text = models.TextField()

    class Meta:
        managed = True

    def __unicode__(self):
        return '[Example ' + str(self.rule.section) + ' ' + str(self.position) + ']'
