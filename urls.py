from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^$', redirect_to,{'url':'/portcullis/'}),
    url(r'^login/$', redirect_to,{'url':'/portcullis/'}),
    url(r'^render_graph/$', 'graphs.display_graphs.render_graph'),
    url(r'^graphs/', include('graphs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^portcullis/', include('portcullis.urls')),
    url(r'^datastreams/', include('datastreams.urls')),
    #url(r'^collector/', include('collector.urls')),
    #url(r'^favicon\.ico$', redirect_to, {'url': '/static/portcullis/favicon.ico'}),
)
