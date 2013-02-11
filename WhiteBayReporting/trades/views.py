from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import csv
from trades.models import Trade
from reports.models import Report
from datetime import date
from django.db.models import Q

def home(request):
    #trade_list = Trade.objects.order_by('tradeDate', 'executionId').all()
    today = date.today()
    #print today.day
    trade_list = Trade.objects.filter(Q(tradeDate__year=today.year) & Q(tradeDate__month=today.month) & Q(tradeDate__day=today.day)).order_by('tradeDate', 'executionId')
    if len(trade_list) == 0:
        error = True
        error_message = "No trades yet."
    return render(request,"trades_view.html", locals())


def upload(request):
    if request.POST:
        try:
            file = request.FILES['content']
            count = 1
            for row in csv.reader(file.read().splitlines(), delimiter=','):
                if count != 1: # Ignore the header row
                    try:
                        Trade.objects.get( executionId = row[8] ) # ignore existed trade, identify by execution id
                    except Trade.DoesNotExist:
                        trade = Trade()
                        trade.account = row[0]
                        trade.symbol = row[1]
                        trade.side= row[2]
                        trade.quantity = row[3]
                        trade.price = row[4]
                        trade.broker = row[5]
                        trade.tradeDate = row[6]
                        trade.exchange = row[7]
                        trade.executionId = row[8]
                        trade.save()
                else:
                    count += 1
                
        except Exception, e:
            error = True
            error_message = str(e.message)
            return render(request,"trades_view.html", locals())

    return HttpResponseRedirect("/")

def uploadMarks(request):
    today = date.today()
    
    if request.POST:
        try:
            file = request.FILES['content']
            count = 1
            for row in csv.reader(file.read().splitlines(), delimiter=','):
                if count != 1: # Ignore the header row
                    try:
                        report = Report.objects.get(Q(symbol=row[0]) & Q(reportDate__year=today.year) & 
                                                        Q(reportDate__month=today.month) & Q(reportDate__day=today.day))
                        report.mark = row[1]
                        report.save()
                    except Report.DoesNotExist:
                        new_report = Report()
                        new_report.symbol = row[0]
                        new_report.mark = row[1]
                        new_report.reportDate = today
                        new_report.save()
                        
                else:
                    count += 1
                
        except Exception, e:
            error = True
            error_message = str(e.message)
            return render(request,"trades_view.html", locals())

    return HttpResponseRedirect("/")