from django import template
from django.contrib.auth.models import User
from baraled.models import *
import datetime

register = template.Library()

@register.assignment_tag
def last_ledstrings(num):
    """
        Ultime frasi lette scritte sulla barra 
    """
    sentences = LedString.objects.filter(user__isnull=False).order_by('-created_on')[:num]
    return sentences
