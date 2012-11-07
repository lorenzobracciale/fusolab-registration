# -*- coding: iso-8859-15 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

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
    sn = models.CharField(unique=True, max_length=16 )
    user = models.ForeignKey('UserProfile')
    created_on = models.DateField(auto_now_add=True)
    def __unicode__(self):
        return u'%s - %s %s' % (self.sn, self.user.user.first_name, self.user.user.last_name)

#bar
class Product(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=30)
    cost = models.DecimalField(max_digits=5, decimal_places=2)
    def __unicode__(self):
        return u'%s' % (self.name)

class PurchasedProduct(models.Model):
    purchased_at = models.DateTimeField(auto_now_add = True)
    name = models.CharField(max_length=30)
    cost = models.DecimalField(max_digits=5, decimal_places=2)
    cashier = models.ForeignKey('UserProfile') 
    def __unicode__(self):
        return self.purchased_at.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT))

class BarCashBalance(models.Model):
    date = models.DateTimeField(auto_now_add = True)
    initial_cash = models.DecimalField(max_digits=6, decimal_places=2)
    final_cash = models.DecimalField(max_digits=6, decimal_places=2)
    withdraw = models.DecimalField(max_digits=6, decimal_places=2)
    deposit = models.DecimalField(max_digits=6, decimal_places=2)
    def __unicode__(self):
        return self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT))
###

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
