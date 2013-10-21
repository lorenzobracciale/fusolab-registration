from django.conf.urls.defaults import *
from django.views.generic import TemplateView

urlpatterns = patterns('',
    url(r'^accounts/edit/$', 'base.views.edit', name='base_account_edit'),
    url(r'activate/(?P<activation_key>\w+)/$', 'base.views.edit', name='edit'),
    url(r'^$', 'base.views.home', name='home' ),
    url(r'^index.html$', 'base.views.home'),
    url(r'^tuttoapposto/(?P<next_page>\S+)$', 'base.views.tuttoapposto', name='tuttoapposto'),
    url(r'^regolamento/$', TemplateView.as_view(template_name='regolamento.html'), name='base_regolamento'),
)
