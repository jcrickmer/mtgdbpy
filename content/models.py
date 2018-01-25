# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Author(models.Model):

    """ Represents a content author, bsed on a Django User.
    """
    #id = models.IntegerField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()

    def __unicode__(self):
        return u"{} [Author {}]".format(self.user.username, self.id)

    class Meta:
        managed = True


class ContentBlock(models.Model):

    """ A block of content.
    """
    #id = models.IntegerField(primary_key=True)
    key = models.CharField(max_length=256)
    content = models.TextField()
    author = models.ForeignKey(Author)
    version = models.IntegerField()
    created_at = models.DateTimeField(null=False, auto_now_add=True)
    updated_at = models.DateTimeField(null=False, auto_now=True)

    def __unicode__(self):
        return u"ContentBlock {} [ver {}]".format(self.key, self.version)

    class Meta:
        managed = True
        unique_together = ('key', 'version',)
