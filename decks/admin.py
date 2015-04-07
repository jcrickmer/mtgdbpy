from django import forms
from django.contrib import admin

from ajax_select import make_ajax_form
from ajax_select.admin import AjaxSelectAdmin
from ajax_select.fields import AutoCompleteSelectField

from decks.models import Deck, DeckCard
from cards.models import PhysicalCard


class DeckModelForm(forms.ModelForm):
    main_board = forms.CharField(widget=forms.Textarea, required=False)
    #side_board = forms.CharField(widget=forms.Textarea)

    def __init__(self, *args, **kwargs):
        #self.main_board = 'hello'
        super(DeckModelForm, self).__init__(*args, **kwargs)
        #self.fields['main_board'].value = 'hello'

    def save(self, commit=True):
        main_board = self.cleaned_data.get('main_board', None)
        #side_board = self.cleaned_data.get('side_board', None)
        # ...do something with extra_field here...
        return super(DeckModelForm, self).save(commit=commit)

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
    inlines = [CardInline]

    form = DeckModelForm


class DeckCardAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    form = make_ajax_form(DeckCard, {'physicalcard': 'deckcard'})


# Register your models here.
admin.site.register(Deck, DeckAdmin)
admin.site.register(DeckCard, DeckCardAdmin)
