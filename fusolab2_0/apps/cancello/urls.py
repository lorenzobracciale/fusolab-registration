from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'open_gate/$', 'cancello.views.open_gate', name='open_gate'),
)
