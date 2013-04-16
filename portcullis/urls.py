from django.conf.urls import patterns, url

urlpatterns = patterns(
    'portcullis.views',
    url(r'^$', 'index.index', name='portcullis-index'),
    url(r'^side_pane/$', 'side_pane.skeleton', name='side_pane-skeleton'),
    url(r'^streams/$', 'side_pane.streams', name='side_pane-streams'),
    url(r'^(?P<content>saved_view)/(?P<content_id>.+)/$', 'index.index', name='portcullis-saved-view'),
)


