from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Count
from ingresso.models import *
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
    response['Content-Disposition'] = 'attachment; filename="entrance.csv"'
    writer = csv.writer(response,delimiter=';')
    writer.writerow([   'data',
                        'apertura',
                        'pagamenti',
                        'prelievi',
                        'depositi',
                        'chiusura',
                        'ingressi',
                        'check_apertura',
                        'check_chiusura'])
                        
    for cl in EntranceBalance.objects.filter(operation=CLOSING):
        d = get_entrance_summary(cl)
        writer.writerow([   d['date'],
                            d['opening_amount'],
                            d[PAYMENT],
                            d[WITHDRAW],
                            d[DEPOSIT],
                            d['closing_amount'],
                            d['receipt_count'],
                            d['opening_check'],
                            d['closing_check']])
    return response
