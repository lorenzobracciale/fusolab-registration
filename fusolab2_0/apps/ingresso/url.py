from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'ingresso/card/$', 'ingresso.cards.card', name='card'),
    url(r'^ingresso/makecard/$', 'ingresso.cards.makecard', name='makecard'),
    url(r'^ingresso/viewcard/$', 'ingresso.cards.viewcard', name='viewcard'),
    url(r'^ingresso/delete/(?P<entranceid>\d+)/$', 'ingresso.views.delete_entrance'),
    url(r'^ingresso/insert/(?P<cost>\S+)/$', 'ingresso.views.entrance', name='entrance'),
    url( r'^users/(?P<q>.+)/', 'ingresso.views.ajax_user_search', name='user_search' ),
)


