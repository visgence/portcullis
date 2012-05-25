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
    #url(r'^render_graph/$', 'graphs.display_graphs.render_graph'),
    url(r'^graphs/', include('graphs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^scaling_functions.js/$', 'graphs.scaling_functions.scaling_functions'),
    url(r'^portcullis/', include('portcullis.urls')),
    url(r'^favicon\.ico$', redirect_to, {'url': '/static/portcullis/favicon.ico'}),
)
