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
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils import simplejson
import json
from decimal import Decimal
from datetime import datetime, timedelta
from django.http import Http404
from ingresso.models import *
from django.contrib.auth.decorators import user_passes_test
from base.tests import in_turnisti
from ingresso.forms import *
from bar.managers import OPENING

from base.regbackend import FusolabBackend

@user_passes_test(in_turnisti)
def card(request):
    entrance_balances = EntranceBalance.objects.filter(operation=OPENING).order_by('-date')
    if entrance_balances.exists():
        customers_n = Entrance.objects.filter(date__gte=entrance_balances[0].date).count()  
    else:
        customers_n = 0 
    return render_to_response('ingresso/card.html', { 'URL_CARD': settings.URL_CARD, 'customers_n': customers_n } , context_instance=RequestContext(request))

@user_passes_test(in_turnisti)
def entrance_balance_form(request, balance_type):
    forms = {
                'open': { 'name': 'Apri Cassa Ingresso', 'form': EntranceOpeningModelForm }, 
                'close': { 'name': 'Chiudi Cassa Ingresso', 'form': EntranceClosingModelForm },
                'withdraw': { 'name': 'Inserisci Prelievo', 'form': EntranceWithdrawModelForm },
                'payment': { 'name': 'Inserisci Pagamento', 'form': EntrancePaymentModelForm },
                'deposit': { 'name': 'Inserisci Deposito', 'form': EntranceDepositModelForm },
            }
    if balance_type in forms.keys():
        formname = forms[balance_type]['name']
        if request.method == 'POST':
            form = forms[balance_type]['form'](request.POST)  
            if form.is_valid():
                form.save()
                return HttpResponseRedirect('/tuttoapposto/ingresso/')
        else:
            form = forms[balance_type]['form'](initial={'cashier': request.user.get_profile()})  
    else:
        raise Http404
    return render_to_response('ingresso/entrance_balance_forms.html', { 'formname': formname, 'form': form } , context_instance=RequestContext(request))


@user_passes_test(in_turnisti)
def delete_entrance(request, entranceid=None):
    resp = {}
    try:
        e = Entrance.objects.get(id=entranceid)
        e.delete()
        resp['txt'] = "Ingresso eliminato"
    except Entrance.DoesNotExist:
        resp['txt'] = "Ingresso non trovato"
    entrance_balances = EntranceBalance.objects.filter(operation=OPENING).order_by('-date')
    resp['customers_n'] = Entrance.objects.filter(date__gte=entrance_balances[0].date).count()
    return HttpResponse(json.dumps(resp), mimetype="application/json" )


@user_passes_test(in_turnisti)
def entrance(request, cost=None):
    resp = {}
    if cost:
        e = Entrance()
        # set the cost
        try:
            e.cost = Decimal(cost) 
        except:
            resp['txt'] = "Il costo non e' valido." 
            return HttpResponse(json.dumps(resp), mimetype="application/json" )
        e.save()
        resp['txt'] = "Aggiunto ingresso di %.1f euro (id %d). <a href='#' class='cancel-entrance' data-eid='%d'>Cancella Ingresso</a>" % (e.cost , e.id, e.id) 
        entrance_balances = EntranceBalance.objects.filter(operation=OPENING).order_by('-date')
        if entrance_balances.exists():
            resp['customers_n'] = Entrance.objects.filter(date__gte=entrance_balances[0].date).count()  
        else:
            resp['customers_n'] = 0 

        return HttpResponse(json.dumps(resp), mimetype="application/json" )
    else:
        resp['txt'] = "Non e' stato inserito nessun costo (mettere 0 se entra aggratis)" 
        return HttpResponse(json.dumps(resp), mimetype="application/json" )


@user_passes_test(in_turnisti)
def viewcard(request):
    sn = request.GET.get('sn') or None
    if sn and len(sn) > 0 :
        try:
            c = Card.objects.get(sn=sn) 
            return HttpResponse("Tessera <a href='/admin/base/card/" + str(c.id) +  "'>" + sn + "</a> appartenente a <a href='/admin/auth/user/" + str(c.user.id) + "'>" + c.user.user.first_name + " " + c.user.user.last_name + "</a>" )
        except Card.DoesNotExist:
            return HttpResponse(sn + ". La tessera non e' di nessun socio.")


@user_passes_test(in_turnisti)
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
        return HttpResponse("Tessera per %s registrata con id %s" % (str(user[0].user.get_full_name()), str(c.id)) )
    return HttpResponse("Errore: non ho trovato il socio o il numero seriale non e' valido.")

def change_mode_bancone_sopra(request):
    import liblo
    UDP_IP = settings.BAR_SOPRA_IP
    UDP_PORT = settings.BAR_SOPRA_PORT
    try:
        target = liblo.Address(UDP_IP, UDP_PORT)
        liblo.send(target, "/modd")
    except liblo.AddressError, err:
        print str(err)
    return HttpResponse('changed sopra')

def change_mode_bancone_sotto(request):
    import liblo
    UDP_IP = settings.BAR_SOTTO_IP
    UDP_PORT = settings.BAR_SOTTO_PORT
    try:
        target = liblo.Address(UDP_IP, UDP_PORT)
        liblo.send(target, "/modd")
    except liblo.AddressError, err:
        print str(err)
    return HttpResponse('changed sotto')

def change_color_bancone_sopra(request, color):
    import liblo
    UDP_IP = settings.BAR_SOPRA_IP
    UDP_PORT = settings.BAR_SOPRA_PORT
    try:
        target = liblo.Address(UDP_IP, UDP_PORT)
        liblo.send(target, "/knbr", float(int(color[0:2], 16))/255.0)
        liblo.send(target, "/knbg", float(int(color[2:4], 16))/255.0)
        liblo.send(target, "/knbb", float(int(color[4:6], 16))/255.0)
    except liblo.AddressError, err:
        print str(err)
    return HttpResponse(color)



def change_color_bancone_sotto(request, color):
    import liblo
    UDP_IP = settings.BAR_SOTTO_IP
    UDP_PORT = settings.BAR_SOTTO_PORT
    try:
        target = liblo.Address(UDP_IP, UDP_PORT)
        liblo.send(target, "/knbr", float(int(color[0:2], 16))/255.0)
        liblo.send(target, "/knbg", float(int(color[2:4], 16))/255.0)
        liblo.send(target, "/knbb", float(int(color[4:6], 16))/255.0)
    except liblo.AddressError, err:
        print str(err)
    return HttpResponse(color)

@user_passes_test(in_turnisti)
def ajax_user_search(request, q=None):
    if q:            
        results = User.objects.filter( 
            Q(email__icontains = q) |
            Q(last_name__icontains = q)).order_by('username')
        for user in results:
            user.cards = Card.objects.filter(user=user.get_profile())
        template = 'ingresso/results.html'
        data = {
            'results': results,
        }
        return render_to_response(template, data, 
            context_instance = RequestContext(request))
    else:
       return HttpResponseNotFound('<h1>Brutta richiesta!</h1>')

