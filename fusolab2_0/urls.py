#from django.conf.urls import patterns, include, url
from django.conf.urls.defaults import *
from django.contrib.auth.views import login, logout
from fusoci.forms import RegistrationFormSocio, EditFormSocio
from fusoci.models import UserProfile
from registration.views import register, activate


# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'fusoci.views.home', name='home' ),
    url(r'^statuto/$', 'fusoci.views.statuto', name='statuto'),

    url(r'^accounts/edit/$', 'fusoci.views.edit', name='edit'),

    url( r'^users/$', 'fusoci.views.ajax_user_search', name = 'user_search' ),
    url(r'^card/$', 'fusoci.views.card', name='card'),
    url(r'^makecard/$', 'fusoci.views.makecard', name='makecard'),
    url(r'^viewcard/$', 'fusoci.views.viewcard', name='viewcard'),


    url(r'^accounts/register/$', register, {'form_class': RegistrationFormSocio,
        'backend': 'fusoci.regbackend.FusolabBackend' },
         name='registration_register'),

    url(r'activate/(?P<activation_key>\w+)/$',
        'fusoci.views.edit', name='edit'),
    url(r'^index.html$', 'fusoci.views.home'),
    url(r'^accounts/', include('registration.backends.default.urls')),
    # Uncomment the admin/doc line below to enable admin documentation:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    url(r'^admin/', include(admin.site.urls)),
)
