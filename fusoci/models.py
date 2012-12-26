# -*- coding: iso-8859-15 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.safestring import mark_safe
from datetime import datetime 

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

class Receipt(models.Model):
    cashier = models.ForeignKey('UserProfile', verbose_name="Cassiere") 
    date = models.DateTimeField(auto_now_add = True)
    total = models.DecimalField("totale", max_digits=10, decimal_places=2)
    def __unicode__(self):
        return "#%d - %.2f EUR %s" % (self.id, self.total, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
    class Meta:
    	ordering = ["date"]
        verbose_name = "Scontrino"
        verbose_name_plural = "Scontrini"

class BarCashBalance(models.Model):
    date = models.DateTimeField("Data")
    cashier = models.ForeignKey('UserProfile', verbose_name="Cassiere") 
    initial_cash = models.DecimalField("Contanti iniziali", default=0, max_digits=6, decimal_places=2)
    final_cash = models.DecimalField("Contanti finali", default=0, max_digits=6, decimal_places=2)
    withdraw = models.DecimalField("Prelevati", default=0, max_digits=6, decimal_places=2)
    deposit = models.DecimalField("Depositati", default=0, max_digits=6, decimal_places=2)
    note = models.TextField(blank=True)
    def __unicode__(self):
        return self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT))
    class Meta:
    	ordering = ["date"]
        verbose_name = "Bilancio Entrate da Bar"
        verbose_name_plural = "Bilanci Entrate da Bar"

class EntranceCashBalance(models.Model):
    date = models.DateTimeField("Data")
    cashier = models.ForeignKey('UserProfile', verbose_name="Cassiere") 
    initial_cash = models.DecimalField("Contanti iniziali", default=0, max_digits=6, decimal_places=2)
    final_cash = models.DecimalField("Contanti finali", default=0, max_digits=6, decimal_places=2)
    withdraw = models.DecimalField("Prelevati", default=0, max_digits=6, decimal_places=2)
    deposit = models.DecimalField("Depositati", default=0, max_digits=6, decimal_places=2)
    note = models.TextField(blank=True)
    def __unicode__(self):
        return self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT))
    class Meta:
    	ordering = ["date"]
        verbose_name = "Bilancio Entrate da Ingresso"
        verbose_name_plural = "Bilanci Entrate da Ingresso"


class Entrance(models.Model):
    date = models.DateTimeField(auto_now_add = True)
    cost = models.DecimalField(max_digits=6, decimal_places=2)
    def __unicode__(self):
        return u"%.1f EURO - %s" % (self.cost, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
    class Meta:
    	ordering = ["date"]
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
