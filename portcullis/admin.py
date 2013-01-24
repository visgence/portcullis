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

admin.site.register(PortcullisUser)
admin.site.register(DataStream, DataStreamAdmin)
admin.site.register(SensorReading, SensorReadingAdmin)
admin.site.register(ScalingFunction)
#admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Device)
admin.site.register(Key)
