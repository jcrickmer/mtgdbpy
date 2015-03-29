from django.contrib import admin
from rules.models import Rule, Example, RulesMeta
from django import forms


class RuleModelForm(forms.ModelForm):
    rule_text = forms.CharField(widget=forms.Textarea)
    rule_text_html = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Rule
        fields = '__all__'


class RuleAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    fields = [
        'id',
        'section',
        'sortsection',
        'rule_text',
        'rule_text_html',
        'parent',]
    form = RuleModelForm


class ExampleModelForm(forms.ModelForm):
    example_text = forms.CharField(widget=forms.Textarea)
    example_text_html = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Example
        fields = '__all__'


class ExampleAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    fields = [
        'id',
        'rule',
        'position',
        'example_text',
        'example_text_html',]
    form = ExampleModelForm



class RulesMetaModelForm(forms.ModelForm):

    class Meta:
        model = RulesMeta
        fields = '__all__'


class RulesMetaAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    fields = [
        'id',
        'source_url',
        'effective_date',
        'import_date',]
    form = RulesMetaModelForm


admin.site.register(Rule, RuleAdmin)
admin.site.register(Example, ExampleAdmin)
admin.site.register(RulesMeta, RulesMetaAdmin)
