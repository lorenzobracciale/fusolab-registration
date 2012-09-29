from django import forms
from django.forms import ModelForm
from registration.forms import RegistrationForm
from django.utils.translation import ugettext_lazy as _
from fusoci.models import UserProfile, DOCUMENT_TYPES
from registration.models import RegistrationProfile
from django.contrib.auth.models import User
from models import UserProfile
import datetime


class RegistrationFormSocio(RegistrationForm):
    first_name = forms.CharField(max_length=50, label=_(u'Nome'))
    last_name = forms.CharField(max_length=50, label=_(u'Cognome'))

    born_date = forms.DateField(input_formats=["%d/%m/%Y"] , label=_(u'Data di Nascita'))
    born_place = forms.CharField(max_length=50, label=_(u'Luogo di Nascita'))
    accepted_eula = forms.BooleanField(label=_(u'Sono d\'accordo'))

    #override
    username = forms.CharField(max_length=30, required=False, label=_(u'Username/Nickname')) 
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                required=False, label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                required=False, label=_("Password (di nuovo)"))

class EditFormSocio(RegistrationForm):
    first_name = forms.CharField(max_length=50, label=_(u'Nome'))
    last_name = forms.CharField(max_length=50, label=_(u'Cognome'))
    born_date = forms.DateField(input_formats=["%d/%m/%Y"] , label=_(u'Data di Nascita'))
    born_place = forms.CharField(max_length=50, label=_(u'Luogo di Nascita'))
    doc_type = forms.ChoiceField(choices=DOCUMENT_TYPES, label=_(u'Documento'))
    doc_id = forms.CharField(max_length=20, label=_(u'N documento'))

    username = forms.RegexField(regex=r'^[\w.@+-]+$',
                                max_length=30,
                                widget=forms.TextInput(),
                                label=_("Username/Nickname"),
                                error_messages={'invalid': _("Questo campo puo' contenere solo lettere, numeri e questi caratteri @/./+/-/_ ")})
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                label=_("Password"), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                label=_("Password (di nuovo)"), required=False)

    photo = forms.ImageField(required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(EditFormSocio, self).__init__(*args, **kwargs)


    def clean(self):
        has_password = self.request.user.has_usable_password()
        if not has_password:
            if 'password1' not in self.cleaned_data and 'password2' not in self.cleaned_data:
                raise forms.ValidationError(_("Non hai impostato nessuna password."))

        if 'password1' in self.cleaned_data or 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("Le password non corrispondono."))

        return self.cleaned_data

    def clean_username(self):
        if self.request.user.username  != self.cleaned_data['username']:
            existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
            if existing.exists():
                raise forms.ValidationError(_("A user with that username already exists."))
        return self.cleaned_data['username']
    
    def do_save(self):
        user = self.request.user
        profile = user.get_profile()

        data = self.cleaned_data 
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.username = data['username']
        if data['password1'] and len(data['password1']) > 0:
            user.password = data['password1']

        profile.born_date, profile.born_place = data['born_date'], data['born_place']
        profile.doc_type, profile.doc_id = data['doc_type'], data['doc_id']
        #TODO profile.photo = 

        profile.user = user
        profile.save()
        user.save()

