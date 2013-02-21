from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
#from forms import EditFormSocio
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from registration.views import activate
from registration.backends import get_backend
from registration.models import RegistrationProfile
from django.contrib.auth.models import User
from django.db.models import Q
from base.models import * 
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from decimal import Decimal
from datetime import datetime, timedelta
from bar.models import *
from base.tests import in_turnisti
from django.contrib.auth.decorators import user_passes_test


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
