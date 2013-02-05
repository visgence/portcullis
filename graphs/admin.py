"""
" graph/admin.py
" Contributing Authors:
"    Jeremiah Davis (Visgence, Inc)
"
" (c) 2012 Visgence, Inc.
"""

from graphs.models import *
from django.contrib import admin
from datetime import datetime

class SavedDSGraphAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'saved_view', 'start_time', 'end_time')

    def saved_view(self, obj):
        views = obj.savedview_set.all()
        link = '<li style="list-style: none;"><a href="/admin/portcullis/savedview/%s/">%s</a></li>'
        links = '<ul>'
        for view in views:
            links += link % (view.key.key, view.key.key)
        links += '</ul>'
        return links
    saved_view.allow_tags = True

    def start_time(self, obj):
        return datetime.fromtimestamp(obj.start)

    def end_time(self, obj):
        return datetime.fromtimestamp(obj.end)

admin.site.register(SavedDSGraph, SavedDSGraphAdmin)
