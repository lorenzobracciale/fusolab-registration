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
from decimal import Decimal
from datetime import datetime, timedelta
from django.http import Http404
from ingresso.models import *
from django.contrib.auth.decorators import user_passes_test
from base.tests import in_turnisti
from ingresso.forms import *

from base.regbackend import FusolabBackend

@user_passes_test(in_turnisti)
def card(request):
    return render_to_response('base/card.html', { 'URL_CARD': settings.URL_CARD } , context_instance=RequestContext(request))

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
    return render_to_response('base/entrance_balance_forms.html', { 'formname': formname, 'form': form } , context_instance=RequestContext(request))


@user_passes_test(in_turnisti)
def delete_entrance(request, entranceid=None):
    try:
        e = Entrance.objects.get(id=entranceid)
        e.delete()
        return HttpResponse("Ingresso eliminato<br /><a href='/ingresso/card'>Torna alla pagina precedente</a>")
    except Entrance.DoesNotExist:
        return HttpResponseNotFound("Ingresso non trovato<br /><a href='/ingresso/card'>Torna alla pagina precedente</a>")


@user_passes_test(in_turnisti)
def entrance(request, cost=None):
    if cost:
        e = Entrance()
        # set the cost
        try:
            e.cost = Decimal(cost) 
        except:
            return HttpResponse("Il costo non e' valido.")
        e.save()
        return HttpResponse("Aggiunto ingresso di %.1f euro (id %d). <a href='/ingresso/delete/%d/'>Cancella Ingresso</a>" % (e.cost , e.id, e.id ) )
    else:
        return HttpResponse("Non e' stato inserito nessun costo (mettere 0 se entra aggratis)")


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
        return HttpResponse("Card registrata con id " + str(c.id) )
    return HttpResponse("Errore: non ho trovato il socio o il sn non e' valido.")

@user_passes_test(in_turnisti)
def open_gate(request):
    import socket
    from fusolab2_0 import settings
    UDP_IP = settings.IP_OPENER
    UDP_PORT = settings.PORT_OPENER
    MESSAGE = settings.OPEN_GATE_PW
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
    return HttpResponse("Cancello Aperto")


@user_passes_test(in_turnisti)
def ajax_user_search(request, q=None):
    if q:            
        results = User.objects.filter( 
            Q(email__icontains = q) |
            Q(last_name__icontains = q)).order_by('username')
        for user in results:
            user.cards = Card.objects.filter(user=user.get_profile())
        template = 'base/results.html'
        data = {
            'results': results,
        }
        return render_to_response(template, data, 
            context_instance = RequestContext(request))
    else:
       return HttpResponseNotFound('<h1>Brutta richiesta!</h1>')

