#from ingresso.managers import BalanceManager
from decimal import Decimal
from django.db import models
from datetime import datetime
from django.db.models import Sum, Q
from django.core.exceptions import ObjectDoesNotExist
from bar.models import *

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

def get_payment_display(key):
    d = dict(PAYMENT_SUBTYPES)
    return d[key] if key in d else None
        
def get_deposit_display(key):
    d = dict(DEPOSIT_SUBTYPES)
    return d[key] if key in d else None

class BalanceManager(models.Manager):

    def is_open(self,time=datetime.now):
        try:
            return super(BalanceManager, self).get_query_set().filter(Q(date__lt=time) & Q(operation__in=[OPENING,CLOSING])).latest('date').operation == OPENING
        except ObjectDoesNotExist:
            return False

    def get_parent_t(self, current_time):
        try:
            return super(BalanceManager, self).get_query_set().filter(Q(operation__in=[OPENING,CASHPOINT]) & Q(date__lt=current_time)).latest('date')
        except ObjectDoesNotExist:
            return None
    
    def get_parent_o(self, current_operation):
        try:
            return super(BalanceManager, self).get_query_set().filter(pk=current_operation.parent.pk).get()
        except ObjectDoesNotExist:
            return None    
    def get_closing(self,current_transaction):
        return super(BalanceManager, self).get_query_set().get(Q(id=current_transaction.id) & Q(operation=CLOSING))
            
    def get_last_closing(self,current_opening):
        if super(BalanceManager, self).get_query_set().filter(id__lt=current_opening.id).exists():
            return super(BalanceManager, self).get_query_set().get(id=current_opening.id).get_previous_by_date(operation=CLOSING).amount
        else:
            return Decimal('0.00')

    def get_closing_amount_before(self,current_opening):
        return super(BalanceManager, self).get_query_set().get(id=current_opening.id).get_previous_by_date(operation=CLOSING).amount

    def get_transactions_for(self, current_opening):
        return super(BalanceManager, self).get_query_set().filter(parent=current_opening.id)

    def get_payments_for(self, current_opening):
        return super(BalanceManager, self).get_query_set().filter(Q(parent=current_opening.id) & Q(operation=PAYMENT)).aggregate(Sum('amount'))['amount__sum']

    def get_deposits_for(self, current_opening):
        return super(BalanceManager, self).get_query_set().filter(Q(parent=current_opening.id) & Q(operation=DEPOSIT)).aggregate(Sum('amount'))['amount__sum']

    def get_withdraws_for(self, current_opening):
        return super(BalanceManager, self).get_query_set().filter(Q(parent=current_opening.id) & Q(operation=WITHDRAW)).aggregate(Sum('amount'))['amount__sum']

    def get_opening_times(self,start_date,end_date):
        list = super(BalanceManager, self).get_query_set().filter(Q(date__range=[start_date,end_date]) & Q(parent__isnull=True)).select_related().order_by('date')
        ret = []
        for l in list:
            ret.append([l.date,super(BalanceManager, self).get_query_set().filter(Q(parent=l.id) & Q(operation=CLOSING)).get().date])
        return ret  

    def get_checkpoint_before(self,saved_balance):
        try:
            return super(BalanceManager, self).get_query_set().get(id=saved_balance.id).get_previous_by_date(operation=CASHPOINT)
        except ObjectDoesNotExist:
            return None  

    def get_last_n(self,n):
        return super(BalanceManager, self).get_query_set().order_by('-date')[:n]



class ReceiptManager(models.Manager):

    def total_amount(self):
        return super(ReceiptManager, self).get_query_set().aggregate(Sum('total'))['total__sum']

    def total_between(self, opening_date, closing_date):
        if super(ReceiptManager, self).get_query_set().filter(date__range=[opening_date,closing_date]).exists():
            return super(ReceiptManager, self).get_query_set().filter(date__range=[opening_date,closing_date]).aggregate(Sum('total'))['total__sum']
        else:
            return Decimal('0.00')

    def receipts_between(self, opening_date, closing_date):
        return super(ReceiptManager, self).get_query_set().filter(date__range=[opening_date,closing_date])


