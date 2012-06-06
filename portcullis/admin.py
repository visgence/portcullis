from portcullis.models import DataStream, SensorReading, ScalingFunction, Permission, Organization
from django.contrib import admin

admin.site.register(DataStream)
admin.site.register(SensorReading)
admin.site.register(ScalingFunction)
admin.site.register(Permission)
admin.site.register(Organization)
