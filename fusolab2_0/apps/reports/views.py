from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext, loader
from django.db.models import Q
#from mm.contrib.django.data_model import DjangoDataModel
from bar.models import *
from bar.managers import *
import datetime
#from mm.contrib.django.grid import DjangoGrid
#import mm
#from excel_response import ExcelResponse
import xlwt
import StringIO

def excel(request, from_day, from_month, from_year, to_day, to_month, to_year):
    ''' generate an excel with the full balance for this reference period '''
    
    from_datetime = datetime.datetime(int(from_year), int(from_month), int(from_day))
    to_datetime = datetime.datetime(int(to_year), int(to_month), int(to_day))

    output_name = 'bilancio_fusolab.xls'
    response = HttpResponse(mimetype="application/ms-excel")
    response['Content-Disposition'] = 'attachment;filename="%s"' %  (output_name )

    book = xlwt.Workbook(encoding='utf8')

    ### create the sheet for the bar and another for the transaction list###
    sheet = book.add_sheet('bar')
    list_sheet = book.add_sheet('elenco')

    #set the headers
    header_style = xlwt.XFStyle() # Create the Style
    font = xlwt.Font() # Create the Font
    font.bold = True
    header_style.font = font # set the font
    borders = xlwt.Borders()
    borders.bottom = xlwt.Borders.THICK
    header_style.borders = borders #set the border
    pattern = xlwt.Pattern()
    pattern.pattern = xlwt.Pattern.SOLID_PATTERN 
    pattern.pattern_fore_colour = 22
    header_style.pattern = pattern

    bar_headers = ['data', 'apertura', 'prelevati', 'depositati', 'pagamenti', 'chiusura', 'cassiere', 'note', 'totale scontrini', 'controllo apertura','controllo chiusura']
#    headers = ['data', 'apertura', 'prelevati', 'depositati', 'pagamenti', 'chiusura', 'cassiere', 'note', 'totale scontrini', 'check1', 'check2', 'ricavi', 'costi', 'risultato']
    for i in range(0, len(bar_headers)):
        sheet.write(0, i, bar_headers[i], header_style)
    tall_style = xlwt.easyxf('font:height 720;') # 36pt
    sheet.row(0).set_style(tall_style)

    list_headers = ['data','operazione','tipo','somma','cassiere','note']
    for i in range(0, len(list_headers)):
        list_sheet.write(0, i, list_headers[i], header_style)
    list_sheet.row(0).set_style(tall_style)    

    qf = Q(date__lte=to_datetime) & Q(date__gte=from_datetime)
    for rowx, bb in  enumerate(BarBalance.objects.filter(qf).order_by('date'), start=1):
        list_sheet.write(rowx,0,str(bb.date))
        list_sheet.write(rowx,1,bb.get_operation_display())            
        list_sheet.write(rowx,2,bb.subtype_display())
        list_sheet.write(rowx,3,bb.amount)
        list_sheet.write(rowx,4,str(bb.cashier))
        list_sheet.write(rowx,5,bb.note)
        
        
    qf = Q(operation=CLOSING) & Q(date__lte=to_datetime) & Q(date__gte=from_datetime) 
    for rowx, bb in enumerate(BarBalance.objects.filter(qf), start=1):
        data = get_bar_summary(bb)
        parent = BarBalance.objects.get_parent_o(bb)
        sheet.write(rowx, 0, data['date'], xlwt.easyxf(num_format_str='dd/mm/yyyy') )
        sheet.write(rowx, 1, data['opening_amount'])
        if parent:
            sheet.write(rowx, 2, data['wi'])
            sheet.write(rowx, 3, data['de'])
            sheet.write(rowx, 4, data['pa'])        
            #sheet.write(rowx, 2, BarBalance.objects.get_withdraws_for(parent))
            #sheet.write(rowx, 3, BarBalance.objects.get_deposits_for(parent))
            #sheet.write(rowx, 4, BarBalance.objects.get_payments_for(parent))
        sheet.write(rowx, 5, data['closing_amount'])
        sheet.write(rowx, 6, str(data['cashier']))
        sheet.write(rowx, 7, data['notes'])
        sheet.write(rowx, 8, data['receipt_count'])
        # excel rows start from one
        # if rowx != 1:
#             sheet.write(rowx, 9, xlwt.Formula('B%d-F%d' % (rowx+1, rowx-1+1))) #check1
#         sheet.write(rowx, 10, xlwt.Formula('N%d-F%d' % (rowx+1, rowx+1))) #check2
#         sheet.write(rowx, 11, xlwt.Formula('F%d-B%d' % (rowx+1, rowx+1))) #ricavi
#         sheet.write(rowx, 12, xlwt.Formula('E%d+C%d-D%d' % (rowx+1, rowx+1, rowx+1))) #costi
#         sheet.write(rowx, 13, xlwt.Formula('L%d-M%d' % (rowx+1, rowx+1))) #risultato
        if rowx != 1:
            sheet.write(rowx, 9, data['opening_check'])        
        sheet.write(rowx, 10, data['closing_check'])






    book.save(response)
    return response


def reports(request):
    return render_to_response('base/reports.html', {} , context_instance=RequestContext(request))


def make_balance(request):
    return HttpResponse("make_balance")

def daily_stats(request):
    return HttpResponse("daily_stats")
