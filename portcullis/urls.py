from django.conf.urls import patterns, include, url
from django.views.generic.simple import redirect_to

urlpatterns = patterns(
    'portcullis.views',
    url(r'^$', 'index.index', name='portcullis-index'),
    url(r'^login/$', 'login.user_login'),
    url(r'^logout/$', 'login.logout'),
    url(r'^streams/$', 'side_pane.streams'),
    url(r'^(?P<content>savedView)/(?P<content_id>.+)/$', 'index.index', name='portcullis-saved-view'),
    url(r'^createSavedView/$', 'savedView.createSavedView', name='portcullis-saveView'),
    url(r'^model_editor/(?P<model_name>.+)/$', 'crud.model_grid', name='portcullis-model-editor')
)


