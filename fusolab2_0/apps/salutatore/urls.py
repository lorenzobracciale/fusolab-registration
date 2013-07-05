from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'say/(?P<sentence>\w*)/$', 'salutatore.views.say', name='salutatore_say'),
        url(r'(?P<cardid>\w{8})/$', 'salutatore.views.salutatore', name='salutatore'),
)


