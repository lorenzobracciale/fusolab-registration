from django.http import HttpResponse, HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext, loader
from django.db.models import Q
#from mm.contrib.django.data_model import DjangoDataModel
from bar.models import *
from bar.managers import *
from ingresso.models import *
from ingresso.managers import *
import datetime
import xlsxwriter
import StringIO


def excel(request, what, from_day, from_month, from_year, to_day, to_month, to_year):
    ''' generate an excel with the full balance for this reference period '''
    
    from_datetime = datetime.datetime(int(from_year), int(from_month), int(from_day))
    to_datetime = datetime.datetime(int(to_year), int(to_month), int(to_day), hour=23, minute=59) + datetime.timedelta(hours=12)

    output_name = "bilancio_"+what+"_fusolab.xlsx"
    output = StringIO.StringIO()

    ### create the sheet for the summary and another for the transaction list###
    workbook = xlsxwriter.Workbook(output)
    sheet = workbook.add_worksheet('riepilogo')
    list_sheet = workbook.add_worksheet('elenco')

    ### create styles for cell content
    header_format = workbook.add_format({'bold': True,'align':'center'})
    header_format.set_border()
    money_format = workbook.add_format({'num_format':'0.00'})
    date_format = workbook.add_format({'num_format':'dd/mm/yy','align':'center','valign':'center',})
    note_format = workbook.add_format()
    note_format.set_text_wrap()
    note_format.set_right()
    warning_under_format = workbook.add_format({'bg_color':'#FFC7CE','font_color':'#9C0006'})
    warning_over_format = workbook.add_format({'bg_color':   '#C6EFCE','font_color': '#006100'})
    check_format = workbook.add_format({'bold': True})
    check_format.set_top()
    check_under_format = workbook.add_format({'bold': True,'bg_color':'#9C0006','font_color':'#FFC7CE'})
    check_under_format.set_top()
    check_over_format = workbook.add_format({'bold': True,'bg_color':'#006100','font_color':'#C6EFCE'})
    check_over_format.set_top()
    line_format = workbook.add_format()
    line_format.set_top()
    
    if what == 'bar':
    
        summary_headers = ['data', 'apertura', 'prelevati', 'depositati', 'pagamenti', 'chiusura', 'ricevute', 'check1', 'check2', 'teorico', 'netto', 'cassiere', 'note']
        for i in range(0, len(summary_headers)):
            sheet.write_string(0, i, summary_headers[i], header_format)

        rowx = 0
        qf = Q(operation=CLOSING) & Q(date__lte=to_datetime) & Q(date__gte=from_datetime) 
        for rowx, bb in enumerate(BarBalance.objects.filter(qf).order_by('date'), start=1):
            data = get_bar_summary(bb)
            parent = BarBalance.objects.get_parent_o(bb)
            sheet.write(rowx, 0, parent.date,date_format) #data
            sheet.write(rowx, 1, data['opening_amount'],money_format) #apertura
            if parent:
                sheet.write(rowx, 2, data['wi'],money_format) #prelevati
                sheet.write(rowx, 3, data['de'],money_format) #depositati
                sheet.write(rowx, 4, data['pa'],money_format) #pagamenti
            sheet.write(rowx, 5, data['closing_amount'],money_format) #chiusura
            
            sheet.write(rowx, 6, data['receipt_amount'],money_format) #ricevute
            if rowx > 1:
                sheet.write(rowx,7,'=B'+str(rowx+1)+'-F'+str(rowx),money_format) #check1    
            sheet.write(rowx,8,'=K'+str(rowx+1)+'-J'+str(rowx+1),money_format) #check2
            sheet.write(rowx,9, '=G'+str(rowx+1)+'+D'+str(rowx+1)+'-E'+str(rowx+1)+'-C'+str(rowx+1),money_format) #teorico
            sheet.write(rowx,10,'=F'+str(rowx+1)+'-B'+str(rowx+1),money_format) #netto
            sheet.write_string(rowx, 11, str(data['cashier'])) # nome cassiere
            sheet.write_string(rowx, 12, ''.join(data['notes']),note_format) #note

        for col in range(13):
            sheet.write(rowx+1,col,'',line_format) 
        
        #add column check
        sheet.write(rowx+1,7,'=SUM(H3:H'+str(rowx+1)+')',check_format)
        sheet.write(rowx+1,8,'=SUM(I2:I'+str(rowx+1)+')',check_format)
        
        ###sheet formatting
        sheet.set_column('A:A', 15)
        sheet.set_column('L:L',12)
        sheet.set_column('M:M',80)
        sheet.conditional_format('H2:I'+str(rowx+1), {'type':     'cell',
                                        'criteria': '<=',
                                        'value':    -settings.MONEY_DELTA,
                                        'format':   warning_under_format})
        sheet.conditional_format('H2:I'+str(rowx+1), {'type':     'cell',
                                        'criteria': '>=',
                                        'value':    settings.MONEY_DELTA,
                                        'format':   warning_over_format}) 
        sheet.conditional_format('H'+str(rowx+2)+':I'+str(rowx+2), {'type':     'cell',
                                        'criteria': '<=',
                                        'value':    -settings.MONEY_DELTA,
                                        'format':   check_under_format})
        sheet.conditional_format('H'+str(rowx+2)+':I'+str(rowx+2), {'type':     'cell',
                                        'criteria': '>=',
                                        'value':    settings.MONEY_DELTA,
                                        'format':   check_over_format})
                                        
        list_headers = ['data','operazione','tipo','somma','cassiere','note']
        for i in range(0, len(list_headers)):
            list_sheet.write_string(0, i, list_headers[i], header_format)

        qf = Q(date__lte=to_datetime) & Q(date__gte=from_datetime)
        for rowx, bb in  enumerate(BarBalance.objects.filter(qf).order_by('date'), start=1):
            
            list_sheet.write(rowx,0,bb.date,date_format)
            list_sheet.write_string(rowx,1,bb.get_operation_display())
            if bb.operation == PAYMENT:            
                list_sheet.write_string(rowx,2,get_payment_display(bb.subtype))
            elif bb.operation == DEPOSIT:
                list_sheet.write_string(rowx,2,get_deposit_display(bb.subtype))        
            list_sheet.write(rowx,3,bb.amount,money_format)
            list_sheet.write_string(rowx,4,str(bb.cashier))
            list_sheet.write_string(rowx,5,bb.note,note_format)        

        for col in range(6):
            list_sheet.write(rowx+1,col,'',line_format)
        
        #list_sheet formatting
        list_sheet.set_column('A:A', 15)        
        list_sheet.set_column('E:E', 15)
        list_sheet.set_column('F:F', 80) 
    
    elif what == 'ingresso':
    
        summary_headers = ['data', 'apertura', 'prelevati', 'depositati', 'pagamenti', 'chiusura', 'ingressi', 'check1', 'check2', 'teorico', 'netto', 'cassiere', 'note']
        for i in range(0, len(summary_headers)):
            sheet.write(0, i, summary_headers[i], header_format)

        rowx = 0
        qf = Q(operation=CLOSING) & Q(date__lte=to_datetime) & Q(date__gte=from_datetime) 
        for rowx, bb in enumerate(EntranceBalance.objects.filter(qf).order_by('date'), start=1):
            data = get_entrance_summary(bb)
            parent = EntranceBalance.objects.get_parent_o(bb)
            sheet.write(rowx, 0, parent.date,date_format)
            sheet.write(rowx, 1, data['opening_amount'],money_format)
            if parent:
                sheet.write(rowx, 2, data['wi'],money_format)
                sheet.write(rowx, 3, data['de'],money_format)
                sheet.write(rowx, 4, data['pa'],money_format)
            sheet.write(rowx, 5, data['closing_amount'],money_format)
            
            sheet.write(rowx, 6, data['receipt_amount'],money_format)
            if rowx > 1:
                sheet.write(rowx,7,'=B'+str(rowx+1)+'-F'+str(rowx),money_format)    
            sheet.write(rowx,8,'=K'+str(rowx+1)+'-J'+str(rowx+1),money_format)
            sheet.write(rowx,9, '=G'+str(rowx+1)+'+D'+str(rowx+1)+'-E'+str(rowx+1)+'-C'+str(rowx+1),money_format)
            sheet.write(rowx,10,'=F'+str(rowx+1)+'-B'+str(rowx+1),money_format)
            sheet.write_string(rowx, 11, str(data['cashier']))
            sheet.write_string(rowx, 12, ''.join(data['notes']),note_format)

        for col in range(13):
            sheet.write(rowx+1,col,'',line_format) 
        
        #add column check
        sheet.write(rowx+1,7,'=SUM(H3:H'+str(rowx+1)+')',check_format)
        sheet.write(rowx+1,8,'=SUM(I2:I'+str(rowx+1)+')',check_format)
        
        ###sheet formatting
        sheet.set_column('A:A', 15)
        sheet.set_column('L:L',12)
        sheet.set_column('M:M',80)
        sheet.conditional_format('H2:I'+str(rowx+1), {'type':     'cell',
                                        'criteria': '<=',
                                        'value':    -settings.MONEY_DELTA,
                                        'format':   warning_under_format})
        sheet.conditional_format('H2:I'+str(rowx+1), {'type':     'cell',
                                        'criteria': '>=',
                                        'value':    settings.MONEY_DELTA,
                                        'format':   warning_over_format}) 
        sheet.conditional_format('H'+str(rowx+2)+':I'+str(rowx+2), {'type':     'cell',
                                        'criteria': '<=',
                                        'value':    -settings.MONEY_DELTA,
                                        'format':   check_under_format})
        sheet.conditional_format('H'+str(rowx+2)+':I'+str(rowx+2), {'type':     'cell',
                                        'criteria': '>=',
                                        'value':    settings.MONEY_DELTA,
                                        'format':   check_over_format})
                                        
        list_headers = ['data','operazione','tipo','somma','cassiere','note']
        for i in range(0, len(list_headers)):
            list_sheet.write(0, i, list_headers[i], header_format)

        qf = Q(date__lte=to_datetime) & Q(date__gte=from_datetime)
        for rowx, bb in  enumerate(EntranceBalance.objects.filter(qf).order_by('date'), start=1):
            
            list_sheet.write(rowx,0,bb.date,date_format)
            list_sheet.write_string(rowx,1,bb.get_operation_display())
            if bb.operation == PAYMENT:            
                list_sheet.write_string(rowx,2,get_payment_display(bb.subtype))
            elif bb.operation == DEPOSIT:
                list_sheet.write_string(rowx,2,get_deposit_display(bb.subtype))        
            list_sheet.write(rowx,3,bb.amount,money_format)
            list_sheet.write_string(rowx,4,str(bb.cashier))
            list_sheet.write_string(rowx,5,bb.note,note_format)        

        for col in range(6):
            list_sheet.write(rowx+1,col,'',line_format)

        
        #list_sheet formatting
        list_sheet.set_column('A:A', 15)        
        list_sheet.set_column('E:E', 15)
        list_sheet.set_column('F:F', 80)
         
    elif what == 'interregno':
        rowx = 0
        summary_headers = ['data', 'precedente', 'prelevati', 'depositati', 'pagamenti', 'ricevute','atteso','punto cassa', 'controllo', 'cassiere', 'note']
        for i in range(0, len(summary_headers)):
            sheet.write_string(0, i, summary_headers[i], header_format)
        
        qf = Q(operation=CASHPOINT) & Q(date__lte=to_datetime) & Q(date__gte=from_datetime) 
        for rowx, bb in enumerate(SmallBalance.objects.filter(qf).order_by('date'), start=1):
            data = get_small_summary(bb)
            #parent = SmallBalance.objects.get_parent_o(bb)

            sheet.write(rowx, 0, bb.date,date_format)
            sheet.write(rowx, 1, data['last_checkpoint'],money_format)
            sheet.write(rowx, 2, data['wi'],money_format)
            sheet.write(rowx, 3, data['de'],money_format)
            sheet.write(rowx, 4, data['pa'],money_format)        
            sheet.write(rowx, 5, data['receipt_amount'],money_format)
            sheet.write(rowx, 6, data['expected_checkpoint'],money_format)
            sheet.write(rowx, 7, data['checkpoint'],money_format)
            sheet.write(rowx, 8, data['check'],money_format)
            sheet.write_string(rowx, 9, str(data['cashier']))
            sheet.write_string(rowx, 10, ''.join(data['notes']),note_format)

        for col in range(11):
            sheet.write(rowx+1,col,'',line_format)

        #add column check
        sheet.write(rowx+1,8,'=SUM(I2:I'+str(rowx+1)+')',check_format)

        sheet.set_column('A:A', 15)
        sheet.set_column('J:J',12)
        sheet.set_column('K:K',80)
        
        sheet.conditional_format('I2:I'+str(rowx+1), {'type':     'cell',
                                        'criteria': '<=',
                                        'value':    -settings.MONEY_DELTA,
                                        'format':   warning_under_format})
        sheet.conditional_format('I2:I'+str(rowx+1), {'type':     'cell',
                                        'criteria': '>=',
                                        'value':    settings.MONEY_DELTA,
                                        'format':   warning_over_format}) 
        sheet.conditional_format('I'+str(rowx+2)+':I'+str(rowx+2), {'type':     'cell',
                                        'criteria': '<=',
                                        'value':    -settings.MONEY_DELTA,
                                        'format':   check_under_format})
        sheet.conditional_format('I'+str(rowx+2)+':I'+str(rowx+2), {'type':     'cell',
                                        'criteria': '>=',
                                        'value':    settings.MONEY_DELTA,
                                        'format':   check_over_format})

        list_headers = ['data','operazione','tipo','somma','cassiere','note']
        for i in range(0, len(list_headers)):
            list_sheet.write_string(0, i, list_headers[i], header_format)   

        qf = Q(date__lte=to_datetime) & Q(date__gte=from_datetime)
        for rowx, bb in  enumerate(SmallBalance.objects.filter(qf).order_by('date'), start=1):
            list_sheet.write(rowx,0,bb.date)
            list_sheet.write_string(rowx,1,bb.get_operation_display())
            if bb.operation == PAYMENT:            
                list_sheet.write_string(rowx,2,get_payment_display(bb.subtype))
            elif bb.operation == DEPOSIT:
                list_sheet.write_string(rowx,2,get_deposit_display(bb.subtype))        
            list_sheet.write(rowx,3,bb.amount,money_format)
            list_sheet.write_string(rowx,4,str(bb.cashier))
            list_sheet.write_string(rowx,5,bb.note,note_format)        
        
        for col in range(6):
            list_sheet.write(rowx+1,col,'',line_format)

        
        #list_sheet formatting
        list_sheet.set_column('A:A', 15)        
        list_sheet.set_column('E:E', 15)
        list_sheet.set_column('F:F', 80) 

    else:
        raise Http404
            
    workbook.close()

    output.seek(0)
    response = HttpResponse(output.read(), mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = "attachment; "+output_name

    return response

# def excel(request, what, from_day, from_month, from_year, to_day, to_month, to_year):
#     ''' generate an excel with the full balance for this reference period '''
#     
#     from_datetime = datetime.datetime(int(from_year), int(from_month), int(from_day))
#     to_datetime = datetime.datetime(int(to_year), int(to_month), int(to_day), hour=23, minute=59) + datetime.timedelta(hours=12)
# 
#     output_name = 'bilancio_'+what+'_fusolab.xls'
#     response = HttpResponse(mimetype="application/ms-excel")
#     response['Content-Disposition'] = 'attachment;filename="%s"' %  (output_name )
# 
#     book = xlwt.Workbook(encoding='utf8')
# 
#     ### create the sheet for the summary and another for the transaction list###
#     sheet = book.add_sheet('riepilogo')
#     list_sheet = book.add_sheet('elenco')
# 
#     #set the headers
#     header_style = xlwt.XFStyle() # Create the Style
#     font = xlwt.Font() # Create the Font
#     font.bold = True
#     header_style.font = font # set the font
#     borders = xlwt.Borders()
#     borders.bottom = xlwt.Borders.THICK
#     header_style.borders = borders #set the border
#     pattern = xlwt.Pattern()
#     pattern.pattern = xlwt.Pattern.SOLID_PATTERN 
#     pattern.pattern_fore_colour = 22
#     header_style.pattern = pattern
# 
#     algn1 = xlwt.Alignment()
#     algn1.wrap = 1
#     note_style = xlwt.XFStyle()
#     note_style.alignment = algn1
# 
#     if what == 'bar':
# 
# 
#         summary_headers = ['data', 'apertura', 'prelevati', 'depositati', 'pagamenti', 'chiusura', 'cassiere', 'note', 'totale scontrini', 'check1', 'check2', 'ricavi', 'costi', 'risultato']
#         for i in range(0, len(summary_headers)):
#             sheet.write(0, i, summary_headers[i], header_style)
#         tall_style = xlwt.easyxf('font:height 720;') # 36pt
#         sheet.row(0).set_style(tall_style)
# 
#         list_headers = ['data','operazione','tipo','somma','cassiere','note']
#         for i in range(0, len(list_headers)):
#             list_sheet.write(0, i, list_headers[i], header_style)
#         list_sheet.row(0).set_style(tall_style)    
# 
#         qf = Q(date__lte=to_datetime) & Q(date__gte=from_datetime)
#         for rowx, bb in  enumerate(BarBalance.objects.filter(qf).order_by('date'), start=1):
#             list_sheet.write(rowx,0,str(bb.date))
#             list_sheet.write(rowx,1,bb.get_operation_display())
#             if bb.operation == PAYMENT:            
#                 list_sheet.write(rowx,2,get_payment_display(bb.subtype))
#             elif bb.operation == DEPOSIT:
#                 list_sheet.write(rowx,2,get_deposit_display(bb.subtype))        
#             list_sheet.write(rowx,3,bb.amount)
#             list_sheet.write(rowx,4,str(bb.cashier))
#             list_sheet.write(rowx,5,bb.note)        
#         
#         qf = Q(operation=CLOSING) & Q(date__lte=to_datetime) & Q(date__gte=from_datetime) 
#         for rowx, bb in enumerate(BarBalance.objects.filter(qf).order_by('date'), start=1):
#             data = get_bar_summary(bb)
#             parent = BarBalance.objects.get_parent_o(bb)
#             sheet.write(rowx, 0, data['date'], xlwt.easyxf(num_format_str='dd/mm/yyyy') )
#             sheet.write(rowx, 1, data['opening_amount'])
#             if parent:
#                 sheet.write(rowx, 2, data['wi'])
#                 sheet.write(rowx, 3, data['de'])
#                 sheet.write(rowx, 4, data['pa'])        
#                 #sheet.write(rowx, 2, BarBalance.objects.get_withdraws_for(parent))
#                 #sheet.write(rowx, 3, BarBalance.objects.get_deposits_for(parent))
#                 #sheet.write(rowx, 4, BarBalance.objects.get_payments_for(parent))
#             sheet.write(rowx, 5, data['closing_amount'])
#             sheet.write(rowx, 6, str(data['cashier']))
#             sheet.write(rowx, 7, data['notes'],note_style)
#             sheet.write(rowx, 8, data['receipt_count'])
#             # excel rows start from one
#             if rowx != 1:
#                 sheet.write(rowx, 9, xlwt.Formula('B%d-F%d' % (rowx+1, rowx-1+1))) #check1
#             sheet.write(rowx, 10, xlwt.Formula('L%d+M%d-I%d' % (rowx+1, rowx+1, rowx+1))) #check2
#             sheet.write(rowx, 11, xlwt.Formula('F%d-B%d' % (rowx+1, rowx+1))) #ricavi
#             sheet.write(rowx, 12, xlwt.Formula('E%d+C%d-D%d' % (rowx+1, rowx+1, rowx+1))) #costi
#             sheet.write(rowx, 13, xlwt.Formula('L%d-M%d' % (rowx+1, rowx+1))) #risultato
# 
#     elif what == 'ingresso':
# 
# 
#         summary_headers = ['data', 'apertura', 'prelevati', 'depositati', 'pagamenti', 'chiusura', 'cassiere', 'note', 'totale ingressi', 'check1', 'check2', 'ricavi', 'costi', 'risultato']
#         for i in range(0, len(summary_headers)):
#             sheet.write(0, i, summary_headers[i], header_style)
#         tall_style = xlwt.easyxf('font:height 720;') # 36pt
#         sheet.row(0).set_style(tall_style)
# 
#         list_headers = ['data','operazione','tipo','somma','cassiere','note']
#         for i in range(0, len(list_headers)):
#             list_sheet.write(0, i, list_headers[i], header_style)
#         list_sheet.row(0).set_style(tall_style)    
# 
#         qf = Q(date__lte=to_datetime) & Q(date__gte=from_datetime)
#         for rowx, bb in  enumerate(EntranceBalance.objects.filter(qf).order_by('date'), start=1):
#             list_sheet.write(rowx,0,str(bb.date))
#             list_sheet.write(rowx,1,bb.get_operation_display())
#             if bb.operation == PAYMENT:            
#                 list_sheet.write(rowx,2,get_payment_display(bb.subtype))
#             elif bb.operation == DEPOSIT:
#                 list_sheet.write(rowx,2,get_deposit_display(bb.subtype))        
#             list_sheet.write(rowx,3,bb.amount)
#             list_sheet.write(rowx,4,str(bb.cashier))
#             list_sheet.write(rowx,5,bb.note)        
#         
#         qf = Q(operation=CLOSING) & Q(date__lte=to_datetime) & Q(date__gte=from_datetime) 
#         for rowx, bb in enumerate(EntranceBalance.objects.filter(qf).order_by('date'), start=1):
#             data = get_entrance_summary(bb)
#             parent = EntranceBalance.objects.get_parent_o(bb)
#             sheet.write(rowx, 0, data['date'], xlwt.easyxf(num_format_str='dd/mm/yyyy') )
#             sheet.write(rowx, 1, data['opening_amount'])
#             if parent:
#                 sheet.write(rowx, 2, data['wi'])
#                 sheet.write(rowx, 3, data['de'])
#                 sheet.write(rowx, 4, data['pa'])        
#                 #sheet.write(rowx, 2, BarBalance.objects.get_withdraws_for(parent))
#                 #sheet.write(rowx, 3, BarBalance.objects.get_deposits_for(parent))
#                 #sheet.write(rowx, 4, BarBalance.objects.get_payments_for(parent))
#             sheet.write(rowx, 5, data['closing_amount'])
#             sheet.write(rowx, 6, str(data['cashier']))
#             sheet.write(rowx, 7, data['notes'],note_style)
#             sheet.write(rowx, 8, data['receipt_count'])
#             # excel rows start from one
#             if rowx != 1:
#                 sheet.write(rowx, 9, xlwt.Formula('B%d-F%d' % (rowx+1, rowx-1+1))) #check1
#             sheet.write(rowx, 10, xlwt.Formula('L%d+M%d-I%d' % (rowx+1, rowx+1, rowx+1))) #check2
#             sheet.write(rowx, 11, xlwt.Formula('F%d-B%d' % (rowx+1, rowx+1))) #ricavi
#             sheet.write(rowx, 12, xlwt.Formula('E%d+C%d-D%d' % (rowx+1, rowx+1, rowx+1))) #costi
#             sheet.write(rowx, 13, xlwt.Formula('L%d-M%d' % (rowx+1, rowx+1))) #risultato
# 
#     elif what == 'interregno':
# 
# 
#         summary_headers = ['data', 'punto di cassa precedente', 'prelevati', 'depositati', 'pagamenti', 'cassiere', 'note', 'totale ricevute','atteso','punto di cassa', 'controllo cassa']
#         for i in range(0, len(summary_headers)):
#             sheet.write(0, i, summary_headers[i], header_style)
#         tall_style = xlwt.easyxf('font:height 720;') # 36pt
#         sheet.row(0).set_style(tall_style)
# 
#         list_headers = ['data','operazione','tipo','somma','cassiere','note']
#         for i in range(0, len(list_headers)):
#             list_sheet.write(0, i, list_headers[i], header_style)
#         list_sheet.row(0).set_style(tall_style)    
# 
#         qf = Q(date__lte=to_datetime) & Q(date__gte=from_datetime)
#         for rowx, bb in  enumerate(SmallBalance.objects.filter(qf).order_by('date'), start=1):
#             list_sheet.write(rowx,0,str(bb.date))
#             list_sheet.write(rowx,1,bb.get_operation_display())
#             if bb.operation == PAYMENT:            
#                 list_sheet.write(rowx,2,get_payment_display(bb.subtype))
#             elif bb.operation == DEPOSIT:
#                 list_sheet.write(rowx,2,get_deposit_display(bb.subtype))        
#             list_sheet.write(rowx,3,bb.amount)
#             list_sheet.write(rowx,4,str(bb.cashier))
#             list_sheet.write(rowx,5,bb.note)        
#         
#         qf = Q(operation=CASHPOINT) & Q(date__lte=to_datetime) & Q(date__gte=from_datetime) 
#         for rowx, bb in enumerate(SmallBalance.objects.filter(qf).order_by('date'), start=1):
#             data = get_small_summary(bb)
#             #parent = SmallBalance.objects.get_parent_o(bb)
# 
#             sheet.write(rowx, 0, data['date'], xlwt.easyxf(num_format_str='dd/mm/yyyy') )
#             sheet.write(rowx, 1, data['last_checkpoint'])
#             sheet.write(rowx, 2, data['wi'])
#             sheet.write(rowx, 3, data['de'])
#             sheet.write(rowx, 4, data['pa'])        
#                 #sheet.write(rowx, 2, BarBalance.objects.get_withdraws_for(parent))
#                 #sheet.write(rowx, 3, BarBalance.objects.get_deposits_for(parent))
#                 #sheet.write(rowx, 4, BarBalance.objects.get_payments_for(parent))
#             sheet.write(rowx, 5, str(data['cashier']))
#             sheet.write(rowx, 6, data['notes'],note_style)
#             sheet.write(rowx, 7, data['receipt_count'])
#             sheet.write(rowx, 8, data['expected_checkpoint'])
#             sheet.write(rowx, 9, data['checkpoint'])
#             sheet.write(rowx, 10, data['check'])
#     else:
#         raise Http404
#             
#     book.save(response)
#     return response

#def reports(request):
#    return render_to_response('base/reports.html', {} , context_instance=RequestContext(request))


#def make_balance(request):
#    return HttpResponse("make_balance")

def daily_stats(request):
    return HttpResponse("daily_stats")
