from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^bar/addpurchasedproduct/$', 'bar.views.addpurchasedproduct', name='addpurchasedproduct'),
    url(r'^bar/deletereceipt/(?P<receiptid>\d+)/$', 'bar.views.deletereceipt'),
    url(r'^bar/$', 'bar.views.barcash', name='barcash'),
)

