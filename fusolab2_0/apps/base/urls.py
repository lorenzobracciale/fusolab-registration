from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^statuto/$', 'base.views.statuto', name='statuto'),
    url(r'^accounts/edit/$', 'base.views.edit', name='edit'),
    url(r'activate/(?P<activation_key>\w+)/$', 'base.views.edit', name='edit'),
    url(r'^$', 'base.views.home', name='home' ),
    url(r'^index.html$', 'base.views.home'),
)
