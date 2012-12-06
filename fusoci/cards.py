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

@csrf_exempt
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

