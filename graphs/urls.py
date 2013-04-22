from django.conf.urls.defaults import patterns, url
from django.views.generic import RedirectView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    'graphs.views',
    url(r'^$', 'display_graphs.display_graph', name='graphs'),
    url(r'^render_simple_graph/$', 'display_graphs.display_simple_graph', name='graphs-simple_graph'),
    url(r'^render_simple/$', 'display_graphs.display_simple_base', name='graphs-simple'),
    url(r'^render_container/$', 'display_graphs.render_graph_container', name='graphs-container'),
    url(r'^favicon\.ico$', RedirectView.as_view(url='/static/portcullis/favicon.ico')),
    url(r'^plotter\.js$', 'display_graphs.plotter', name='graphs-plotter'),
)

