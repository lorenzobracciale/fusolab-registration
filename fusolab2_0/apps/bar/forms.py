from base.models import *
from bar.models import *
from bar.managers import *
from django import forms
from django.forms import ModelForm
from django.forms.widgets import HiddenInput
from registration.forms import RegistrationForm
from django.utils.translation import ugettext_lazy as _
from base.models import UserProfile, DOCUMENT_TYPES
from registration.models import RegistrationProfile
from django.contrib.auth.models import User
from form_utils.widgets import ImageWidget
import datetime


class BarBalanceModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BarBalanceModelForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = BarBalance  
        exclude = ('parent','subtype', 'date')
        widgets = {
            'cashier': HiddenInput(),
        }
        
            
class BarOpeningModelForm(BarBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(BarOpeningModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=OPENING)  

class BarClosingModelForm(BarBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(BarClosingModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=CLOSING)  

class BarPaymentModelForm(BarBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(BarPaymentModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=PAYMENT)
        self.fields['subtype'] = forms.CharField(widget=forms.Select(choices=PAYMENT_SUBTYPES))

        
class BarDepositModelForm(BarBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(BarDepositModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=DEPOSIT)  
        self.fields['subtype'] = forms.CharField(widget=forms.Select(choices=DEPOSIT_SUBTYPES))
        
class BarWithdrawModelForm(BarBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(BarWithdrawModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=WITHDRAW) 

#
#   SMALL FORMS
#


class SmallBalanceModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(SmallBalanceModelForm, self).__init__(*args, **kwargs)
        
    class Meta:
        model = SmallBalance    
        exclude = ('parent','subtype', 'date')
        widgets = {
            'cashier': HiddenInput(),
        }
        
            
class SmallCashpointModelForm(SmallBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(SmallCashpointModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=CASHPOINT)    

class SmallPaymentModelForm(SmallBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(SmallPaymentModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=PAYMENT)
        self.fields['subtype'] = forms.CharField(widget=forms.Select(choices=PAYMENT_SUBTYPES))
                
class SmallDepositModelForm(SmallBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(SmallDepositModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=DEPOSIT)  
        self.fields['subtype'] = forms.CharField(widget=forms.Select(choices=DEPOSIT_SUBTYPES))
        
class SmallWithdrawModelForm(SmallBalanceModelForm):
    def __init__(self, *args, **kwargs):
        super(SmallWithdrawModelForm, self).__init__(*args, **kwargs)
        self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=WITHDRAW) 
