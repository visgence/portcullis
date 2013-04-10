from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns(
    'datastreams.views',
    url(r'^create/$', 'create.createDs', name='datastream-createDs'),
    url(r'^join_column/$', 'get_data.get_data_by_ds_column', name='datastream-join-column')
)
