#from bar.managers import BalanceManager
from decimal import Decimal
from django.db import models
from django.db.models import Sum, Q
from datetime import datetime
from bar.managers import BalanceManager

#class EntranceManager(models.Manager): #lorenzo
class EntranceManager(BalanceManager):
	def total_between(self, opening_date, closing_date):
		if super(EntranceManager, self).get_query_set().filter(date__range=[opening_date,closing_date]).exists():
			return super(EntranceManager, self).get_query_set().filter(date__range=[opening_date,closing_date]).aggregate(Sum('cost'))['cost__sum']
		else:
			return Decimal('0.00')

	def count_between(self, opening_date, closing_date):
		if super(EntranceManager, self).get_query_set().filter(date__range=[opening_date,closing_date]).exists():
			return super(EntranceManager, self).get_query_set().filter(date__range=[opening_date,closing_date]).count()
		else:
			return 0	

