from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Count
from fusoci.models import * 
from django.conf import settings
from django.utils import simplejson
from decimal import Decimal
from datetime import datetime, timedelta
import qsstats


@staff_member_required
def trends(request):
    products = [] 
    mnow = datetime.now()
    if mnow.hour < 12:
        mnow = mnow - timedelta(days=1)
    for p in Product.objects.all():
        products.append( {'name': p.name, 'quantity': PurchasedProduct.objects.filter(name=p.name).count()} )
    return render_to_response('fusoci/trends.html', {'products' : products, 'mnow': mnow} , context_instance=RequestContext(request))

@staff_member_required
def ajax_stats(request, what=None, interval=None, dd=None, mm=None, yyyy=None):
    data = {"labels" : [], "trend" : [], "total" : [] }
    day, month, year = int(dd), int(mm), int(yyyy)
    pp = None
    qss = None

    if interval == "daily":
        delta = timedelta(minutes=15)
        starttime = datetime(year,month,day,12,00,00)
        endtime = starttime + timedelta(hours=20)
    elif interval == "monthly":
        delta = timedelta(days=1)
        endtime = datetime(year,month,day,12,00,00)
        starttime = endtime - timedelta(days=30)

    if what == "bar":
        current_step = starttime
        total = {}
        buf = {}
        while (current_step < endtime):
            pp = PurchasedProduct.objects.filter(receipt__date__range=[current_step, current_step + delta]).values('name').annotate(pcount=Count('receipt'))
            for p in pp:
                pname = p['name']
                if not buf.has_key(pname):
                    buf[pname] = []
                if not total.has_key(pname):
                    total[pname] = 0
                try:
                    tmpcount = int(p['pcount'])
                except ValueError:
                    tmpcount = 0
                total[pname] += tmpcount
                buf[pname].append([current_step.strftime("%Y-%m-%d %I:%M%p") , tmpcount] )
            current_step = current_step + delta

        for p in buf.keys():
			data["labels"].append(p)
			data["trend"].append(buf[p])
			data["total"].append([total[p]])

    elif what == "money-bar":
        current_step = starttime
        money = {}
        buf = {}
        while (current_step < endtime):
            pp = PurchasedProduct.objects.filter(receipt__date__range=[current_step, current_step + delta]).values('name').annotate(ptotal=Sum('receipt__total'))
            for p in pp:
                pname = p['name']
                if not buf.has_key(pname):
                    buf[pname] = []
                if not money.has_key(pname):
                    money[pname] = 0.0
                try:
                    tmptot = float(p['ptotal'])
                except ValueError:
                    tmptot = 0.0
                money[pname] += tmptot
                buf[pname].append([current_step.strftime("%Y-%m-%d %I:%M%p") , money[pname]])
            current_step = current_step + delta

        for p in buf.keys():
            data["labels"].append(p)
            # to improve display
            st = starttime - timedelta(seconds=30)
            buf[p].insert(0, [st.strftime("%Y-%m-%d %I:%M%p") , 0 ])
            et = endtime + timedelta(seconds=30)
            buf[p].append([et.strftime("%Y-%m-%d %I:%M%p") , money[p]])
            data["data"].append(buf[p]) 

    return HttpResponse( simplejson.dumps(data), mimetype="application/json" )

