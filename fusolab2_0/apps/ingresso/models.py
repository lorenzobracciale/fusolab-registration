# -*- coding: iso-8859-15 -*-
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from decimal import Decimal 
from datetime import datetime 
from bar.models import SmallBalance, Balance    
from ingresso.managers import *
from base.models import *
from bar.managers import *
from django.conf import settings

DATE_FORMAT = "%d-%m-%Y" 
TIME_FORMAT = "%H:%M:%S"
MONEY_DELTA = 10.0

class Card(models.Model):
    sn = models.CharField("Seriale", unique=True, max_length=16)
    user = models.ForeignKey('base.UserProfile', verbose_name="Utente")
    created_on = models.DateField(auto_now_add=True)
    def __unicode__(self):
        return u'%s - %s %s' % (self.sn, self.user.user.first_name, self.user.user.last_name)
    class Meta:
        verbose_name = "Tessera"
        verbose_name_plural = "Tessere"

class Entrance(models.Model):
    date = models.DateTimeField(auto_now_add = True)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    def __unicode__(self):
        return u"%.1f EURO - %s" % (self.cost, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
    
    objects = EntranceManager()    
    
    class Meta:
        verbose_name = "Ingresso"
        verbose_name_plural = "Ingressi"



class EntranceBalance(Balance):
    def __unicode__(self):
        if self.operation == OPENING:
            return "%d - -  %s %.2f %s" % (self.id, self.get_operation_display(), self.amount, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
        else:
            return "%d - %d %s %.2f %s" % (self.id, self.parent.id, self.get_operation_display(), self.amount, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))    

    class Meta:
        verbose_name = "Voce di bilancio dell'entrata"
        verbose_name_plural = "Voci di bilancio dell'entrata"       

    #assegna l'id automaticamente durante il salvataggio per raggruppare gli eventi
    def save(self, *args, **kwargs):
        if self.operation != OPENING:
            self.parent = EntranceBalance.objects.get_parent_t(self.date)
        super(EntranceBalance, self).save(*args, **kwargs)

def get_entrance_summary(closing):
    notes = []
    d = {}
    d['date'] = closing.parent.date.strftime("%d/%m/%Y")
    d['opening_amount'] = closing.parent.amount
    if closing.parent.note:
        notes.append("apertura "+str(closing.parent.amount)+" "+closing.parent.note)
    d['last_closing_amount'] = EntranceBalance.objects.get_last_closing(closing.parent)

    d['closing_amount'] = closing.amount
    
    #calcolo del valore atteso della chiusura
    d['expected_balance'] = 0
    d['expected_balance']+=closing.parent.amount
    
    try:
        opening_transactions = EntranceBalance.objects.get_transactions_for(closing.parent)
    except(IndexError, EntranceBalance.DoesNotExist):
        pass
        #send_mail('allarme chiusura bar', 'errore tragico #1', 'cassafusolab@gmail.com',NOTIFICATION_ADDRESS_LIST, fail_silently=False)
    if Entrance.objects.total_between(closing.parent.date,closing.date):
        d['receipt_count'] = Entrance.objects.total_between(closing.parent.date,closing.date)
    else:
        d['receipt_count'] = 0
    d['expected_balance']+=d['receipt_count']
    
    d[DEPOSIT] = 0
    d[PAYMENT] = 0
    d[WITHDRAW] = 0
    d[CLOSING] = 0
    
    for transaction in opening_transactions:
        d[transaction.operation]+=transaction.amount
        if transaction.operation in [DEPOSIT]:
            d['expected_balance']+=transaction.amount
        elif transaction.operation in [PAYMENT,WITHDRAW]:
            d['expected_balance']-=transaction.amount
            
        if transaction.note:
                notes.append(transaction.get_operation_display()+" "+str(transaction.amount)+": "+transaction.note)

    d['notes'] = notes
    d['opening_check'] = d['opening_amount'] - d['last_closing_amount']
    d['closing_check'] = d['closing_amount'] - d['expected_balance']
    
    if (d['opening_check'] < - settings.MONEY_DELTA):
        d['opening_warning'] = True
        d['warning'] = True
    if (d['closing_check'] < - settings.MONEY_DELTA):
        d['closing_warning'] = True    
        d['warning'] = True  
            
    return d
    
import signals
