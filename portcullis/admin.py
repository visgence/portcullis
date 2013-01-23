from portcullis.models import *
from django.contrib import admin

'''
class OrganizationAdmin(admin.ModelAdmin):
    filter_horizontal = ('members', 'devices', 'suborganizations',)
'''

class DataStreamAdmin(admin.ModelAdmin):
    list_display = ('name', 'id', 'node_id', 'port_id')
    search_fields = ['name', 'id', 'owner__username', 'owner__email', 'can_post__key', 'can_read__key',
                     'description']
    filter_horizontal = ('can_read', 'can_post')

admin.site.register(PortcullisUser)
admin.site.register(DataStream, DataStreamAdmin)
admin.site.register(SensorReading)
admin.site.register(ScalingFunction)
#admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Device)
admin.site.register(Key)
