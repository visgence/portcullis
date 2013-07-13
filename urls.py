from django.conf.urls import patterns, include, url
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns(
    '',
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^$', RedirectView.as_view(url='/portcullis/')),
    url(r'^graphs/', include('graphs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^portcullis/', include('portcullis.urls')),
    url(r'^api/', include('api.urls')),
    url(r'chucho/', include('chucho.urls')),
)

urlpatterns += staticfiles_urlpatterns()
