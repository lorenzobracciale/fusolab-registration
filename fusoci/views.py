from django.http import HttpResponse
from django.contrib.auth import logout
import datetime


def home(request):
   return HttpResponse('<h1>Page was found</h1>')

