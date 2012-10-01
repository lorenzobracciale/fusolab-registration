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
    first_name = forms.CharField(max_length=50, required=True, label=_(u'Nome'))
    last_name = forms.CharField(max_length=50, required=True, label=_(u'Cognome'))

    born_date = forms.DateField(input_formats=["%d/%m/%Y"] , label=_(u'Data di Nascita (gg/mm/aaaa)'))
    born_place = forms.CharField(max_length=50, label=_(u'Luogo di Nascita'))
    accepted_eula = forms.BooleanField(label=_(u'Si, lo voglio'))

    #override
    username = forms.CharField(max_length=30, required=False, label=_(u'Username/Nickname')) 
    password1 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                required=False, label=_("Password"))
    password2 = forms.CharField(widget=forms.PasswordInput(render_value=False),
                                required=False, label=_("Password (di nuovo)"))
    def clean(self):
        cdata = self.cleaned_data
        if 'first_name' in cdata and 'last_name' in cdata and 'email' in cdata:
            if User.objects.filter(first_name=cdata['first_name'], last_name=cdata['last_name'], email=cdata['email']).count() > 0:
                raise forms.ValidationError(_("Risulti gia' iscritto. Se ti sei dimenticato la password, Vai su login->ho dimenticato la password."))

            # check for funny names
            from funnynames import funny_names
            firstlastname = self.cleaned_data['first_name'] + self.cleaned_data['last_name']
            firstlastname = firstlastname.lower()

            for funny_name in funny_names:
                if len(funny_name) > 0: #sanity check 
                    found = True 
                    for part in funny_name:
                        if firstlastname.find(part.lower()) < 0:
                            found = False 
                    if found:
                        raise forms.ValidationError(_("LOL!"))

        return cdata

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
        self.activation_key = kwargs.pop('activation_key', None)
        self.activating_user = kwargs.pop('activating_user', None)
        super(EditFormSocio, self).__init__(*args, **kwargs)


    def clean(self):
        if self.activation_key:
            try:
                user = RegistrationProfile.objects.get(activation_key=self.activation_key).user
            except RegistrationProfile.DoesNotExist:
                user = None
        else:
            user = self.request.user

        if not user: #give error
            return render_to_response('registration/activate.html', { } , context_instance=RequestContext(request))

        has_password = user.is_authenticated() and user.has_usable_password()

        if not has_password:
            if ('password1' not in self.cleaned_data or len(self.cleaned_data['password1']) <= 0)  or ('password2' not in self.cleaned_data or len(self.cleaned_data['password2']) <= 0 ):
                    raise forms.ValidationError(_("Non hai nessuna password impostata. Imposta una password per poterti autenticare."))

        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("Le password non corrispondono."))

        return self.cleaned_data

    def clean_username(self):
        if self.activating_user:
            user = self.activating_user

        if user.username == self.cleaned_data['username']:
            return self.cleaned_data['username']

        # if change username and has activation key, or if just change username:
        if self.request.user.username  != self.cleaned_data['username']:
            existing = User.objects.filter(username__iexact=self.cleaned_data['username'])
            if existing.exists():
                raise forms.ValidationError(_("Questo username e' stato gia' preso da un altro utente."))
        return self.cleaned_data['username']
    
    def do_save(self, user):
        if user:
            user = user
        else:
            user = self.request.user

        profile = user.get_profile()

        data = self.cleaned_data 
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.username = data['username']
        if data['password1'] and len(data['password1']) > 0:
            user.set_password(data['password1'])

        profile.born_date, profile.born_place = data['born_date'], data['born_place']
        profile.doc_type, profile.doc_id = data['doc_type'], data['doc_id']
        #TODO profile.photo = 

        profile.user = user
        profile.save()
        user.save()

