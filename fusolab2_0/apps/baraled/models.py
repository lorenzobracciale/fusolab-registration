from django.db import models
from django.db.models.signals import post_save
from base.models import *
import socket
from fusolab2_0 import settings


class LedString(models.Model):
    """
        Frasi scritte sulla Bara di Led 
    """
    user = models.ForeignKey('base.UserProfile', blank=True, null=True)
    created_on = models.DateTimeField(auto_now_add = True)
    sentence = models.CharField(max_length=800)
    coded_sentence = models.CharField(max_length=900) #con tag <ID00> bla bla

    def __unicode__(self):
        if self.user:
            return u"%s - %s - %s" % (self.user, self.created_on.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)), self.sentence )
        else:
            return u"Sconosciuto - %s - %s" % (self.created_on.strftime("%s %s" % (DATE_FORMAT, TIME_FORMAT)), self.sentence )


#Signals 

def send_ledbar_cmd(sender, instance, **kwargs):
    '''
    After being saved, each LedString sends an UPD message to the Arduino that controls the led bar
    '''
    BARALED_IP = settings.IP_OPENER
    BARALED_PORT = settings.PORT_OPENER
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(instance.coded_sentence, (BARALED_IP, BARALED_PORT))
    sock.close()


post_save.connect(send_ledbar_cmd, sender=LedString, dispatch_uid="send_ledbar_cmd")

