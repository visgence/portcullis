from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

urlpatterns = patterns('portcullis.views',
     url(r'^$', 'index.index', name='portcullis-index'),
     url(r'^login/$', 'login.user_login'),
     url(r'^logout/$', 'login.logout'),
     url(r'^user_streams/$', 'side_pane.streams'),
     url(r'^shared_view/(?P<token>.+)/$', 'shared_view.sharedView'),
     url(r'^createSavedView/$', 'shared_view.createSavedView')
)


