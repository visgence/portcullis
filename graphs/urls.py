from django.conf.urls.defaults import patterns, include, url
from django.views.generic import RedirectView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('graphs.views',
    url(r'^$', 'display_graphs.display_graph'),
    url(r'^render_simple_graph/$', 'display_graphs.display_simple_graph'),
    url(r'^render_simple/$', 'display_graphs.display_simple_base'),
    url(r'^render_container/$', 'display_graphs.render_graph_container'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/portcullis/favicon.ico')),
    url(r'^scaling_functions.js/$', 'scaling_functions.scaling_functions'),
)

