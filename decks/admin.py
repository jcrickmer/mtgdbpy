from django import forms
from django.contrib import admin

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.fields import AutoCompleteSelectField

from decks.models import Deck, DeckCard, Tournament, TournamentDeck
from cards.models import PhysicalCard
import sys


class DeckModelForm(forms.ModelForm):
    main_board = forms.CharField(widget=forms.Textarea, required=False)
    #side_board = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        super(DeckModelForm, self).__init__(*args, **kwargs)
        if self.instance is not None:
            self.fields['main_board'].initial = self.instance.cards_as_text()

    def save(self, commit=True):
        main_board = self.cleaned_data.get('main_board', None)
        #side_board = self.cleaned_data.get('side_board', None)
        result = super(DeckModelForm, self).save(commit=commit)
        # Something is broken. I shouldn't have to call save() here - the line above me should have done it.
        result.save()
        result.set_cards_from_text(main_board)
        return result

    class Meta:
        model = Deck
        fields = ['id', 'name', 'authorname', 'url', 'format', 'visibility']


class CardInline(admin.TabularInline):
    model = DeckCard
    extra = 1
    form = make_ajax_form(DeckCard, {'physicalcard': 'deckcard'})

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == 'physicalcard':
            kwargs['queryset'] = PhysicalCard.objects.filter(id__gte=14200)
        return super(CardInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class DeckAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    #inlines = [CardInline]

    form = DeckModelForm


class DeckCardAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    form = make_ajax_form(DeckCard, {'physicalcard': 'deckcard'})


class TournamentAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    ordering = ['-start_date']


class TournamentDeckAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)


# Register your models here.
admin.site.register(Deck, DeckAdmin)
admin.site.register(DeckCard, DeckCardAdmin)
admin.site.register(Tournament, TournamentAdmin)
admin.site.register(TournamentDeck, TournamentDeckAdmin)
