from django.db import models
from django.contrib.auth.models import User

class GatePermission(models.Model):
    PERMISSION_TYPE = (
        ('a', 'Tutto'),        
        ('d', 'Porta d\' ingresso'),        
        ('c', 'Cancello automatico'),        
    )
    user = models.ForeignKey('base.UserProfile', verbose_name="Utente")
    from_date = models.DateField('Da')
    to_date = models.DateField('A')
    created_via = models.CharField('Tipo di permesso', choices=PERMISSION_TYPE, max_length=2, default='a')

    class Meta:
        ordering = ['-from_date']
        verbose_name = "Permesso Apertura"
        verbose_name_plural = "Permessi Apertura" 

    def __unicode__ (self):
        return "%s" % (str(self.user))

