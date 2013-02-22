# -*- coding: iso-8859-15 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from decimal import Decimal 
from datetime import datetime 
from bar.managers import * 
from base.models import UserProfile

DATE_FORMAT = "%d-%m-%Y" 
TIME_FORMAT = "%H:%M:%S"

#bar
class Product(models.Model):
    keycode = models.IntegerField("tasto rapido per cassiere") #rapid keycode for cash 
    name = models.CharField("nome", max_length=30)
    cost = models.DecimalField("prezzo", max_digits=5, decimal_places=2)
    #internal_cost = models.DecimalField("prezzo per interni", max_digits=5, decimal_places=2, blank=True)
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

class Receipt(models.Model):
	cashier = models.ForeignKey('base.UserProfile', verbose_name="Cassiere")
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
#	ABSTRACT BALANCE 
#

class Balance(models.Model):
    operation = models.CharField(max_length=2, choices=OPERATION_TYPES)	
    subtype = models.CharField(max_length=2, blank=True, null=True)
    parent = models.ForeignKey('self', blank=True, null=True, editable=False)
    amount = models.DecimalField("Somma", max_digits=10, decimal_places=2,  validators=[MinValueValidator(Decimal('0.00'))])
    date = models.DateTimeField("Data", default=datetime.now)
    cashier = models.ForeignKey('base.UserProfile', verbose_name="Cassiere")
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
		if self.operation == OPENING:
			return "%d - -  %s %.2f %s" % (self.id, self.get_operation_display(), self.amount, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
		else:
			return "%d - %d %s %.2f %s" % (self.id, self.parent.id, self.get_operation_display(), self.amount, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
		
	class Meta:
		verbose_name = "Voce di bilancio del Bar"
		verbose_name_plural = "Voci di bilancio del Bar"		

	#assegna l'id automaticamente durante il salvataggio per raggruppare gli eventi
	def save(self, *args, **kwargs):
		if self.operation != OPENING:
			self.parent = BarBalance.objects.get_parent(self.date)
		super(BarBalance, self).save(*args, **kwargs)

	
		
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
		if self.operation != CASHPOINT:
			self.parent = SmallBalance.objects.get_parent(self.date)
		super(SmallBalance, self).save(*args, **kwargs)

