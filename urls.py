from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from dajaxice.core import dajaxice_autodiscover, dajaxice_config
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from settings import APP_PATH, DEBUG

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
dajaxice_autodiscover()

urlpatterns = patterns(
    '',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^$', RedirectView.as_view(url='/portcullis/')),
    url(r'^graphs/', include('graphs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^portcullis/', include('portcullis.urls')),
    url(r'^datastreams/', include('datastreams.urls')),
    url(r'^collector/', include('collector.urls')),
    url(r'^api/', include('collector.shortUrls')),
    url(r'(?i)^utilities/', include('chucho.urls')),
    url(dajaxice_config.dajaxice_url, include('dajaxice.urls')),
)

urlpatterns += staticfiles_urlpatterns()

if DEBUG:
    urlpatterns += url(r'^images\/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': APP_PATH + 'chucho/static/plugins/slickGrid/images'}),
