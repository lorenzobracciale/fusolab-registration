from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
import datetime


def home(request):
    return render_to_response('fusoci/index.html', {} , context_instance=RequestContext(request))
