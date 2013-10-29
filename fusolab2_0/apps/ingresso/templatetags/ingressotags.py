from django import template
from django.contrib.auth.models import User
from ingresso.models import *
from bar.models import *
from bar.managers import OPENING
import datetime

register = template.Library()

alcoholic_list = [
            {'name': 'Birra chiara', 'alcol_per_liter': 0.048, 'lt': 0.3},
            {'name': 'Birra DM', 'alcol_per_liter': 0.065, 'lt': 0.3},
            {'name': 'Shot', 'alcol_per_liter': 0.4, 'lt': 0.1},
            {'name': 'Amari', 'alcol_per_liter': 0.35, 'lt': 0.1},
            {'name': 'Birra in Bottiglia', 'alcol_per_liter': 0.068, 'lt': 0.3},
            {'name': 'Cocktail', 'alcol_per_liter': 0.20, 'lt': 0.3},
            ]


@register.assignment_tag
def entrances():
    """
       Gente entrata in questa serata 
    """
    if EntranceBalance.objects.is_open():
        open_date_en = EntranceBalance.objects.filter(operation=OPENING).order_by('-date')[0].date
        open_date_bar = BarBalance.objects.filter(operation=OPENING).order_by('-date')[0].date
        open_date = open_date_en if open_date_en < open_date_bar else open_date_bar
        return Entrance.objects.count_between(open_date, datetime.datetime.now())
    else:
        return 0

@register.assignment_tag
def alcohol_l():
    """
        Litri di alcol ingurgitati 
    """
    if BarBalance.objects.is_open():
        open_date_en = EntranceBalance.objects.filter(operation=OPENING).order_by('-date')[0].date
        open_date_bar = BarBalance.objects.filter(operation=OPENING).order_by('-date')[0].date
        open_date = open_date_en if open_date_en < open_date_bar else open_date_bar
        alcohol_lt = 0.0
        for alcholic in alcoholic_list:
            alcohol_lt += PurchasedProduct.objects.filter(receipt__date__gte=open_date, name__icontains=alcholic['name'] ).count() * alcholic['alcol_per_liter'] * alcholic['lt']
        return alcohol_lt
    else:
        return 0

@register.assignment_tag
def alcoholic_l():
    """
        Litri di alcol ingurgitati 
    """
    if BarBalance.objects.is_open():
        open_date_en = EntranceBalance.objects.filter(operation=OPENING).order_by('-date')[0].date
        open_date_bar = BarBalance.objects.filter(operation=OPENING).order_by('-date')[0].date
        open_date = open_date_en if open_date_en < open_date_bar else open_date_bar
        alcoholic_lt = 0.0
        for alcholic in alcoholic_list:
            alcoholic_lt += PurchasedProduct.objects.filter(receipt__date__gte=open_date, name__icontains=alcholic['name'] ).count() * alcholic['lt']
        return alcohol_lt
    else:
        return 0



@register.assignment_tag
def tasso_alcolemico():
    """
        Tasso alcolemico medio 
    """
    e = entrances()
    l = alcohol_l()
    return float(l)/float(e) if e else 0.0



