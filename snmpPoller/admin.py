from snmpPoller.models import *
from django.contrib import admin


class SnmpStreamAdmin(admin.ModelAdmin):
    list_display = ('dataStream_id','host_hostname','oid')

    def dataStream_id(self,obj):
        return obj.dataStream.id
    
    def host_hostname(self,obj):
        return obj.host.hostname


admin.site.register(Host)
admin.site.register(SnmpStream,SnmpStreamAdmin)
