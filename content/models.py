# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
import re
from cards.models import BaseCard
from django.core.urlresolvers import reverse

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
    key = models.CharField(max_length=128)
    content = models.TextField()
    author = models.ForeignKey(Author)
    version = models.IntegerField()
    created_at = models.DateTimeField(null=False, auto_now_add=True)
    updated_at = models.DateTimeField(null=False, auto_now=True)

    DRAFT = 'draft'
    LIVE = 'live'
    INACTIVE = 'inactive'
    STATUS_CHOICES = ((DRAFT, DRAFT), (LIVE, LIVE), (INACTIVE, INACTIVE))

    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=DRAFT)

    def _make_ahref_html_for_card_name(self, cardname):
        result = cardname
        basecard = BaseCard.objects.filter(name=cardname).first()
        if basecard:
            card = basecard.physicalcard.get_latest_card()
            url = reverse('cards:detail', kwargs={'multiverseid': str(card.multiverseid), 'slug': card.url_slug()})
            result = u'<a href="{}" data-mid="{}">{}</a>'.format(url, card.multiverseid, basecard.physicalcard.get_card_name())
        return result

    def content_final(self):
        """ Make the content redy for display on the site.
        """
        result = self.content.replace("\n\n", "<br><br>")
        result = result.replace("\r\n\r\n", "<br><br>")
        pattern = re.compile(ur'\[\[([^\]]+)\]\]', re.U)
        result = pattern.sub(lambda m: self._make_ahref_html_for_card_name(m.group(1)), result)
        return result

    def __unicode__(self):
        return u"ContentBlock {} [ver {}]".format(self.key, self.version)

    class Meta:
        managed = True
        unique_together = ('key', 'version',)
