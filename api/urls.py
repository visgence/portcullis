from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('api.views',
    url(r'^add_reading/$','reading_loader.add_reading'),
    url(r'^addList/$', 'reading_loader.add_list'),
    url(r'^add/(?P<auth_token>.+)$', 'reading_loader.add_list'),
    url(r'^create/$', 'create_ds.create_datastreams', name='api-create-datastreams'),
    url(r'^join_column/$', 'get_data.get_data_by_ds_column', name='api-join-column'),
    url(r'^render_graph/$', 'get_data.render_graph', name='api-render_graph'),
    url(r'^sharedGraph/(?P<token>.+)/(?P<id>\d{1,4})/$', 'get_data.shared_graph', name='api-sharedGraph'),
    url(r'^scaling_functions.js/$', 'scaling_functions.scaling_functions'),
    url(r'^create_saved_view/$', 'create_shared.create_saved_view', name='api-create-saved-view'),
    url(r'^login/$', 'login.user_login', name='api-login'),
    url(r'^logout/$', 'login.logout', name='api-logout'),
    url(r'^passwordForm/$', 'login.password_form', name='api-password_form'),
    url(r'^changePassword/$', 'login.change_password', name='api-change_password'),
)
