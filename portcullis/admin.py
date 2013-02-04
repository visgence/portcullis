from portcullis.models import *
from django.contrib import admin

from datetime import datetime

'''
class OrganizationAdmin(admin.ModelAdmin):
    filter_horizontal = ('members', 'devices', 'suborganizations',)
'''

class DataStreamAdmin(admin.ModelAdmin):
    list_display = ('name',  'owner', 'id', 'node', 'port', 'units', 'description', 'color',
                    'min_value', 'max_value', 'scale_function')
    search_fields = ['name', 'id', 'owner__username', 'owner__email', 'can_post__key', 'can_read__key',
                     'description']
    filter_horizontal = ('can_read', 'can_post')

    def node(self, obj):
        return obj.node_id

    def port(self, obj):
        return obj.port_id

    def owner(self, obj):
        return obj.owner.username

    def scale_function(self, obj):
        return obj.scaling_function.name


class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'UTC_Date', 'value', 'dataStream')
    list_filter = ('datastream',)

    def UTC_Date(self, obj):
        return datetime.utcfromtimestamp(obj.timestamp)

    def dataStream(self, obj):
        return 'ID %d: %s' % (obj.datastream.id, obj.datastream.name)

class KeyAdmin(admin.ModelAdmin):
    list_display = ('key', 'owner', 'description', 'expiration', 'num_uses')
    list_filter = ('owner', 'expiration')

class SavedViewAdmin(admin.ModelAdmin):
    list_display = ('key_str', 'owner', 'widget_list')

    def owner(self, obj):
        return obj.key.owner

    def key_str(self, obj):
        return obj.key.key

    def widget_list(self, obj):
        wlink = '<li><a href="/admin/portcullis/savedwidget/%s/">%s</a></li>'
        graphlink = '<li><a href="/admin/graphs/saveddsgraph/%s/">%s</a></li>'
        links = '<ul style="list-style: none">'
        for w in obj.widget.all():
            try:
                links += graphlink % (str(w.id), w.saveddsgraph.__unicode__())
            except:
                links += wlink % (str(w.id), str(w))
            
        return links + '</ul>'
    widget_list.allow_tags = True

admin.site.register(PortcullisUser)
admin.site.register(DataStream, DataStreamAdmin)
admin.site.register(SensorReading, SensorReadingAdmin)
admin.site.register(ScalingFunction)
#admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Device)
admin.site.register(Key, KeyAdmin)
admin.site.register(SavedView, SavedViewAdmin)
admin.site.register(SavedWidget)
