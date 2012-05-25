from snmpPoller.models import *
from django.contrib import admin

admin.site.register(Host)
#admin.site.register(SnmpStream)

class SnmpStreamAdmin:
    list_display = ('dataStream.id','host.hostname','oid')
