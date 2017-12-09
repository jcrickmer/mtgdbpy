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


class CardModelForm(forms.ModelForm):
    flavor_text = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = Card
        fields = '__all__'


class CardAdmin(admin.ModelAdmin):
    search_fields = ['basecard__name', ]
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

    list_display = ('get_name', 'rarity', 'multiverseid', 'expansionset', 'card_number')

    def get_name(self, obj):
        return obj.basecard.name
    get_name.short_description = 'Card Name'


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
    expansionsets = ModelMultipleChoiceField(queryset=ExpansionSet.objects.all().order_by('-releasedate'))

    class Meta:
        model = Format
        fields = '__all__'


class FormatBannedCardInline(admin.TabularInline):
    readonly_fields = ('id',)
    model = Format.bannedcards.through
    form = make_ajax_form(FormatBannedCard, {
        'physicalcard': 'physicalcard'      # ForeignKeyField
    })


class FormatAdmin(admin.ModelAdmin):
    readonly_fields = ('id', 'cur_size')
    inlines = [FormatBannedCardInline, ]

    list_display = ('id', 'format', 'formatname', 'abbr', 'start_date', 'end_date')
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
              'expansionsets',
              ]
    form = FormatModelForm

    def cur_size(self, obj):
        return FormatBasecard.objects.filter(format=obj).count()
    cur_size.short_description = 'Current Card Count'


class BaseCardAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
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
    list_display = ('name', 'get_pcard_id')
    list_display_links = ('name', )

    def get_pcard_id(self, obj):
        return obj.id
    get_pcard_id.short_description = 'Physical Card Id'


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


# Register your models here.
admin.site.register(Color, ColorAdmin)
admin.site.register(Rarity)
admin.site.register(Card, CardAdmin)
admin.site.register(BaseCard, BaseCardAdmin)
admin.site.register(Mark, MarkAdmin)
admin.site.register(ExpansionSet, ExpansionSetAdmin)
admin.site.register(PhysicalCard, PhysicalCardAdmin)
admin.site.register(Type, TypeAdmin)
admin.site.register(CardType, CardTypeAdmin)
admin.site.register(Supertype, SupertypeAdmin)
admin.site.register(Subtype, SubtypeAdmin)
admin.site.register(CardSubtype, CardSubtypeAdmin)
admin.site.register(Format, FormatAdmin)
admin.site.register(Association, AssociationAdmin)
