from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('collector.views',
    url(r'^add_reading/$','data_loader.add_reading'),
    url(r'^addList/$', 'data_loader.add_list'),
)
