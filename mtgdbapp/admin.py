from django.contrib import admin
from mtgdbapp.models import Color, Rarity, Card, BaseCard, Mark, ExpansionSet, Subtype, Type, CardType, CardSubtype
from django import forms

class CardModelForm(forms.ModelForm):
    flavor_text = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = Card

class CardAdmin(admin.ModelAdmin):
	readonly_fields = ('id',)
	fields = ['id','expansionset','basecard','multiverseid','rarity','flavor_text','card_number','mark']
	form = CardModelForm

class BaseCardModelForm(forms.ModelForm):
    rules_text = forms.CharField(widget=forms.Textarea)
    class Meta:
        model = BaseCard

class TypeAdmin(admin.ModelAdmin):
	readonly_fields = ('id',)

class CardTypeAdmin(admin.ModelAdmin):
	readonly_fields = ('id',)
	ordering = ['position']

class CardTypeInline(admin.TabularInline):
	readonly_fields = ('id',)
	ordering = ['position']
	model = BaseCard.types.through

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

class CardColorInline(admin.TabularInline):
	readonly_fields = ('id',)
	model = BaseCard.colors.through

class BaseCardAdmin(admin.ModelAdmin):
	readonly_fields = ('id','cmc')
	fields = ['id','name','rules_text','mana_cost','cmc','power','toughness','loyalty']
	inlines = [CardColorInline,CardTypeInline,CardSubtypeInline]
	form = BaseCardModelForm
	
# Register your models here.
admin.site.register(Color)
admin.site.register(Rarity)
admin.site.register(Card, CardAdmin)
admin.site.register(BaseCard, BaseCardAdmin)
admin.site.register(Mark)
admin.site.register(ExpansionSet)
admin.site.register(Type,TypeAdmin)
admin.site.register(CardType,CardTypeAdmin)
admin.site.register(Subtype,SubtypeAdmin)
admin.site.register(CardSubtype,CardSubtypeAdmin)
