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

@staff_member_required
def card(request):
    return render_to_response('fusoci/card.html', { 'URL_CARD': settings.URL_CARD } , context_instance=RequestContext(request))

@staff_member_required
def delete_entrance(request, entranceid=None):
    try:
        e = Entrance.objects.get(id=entranceid)
        e.delete()
        return HttpResponse("Ingresso eliminato<br /><a href='/card/'>Torna alla pagina precedente</a>")
    except Entrance.DoesNotExist:
        return HttpResponseNotFound("Ingresso non trovato<br /><a href='/card/'>Torna alla pagina precedente</a>")


@staff_member_required
def entrance(request, cost=None):
    if cost:
        e = Entrance()
        # set the cost
        try:
            e.cost = Decimal(cost) 
        except:
            return HttpResponse("Il costo non e' valido.")
        e.save()
        return HttpResponse("Aggiunto ingresso di %.1f euro (id %d). <a href='/entrance/delete/%d/'>Cancella Ingresso</a>" % (e.cost , e.id, e.id ) )
    else:
        return HttpResponse("Non e' stato inserito nessun costo (mettere 0 se entra aggratis)")


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
def ajax_user_search(request, q=None):
    if q:            
        results = User.objects.filter( 
            Q(email__icontains = q) |
            Q(last_name__icontains = q)).order_by('username')
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

