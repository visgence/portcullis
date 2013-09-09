from django.conf.urls import patterns, url

urlpatterns = patterns(
    'portcullis.views',
    url(r'^$', 'index.index', name='portcullis-index'),
    url(r'^side_pane/$', 'side_pane.skeleton', name='side_pane-skeleton'),
    url(r'^side_pane/get_subtree/$', 'side_pane.stream_subtree', name='side_pane-subtree'),
    url(r'^streams/$', 'side_pane.streams', name='side_pane-streams'),
)


