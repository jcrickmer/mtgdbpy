# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django import forms
from cards.models import Format
from django.utils import timezone


class CopyFormatForm(forms.Form):
    new_name_of_format = forms.CharField(
        required=True,
    )

    def form_action(self, format, user):
        new_format = Format.cards.copy_format(format, new_name_of_format=self.cleaned_data['new_name_of_format'])
        return new_format

    def save(self, format, user):
        format = self.form_action(format, user)

        return format
