# -*- coding: iso-8859-15 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from datetime import datetime 
from django.db.models import Sum, Q, F
import math

DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%H:%M:%S"
MONEY_DELTA = 0.0
NOTIFICATION_ADDRESS_LIST = ['dario.luzzi@gmail.com','arnardospippoli@gmail.com']


DOCUMENT_TYPES = ( ('ci', 'Carta d\'identita\''), ('pp', 'Passaporto'), ('pa', 'Patente')   )
DATE_FORMAT = "%d-%m-%Y" 
TIME_FORMAT = "%H:%M:%S"

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    doc_type = models.CharField(max_length=2, choices=DOCUMENT_TYPES, blank=True)
    doc_id = models.CharField(max_length=20, blank=True)
    born_date = models.DateField(blank=True, null=True)
    born_place = models.CharField(max_length=50, blank=True)

    photo = models.ImageField(upload_to='photo/', blank=True) #TODO fare check nel form per size ed eventualmente resizing
    how_hear = models.CharField(max_length=500, blank=True)

    def __unicode__(self):
        return u'%s %s' % (self.user.first_name, self.user.last_name)
	class Meta:
		verbose_name = "Utente"
		verbose_name_plural = "Utenti"		
    

class Card(models.Model):
    sn = models.CharField("Seriale", unique=True, max_length=16)
    user = models.ForeignKey('UserProfile', verbose_name="Utente")
    created_on = models.DateField(auto_now_add=True)
    def __unicode__(self):
        return u'%s - %s %s' % (self.sn, self.user.user.first_name, self.user.user.last_name)
    class Meta:
        verbose_name = "Tessera"
        verbose_name_plural = "Tessere"

#bar
class Product(models.Model):
    keycode = models.IntegerField("tasto rapido per cassiere") #rapid keycode for cash 
    name = models.CharField("nome", max_length=30)
    cost = models.DecimalField("prezzo", max_digits=5, decimal_places=2)
    internal_cost = models.DecimalField("prezzo per interni", max_digits=5, decimal_places=2, blank=True)
    def __unicode__(self):
        return u'%d %s %s%s' % (self.keycode, self.name, self.cost, 'e' )
    class Meta:
        verbose_name = "Prodotto"
        verbose_name_plural = "Prodotti"

class PurchasedProduct(models.Model):
    name = models.CharField("nome", max_length=30)
    cost = models.DecimalField("prezzo", max_digits=5, decimal_places=2)
    receipt = models.ForeignKey('Receipt')
    def __unicode__(self):
        return self.name + " " + self.receipt.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT))
    class Meta:
        verbose_name = "Consumazione"
        verbose_name_plural = "Consumazioni"

#class Receipt(models.Model):
#    cashier = models.ForeignKey('UserProfile', verbose_name="Cassiere") 
#    date = models.DateTimeField(auto_now_add = True)
#    total = models.DecimalField("totale", max_digits=10, decimal_places=2)
#    def __unicode__(self):
#        return "#%d - %.2f EUR %s" % (self.id, self.total, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
#    class Meta:
#        verbose_name = "Scontrino"
#        verbose_name_plural = "Scontrini"
#
#class BarCashBalance(models.Model):
#    date = models.DateTimeField("Data")
#    cashier = models.ForeignKey('UserProfile', verbose_name="Cassiere") 
#    initial_cash = models.DecimalField("Contanti iniziali", default=0, max_digits=6, decimal_places=2)
#    final_cash = models.DecimalField("Contanti finali", default=0, max_digits=6, decimal_places=2)
#    withdraw = models.DecimalField("Prelevati", default=0, max_digits=6, decimal_places=2)
#    deposit = models.DecimalField("Depositati", default=0, max_digits=6, decimal_places=2)
#    note = models.TextField(blank=True)
#    def __unicode__(self):
#        return self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT))
#    class Meta:
#        verbose_name = "Bilancio Entrate da Bar"
#        verbose_name_plural = "Bilanci Entrate da Bar"
#
#class EntranceCashBalance(models.Model):
#    date = models.DateTimeField("Data")
#    cashier = models.ForeignKey('UserProfile', verbose_name="Cassiere") 
#    initial_cash = models.DecimalField("Contanti iniziali", default=0, max_digits=6, decimal_places=2)
#    final_cash = models.DecimalField("Contanti finali", default=0, max_digits=6, decimal_places=2)
#    withdraw = models.DecimalField("Prelevati", default=0, max_digits=6, decimal_places=2)
#    deposit = models.DecimalField("Depositati", default=0, max_digits=6, decimal_places=2)
#    note = models.TextField(blank=True)
#    def __unicode__(self):
#        return self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT))
#    class Meta:
#        verbose_name = "Bilancio Entrate da Ingresso"
#        verbose_name_plural = "Bilanci Entrate da Ingresso"


class Entrance(models.Model):
    date = models.DateTimeField(auto_now_add = True)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    def __unicode__(self):
        return u"%.1f EURO - %s" % (self.cost, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
    class Meta:
        verbose_name = "Ingresso"
        verbose_name_plural = "Ingressi"

class Greeting(models.Model):
    user = models.ForeignKey('UserProfile')
    date = models.DateTimeField(auto_now_add = True)
    def __unicode__(self):
        return u"%s - %s" % (self.user, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
###

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)



### dario
class ReceiptManager(models.Manager):
	def total_between(self, opening_date, closing_date):
		return super(ReceiptManager, self).get_query_set().filter(date__range=[opening_date,closing_date]).aggregate(Sum('total'))['total__sum']
	def receipts_between(self, opening_date, closing_date):
		return super(ReceiptManager, self).get_query_set().filter(date__range=[opening_date,closing_date])

class Receipt(models.Model):
	cashier = models.ForeignKey('UserProfile', verbose_name="Cassiere")
	date = models.DateTimeField(auto_now_add = True)
	total = models.DecimalField("totale", max_digits=10, decimal_places=2)
	
	objects = ReceiptManager()
	
	def __unicode__(self):
		return "#%d - %.2f EUR %s" % (self.id, self.total, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
	
	class Meta:
		ordering = ['-date']
		verbose_name = "Scontrino"
		verbose_name_plural = "Scontrini"

#
#	ABSTRACT BALANCE MANAGER
#
	
class BalanceManager(models.Manager):

	def is_open(self,time=datetime.now):
		return super(BalanceManager, self).get_query_set().filter(Q(date__lt=time) & Q(operation__in=[Balance.OPENING,Balance.CLOSING])).latest('date').operation == Balance.OPENING

	def get_parent(self, time):
		return super(BalanceManager, self).get_query_set().filter(Q(operation=Balance.OPENING) & Q(date__lt=time)).latest('date')
	
	def get_closing_amount_before(self,current_opening):
		return super(BalanceManager, self).get_query_set().get(id=current_opening.id).get_previous_by_date(operation=Balance.CLOSING).amount

	def get_transactions_for(self, current_opening):
		return super(BalanceManager, self).get_query_set().filter(parent=current_opening)
	
	def get_opening_times(self,start_date,end_date):
		list = super(BalanceManager, self).get_query_set().filter(Q(date__range=[start_date,end_date]) & Q(parent__isnull=True)).select_related()
		ret = []
		for l in list:
			ret.append([l.date,BarBalance.objects.filter(Q(parent=l.id) & Q(operation=BarBalance.CLOSING)).get().date])
		return ret	

	def get_checkpoint_before(self,saved_balance):
		return super(BalanceManager, self).get_query_set().get(id=saved_balance.id).get_previous_by_date(operation=Balance.CASHPOINT)

#
#	ABSTRACT BALANCE 
#

class Balance(models.Model):
	OPENING = 'op'
	CLOSING = 'cl'
	PAYMENT = 'pa'
	DEPOSIT = 'de'
	WITHDRAW = 'wi'	
	CASHPOINT = 'pt'
	OPERATION_TYPES = ( 
		(OPENING, 'apertura'),
		(CLOSING, 'chiusura'),
		(PAYMENT, 'pagamento'),
		(DEPOSIT, 'deposito'),
		(WITHDRAW, 'prelievo tesoriere'),
		(CASHPOINT, 'punto di cassa')
	)
	operation = models.CharField(max_length=2, choices=OPERATION_TYPES)	
	parent = models.ForeignKey('self', blank=True, null=True, editable=False)
	amount = models.DecimalField("Somma", max_digits=10, decimal_places=2)
	date = models.DateTimeField("Data", default=datetime.now)
	cashier = models.ForeignKey('UserProfile', verbose_name="Cassiere")
	note = models.TextField(blank=True)
	
	objects = BalanceManager()		

	class Meta:
		ordering = ['-date']
		abstract = True	


#
#	BAR BALANCE
#

class BarBalance(Balance):

	def __unicode__(self):
		if self.operation == self.OPENING:
			return "%d - -  %s %.2f %s" % (self.id, self.get_operation_display(), self.amount, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
		else:
			return "%d - %d %s %.2f %s" % (self.id, self.parent.id, self.get_operation_display(), self.amount, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
		
	class Meta:
		verbose_name = "Voce di bilancio del Bar"
		verbose_name_plural = "Voci di bilancio del Bar"		

	#assegna l'id automaticamente durante il salvataggio per raggruppare gli eventi
	def save(self, *args, **kwargs):
		if self.operation != self.OPENING:
			self.parent = BarBalance.objects.get_parent(self.date)
		super(BarBalance, self).save(*args, **kwargs)

	
#
#	ENTRANCE BALANCE
#

class EntranceBalance(Balance):

	def __unicode__(self):
		if self.operation == self.OPENING:
			return "%d - -  %s %.2f %s" % (self.id, self.get_operation_display(), self.amount, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
		else:
			return "%d - %d %s %.2f %s" % (self.id, self.parent.id, self.get_operation_display(), self.amount, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))	

	class Meta:
		verbose_name = "Voce di bilancio dell'entrata"
		verbose_name_plural = "Voci di bilancio dell'entrata"		

	#assegna l'id automaticamente durante il salvataggio per raggruppare gli eventi
	def save(self, *args, **kwargs):
		if self.operation != self.OPENING:
			self.parent = EntranceBalance.objects.get_parent(self.date)
		super(EntranceBalance, self).save(*args, **kwargs)

		
#
#	SMALL BALANCE
#

class SmallBalance(Balance):

	def __unicode__(self):
		return "%d - %s %.2f %s" % (self.id, self.get_operation_display(), self.amount, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
		
	class Meta:
		ordering = ['-date']
		verbose_name = "Voce di bilancio dell'Interregno"
		verbose_name_plural = "Voci di bilancio dell'Interregno"		

	#assegna l'id automaticamente durante il salvataggio per raggruppare gli eventi
	def save(self, *args, **kwargs):
		if self.operation != self.CASHPOINT:
			self.parent = SmallBalance.objects.get_parent(self.date)
		super(SmallBalance, self).save(*args, **kwargs)


#import signals
