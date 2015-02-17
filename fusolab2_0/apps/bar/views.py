from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template import RequestContext, loader
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from decimal import Decimal
from datetime import datetime, timedelta
from base.models import * 
from bar.models import *
from base.tests import in_turnisti
from django.contrib.auth.decorators import user_passes_test
from bar.forms import *
from math import ceil
import json
import qsstats
import time


@user_passes_test(in_turnisti)
def barcash(request):
    p = Product.objects.all()
    return render_to_response('bar/cash.html', { 'products': p } , context_instance=RequestContext(request))

#@user_passes_test(in_turnisti)
#def barcash2(request):
#    p = Product.objects.all()
#    return render_to_response('bar/cash2.html', { 'products': p } , context_instance=RequestContext(request))


@user_passes_test(in_turnisti)
def deletereceipt(request, receiptid):
    total = 0.0
    try:
        r = Receipt.objects.get(id=receiptid)
        total = r.total
        r.delete()
    except Receipt.DoesNotExist:
        return HttpResponseNotFound("Non e' stato trovato nessuno scontrino con id %s. Come hai fatto a finire qua? Contattare un nerd."  % (receiptid) )

    return HttpResponse("Lo scontrino da %.2f euro con id %s e' stato cancellato con successo" % (total, receiptid) )


@csrf_exempt
#@user_passes_test(in_turnisti)
#def addpurchasedproduct(request):
#    data = request.POST.get('q')
#    total = 0.0
#    if (data):
#       r = Receipt()
#
#       r.cashier = request.user.get_profile()
#       r.total = total
#       r.save()
#       jdata = simplejson.loads(data)
#       for p in jdata: #data.getlist('purchased_products') :
#           p_type = Product.objects.get(id = int(p['type']) ) 
#           for i in range(0, int(p['quantity'] ) ):
#               pp = PurchasedProduct()
#
#               pp.name = p_type.name
#               pp.cost = p_type.cost
#               total = total + float(pp.cost) 
#               pp.receipt = r
#               pp.save()
#       r.total = total
#       r.save()
#       #return HttpResponse( "{'receipt_id' : " + str(r.id) + "}", mimetype="application/json")
#       response_data = { 'receipt_id' : r.id }
#       return HttpResponse( simplejson.dumps(response_data), mimetype="application/json" )
#    else:
#       return HttpResponseNotFound("errore: non sono stati trovati dati")

@csrf_exempt
@user_passes_test(in_turnisti)
def addpurchasedproduct(request):
    data = request.POST.get('q')
    total = 0.0
    if (data):
       r = Receipt()

       r.cashier = request.user.get_profile()
       r.total = total
       r.save()
       jdata = simplejson.loads(data)
       for p in jdata: #data.getlist('purchased_products') :
           p_type = Product.objects.get(id = int(p['type']) ) 
           for i in range(0, int(p['quantity'] ) ):
               pp = PurchasedProduct()

               pp.name = p_type.name
               pp.cost = float(p['price'])#p_type.cost
               total = total + float(pp.cost) 
               pp.receipt = r
               pp.save()
       r.total = total
       r.save()
       #return HttpResponse( "{'receipt_id' : " + str(r.id) + "}", mimetype="application/json")
       response_data = { 'receipt_id' : r.id }
       return HttpResponse( simplejson.dumps(response_data), mimetype="application/json" )
    else:
       return HttpResponseNotFound("errore: non sono stati trovati dati")

@user_passes_test(in_turnisti)
def bar_balance_form(request, balance_type):
    forms = {
                'open': { 'name': 'Apri Cassa Bar', 'form': BarOpeningModelForm }, 
                'close': { 'name': 'Chiudi Cassa Bar', 'form': BarClosingModelForm },
                'withdraw': { 'name': 'Inserisci Prelievo', 'form': BarWithdrawModelForm },
                'payment': { 'name': 'Inserisci Pagamento', 'form': BarPaymentModelForm },
                'deposit': { 'name': 'Inserisci Deposito', 'form': BarDepositModelForm },
            }
    if balance_type in forms.keys():
        formname = forms[balance_type]['name']
        if request.method == 'POST':
            form = forms[balance_type]['form'](request.POST)  
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/tuttoapposto/bar/')
        else:
            form = forms[balance_type]['form'](initial={'cashier': request.user.get_profile()})  
    else:
        raise Http404
    return render_to_response('bar/bar_balance_forms.html', { 'formname': formname, 'form': form } , context_instance=RequestContext(request))


@user_passes_test(in_turnisti)
def bar_smallbalance_form(request, balance_type):
    forms = {
                'point': { 'name': 'Punto di Cassa', 'form': SmallCashpointModelForm}, 
                'payment': { 'name': 'Pagamento ', 'form': SmallPaymentModelForm},
                'deposit': { 'name': 'Deposito', 'form': SmallDepositModelForm},
                'withdraw': { 'name': 'Prelievo', 'form': SmallWithdrawModelForm},
            }
    if balance_type in forms.keys():
        formname = forms[balance_type]['name']
        if request.method == 'POST':
            form = forms[balance_type]['form'](request.POST)  
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/tuttoapposto/bar/')
        else:
            form = forms[balance_type]['form'](initial={'cashier': request.user.get_profile()})  
    else:
        raise Http404
    return render_to_response('bar/bar_balance_forms.html', { 'formname': formname, 'form': form } , context_instance=RequestContext(request))


def stock_market_activate(request):
    pd = PriceListDisplay.objects.get(pk=1)
    pd.variation_active = True
    pd.save()
    return HttpResponse("OK attivato")


def stock_market_deactivate(request):
    pd = PriceListDisplay.objects.get(pk=1)
    pd.variation_active = False
    pd.save()
    #Restore price to their default
    for p in Product.objects.filter(can_change=True):
        p.cost = p.default_price
        p.save()
    return HttpResponse("OK disattivato")

def stock_market_current_prices(request):
    prices = []
    for p in Product.objects.all():
        prices.append({'id': p.id, 'price': float(p.cost)})
    return HttpResponse(json.dumps(prices), content_type="application/json")



# listino
def price_list(request):
    bar_items = Product.objects.all().exclude(name__icontains = ' int').exclude(name__icontains = 'cibo aperitivo') #filter out internal products and extra stuff
    # rename
    new_names = {
            'birra chiara': ('birra chiara', 'alla spina'),
            'birra dm': ('doppio malto', 'alla spina'),
            'birra in bottiglia': ('birra artigianale', ''),
            }
    for item in bar_items:
        if item.name.lower() in new_names.keys():
            item.name = new_names[item.name.lower()]
        else:
            item.name = (item.name, '')
    ctx = {'items' : bar_items}
    return render_to_response('bar/price_list.html', ctx , context_instance=RequestContext(request))

def poll_price_list(request):
    response_data = {}
    messages = []
    stockmarket = []
    prices = [] 
    # TODO these messages can be set according to price variation
    frasi_simpatiche = [
        'ATTENZIONE si avvisano i gentilissimi soci fusolab tra poco cambiera\' il listino',
        'Birra in calo: colpa del caldo?',
        'E\' tua la jaguar parcheggiata davanti all\'ingresso?',
    ]
    messages = frasi_simpatiche

    isUpdated = False
    for p in Product.objects.all():
        prices.append({'id': p.id, 'price': float(p.cost), 'name': p.name})
        if p.trend == 'r':
            s = "%s (%s) %d <span class='rise'>&#9650;</span>" % (p.name, p.symbol, p.cost)
        elif p.trend == 'f':
            s = "%s (%s) %d <span class='dawn'>&#9660;</span>" % (p.name, p.symbol, p.cost)

        if p.updated:
            isUpdated = True
    #if response_data is empty, no update happens
    if isUpdated:
        response_data['prices'] =  prices
        response_data['messages'] = messages
        response_data['stockmarket'] = stockmarket
    else:
        response_data['prices'] = []
        response_data['messages'] = []
        response_data['stockmarket'] = []
    #response_data['stockmarket'] = ['Ingressi (INR) 142.0 <span class="rise">&#9650;</span>', 'BIRRE (BRR) 412.0 <span class="rise">&#9650;</span>', 'COCKTAIL (CKT) 112.0 <span class="dawn">&#9660;</span>']
    return HttpResponse(json.dumps(response_data), content_type="application/json")

def datetimeIterator(from_date=None, to_date=None, delta=timedelta(minutes=1)):
    from_date = from_date or datetime.now()
    while to_date is None or from_date <= to_date:
        yield from_date
        from_date = from_date + delta
    return

def get_market_stats(request,product,granularity):
    #granularity = 30
    response_data = {}
    s = []  
    # if not BarBalance.objects.is_open():
    #     pass
    #     #return HttpResponse(json.dumps(response_data), content_type="application/json")                
    # else:
        #start = BarBalance.objects.get_parent_t().date
    start = datetime.datetime(2015,01,17,19,7,31)
    #now = datetime.now()
    now = datetime.datetime(2015,01,18,6,9,0)
    interval = datetime.timedelta(seconds=int(granularity)*60)
    qs = PurchasedProduct.objects.filter(receipt__date__range=[start,now])

    qqs = qs.filter(name=product)
    sold = []
    d = []
    i = 0
    for sample_time in datetimeIterator(start,now,interval):
        e = int(granularity) + qqs.filter( receipt__date__range = [sample_time,sample_time+interval] ).count()
        sold.append( e )
        if i > 0: 
            stamp  = sample_time+interval
            d.append( [  int(time.mktime(stamp.timetuple())*1000) , ceil(100*(sold[i]-sold[i-1])/(sold[i-1]+0.01))] )
        i+=1
    s.append( { 'key' : product , 'values' : d } )
    response_data['data']  = s
    return HttpResponse(json.dumps(response_data), content_type="application/json")
