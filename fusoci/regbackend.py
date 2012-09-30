# regbackend.py
import profile, re, unidecode
from fusoci.forms import RegistrationFormSocio
from registration.backends.default import DefaultBackend

from django.contrib.sites.models import Site
from django.contrib.auth.models import User 
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from registration.models import RegistrationProfile
from registration import signals

from models import UserProfile

from fusoci.forms import EditFormSocio

def slugify(str):
    str = unidecode.unidecode(str).lower()
    return re.sub(r'\W+','-',str)

class FusolabBackend(DefaultBackend):
    def register(self, request, **kwargs):
        import string, random
        email = kwargs['email']
        first_name, last_name = kwargs['first_name'], kwargs['last_name']
        born_date, born_place = kwargs['born_date'], kwargs['born_place']
        proposed_username = first_name + last_name 
        proposed_username = slugify(proposed_username) 
        #assure username is unique
        username = proposed_username
        unique_n = 0
        while True:
            if User.objects.filter(username=proposed_username).count() > 0:
                unique_n += 1
                proposed_username = username + str(unique_n)
            else:
                break
        username = proposed_username
        #now username is unique
        password = ''  #soon will be unusable
        if Site._meta.installed:
            site = Site.objects.get_current()
        else:
            site = RequestSite(request)
        new_user = RegistrationProfile.objects.create_inactive_user(username, email,
                                                                    password, site)
        new_user.first_name = first_name
        new_user.last_name = last_name
        new_user.set_unusable_password()
        new_user.save()

        userprofile = new_user.get_profile()
        userprofile.born_place = born_place 
        userprofile.born_date = born_date
        userprofile.save()

        signals.user_registered.send(sender=self.__class__,
                                     user=new_user,
                                     request=request)
        return new_user
