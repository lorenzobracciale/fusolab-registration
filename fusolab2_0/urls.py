#from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from base.forms import RegistrationFormSocio, EditFormSocio
from base.models import UserProfile
from registration.views import register, activate


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^bar/', include('bar.urls')),
    url(r'^ingresso/', include('ingresso.urls')),
    url(r'^salutatore/', include('salutatore.urls')),
    url(r'^baraled/', include('baraled.urls')),
    url(r'^reports/', include('reports.urls')),
    url(r'^cancello/', include('cancello.urls')),


    url(r'^accounts/register/$', register, {'form_class': RegistrationFormSocio,
        'backend': 'base.regbackend.FusolabBackend' },
         name='registration_register'),
    url(r'^accounts/', include('registration.backends.default.urls')),

    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^grappelli/', include('grappelli.urls')), # grappelli URLS
    url(r'^admin/', include(admin.site.urls)),

    url(r'^', include('base.urls')),
    #include('base.urls'),
)
