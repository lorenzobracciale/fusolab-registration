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
from django.conf import settings
import simplejson


DATE_FORMAT = "%d-%m-%Y" 
TIME_FORMAT = "%H:%M:%S"
PRICE_CHANGE_TYPES = (
    ('r', 'rise'),        
    ('f', 'fall'), 
    ('s', 'stable'),           
)

#bar
class Product(models.Model):
    keycode = models.IntegerField("tasto rapido per cassiere") #rapid keycode for cash 
    name = models.CharField("nome", max_length=30)
    cost = models.DecimalField("prezzo attuale", max_digits=5, decimal_places=2)
    default_price = models.DecimalField("prezzo standard", max_digits=5, decimal_places=2) 
    symbol = models.CharField("sigla stile NASDAQ", max_length=30) #ad es. INRR BRR etcc
    trend = models.CharField('trend', max_length=2, choices=PRICE_CHANGE_TYPES)	
    updated = models.BooleanField('aggiornato', default=False)
    min_price = models.DecimalField("prezzo minimo", max_digits=5, decimal_places=2)
    max_price = models.DecimalField("prezzo massimo", max_digits=5, decimal_places=2)
    can_change = models.BooleanField(default=True)
    #internal_cost = models.DecimalField("prezzo per interni", max_digits=5, decimal_places=2, blank=True)
    def __unicode__(self):
        return u'%d %s %s euro (%s - %s)' % (self.keycode, self.name, self.default_price, self.min_price, self.max_price )
    class Meta:
        verbose_name = "Prodotto"
        verbose_name_plural = "Prodotti"

class PriceListDisplay(models.Model):
    """ Singleton for the message in the display """ 
    messages  = models.TextField('messaggi separati da ;', max_length=3000)
    entrance_number = models.IntegerField('Numero ingressi', default=0)
    entrance_symbol = models.CharField("sigla stile NASDAQ", max_length=30, default="INRR")
    entrance_trend = models.CharField('trend', max_length=2, choices=PRICE_CHANGE_TYPES)
    variation_active = models.BooleanField('aggiornato', default=False)
    def __unicode__(self):
        return self.messages
    class Meta:
        verbose_name = "Display prezzi"
        verbose_name_plural = "Display prezzi"
    def save(self):
        self.id=1
        super(PriceListDisplay, self).save()
    def delete(self):
        pass

class PurchasedProduct(models.Model):
    name = models.CharField("nome", max_length=30)
    cost = models.DecimalField("prezzo", max_digits=5, decimal_places=2)
    receipt = models.ForeignKey('Receipt')
    
    objects = PurchasedProductManager()
    
    def __unicode__(self):
        return self.name + " " + self.receipt.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT))
    class Meta:
        verbose_name = "Consumazione"
        verbose_name_plural = "Consumazioni"

class Receipt(models.Model):
	cashier = models.ForeignKey('base.UserProfile', verbose_name="Cassiere")
	date = models.DateTimeField(default=datetime.now)#auto_now_add = True)
	total = models.DecimalField("totale", max_digits=10, decimal_places=2)

	objects = ReceiptManager()

	def __unicode__(self):
		return "#%d - %.2f EUR %s" % (self.id, self.total, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))

	class Meta:
		ordering = ['date']
		verbose_name = "Scontrino"
		verbose_name_plural = "Scontrini"

#
#	ABSTRACT BALANCE 
#

class Balance(models.Model):
    operation = models.CharField(max_length=2, choices=OPERATION_TYPES)	
    subtype = models.CharField(max_length=2, blank=True, null=True, choices=PAYMENT_SUBTYPES + DEPOSIT_SUBTYPES)
    parent = models.ForeignKey('self', blank=True, null=True, editable=False)
    amount = models.DecimalField("Somma", max_digits=10, decimal_places=2,  validators=[MinValueValidator(Decimal('0.00'))])
    date = models.DateTimeField("Data", default=datetime.now)
    cashier = models.ForeignKey('base.UserProfile', verbose_name="Cassiere")
    note = models.TextField(blank=True)
    objects = BalanceManager()		

    class Meta:
        abstract = True	


#
#	BAR BALANCE
#

class BarBalance(Balance):
    promoter = models.CharField("Organizzatore (se esterno)",  max_length=30, blank=True, null=True)
    name = models.CharField("Nome della serata",  max_length=100, blank=True, null=True)
    def __unicode__(self):
        if self.operation == OPENING:
            return "%d - -  %s %.2f %s" % (self.id, self.get_operation_display(), self.amount, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
        else:
            return "%d - %d %s %.2f %s" % (self.id, self.parent.id, self.get_operation_display(), self.amount, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
    
    class Meta:
        ordering = ['date']
        verbose_name = "Voce di bilancio del Bar"
        verbose_name_plural = "Voci di bilancio del Bar"		

	#assegna l'id automaticamente durante il salvataggio per raggruppare gli eventi
    def save(self, *args, **kwargs):
        if self.operation != OPENING:
            self.parent = BarBalance.objects.get_parent_t(self.date)
        super(BarBalance, self).save(*args, **kwargs)

	
		
#
#	SMALL BALANCE
#

class SmallBalance(Balance):

	def __unicode__(self):
		return "%d - %s %.2f %s" % (self.id, self.get_operation_display(), self.amount, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
		
	class Meta:
		ordering = ['date']
		verbose_name = "Voce di bilancio dell'Interregno"
		verbose_name_plural = "Voci di bilancio dell'Interregno"		

	#assegna l'id automaticamente durante il salvataggio per raggruppare gli eventi
	def save(self, *args, **kwargs):
		if self.operation != CASHPOINT:
			self.parent = SmallBalance.objects.get_parent_t(self.date)
		super(SmallBalance, self).save(*args, **kwargs)

def get_bar_summary(closing):
    notes = []
    d = {}
    
    notes.append("apertura "+ str(closing.parent.amount))
    if closing.parent.promoter:
        notes.append(" "+closing.parent.promoter) 
    if closing.parent.name:
        notes.append(" "+closing.parent.name)         
    if closing.parent.note:
        notes.append(closing.parent.note.replace("\r\n"," "+"\n"))
    else:
        notes.append("\n")

    d['date'] = closing.parent.date.strftime("%d/%m/%Y")
    d['cashier'] = closing.cashier
    d['opening_amount'] = closing.parent.amount
    d['last_closing_amount'] = BarBalance.objects.get_last_closing(closing.parent)
    d['closing_amount'] = closing.amount
    
    #calcolo del valore atteso della chiusura
    d['expected_balance'] = 0
    d['expected_balance']+=d['opening_amount']

    if Receipt.objects.total_between(closing.parent.date,closing.date):
        d['receipt_amount'] = Receipt.objects.total_between(closing.parent.date,closing.date)
    else:
        d['receipt_amount'] = 0
    d['expected_balance']+=d['receipt_amount']

    try:
        opening_transactions = BarBalance.objects.get_transactions_for(closing.parent)
    except(IndexError, BarBalance.DoesNotExist):
        pass
        #send_mail('allarme chiusura bar', 'errore tragico #1', 'cassafusolab@gmail.com',NOTIFICATION_ADDRESS_LIST, fail_silently=False)

    
    d[DEPOSIT] = 0
    d[PAYMENT] = 0
    d[WITHDRAW] = 0
    d[CLOSING] = 0
    d[OPENING] = 0 #lorenzo - altrimenti errore 2 nel for
    
    for transaction in opening_transactions:
        d[transaction.operation]+=transaction.amount
        notes.append(transaction.get_operation_display() + " " + str(transaction.amount))
        if transaction.operation in [DEPOSIT]:
            d['expected_balance']+=transaction.amount
            if transaction.subtype:
                notes.append(" "+get_deposit_display(transaction.subtype))
            if transaction.note:
                notes.append(" "+transaction.note.replace("\r\n"," ")+"\n")
            else:
                notes.append("\n")
        elif transaction.operation in [PAYMENT]:
            d['expected_balance']-=transaction.amount
            if transaction.subtype:
                notes.append(" "+get_payment_display(transaction.subtype))
            if transaction.note:
                notes.append(" "+transaction.note.replace("\r\n"," ")+"\n")
            else:
                notes.append("\n")
        elif transaction.operation in [WITHDRAW]:
            d['expected_balance']-=transaction.amount
            if transaction.note:
                notes.append(" "+transaction.note.replace("\r\n"," ")+"\n")
            else:
                notes.append("\n")
        else:         
            if transaction.note:
                notes.append(" "+transaction.note.replace("\r\n"," ")+"\n")
           

    d['notes'] = notes
    d['opening_check'] = d['opening_amount'] - d['last_closing_amount']
    d['closing_check'] = d['closing_amount'] - d['expected_balance']
    
    if (abs(d['opening_check']) > settings.MONEY_DELTA):
        d['opening_warning'] = True
        d['warning'] = True
    if (abs(d['closing_check']) > settings.MONEY_DELTA):
        d['closing_warning'] = True    
        d['warning'] = True    
 
    
    return d
 
def get_small_summary(checkpoint):
    notes = []
    d = {}
    d['date'] = checkpoint.date.strftime("%d/%m/%Y")
    d['checkpoint'] = checkpoint.amount
    d['cashier'] = checkpoint.cashier
    l = SmallBalance.objects.get_checkpoint_before(checkpoint)  
    if l:       
        d['last_checkpoint'] = SmallBalance.objects.get_checkpoint_before(checkpoint).amount
        start_date = SmallBalance.objects.get_checkpoint_before(checkpoint).date
        try:
            checkpoint_transactions = SmallBalance.objects.get_transactions_for(l)
        except(IndexError, SmallBalance.DoesNotExist):
            checkpoint_transactions = None   
    else:
        d['last_checkpoint'] = 0
        start_date = datetime(2012,11,01,00,00,00)
        checkpoint_transactions = None

    d['expected_checkpoint'] = d['last_checkpoint']
    receipts = Receipt.objects.filter(date__range=[start_date,checkpoint.date]).order_by('date')
    for o in BarBalance.objects.get_opening_times(start_date,checkpoint.date):
        receipts = receipts.exclude(date__range=[o[0],o[1]])
        
    if receipts:
        d['receipt_amount'] = receipts.aggregate(Sum('total'))['total__sum']
    else:
        d['receipt_amount'] = 0      
    
    d['expected_checkpoint'] += d['receipt_amount']
       
    d[DEPOSIT] = 0
    d[PAYMENT] = 0
    d[WITHDRAW] = 0
    if checkpoint_transactions:
        for transaction in checkpoint_transactions:
            d[transaction.operation]+=transaction.amount
            notes.append(transaction.get_operation_display() + " " + str(transaction.amount))
            if transaction.operation in [DEPOSIT]:
                d['expected_checkpoint']+=transaction.amount
                if transaction.subtype:
                    notes.append(" "+get_deposit_display(transaction.subtype))
                if transaction.note:
                    notes.append(" "+transaction.note.replace("\r\n"," ")+"\n")
                else:
                    notes.append("\n")
            elif transaction.operation in [PAYMENT]:
                d['expected_checkpoint']-=transaction.amount
                if transaction.subtype:
                    notes.append(" "+get_payment_display(transaction.subtype))
                if transaction.note:
                    notes.append(" "+transaction.note.replace("\r\n"," ")+"\n")
                else:
                    notes.append("\n")
            elif transaction.operation in [WITHDRAW]:
                d['expected_checkpoint']-=transaction.amount
                if transaction.note:
                    notes.append(" "+transaction.note.replace("\r\n"," ")+"\n")
                else:
                    notes.append("\n")
            else:         
                if transaction.note:
                    notes.append(" "+transaction.note.replace("\r\n"," ")+"\n")

    d['notes'] = notes
    d['check'] = d['checkpoint'] - d['expected_checkpoint']
    if (d['check'] < - settings.MONEY_DELTA):
        d['warning'] = True
    return d    

   
import signals
