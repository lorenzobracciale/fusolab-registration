from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'card$', 'ingresso.views.card', name='card'),
    url(r'makecard/$', 'ingresso.views.makecard', name='makecard'),
    url(r'viewcard/$', 'ingresso.views.viewcard', name='viewcard'),
    url(r'delete/(?P<entranceid>\d+)/$', 'ingresso.views.delete_entrance'),
    url(r'insert/(?P<cost>\S+)/$', 'ingresso.views.entrance', name='entrance'),
    url( r'users/(?P<q>.+)/', 'ingresso.views.ajax_user_search', name='ajax_user_search' ),
)


