from django import forms
from registration.forms import RegistrationForm
from django.utils.translation import ugettext_lazy as _
from fusoci.models import UserProfile, DOCUMENT_TYPES
from registration.models import RegistrationProfile
import datetime


class RegistrationFormSocio(RegistrationForm):
    # form = MyForm({'charfield1': 'foo', 'charfield2': 'bar'})
    username = forms.CharField(max_length=30, required=False, label=_(u'Username/Nickname')) 
    born_date = forms.DateField(input_formats=["%d/%m/%Y"] , label=_(u'Data di Nascita'))
    born_place = forms.CharField(max_length=50, required=True, label=_(u'Luogo di Nascita'))
    first_name = forms.CharField(max_length=50, required=True, label=_(u'Nome'))
    last_name = forms.CharField(max_length=50, required=True, label=_(u'Cognome'))
    #doc_type = forms.ChoiceField(choices=DOCUMENT_TYPES, required=True)
    #doc_id = forms.CharField(max_length=20, required=True)
    accepted_eula = forms.BooleanField(required=True, label=_(u'Sono d\'accordo'))
    #photo
    def do_save(self):
        new_u = User(username=str(time()),email= self.cleaned_data.get('email'),)
        new_u.save()
        new_p = Profile.objects.create_profile(new_u)
        new_p.save()
        return new_p
    def save(self, profile_callback=None):
        new_user = RegistrationProfile.objects.create_inactive_user(username=str(time()),
        password=self.cleaned_data['password1'],
        email = self.cleaned_data['email'])
        new_profile = Profile(user=new_user, born_place=self.cleaned_data['born_place'], born_date=self.cleaned_data['born_date'], first_name=self.cleaned_data['first_name'], last_name=self.cleaned_data['last_name'])
        new_profile.save()
        return new_user
