# -*- coding: utf-8 -*-

from django.contrib import admin
from cards.models import Color, Rarity, Card, BaseCard, Mark, ExpansionSet, Supertype, Subtype, Type, CardType, CardSubtype, PhysicalCard
from cards.models import Format, FormatExpansionSet, FormatBannedCard, FormatBasecard
from cards.models import Association, AssociationCard
from cards.models import CardPrice
from django.utils.safestring import mark_safe
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
    search_fields = ['id', 'basecard__name', 'basecard__filing_name']
    readonly_fields = ('id', 'basecard_link')
    fields = [
        'id',
        'expansionset',
        'basecard_link',
        'multiverseid',
        'rarity',
        'flavor_text',
        'card_number',
        'mark']

    form = CardModelForm

    list_display = ('id', 'get_name', 'rarity', 'multiverseid', 'expansionset_name_and_abbr', 'card_number', 'basecard_id', 'pcard_id')
    list_display_links = ('id', 'get_name')

    def basecard_link(self, card):
        bc_url = reverse('admin:cards_basecard_change', kwargs={
            'object_id': card.basecard.pk})
        return mark_safe('<a href="{}">{}</a>'.format(bc_url, card.basecard.id))
    basecard_link.short_description = 'BaseCard Id'

    def pcard_id(self, card):
        return card.basecard.physicalcard_id
    pcard_id.short_description = 'Physical Card Id'

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
    list_display = ('id', 'name', 'abbr', 'release_date')
    list_display_links = ('id', 'name', 'abbr')
    ordering = ('-releasedate',)

    def release_date(self, expansionset):
        return expansionset.releasedate


class TypeAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('id', 'type', 'card_count')
    list_display_links = ('id', 'type')

    def card_count(self, type):
        return type.cardtype_set.all().count()

    card_count.short_description = 'Card Count'


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
    list_display = ('id', 'supertype', 'card_count')
    list_display_links = ('id', 'supertype')

    def card_count(self, supertype):
        return supertype.cardsupertype_set.all().count()

    card_count.short_description = 'Card Count'


class SubtypeAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('id', 'subtype', 'card_count')
    list_display_links = ('id', 'subtype')

    def card_count(self, subtype):
        return subtype.cardsubtype_set.all().count()

    card_count.short_description = 'Card Count'


class CardSubtypeAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    ordering = ['position']


class CardSubtypeInline(admin.TabularInline):
    readonly_fields = ('id',)
    ordering = ['position']
    model = BaseCard.subtypes.through


class ColorAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('id', 'color')
    list_display_links = ('id', 'color')


class CardColorAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class MarkAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


class CardColorInline(admin.StackedInline):
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
    search_fields = ['id', 'name', 'filing_name']
    readonly_fields = ('id', 'cmc', 'pcard_link')
    fields = [
        'id',
        'pcard_link',
        'name',
        'rules_text',
        'mana_cost',
        'cmc',
        'power',
        'toughness',
        'loyalty']
    inlines = [CardColorInline, CardSupertypeInline, CardTypeInline, CardSubtypeInline]
    form = BaseCardModelForm
    list_display = (
        'id',
        'name',
        'filing_name',
        'basecard_full_type',
        'physicalcard_id',
        'cardposition',
        'basecard_print_count',
        'created_at',
        'updated_at')
    list_display_links = ('id', 'name', 'filing_name')

    def pcard_link(self, basecard):
        pc_url = reverse('admin:cards_physicalcard_change', kwargs={
            'object_id': basecard.physicalcard.pk})
        return mark_safe('<a href="{}">{}</a>'.format(pc_url, basecard.physicalcard.id))
    pcard_link.short_description = 'PhysicalCard Id'

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
    list_display_links = ['id', 'name']


class RarityAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ['id', 'rarity', 'sortorder', 'card_count']
    list_display_links = ['id', 'rarity']
    ordering = ['sortorder', ]

    def card_count(self, rarity):
        return rarity.card_set.all().count()

    card_count.short_description = 'Card Count'


class CardPriceAdmin(admin.ModelAdmin):
    search_fields = ['id', 'card__basecard__name', 'card__basecard__filing_name']
    readonly_fields = ('id', 'card_link')
    list_display = ('id', 'card_name', 'expset', 'printing', 'formatted_price', 'at_datetime')
    list_display_links = ('id', 'card_name', 'expset', 'printing', 'formatted_price', 'at_datetime')
    ordering = ['-at_datetime', ]

    # Both card and card_link are listed in the fields to be able to handle bot the "add" and "change" requests.
    # Depending on the request path, the fields will be slightly modified in the get_fieldsets() method and the
    # get_readonly_fields() method.
    fields = ['id', 'card', 'card_link', 'printing', 'price', 'at_datetime']

    def card_name(self, cardprice):
        return cardprice.card.basecard.physicalcard.get_card_name()

    def formatted_price(self, cardprice):
        return '${:.2f}'.format(cardprice.price)

    formatted_price.short_description = 'Price'

    def expset(self, cardprice):
        return cardprice.card.expansionset.name

    def card_link(self, cardprice):
        card_url = reverse('admin:cards_card_change', kwargs={
            'object_id': cardprice.card.pk})
        return mark_safe('<a href="{}">{} [{}]</a>'.format(card_url,
                                                           cardprice.card.basecard.physicalcard.get_card_name(),
                                                           cardprice.card.expansionset.name))

    card_link.short_decription = 'Card'

    def get_fieldsets(self, request, obj=None):
        # If the operation is to add a new CardPrice, then let's REMOVE the "card_link" field all together.
        result = super().get_fieldsets(request, obj=obj)
        if 'cardprice/add' in request.path_info:
            # let's remove card_link from the list of fields...
            new_fields_list = list()
            for field in result[0][1]['fields']:
                if field != 'card_link':
                    new_fields_list.append(field)
            result[0][1]['fields'] = new_fields_list

        return result

    def get_readonly_fields(self, request, obj=None):
        # If the operation is NOT an "add" (like it is a "change"), then let's make the "card" field readonly. This
        # will greatly improve page load time, and it isn't an action we really want the admin user to be taking
        # anyway.
        ro_fields = super().get_readonly_fields(request, obj=obj)
        if 'cardprice/add' not in request.path_info:
            new_ros = list(ro_fields)
            new_ros.append('card')
            ro_fields = tuple(new_ros)
        return ro_fields

    # When "adding" a new CardPrice, let's use an AJAX form for the card. Note that this is also configured in
    # settings.py and cards.lookups.CardLookup
    form = make_ajax_form(CardPrice, {
        'card': 'card'      # ForeignKeyField
    })


# Register your models here.
admin.site.register(Color, ColorAdmin)
admin.site.register(Rarity, RarityAdmin)
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
admin.site.register(CardPrice, CardPriceAdmin)
