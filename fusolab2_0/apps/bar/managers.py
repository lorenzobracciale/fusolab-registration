#from ingresso.managers import BalanceManager
from django.db import models
from datetime import datetime
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
#from bar.models import Balance

OPENING = 'op'
CLOSING = 'cl'
PAYMENT = 'pa'
DEPOSIT = 'de'
WITHDRAW = 'wi'	
CASHPOINT = 'pt'
OPERATION_TYPES = ( 
    (OPENING, 'apertura'),
    (CLOSING, 'chiusura'),
    (PAYMENT, 'pagamento'),
    (DEPOSIT, 'deposito'),
    (WITHDRAW, 'prelievo tesoriere'),
    (CASHPOINT, 'punto di cassa')
)
PAYMENT_SUBTYPES = (
    ('ar','artisti'),
    ('ba','barman'),
    ('pu','pulizie'),
    ('va','varie')
)	
DEPOSIT_SUBTYPES = (
    ('co','contante'),
    ('do','donazione')
)


class BalanceManager(models.Manager):

    def is_open(self,time=datetime.now):
        try:
            return super(BalanceManager, self).get_query_set().filter(Q(date__lt=time) & Q(operation__in=[OPENING,CLOSING])).latest('date').operation == OPENING
        except ObjectDoesNotExist:
            return False

    def get_parent(self, time):
        try:
            return super(BalanceManager, self).get_query_set().filter(Q(operation__in=[OPENING,CASHPOINT]) & Q(date__lt=time)).latest('date')
        except ObjectDoesNotExist:
            return None

    def get_closing_amount_before(self,current_opening):
        return super(BalanceManager, self).get_query_set().get(id=current_opening.id).get_previous_by_date(operation=CLOSING).amount

    def get_transactions_for(self, current_opening):
        return super(BalanceManager, self).get_query_set().filter(parent=current_opening)

    def get_opening_times(self,start_date,end_date):
        list = super(BalanceManager, self).get_query_set().filter(Q(date__range=[start_date,end_date]) & Q(parent__isnull=True)).select_related()
        ret = []
        for l in list:
            ret.append([l.date,Balance.objects.filter(Q(parent=l.id) & Q(operation=CLOSING)).get().date])
        return ret  

    def get_checkpoint_before(self,saved_balance):
        return super(BalanceManager, self).get_query_set().get(id=saved_balance.id).get_previous_by_date(operation=CASHPOINT)

    def get_last_n(self,n):
        return super(BalanceManager, self).get_query_set().order_by('-date')[:n]

class ReceiptManager(models.Manager):
	def total_between(self, opening_date, closing_date):
		if super(ReceiptManager, self).get_query_set().filter(date__range=[opening_date,closing_date]).exists():
			return super(ReceiptManager, self).get_query_set().filter(date__range=[opening_date,closing_date]).aggregate(Sum('total'))['total__sum']
		else:
			return Decimal('0.00')
	def receipts_between(self, opening_date, closing_date):
		return super(ReceiptManager, self).get_query_set().filter(date__range=[opening_date,closing_date])


