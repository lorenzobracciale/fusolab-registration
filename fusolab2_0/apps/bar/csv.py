from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Count
from bar.models import *
from django.conf import settings
from django.utils import simplejson
from decimal import Decimal
from datetime import datetime, timedelta
import csv

DATETIME_FORMAT = "%d/%m/%Y %H:%M"
DATE_FORMAT = "%d/%m/%Y"

@staff_member_required
def create_resume(request):
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename="bar.csv"'
    writer = csv.writer(response,delimiter=';')
    writer.writerow(['data',
                        'apertura',
                        'pagamenti',
                        'prelievi',
                        'depositi',
                        'chiusura',
                        'ricevute',
                        'check_apertura',
                        'check_chiusura',
                        'ricavo',
                        'costi',
                        'guadagno'])
    for cl in BarBalance.objects.filter(operation=CLOSING):
        date = op.date
        opening = op.amount
        payments = BarBalance.objects.get_payments_for(op)
        withdraws = BarBalance.objects.get_withdraws_for(op)
        deposits = BarBalance.objects.get_deposits_for(op)
        closing = BarBalance.filter

