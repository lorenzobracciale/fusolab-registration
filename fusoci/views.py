from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from forms import EditFormSocio
from django.contrib.auth.decorators import login_required
import datetime
from registration.views import activate
from registration.backends import get_backend
from registration.models import RegistrationProfile

from fusoci.regbackend import FusolabBackend

def home(request):
    return render_to_response('fusoci/index.html', {} , context_instance=RequestContext(request))

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
            form = EditFormSocio(request.POST, request=request, activation_key=activation_key, activating_user=user)  
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
                        #TODO pic
                        }
            if activation_key:
                init_dict.pop('username') #force users to choose a username
            form = EditFormSocio(initial=init_dict, request=request) #create empty form
        return render_to_response('registration/edit.html', {'form': form} , context_instance=RequestContext(request))

    else: #user is not authenticated or no activation key is provided
        return HttpResponseRedirect("/accounts/login/")
