from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^$', redirect_to,{'url':'/portcullis/'}),
    url(r'^graphs/', include('graphs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^portcullis/', include('portcullis.urls')),
    url(r'^datastreams/', include('datastreams.urls')),
    url(r'^collector/', include('collector.urls')),
)
