#!/usr/bin/env python

import sys, os
from json import dumps, loads, JSONEncoder

sys.path.append('/var/www/fusolab/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'fusolab2_0.settings'
from django.contrib.auth.models import User, Group
from bar.models import *
from base.models import *
from ingresso.models import *
from registration.models import *
from reports.models import *
from bar.managers import *
from salutatore.models import *
import time
import iso8601
from copy import deepcopy
musers = {}
# USERS
def import_user():
    print "Importo USER"
    f = open('users.json', 'r')
    for o in loads(f.read()):
        u = User()
        #u.pk = o['pk']
        musers[o['pk']] = {'old_fields':  o['fields']}
        print "PK:", o['pk']
        print "nome:", o['fields']['first_name'],  o['fields']['last_name']

        try:
            g = Group.objects.get(name = "turnisti")
        except:
            g = None
        if not g:
            g = Group.objects.create(name = "turnisti")
            g.save()

        for k,v in o['fields'].items():
            toadd = False 
            if (k == "is_superuser" or k == 'is_staff') and v == True:
                v = False
                toadd = True
                #add user in turnisti
            # problema con 3584
            #if k== "user_permissions" and o['pk'] == 3584:
            #    v = []
            print k,v
            if k != 'groups' and k != "user_permissions":
                setattr(u, k, v)
        print "Aggiungo: " , u
        if u.username == 'fusoci':
            u.is_superuser = u.is_staff = True
        if u.username != 'root':
            u.save()
            #u = User.objects.get(username = o['fields']['username'])
            musers[o['pk']]['new_pk'] = u.pk
            if toadd:
                u.groups.add(g) 
                u.save()
                pass

    f.close()

muserprofile = {}
#USERPROFILES
def import_userprofile():
    print "Importo USERPROFILE"
    f = open('userprofiles.json', 'r')
    for o in loads(f.read()):
        print "pk: " , o['pk']
        try:
            u =  UserProfile.objects.get(user__pk = musers[o['fields']['user']]['new_pk'])
        except:
            u =  UserProfile()
        for k,v in o['fields'].items():
            if k == 'user':
                #k = 'user_id'
                v = User.objects.get(pk = musers[v]['new_pk'] )
            setattr(u, k, v)
        print "Aggiungo: " , u
        #u.full_clean()
        u.save()
        muserprofile[o['pk']] = u.pk
    f.close()


#CARD
def import_card():
    print "Importo CARD"
    f = open('cards.json', 'r')
    for o in loads(f.read()):
        u =  Card()
        for k,v in o['fields'].items():
            if k == 'user':
                v = UserProfile.objects.get(pk = muserprofile[v])
                #k = 'user_id'
            setattr(u, k, v)
        print "Aggiungo card: "# , u
        #u.full_clean()
        u.save()
    f.close()

#GREETINGS
def import_greeting():
    print "Importo GREETING"
    f = open('greetings.json', 'r')
    for o in loads(f.read()):
        u =  Greeting()
        for k,v in o['fields'].items():
            if k == 'user':
                #k = 'user_id'
                v = UserProfile.objects.get(pk = muserprofile[v])
            setattr(u, k, v)
        print "Aggiungo greeting: "# , u
        #u.full_clean()
        u.save()
    f.close()

#PRODUCT
def import_product():
    print "Importo PRODUCTS"
    f = open('products.json', 'r')
    for o in loads(f.read()):
        u =  Product()
        for k,v in o['fields'].items():
            if k != 'internal_cost':
                setattr(u, k, v)
        print "Aggiungo products: "# , u
        #u.full_clean()
        u.save()
    f.close()

#RECEIPT
mreceipts = {}
def import_receipt():
    print "Importo RECEIPT"
    f = open('receipts.json', 'r')
    for o in loads(f.read()):
        u =  Receipt()
        for k,v in o['fields'].items():
            if k == 'cashier':
                v = UserProfile.objects.get(pk = muserprofile[v])
                #k = 'cashier_id'
            setattr(u, k, v)
        print "Aggiungo purchased products: "# , u
        #u.full_clean()
        u.save()
        mreceipts[o['pk']] = u.pk
    f.close()



#PURCHASEDPRODUCT
def import_purchasedproduct():
    print "Importo PURCHASEDPRODUCTS"
    f = open('purchasedproducts.json', 'r')
    for o in loads(f.read()):
        u =  PurchasedProduct()
        for k,v in o['fields'].items():
            if k == 'receipt':
                v = Receipt.objects.get(pk = mreceipts[v])
                #k = 'receipt_id'
            setattr(u, k, v)
        print "Aggiungo purchased products: "# , u
        #u.full_clean()
        u.save()
    f.close()

#BarCashBalance
def import_barcashbalance():
    print "Importo BARCASHBALANCE"
    f = open('barcashbalances.json', 'r')
    for o in loads(f.read()):
        u =  BarBalance()
        print o
        fields = o['fields']
        #u.date = iso8601.parse_date(fields['date']) if type(fields['date']) is unicode else fields['date']
        u.date = datetime.strptime(fields['date'], "%Y-%m-%d %H:%M:%S" ) #2012-11-10 02:44:51
        u.date.replace(tzinfo=None)
        u.cashier = UserProfile.objects.get(pk = muserprofile[fields['cashier']])
        u.note = fields['note']
        # opening
        u.operation = OPENING #OPENING, CLOSING, PAYMENT, DEPOSIT, WITHDRAW, CASHPOINT
        u.amount = fields['initial_cash']
        u.save()
        u.parent = u
        u.save()
        #withdraw
        if fields['withdraw'] > 0:
            u2 = deepcopy(u)
            u2.operation = WITHDRAW
            u2.pk = None
            u2.parent = u
            u2.amount = fields['withdraw']
            u2.save()
        #deposit
        if fields['deposit'] >0:
            u3 = deepcopy(u)
            u3.operation = DEPOSIT
            u3.pk = None
            u3.parent = u
            u3.amount = fields['deposit']
            u3.save()
        # closing
        u4 = deepcopy(u)
        u4.operation = CLOSING
        u4.pk = None
        u4.parent = u
        u4.amount = fields['final_cash']
        u4.save()
        print "Aggiungo bar balance : "# , u
    f.close()


#EntranceCashBalance
def import_entrancecashbalance():
    f = open('entrancecashbalances.json', 'r')
    for o in loads(f.read()):
        u =  EntranceBalance()
        fields = o['fields']
        u.date = datetime.strptime(fields['date'], "%Y-%m-%d %H:%M:%S" ) #2012-11-10 02:44:51
        u.date.replace(tzinfo=None)
        u.cashier = UserProfile.objects.get(pk = muserprofile[fields['cashier']])
        u.note = fields['note']
        # opening
        u.operation = OPENING #OPENING, CLOSING, PAYMENT, DEPOSIT, WITHDRAW, CASHPOINT
        u.amount = fields['initial_cash']
        u.save()
        u.parent = u
        u.save()
        #withdraw
        if fields['withdraw'] > 0:
            u2 = deepcopy(u)
            u2.operation = WITHDRAW
            u2.pk = None
            u2.parent = u
            u2.amount = fields['withdraw']
            u2.save()
        #deposit
        if fields['deposit'] >0:
            u3 = deepcopy(u)
            u3.operation = DEPOSIT
            u3.pk = None
            u3.parent = u
            u3.amount = fields['deposit']
            u3.save()
        # closing
        u4 = deepcopy(u)
        u4.operation = CLOSING
        u4.pk = None
        u4.parent = u
        u4.amount = fields['final_cash']
        u4.save()
        print "Aggiungo entrance balance : "# , u
        #u.full_clean()
        #u.save()
    f.close()

def main():
    import_user()
    import_userprofile()
    import_card()
    import_product()
    import_greeting()
    #import_receipt()
    #import_purchasedproduct()
    # problemi sul parent dei primi valori
    #import_barcashbalance()
    #import_entrancecashbalance()

if  __name__ =='__main__':main()

#TODO ripristinare add now in receipt
# ripristinare email tesoriere
