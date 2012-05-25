from snmpPoller.models import *
from django.contrib import admin


class SnmpStreamAdmin(admin.ModelAdmin):
    list_display = ('dataStream.id','host.hostname','oid')

admin.site.register(Host)
admin.site.register(SnmpStream,SnmpStreamAdmin)
