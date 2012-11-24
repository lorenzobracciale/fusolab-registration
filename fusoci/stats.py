from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q
from fusoci.models import * 
from django.conf import settings
from django.utils import simplejson
from decimal import Decimal
from datetime import datetime, timedelta
import qsstats


@staff_member_required
def stats(request):
    products = [] 
    mnow = datetime.now()
    if mnow.hour < 12:
        mnow = mnow - timedelta(days=1)
    for p in Product.objects.all():
        products.append( {'name': p.name, 'quantity': PurchasedProduct.objects.filter(name=p.name).count()} )
    return render_to_response('fusoci/stats.html', {'products' : products, 'mnow': mnow} , context_instance=RequestContext(request))

@staff_member_required
def ajax_stats2(request, what=None, interval=None, dd=None, mm=None, yyyy=None):
    data = {"labels" : [], "data" : [] }
    day, month, year = int(dd), int(mm), int(yyyy)
    pp = None
    qss = None
    any_result = True
    if what == "bar":
        if interval == "daily":
            delta = timedelta(minutes=15)
            starttime = datetime(year,month,day,12,00,00)
            endtime = starttime + timedelta(hours=20)
            try:
                p = PurchasedProduct.objects.filter(receipt__date__range=[starttime, endtime])
                starttime = p.order_by('receipt__date')[0].receipt.date
                endtime = p.latest('receipt__date').receipt.date
            except (IndexError, PurchasedProduct.DoesNotExist):
                any_result = False


            for product_type in Product.objects.all():
                data["labels"].append(product_type.name)

                current_step = starttime
                buf = []
                cumulative = 0
                while (current_step < endtime) and any_result == True:
                    pp = PurchasedProduct.objects.filter(receipt__date__range=[current_step, current_step + delta]).filter(name=product_type.name)
                    current_step = current_step + delta
                    cumulative = cumulative +  pp.count() 
                    if pp.count() > 0:
                        buf.append([current_step.strftime("%Y-%m-%d %I:%M%p") , cumulative])
                data["data"].append(buf) 
    return HttpResponse( simplejson.dumps(data), mimetype="application/json" )

@staff_member_required
def ajax_stats(request, what=None, interval=None):
    data = {"labels" : [], "data" : [] } 
    pp = None
    qss = None
    if what == "bar":
        if interval == "daily":
            pp = PurchasedProduct.objects.filter(receipt__date__gte=datetime.now()-timedelta(hours=12))
            #qs = PurchasedProduct.objects.all()
            #qss = qsstats.QuerySetStats(qs, 'receipt')
        elif interval == "monthly":
            pp = PurchasedProduct.objects.filter(receipt__date__gte=datetime.now()-timedelta(days=30))
        else:
            return HttpResponseNotFound("Interval is not valid")

        for product_type in Product.objects.all():
            data["labels"].append(product_type.name)
            buf = []
            item_n = 0
            for p in pp.filter(name = product_type.name):
                item_n += 1
                buf.append([p.receipt.date.strftime("%Y-%m-%d %I:%M%p" ) , item_n])
            #today = datetime.now()
            #yesterday = today - timedelta(hours=12)
            #for q in qss.time_series(yesterday, today):
            #    buf.append(q[0], q[1])
            data["data"].append(buf)

    elif what == "money-bar":
        if interval == "daily":
            rr = Receipt.objects.filter(date__gte=datetime.now()-timedelta(hours=12))
        elif interval == "monthly":
            rr = Receipt.objects.filter(date__gte=datetime.now()-timedelta(days=30))
        else:
            return HttpResponseNotFound("Interval is not valid")
        data["labels"].append("Incasso")
        buf = []
        money = 0.0
        for r in rr:
            money = money + float(r.total)
            buf.append([r.date.strftime("%Y-%m-%d %I:%M%p" ) , money])
        data["data"].append(buf)

    return HttpResponse( simplejson.dumps(data), mimetype="application/json" )
    

