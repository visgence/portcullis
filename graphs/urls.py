from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('graphs.views',
    url(r'^$', 'display_graphs.display_graph'),
    url(r'^render_container/$', 'display_graphs.render_graph_container'),
    url(r'^render_graph/$', 'display_graphs.render_graph'),
    url(r'^favicon\.ico$', redirect_to, {'url': '/static/portcullis/favicon.ico'}),
    url(r'^scaling_functions.js/$', 'scaling_functions.scaling_functions'),
    url(r'^sharedGraph/(?P<token>.+)/(?P<id>\d{1,4})/$', 'display_graphs.shared_graph'),
)

