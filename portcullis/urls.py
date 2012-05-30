from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('portcullis.login',
    # Examples:
    # url(r'^$', 'portcullis.views.home', name='home'),
    # url(r'^portcullis/', include('portcullis.foo.urls')),
     url(r'^$', 'user_login'),
     url(r'^login/$', 'user_login'),
     url(r'^logout/$', 'logout'),
     
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('portcullis.index',
     url(r'^user_streams/$', 'user_streams'),
)
