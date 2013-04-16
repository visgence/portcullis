from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('api.views',
    url(r'^add_reading/$','data_loader.add_reading'),
    url(r'^addList/$', 'data_loader.add_list'),
    url(r'^add/(?P<auth_token>.+)$', 'data_loader.add_list'),
)
