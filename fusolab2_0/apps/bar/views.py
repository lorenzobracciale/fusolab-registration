from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
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
import json


@user_passes_test(in_turnisti)
def barcash(request):
    p = Product.objects.all()
    return render_to_response('bar/cash.html', { 'products': p } , context_instance=RequestContext(request))


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
               pp.cost = p_type.cost
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
    response_data['messages'] = [ 'ATTENZIONE si avvisano i gentilissimi soci fusolab tra poco cambiera\' il listino', 'Birra in calo: colpa del caldo?', 'Cocktail in aumento smodato: hai mai provato il fusococktail?', 'Arrivano i nostri: picco di 5 ingressi 5 minuti fa' ]
    prices = [] 
    for p in Product.objects.all():
        prices.append({'id': p.id, 'price': float(p.cost), 'name': p.name})
    response_data['prices'] =  prices
    response_data['stockmarket'] = ['Ingressi (INR) 142.0 <span class="rise">&#9650;</span>', 'BIRRE (BRR) 412.0 <span class="rise">&#9650;</span>', 'COCKTAIL (CKT) 112.0 <span class="dawn">&#9660;</span>']
    return HttpResponse(json.dumps(response_data), content_type="application/json")

