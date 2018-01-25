# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from content.models import ContentBlock, Author


class AuthorAdmin(admin.ModelAdmin):
    readonly_fields = ('id',)
    list_display = ('id', 'user')


class ContentBlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'key')
    readonly_fields = ('id',)

# Register your models here.
admin.site.register(Author, AuthorAdmin)
admin.site.register(ContentBlock, ContentBlockAdmin)
