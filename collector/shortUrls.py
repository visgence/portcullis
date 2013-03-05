from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('collector.views',
#    url(r'^add_reading/$','data_loader.add_reading'),
#    url(r'^add_reading_bulk/$','data_loader.add_reading_bulk'),
#    url(r'^add_reading_bulk_hash/$','data_loader.add_reading_bulk_hash'),
    url(r'^add/(?P<auth_token>.{1,16})$', 'data_loader.add_list'),
)
