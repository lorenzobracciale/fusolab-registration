from django.conf.urls.defaults import *

urlpatterns = patterns('',
        url(r'^salutatore/(?P<cardid>\w{8})/$', 'salutatore.views.salutatore', name='salutatore'),
)


