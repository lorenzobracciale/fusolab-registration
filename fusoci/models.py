# -*- coding: iso-8859-15 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

DOCUMENT_TYPES = ( ('ci', 'Carta d\'identita\''), ('pp', 'Passaporto'), ('pa', 'Patente')   )

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    accepted_eula = models.BooleanField()

    doc_type = models.CharField(max_length=2, choices=DOCUMENT_TYPES, blank=True)
    doc_id = models.CharField(max_length=20, blank=True)
    born_date = models.DateField()
    born_place = models.CharField(max_length=50)

#    photo = models.ImageField(upload_to='/photo/')
    
    date_inserted = models.DateField(auto_now_add=True)

