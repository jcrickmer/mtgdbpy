# -*- coding: utf-8 -*-

from django.contrib import admin
from cards.models import Color, Rarity, Card, BaseCard, Mark, ExpansionSet, Supertype, Subtype, Type, CardType, CardSubtype, PhysicalCard
from cards.models import Format, FormatExpansionSet, FormatBannedCard, FormatBasecard
from cards.models import Association, AssociationCard
from django import forms
from django.db import models
from django.forms import SelectMultiple, ModelMultipleChoiceField

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.fields import AutoCompleteSelectField
import sys

from django.utils.html import format_html
from django.conf.urls import url
from django.urls import reverse
from .forms import CopyFormatForm
from django.http import HttpResponseRedirect
from django.template.response import TemplateResponse

from cards.tasks import populate_format_cards

import logging
logger = logging.getLogger(__name__)


class CardModelForm(forms.ModelForm):
    flavor_text = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Card
        fields = '__all__'


class CardAdmin(admin.ModelAdmin):
    search_fields = ['id','basecard__name', 'basecard__filing_name']
    readonly_fields = ('id', 'basecard')
    fields = [
        'id',
        'expansionset',
        'basecard',
        'multiverseid',
        'rarity',
        'flavor_text',
        'card_number',
        'mark']

    form = CardModelForm

    list_display = ('id','get_name', 'rarity', 'multiverseid', 'expansionset_name_and_abbr', 'card_number')
    list_display_links = ('id', 'get_name')

    def get_name(self, obj):
        return obj.basecard.name
    get_name.short_description = 'Card Name'

    def expansionset_name_and_abbr(self, card):
        return '{} ({})'.format(card.expansionset.name, card.expansionset.abbr)
    expansionset_name_and_abbr.short_description = 'Expansion Set'


class BaseCardModelForm(forms.ModelForm):
    rules_text = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = BaseCard
        fields = '__all__'


class ExpansionSetAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class TypeAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class CardTypeAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    ordering = ['position']


class CardTypeInline(admin.TabularInline):
    readonly_fields = ('id',)
    ordering = ['position']
    model = BaseCard.types.through


class CardSupertypeInline(admin.TabularInline):
    readonly_fields = ('id',)
    model = BaseCard.supertypes.through


class SupertypeAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class SubtypeAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class CardSubtypeAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    ordering = ['position']


class CardSubtypeInline(admin.TabularInline):
    readonly_fields = ('id',)
    ordering = ['position']
    model = BaseCard.subtypes.through


class ColorAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class CardColorAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class MarkAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class CardColorInline(admin.TabularInline):
    readonly_fields = ('id',)
    model = BaseCard.colors.through


class PhysicalCardAdmin(admin.ModelAdmin):
    search_fields = ['basecard__name', ]
    readonly_fields = ('id', 'get_name')
    fields = ['id', 'get_name', 'layout']
    list_display = ('id', 'get_name', 'layout')
    list_display_links = ('id', 'get_name', )

    def get_name(self, obj):
        return obj.get_card_name()
    get_name.short_description = 'Card Name'


class FormatModelForm(forms.ModelForm):
    expansionsets = ModelMultipleChoiceField(queryset=ExpansionSet.objects.all().order_by('-releasedate'), required=False)

    # Lots of issues with the ExpansionSets being "required", which I don't quite understand. This was some helpful
    # debugging code to let me see exactly what the issue is/was.
    # def is_valid(self):
    #    from django.utils.encoding import force_text
    #    logger.error(force_text(self.errors))
    #    return super(FormatModelForm, self).is_valid()

    class Meta:
        model = Format
        fields = '__all__'


class FormatBannedCardInline(admin.TabularInline):
    readonly_fields = ('id',)
    model = Format.bannedcards.through
    form = make_ajax_form(FormatBannedCard, {
        'physicalcard': 'physicalcard'      # ForeignKeyField
    })


class FormatExpansionSetInline(admin.TabularInline):
    readonly_fields = ('id',)
    model = Format.expansionsets.through
    form = make_ajax_form(FormatExpansionSet, {
        'expansionset': 'expansionset'      # ForeignKeyField
    })


class FormatAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'cur_size')
    inlines = [FormatBannedCardInline, FormatExpansionSetInline]

    list_display = ('id', 'format', 'formatname', 'abbr', 'start_date', 'end_date', 'card_count', 'format_actions')
    list_display_links = ('format', )

    fields = ['id',
              'format',
              'formatname',
              'abbr',
              'start_date',
              'end_date',
              'min_cards_main',
              'max_cards_main',
              'min_cards_side',
              'max_cards_side',
              'max_nonbl_card_count',
              'uses_command_zone',
              'validator',
              'cur_size',
              ]
    form = FormatModelForm

    def get_urls(self):
        urls = super(FormatAdmin, self).get_urls()
        custom_urls = [
            url(
                r'^(?P<format_id>.+)/copy/$',
                self.admin_site.admin_view(self.process_copy),
                name='format-copy',
            ),
            url(
                r'^(?P<format_id>.+)/populate/$',
                self.admin_site.admin_view(self.process_populate),
                name='format-populate',
            ),
        ]
        return custom_urls + urls

    def format_actions(self, format):
        buttons = list()
        buttons.append(format_html(
            '<a class="button" href="{}">Copy</a>',
            reverse('admin:format-copy', args=[format.pk]),
        ))
        buttons.append(format_html(
            '<a class="button" href="{}">Populate</a>',
            reverse('admin:format-populate', args=[format.pk]),
        ))
        return format_html(' '.join(buttons))

    format_actions.short_description = 'Format Actions'
    format_actions.allow_tags = True

    def card_count(self, format):
        ''' Return the current number of cards in the format.
        '''
        return format.card_count()

    card_count.short_description = 'Cards in format'
    card_count.allow_tags = False

    def process_copy(self, request, format_id, *args, **kwargs):
        return self.process_action(
            request=request,
            format_id=format_id,
            action_form=CopyFormatForm,
            action_title='Copy',
        )

    def process_populate(self, request, format_id, *args, **kwargs):
        ''' The admin user wants to populate the format with the FormatExpansionSet and FormatBannedCard lists. For
            performance reasons, this action is not done with the format is initially created.

            Once the user has initiated this request, go ahead and return them back to the Format list page with a note
            that we got the process started.
        '''
        format = Format.objects.get(pk=format_id)
        async_result = populate_format_cards.delay(format_id)
        self.message_user(
            request,
            'Populate task for format "{}" started. Current status is {}.'.format(
                format.format,
                async_result.status))
        url = reverse('admin:cards_format_changelist', current_app=self.admin_site.name)
        return HttpResponseRedirect(url)

    def process_action(self, request, format_id, action_form, action_title):
        format = self.get_object(request, format_id)
        if request.method != 'POST':
            form = action_form(initial={'new_name_of_format': 'Copy of {}'.format(format.format)})
        else:
            form = action_form(request.POST)
            if form.is_valid():
                new_format = form.save(format, request.user)
                self.message_user(request, 'Success')
                url = reverse('admin:cards_format_change', args=[new_format.pk], current_app=self.admin_site.name, )
                return HttpResponseRedirect(url)
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['form'] = form
        context['format'] = format
        context['title'] = action_title
        return TemplateResponse(
            request,
            'admin/format_actions.html',
            context,
        )

    def cur_size(self, obj):
        return FormatBasecard.objects.filter(format=obj).count()
    cur_size.short_description = 'Current Card Count'


class BaseCardAdmin(admin.ModelAdmin):
    search_fields = ['id','name', 'filing_name']
    readonly_fields = ('id', 'cmc', 'physicalcard')
    fields = [
        'id',
        'physicalcard',
        'name',
        'rules_text',
        'mana_cost',
        'cmc',
        'power',
        'toughness',
        'loyalty']
    inlines = [CardColorInline, CardSupertypeInline, CardTypeInline, CardSubtypeInline]
    form = BaseCardModelForm
    list_display = ('id', 'name', 'filing_name', 'basecard_full_type', 'physicalcard_id', 'cardposition', 'basecard_print_count','created_at', 'updated_at')
    list_display_links = ('id', 'name', 'filing_name')

    def basecard_full_type(self, basecard):
        return basecard.get_full_type_str()
    basecard_full_type.short_description = 'Full Type'
    def basecard_print_count(self, basecard):
        return basecard.card_set.all().count()

class FormatExpansionSetAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    form = make_ajax_form(FormatExpansionSet, {
        'expansionset': 'expansionset'      # ForeignKeyField
    })


class AssociationCardInline(admin.TabularInline):
    readonly_fields = ('id',)
    model = Association.associationcards.through
    form = make_ajax_form(AssociationCard, {
        'physicalcard': 'physicalcard'      # ForeignKeyField
    })


class AssociationAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    inlines = [AssociationCardInline, ]
    list_display = ['id', 'name', 'classification', 'card_count', 'created_at', 'updated_at']
    list_display_links = ['id','name']

# Register your models here.
admin.site.register(Color, ColorAdmin)
admin.site.register(Rarity)
admin.site.register(Card, CardAdmin)
admin.site.register(BaseCard, BaseCardAdmin)
admin.site.register(Mark, MarkAdmin)
admin.site.register(ExpansionSet, ExpansionSetAdmin)
admin.site.register(PhysicalCard, PhysicalCardAdmin)
admin.site.register(Type, TypeAdmin)
#admin.site.register(CardType, CardTypeAdmin)
admin.site.register(Supertype, SupertypeAdmin)
admin.site.register(Subtype, SubtypeAdmin)
#admin.site.register(CardSubtype, CardSubtypeAdmin)
admin.site.register(Format, FormatAdmin)
admin.site.register(Association, AssociationAdmin)
