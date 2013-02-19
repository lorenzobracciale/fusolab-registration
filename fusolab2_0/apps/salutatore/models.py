from django.db import models
from base.models import *

class Greeting(models.Model):
    user = models.ForeignKey('base.UserProfile')
    date = models.DateTimeField(auto_now_add = True)
    def __unicode__(self):
        return u"%s - %s" % (self.user, self.date.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)))
