from django.db import models
from django.contrib.auth.models import User

class GatePermission(models.Model):
    user = models.ForeignKey('base.UserProfile', verbose_name="Utente")
    from_date = models.DateField()
    to_date = models.DateField()

