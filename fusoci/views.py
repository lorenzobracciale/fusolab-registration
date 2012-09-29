from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from forms import EditFormSocio
from django.contrib.auth.decorators import login_required
import datetime


def home(request):
    return render_to_response('fusoci/index.html', {} , context_instance=RequestContext(request))

@login_required(login_url='/accounts/login/')
def edit(request):
    user = request.user
    profile = user.get_profile()
    if request.method == 'POST':
        form = EditFormSocio(request.POST, request=request)  
        if form.is_valid():
            form.do_save()
            return render_to_response('registration/edit_complete.html', { } , context_instance=RequestContext(request))
    else:
        init_dict={ 'first_name': user.first_name, 
                    'last_name': user.last_name,
                    'username': user.username,
                    'email': user.email,
                    'born_date': profile.born_date.strftime('%d/%m/%Y'),
                    'born_place': profile.born_place,
                    'doc_type': profile.doc_type,
                    'doc_id': profile.doc_id,
                    #TODO pic
                    }
        form = EditFormSocio(initial=init_dict, request=request)
    return render_to_response('registration/edit.html', {'form': form} , context_instance=RequestContext(request))
