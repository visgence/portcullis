from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('collector.data_loader',
    url(r'^add_reading/$','add_reading'),
)
