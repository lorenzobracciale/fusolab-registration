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


@staff_member_required
def csv_statistics(request, what=None):
	response = HttpResponse(mimetype='text')
	writer = csv.writer(response,delimiter=';')

	if what == 'bar':
		writer.writerow(['data','apertura','prelevati','depositati','chiusura','cassiere'])
		b = BarCashBalance.objects.all()
		for bb in b:
			writer.writerow(  [bb.date.strftime("%Y-%m-%d %H:%M"),bb.initial_cash,bb.withdraw,bb.deposit,bb.final_cash,bb.cashier]   )
		
	elif what == 'entrance':
		writer.writerow(['data','apertura','prelevati','depositati','chiusura','cassiere'])
		e = EntranceCashBalance.objects.all()
		for ee in e:
			writer.writerow(  [ee.date.strftime("%Y-%m-%d %H:%M"),ee.initial_cash,ee.withdraw,ee.deposit,ee.final_cash,ee.cashier]   )

	elif what == 'receipts':
		writer.writerow(['data','totale ricevute'])
		#hardcoded starttime 10 Novembre 2012 12:00
		current_step = datetime(2012,11,10,12,00,00)
		while (current_step < datetime.now()):
			r = Receipt.objects.filter(  date__range=[ current_step,current_step+timedelta(hours=24)  ]  ).aggregate(tot=Sum('total'))
			writer.writerow( [current_step.strftime("%Y-%m-%d"),r['tot']])
			current_step = current_step + timedelta(hours=24)
		
	else:
		return HttpResponseNotFound('bad request')
	return response
