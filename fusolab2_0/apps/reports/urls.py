from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^/daily_stats/$', 'reports.views.daily_stats', name='reports_daily_stats'),    
    url(r'^/make_balance/$', 'reports.views.make_balance', name='reports_make_balance'),    

    url(r'^excel/(?P<what>\S+)/(?P<from_day>\d{2})/(?P<from_month>\d{2})/(?P<from_year>\d{4})/(?P<to_day>\d{2})/(?P<to_month>\d{2})/(?P<to_year>\d{4})/$', 'reports.views.excel', name='excel'),
    #url(r'^stats/(?P<what>\S+)/(?P<interval>\S+)/(?P<dd>\d{2})/(?P<mm>\d{2})/(?P<yyyy>\d{4})/$', 'stats.stats.ajax_stats', name='ajax_stats'),
    #url(r'^stats/$', 'stats.stats.stats', name='stats'),
    #url(r'^devstats/(?P<what>\S+)/(?P<interval>\S+)/(?P<dd>\d{2})/(?P<mm>\d{2})/(?P<yyyy>\d{4})/$', 'stats.stats.ajax_stats_dev', name='ajax_stats_dev'),
    #url(r'^trends/(?P<what>\S+)/(?P<interval>\S+)/(?P<dd>\d{2})/(?P<mm>\d{2})/(?P<yyyy>\d{4})/$', 'stats.trends.ajax_stats', name='ajax_stats'),
    #url(r'^trends/$', 'stats.trends.trends', name='trends'),
    url(r'^$', 'reports.views.reports', name='reports'),    
)
