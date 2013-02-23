from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'addpurchasedproduct/$', 'bar.views.addpurchasedproduct', name='addpurchasedproduct'),
    url(r'deletereceipt/(?P<receiptid>\d+)/$', 'bar.views.deletereceipt'),
    url(r'smallbalance/(?P<balance_type>\w+)/$', 'bar.views.bar_smallbalance_form', name='bar_small_form'),
    url(r'balance/(?P<balance_type>\w+)/$', 'bar.views.bar_balance_form', name='bar_form'),
    url(r'$', 'bar.views.barcash', name='barcash'),
)

