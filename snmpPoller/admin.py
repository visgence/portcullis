from snmpPoller.models import *
from django.contrib import admin


class SnmpStreamAdmin:
    list_display = ('dataStream.id','host.hostname','oid')

admin.site.register(Host)
admin.site.register(SnmpStream,SnmpStreamAdmin)
