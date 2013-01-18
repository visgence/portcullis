from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

urlpatterns = patterns('portcullis.views',
     url(r'^$', redirect_to, {'url': 'user_streams'}),
     url(r'^login/$', 'login.user_login'),
     url(r'^logout/$', 'login.logout'),
     url(r'^user_streams/$', 'user_portal.user_streams'),
)


