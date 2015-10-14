from django import template
from django.contrib.auth.models import User
from salutatore.models import *
import datetime

register = template.Library()


@register.assignment_tag
def last_salutati(num):
    """
        Ultimi utenti salutati dal salutatore
    """
    greetings = Greeting.objects.all().order_by('-date')[:num]
    #users = [g.user.user for g in greetings]
    #users = User.objects.filter(last_login__gt=sql_datetime,
    #                            is_active__exact=1).order_by('-last_login')[:num]
    return greetings 


@register.assignment_tag
def last_sentences(num):
    """
        Ultime frasi lette dal salutatore
    """
    sentences = ToBeSaid.objects.filter(user__isnull=False).order_by('-created_on')[:num]
    return sentences
