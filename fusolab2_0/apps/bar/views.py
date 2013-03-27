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


@user_passes_test(in_turnisti)
def barcash(request):
    p = Product.objects.all()
    return render_to_response('base/cash.html', { 'products': p } , context_instance=RequestContext(request))


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
       return HttpResponseNotFound

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
    return render_to_response('base/bar_balance_forms.html', { 'formname': formname, 'form': form } , context_instance=RequestContext(request))


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
    return render_to_response('base/bar_balance_forms.html', { 'formname': formname, 'form': form } , context_instance=RequestContext(request))



