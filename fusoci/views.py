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
def card(request):
    return render_to_response('fusoci/card.html', { 'URL_CARD': settings.URL_CARD } , context_instance=RequestContext(request))

@staff_member_required

def entrance(request, cardid=None, cost=None):
    if cardid and cost:
        e = Entrance()
        # set the cost
        try:
            e.cost = Decimal(cost) 
        except:
            return HttpResponseNotFound("Il costo non e' valido.")
        # set the user
        try:
            c = Card.objects.get(sn = cardid)
            e.user = c.user 
        except:
            return HttpResponseNotFound("La carta non e' valida.")
        #get last entrance for that user or none
        try:
            last_entrance = Entrance.objects.filter(user = c.user).order_by('-date')[0]
        except:
            last_entrance = None
        #if last_entrance: 
        #    if (datetime.datetime.now() - last_entrance.date).seconds/3600 < 12 h:
        #    return HttpResponseNotFound("Oggi e' gia stata registrata un'entrata per questo utente")
        e.save()
        return HttpResponse("E' entrato %s - %s" % (c.user.user.first_name , e.user.user.last_name ) )
    else:
        return HttpResponseNotFound("No card id or cost")

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


@staff_member_required
def viewcard(request):
    sn = request.GET.get('sn') or None
    if sn and len(sn) > 0 :
        try:
            c = Card.objects.get(sn=sn) 
            return HttpResponse("Tessera <a href='/admin/fusoci/card/" + str(c.id) +  "'>" + sn + "</a> appartenente a <a href='/admin/auth/user/" + str(c.user.id) + "'>" + c.user.user.first_name + " " + c.user.user.last_name + "</a>" )
        except Card.DoesNotExist:
            return HttpResponse(sn + ". La tessera non e' di nessun socio.")


@staff_member_required
def makecard(request):
    userid = request.GET.get('userid') or None
    user = UserProfile.objects.filter(user__id=userid)
    sn = request.GET.get('sn') or None
    if user and sn:
        c = Card(sn=sn, user=user[0]) 
        try:
            c.save()
        except:
            return HttpResponse("Errore: non e' stato possibile inserire la carta nel database. Tessera gia' inserita? ")
        return HttpResponse("Card registrata con id " + str(c.id) )
    return HttpResponse("Errore: non ho trovato il socio o il sn non e' valido.")


@staff_member_required
def ajax_user_search(request):
    if request.is_ajax():
        q = request.GET.get('q')
        if q is not None:            
            results = User.objects.filter( 
                Q(email__icontains = q) |
                Q(last_name__icontains = q)).order_by('username')
            #results = [user.cards = list(Card.objects.filter(user=user.get_profile())) for user in results]
            for user in results:
                user.cards = Card.objects.filter(user=user.get_profile())
            template = 'fusoci/results.html'
            data = {
                'results': results,
            }
            return render_to_response(template, data, 
                context_instance = RequestContext(request))
    else:
       return HttpResponseNotFound('<h1>Brutta richiesta!</h1>')

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
