from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models import Sum
from django.db.models import Count
from fusoci.models import * 
from django.conf import settings
from django.utils import simplejson
from decimal import Decimal
from datetime import datetime, timedelta
import csv

DATETIME_FORMAT = "%d/%m/%Y %H:%M"
DATE_FORMAT = "%d/%m/%Y"

@staff_member_required
def csv_statistics(request, what=None):
	response = HttpResponse(mimetype='text/csv')
	response['Content-Disposition'] = 'attachment; filename="'+what+'.csv"'
	writer = csv.writer(response,delimiter=';')

	if what == 'bar':
		writer.writerow(['data','apertura','prelevati','depositati','chiusura','cassiere'])
		b = BarCashBalance.objects.all()
		for bb in b:
			writer.writerow([	bb.date.strftime(DATETIME_FORMAT),
								str(bb.initial_cash).replace('.',','),
								str(bb.withdraw).replace('.',','),
								str(bb.deposit).replace('.',','),
								str(bb.final_cash).replace('.',','),
								bb.cashier
			])
		
	elif what == 'entrance':
		writer.writerow(['data','apertura','prelevati','depositati','chiusura','cassiere'])
		e = EntranceCashBalance.objects.all()
		for ee in e:
			writer.writerow([	ee.date.strftime(DATETIME_FORMAT),
								str(ee.initial_cash).replace('.',','),
								str(ee.withdraw).replace('.',','),
								str(ee.deposit).replace('.',','),
								str(ee.final_cash).replace('.',','),
								ee.cashier
			])

	elif what == 'receipts':
		writer.writerow(['data','totale ricevute'])
		#hardcoded starttime 10 Novembre 2012 12:00
		current_step = datetime(2012,11,10,12,00,00)
		while (current_step < datetime.now()):
			r = Receipt.objects.filter(  date__range=[ current_step,current_step+timedelta(hours=24)  ]  ).aggregate(tot=Sum('total'))
			if r['tot']>0:
				writer.writerow([	current_step.strftime(DATE_FORMAT),
									str(r['tot']).replace('.',',')
								])
			current_step = current_step + timedelta(hours=24)
		
	else:
		return HttpResponseNotFound('bad request')
	return response
