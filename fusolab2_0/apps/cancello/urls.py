from django.conf.urls.defaults import *
from django.views.generic import TemplateView

urlpatterns = patterns('',
   url(r'open_gate/$', 'cancello.views.open_gate', name='open_gate'),
   url(r'open_door/$', 'cancello.views.open_door', name='open_door'),
   url(r'$', TemplateView.as_view(template_name='cancello/apritore.html'), name="cancello_opener"),
)
