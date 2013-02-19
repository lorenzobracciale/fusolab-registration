from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'addpurchasedproduct/$', 'bar.views.addpurchasedproduct', name='addpurchasedproduct'),
    url(r'deletereceipt/(?P<receiptid>\d+)/$', 'bar.views.deletereceipt'),
    url(r'cash$', 'bar.views.barcash', name='barcash'),
)

