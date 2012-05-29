from django.conf.urls.defaults import patterns, include, url
from django.views.generic.simple import redirect_to
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('graphs.display_graphs',
    url(r'^$', 'display_graphs'),
    url(r'^render_graph/$', 'render_graph'),
    #url(r'^admin/', include(admin.site.urls)),
    #url(r'^graphs/$', 'display_graphs.display_graphs'),
    #url(r'^scaling_functions.js/$', 'scaling_functions.scaling_functions'),
    url(r'^favicon\.ico$', redirect_to, {'url': '/static/portcullis/favicon.ico'}),
)

urlpatterns += patterns('graphs.scaling_functions',
    url(r'^scaling_functions.js/$', 'scaling_functions'),
)
