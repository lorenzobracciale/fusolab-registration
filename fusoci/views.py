from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from forms import EditFormSocio
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from registration.views import activate
from registration.backends import get_backend
from registration.models import RegistrationProfile
from django.contrib.auth.models import User
from django.db.models import Q
from fusoci.models import * 
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
from decimal import Decimal
from datetime import datetime, timedelta


from fusoci.regbackend import FusolabBackend

def home(request):
    return render_to_response('fusoci/index.html', {} , context_instance=RequestContext(request))

def statuto(request):
    return render_to_response('fusoci/statuto.html', {} , context_instance=RequestContext(request))

@staff_member_required
def barcash(request):
    p = Product.objects.all()
    return render_to_response('fusoci/cash.html', { 'products': p } , context_instance=RequestContext(request))


@staff_member_required
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
@staff_member_required
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


def edit(request, activation_key=None):
    if request.user.is_authenticated() or activation_key:
        if activation_key:
            #grab user 
            try:
                user = RegistrationProfile.objects.get(activation_key=activation_key).user
            except RegistrationProfile.DoesNotExist:
                user = None
        else:
            user = request.user
        if not user:
            return render_to_response('registration/activate.html', { } , context_instance=RequestContext(request))

        profile = user.get_profile()
        if request.method == 'POST':
            form = EditFormSocio(request.POST, request.FILES, request=request, activation_key=activation_key, activating_user=user)  
            if form.is_valid():
                if activation_key:
                    activate(request, backend='fusoci.regbackend.FusolabBackend', activation_key=activation_key)
                    user.is_active = True
                    user.save()
                form.do_save(user=user)
                return render_to_response('registration/edit_complete.html', { } , context_instance=RequestContext(request))
        else:
            if profile.born_date:
                mydate = profile.born_date.strftime('%d/%m/%Y')
            else:
                mydate = ''

            init_dict={ 'first_name': user.first_name, 
                        'last_name': user.last_name,
                        'username': user.username,
                        'email': user.email,
                        'born_date': mydate, 
                        'born_place': profile.born_place,
                        'doc_type': profile.doc_type,
                        'doc_id': profile.doc_id,
                        'how_hear': profile.how_hear,
                        'photo': profile.photo,
                        }
            if activation_key:
                init_dict.pop('username') #force users to choose a username
            form = EditFormSocio(initial=init_dict, request=request) #create empty form
        return render_to_response('registration/edit.html', {'form': form} , context_instance=RequestContext(request))

    else: #user is not authenticated or no activation key is provided
        return HttpResponseRedirect("/accounts/login/")
