from django.db import models
from base.models import *

class Greeting(models.Model):
    """
        Saluti manuali, quelli che passono la tessera
    """
    user = models.ForeignKey('base.UserProfile')
    date = models.DateTimeField(auto_now_add = True)
    def __unicode__(self):
        return u"%s - %s" % (self.user, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))


class ToBeSaid(models.Model):
    """
        Frasi che il salutatore, via polling, legge
    """
    user = models.ForeignKey('base.UserProfile', blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add = True)
    polled = models.BooleanField(default=False)
    sentence = models.CharField(max_length=500)

    def __unicode__(self):
        if self.user:
            return u"%s - %s - %s" % (self.user, self.created_on.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)), self.sentence )
        else:
            return u"Sconosciuto - %s - %s" % (self.created_on.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)), self.sentence )

