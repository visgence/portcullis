from portcullis.models import *
from django.contrib import admin

class OrganizationAdmin(admin.ModelAdmin):
    filter_horizontal = ('members', 'devices', 'suborganizations',)

admin.site.register(DataStream)
admin.site.register(SensorReading)
admin.site.register(ScalingFunction)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Device)
admin.site.register(Key)
#admin.site.register(UserPermission)
admin.site.register(DevicePermission)
