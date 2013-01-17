from django.conf.urls import patterns, include, url

urlpatterns = patterns('portcullis.views',
     url(r'^$', 'login.user_login'),
     url(r'^login/$', 'login.user_login'),
     url(r'^logout/$', 'login.logout'),
     url(r'^user_streams/$', 'user_portal.user_streams'),
)


