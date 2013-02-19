from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'^salutatore/(?P<cardid>\w{8})/$', 'salutatore.salutatore', name='salutatore'),
)


