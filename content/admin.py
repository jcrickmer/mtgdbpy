# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from content.models import ContentBlock, Author

from django import forms

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.fields import AutoCompleteSelectField

from cards.models import PhysicalCard, BaseCard, Card
import re
import sys


class AuthorAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('id', 'user')


class ContentBlockForm(forms.ModelForm):
    key_card = AutoCompleteSelectField(
        'physicalcard',
        required=False,
        help_text='If a card is selected, the Key will be updated with the database id (PhysicalCard) for the selected card.')
    key_position = forms.ChoiceField(
        choices=(
            ('',
             ''),
            ('top',
             'top'),
            ('mid',
             'mid'),
            ('bottom',
             'bottom')),
        required=False,
        help_text='If selected, the Key will be updated to select this position.')

    def save(self, commit=True):
        result = super(ContentBlockForm, self).save(commit=commit)

        key_card = self.cleaned_data.get('key_card', None)
        key_position = self.cleaned_data.get('key_position', None)
        if key_card and key_position:
            #sys.stderr.write("ContentBlockForm - setting key from key_card and key_position. {}\n".format(key_card))
            result.key = u'PhysicalCard-{}__{}'.format(key_card.id, key_position)
            result.save()
            # now, let's bust cache so that people can see the work that they did:
            temp_frag_name = 'card_details_html'
            icards = Card.objects.filter(basecard__physicalcard=key_card)
            for icard in icards:
                invalidate_template_fragment(temp_frag_name, icard.multiverseid)
        return result

    class Meta:
        help_texts = {
            'key': "The key can be a URL, like 'cards/stats/modern/', or it can be the database id of a card, with the prefix 'PhysicalCard-[id]'. Then two underscores are used to denote the position on the page to show the content.",
            'content': "Limited HTML can be used to help format the content. Two newlines (returns) will be treated as a paragraph break. The link to a card, put the card name in double square braclets, e.g., [[Plains]]."}


class ContentBlockAdmin(admin.ModelAdmin):
    search_fields = ['key', ]
    list_display = ('id', 'key', 'status')
    readonly_fields = ('id',)
    fields = ('key', 'key_card', 'key_position', 'status', 'content', 'author', 'version', 'id')
    list_display_links = ('id', 'key', )
    form = ContentBlockForm

    def get_form(self, request, obj=None, **kwargs):
        form = super(ContentBlockAdmin, self).get_form(request, obj, **kwargs)
        if obj:
            sys.stderr.write("ContentBlockAdmin - obj is {}\n".format(obj))
            pattern = re.compile(ur'PhysicalCard-(\d+)_')
            pc_match = pattern.search(obj.key)
            if pc_match:
                form.base_fields['key_card'].initial = int(pc_match.group(1))
            if obj.key.find('__top') > 0:  # really, shouldn't be first
                form.base_fields['key_position'].initial = 'top'
            elif obj.key.find('__mid') > 0:  # really, shouldn't be first
                form.base_fields['key_position'].initial = 'mid'
            elif obj.key.find('__bottom') > 0:  # really, shouldn't be first
                form.base_fields['key_position'].initial = 'bottom'

        return form

# Register your models here.
admin.site.register(Author, AuthorAdmin)
admin.site.register(ContentBlock, ContentBlockAdmin)
