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

)

urlpatterns += patterns('portcullis.user_portal',
     url(r'^user_streams/$', 'user_streams'),
)
