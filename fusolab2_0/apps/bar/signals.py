# -*- coding: iso-8859-15 -*-
from django.db.models.signals import post_save
from django.template import Context, Template
from django.template.loader import get_template
from django.dispatch import receiver
from django.core.mail import EmailMessage
from bar.models import *
from django.conf import settings

#"value 1 is %s, value 2 is %s." % (value1, value2)

DATE_FORMAT = "%d-%m-%Y"
TIME_FORMAT = "%H:%M:%S"


@receiver(post_save, sender=BarBalance)
def bar_handler(sender, **kwargs):
    saved_balance = kwargs['instance']

    if saved_balance.operation == CLOSING:
        subject  =  ''
        template = get_template('closing_mail.html')
       
        print "saved_balance parent:" , saved_balance.parent
        d = get_bar_summary(saved_balance)
        context = Context(d)
        content = template.render(context)
        
        if ('warning' in d):
            subject += 'WARNING '
        subject += 'riepilogo bar '+saved_balance.parent.date.strftime("%d/%m/%Y")
        
        msg = EmailMessage(subject, content, 'cassafusolab@gmail.com', to=settings.EMAIL_NOTIFICATION_LIST)
        msg.content_subtype = "html"
        msg.send()

@receiver(post_save, sender=SmallBalance)
def bar_handler(sender, **kwargs):
    saved_balance = kwargs['instance']

    if saved_balance.operation == CASHPOINT:
        subject  =  ''
        template = get_template('base/smallbalance_mail.html')
       
        print "saved_balance parent:" , saved_balance.parent
        d = get_small_summary(saved_balance)
        context = Context(d)
        content = template.render(context)
        
        if ('warning' in d):
            subject += 'WARNING '
        subject += 'riepilogo interregno '+saved_balance.date.strftime("%d/%m/%Y")
        
        msg = EmailMessage(subject, content, 'cassafusolab@gmail.com', to=settings.EMAIL_NOTIFICATION_LIST)
        msg.content_subtype = "html"
        msg.send()
