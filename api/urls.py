from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('api.views',
    url(r'^add_reading/$','reading_loader.add_reading'),
    url(r'^addList/$', 'reading_loader.add_list'),
    url(r'^add/(?P<auth_token>.+)$', 'reading_loader.add_list'),
    url(r'^create/$', 'create_ds.createDs', name='datastream-createDs'),
    url(r'^join_column/$', 'get_data.get_data_by_ds_column', name='datastream-join-column'),
    url(r'^render_graph/$', 'get_data.render_graph'),
    url(r'^sharedGraph/(?P<token>.+)/(?P<id>\d{1,4})/$', 'get_data.shared_graph'),
)
