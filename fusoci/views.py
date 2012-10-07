from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from forms import EditFormSocio
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
import datetime
from registration.views import activate
from registration.backends import get_backend
from registration.models import RegistrationProfile
from django.contrib.auth.models import User
from django.db.models import Q
from fusoci.models import UserProfile, Card
from django.conf import settings


from fusoci.regbackend import FusolabBackend

def home(request):
    return render_to_response('fusoci/index.html', {} , context_instance=RequestContext(request))

def statuto(request):
    return render_to_response('fusoci/statuto.html', {} , context_instance=RequestContext(request))

@staff_member_required
def card(request):
    return render_to_response('fusoci/card.html', { 'URL_CARD': settings.URL_CARD } , context_instance=RequestContext(request))

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
        return HttpResponse("Card registrata!")
    return HttpResponse("Errore: non ho trovato il socio o il sn non e' valido.")


@staff_member_required
def ajax_user_search(request):
    if request.is_ajax():
        q = request.GET.get('q')
        if q is not None:            
            results = User.objects.filter( 
                Q(email__contains = q) |
                Q(last_name__contains = q)).order_by('username')
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
                        #TODO pic
                        }
            if activation_key:
                init_dict.pop('username') #force users to choose a username
            form = EditFormSocio(initial=init_dict, request=request) #create empty form
        return render_to_response('registration/edit.html', {'form': form} , context_instance=RequestContext(request))

    else: #user is not authenticated or no activation key is provided
        return HttpResponseRedirect("/accounts/login/")
