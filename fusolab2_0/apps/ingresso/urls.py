from django.conf.urls.defaults import *
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'balance/(?P<balance_type>\w+)/$', 'ingresso.views.entrance_balance_form', name='entrance_form'),
    url(r'makecard/$', 'ingresso.views.makecard', name='makecard'),
    url(r'viewcard/$', 'ingresso.views.viewcard', name='viewcard'),
    url(r'delete/(?P<entranceid>\d+)/$', 'ingresso.views.delete_entrance'),
    url(r'insert/(?P<cost>\S+)/$', 'ingresso.views.entrance', name='entrance'),
    url( r'users/(?P<q>.+)/', 'ingresso.views.ajax_user_search', name='ajax_user_search' ),
    url(r'csv','ingresso.csv_tool.create_resume', name='create_resume'),
    url(r'^guida_ingresso/$', TemplateView.as_view(template_name='ingresso/guida.html'), name='ingresso_guide'),
    url(r'$', 'ingresso.views.card', name='ingresso_home'),
)


