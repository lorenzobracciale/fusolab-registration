from django import forms
from django.forms import ModelForm
from datetime import datetime
from register.models import *

	#
	#	BAR FORMS
	#


class BarBalanceModelForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(BarBalanceModelForm, self).__init__(*args, **kwargs)
		
	class Meta:
		model = BarBalance	
		exclude = ('parent')
		
			
class BarOpeningModelForm(BarBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(BarOpeningModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.OPENING)	

class BarClosingModelForm(BarBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(BarClosingModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.CLOSING)	

class BarPaymentModelForm(BarBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(BarPaymentModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.PAYMENT)
		
class BarDepositModelForm(BarBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(BarDepositModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.DEPOSIT)	

class BarWithdrawModelForm(BarBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(BarWithdrawModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.WITHDRAW)	

	#
	#	ENTRANCE FORMS
	#


class EntranceBalanceModelForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(EntranceBalanceModelForm, self).__init__(*args, **kwargs)
		
	class Meta:
		model = EntranceBalance	
		exclude = ('parent')
		
			
class EntranceOpeningModelForm(EntranceBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(EntranceOpeningModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.OPENING)	

class EntranceClosingModelForm(EntranceBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(EntranceClosingModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.CLOSING)	

class EntrancePaymentModelForm(EntranceBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(EntrancePaymentModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.PAYMENT)
		
class EntranceDepositModelForm(EntranceBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(EntranceDepositModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.DEPOSIT)	

class EntranceWithdrawModelForm(EntranceBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(EntranceWithdrawModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.WITHDRAW)	

	#
	#	SMALL FORMS
	#


class SmallBalanceModelForm(ModelForm):
	def __init__(self, *args, **kwargs):
		super(SmallBalanceModelForm, self).__init__(*args, **kwargs)
		
	class Meta:
		model = SmallBalance	
		exclude = ('parent')
		
			
class SmallCashpointModelForm(SmallBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(SmallCashpointModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.CASHPOINT)	

class SmallPaymentModelForm(SmallBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(SmallPaymentModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.PAYMENT)
		
class SmallDepositModelForm(SmallBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(SmallDepositModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.DEPOSIT)	

class SmallWithdrawModelForm(SmallBalanceModelForm):
	def __init__(self, *args, **kwargs):
		super(SmallWithdrawModelForm, self).__init__(*args, **kwargs)
		self.fields['operation'] = forms.CharField(widget=forms.HiddenInput(),initial=Balance.WITHDRAW)	
