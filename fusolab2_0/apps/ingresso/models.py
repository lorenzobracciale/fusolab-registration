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

DATE_FORMAT = "%d-%m-%Y" 
TIME_FORMAT = "%H:%M:%S"

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
			self.parent = EntranceBalance.objects.get_parent(self.date)
		super(EntranceBalance, self).save(*args, **kwargs)


