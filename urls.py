from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'regionix.views.home', name='home'),
    # url(r'^regionix/', include('regionix.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^$', redirect_to,{'url':'/portcullis/'}),
    url(r'^render_graph/$', 'drawbridge.views.render_graph'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^portcullis/', include('portcullis.urls')),
    url(r'^favicon\.ico$', redirect_to, {'url': '/static/portcullis/favicon.ico'}),
)
