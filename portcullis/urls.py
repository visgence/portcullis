from django.conf.urls import patterns, url

urlpatterns = patterns(
    'portcullis.views',
    url(r'^$', 'index.index', name='portcullis-index'),
    
    url(r'^utilities/index/$', 'index.utilitiesIndex', name='portcullis-utilities-index'),
    url(r'^sensors/index/$', 'index.sensorsIndex', name='portcullis-sensors-index'),
   
    url(r'^signup/page/$', 'signup.signupPage', name='portcullis-signup-page'),
    url(r'^signup/$', 'signup.signup', name='portcullis-signup'),
)


