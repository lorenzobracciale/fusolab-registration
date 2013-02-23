from base.models import *
from ingresso.models import *
from bar.managers import *
from django import forms
from django.forms import ModelForm
from registration.forms import RegistrationForm
from django.utils.translation import ugettext_lazy as _
from base.models import UserProfile, DOCUMENT_TYPES
from registration.models import RegistrationProfile
from django.contrib.auth.models import User
from form_utils.widgets import ImageWidget
from django.forms.widgets import HiddenInput
import datetime


class EntranceBalanceModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(EntranceBalanceModelForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = EntranceBalance 
        exclude = ('parent','subtype', 'date')
        widgets = {
            'cashier': HiddenInput(),
        }
            
class EntranceOpeningModelForm(EntranceBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(EntranceOpeningModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=OPENING)  

class EntranceClosingModelForm(EntranceBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(EntranceClosingModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=CLOSING)  

class EntrancePaymentModelForm(EntranceBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(EntrancePaymentModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=PAYMENT)
        self.fields['subtype'] = forms.CharField(widget=forms.Select(choices=PAYMENT_SUBTYPES))
                
class EntranceDepositModelForm(EntranceBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(EntranceDepositModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=DEPOSIT)  
        self.fields['subtype'] = forms.CharField(widget=forms.Select(choices=DEPOSIT_SUBTYPES))

class EntranceWithdrawModelForm(EntranceBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(EntranceWithdrawModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=WITHDRAW) 

