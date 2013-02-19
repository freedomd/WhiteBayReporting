from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import csv
from trades.models import Trade
from reports.models import Report
from datetime import date
from django.db.models import Q
from reports.logic import newReport

@login_required
def tradeView(request):
    #trade_list = Trade.objects.order_by('tradeDate', 'executionId').all()
    today = date.today()
    #print today.day
    trade_list = Trade.objects.filter(Q(tradeDate__year=today.year) & Q(tradeDate__month=today.month) & Q(tradeDate__day=today.day)).order_by('id')
    #trade_list = Trade.objects.filter(Q(tradeDate__year=today.year) & Q(tradeDate__month=2) & Q(tradeDate__day=13)).order_by('id')
    if len(trade_list) == 0:
        error = True
        error_message = "No trades yet today."
    return render(request,"trades_view.html", locals())

@login_required
def documentView(request):
    return render(request,"documents_view.html", locals())

@login_required
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
            print e.message
            return HttpResponseRedirect("/trade/")

    return HttpResponseRedirect("/trade/")

@login_required
def uploadMarks(request):
    today = date.today()
    
    if request.POST:
        try:
            file = request.FILES['content']
            count = 1
            for row in csv.reader(file.read().splitlines(), delimiter=','):
                if count != 1: # Ignore the header row
                    new_report = newReport(row[0]) # create new report for today
                    new_report.closing = row[1]
                    new_report.save()
                else:
                    count += 1
                
        except Exception, e:
            print e.message
            return HttpResponseRedirect("/")

    return HttpResponseRedirect("/")