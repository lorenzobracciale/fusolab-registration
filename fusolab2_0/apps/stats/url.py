from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^stats/(?P<what>\S+)/(?P<interval>\S+)/(?P<dd>\d{2})/(?P<mm>\d{2})/(?P<yyyy>\d{4})/$', 'stats.stats.ajax_stats', name='ajax_stats'),
    url(r'^stats/$', 'fusoci.stats.stats', name='stats'),
    url(r'^devstats/(?P<what>\S+)/(?P<interval>\S+)/(?P<dd>\d{2})/(?P<mm>\d{2})/(?P<yyyy>\d{4})/$', 'stats.stats.ajax_stats_dev', name='ajax_stats_dev'),
    
    url(r'^trends/(?P<what>\S+)/(?P<interval>\S+)/(?P<dd>\d{2})/(?P<mm>\d{2})/(?P<yyyy>\d{4})/$', 'stats.trends.ajax_stats', name='ajax_stats'),
    url(r'^trends/$', 'stats.trends.trends', name='trends'),
)



