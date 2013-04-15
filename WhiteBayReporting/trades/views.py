from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
import csv
from trades.models import Trade
from reports.models import Report
from datetime import date
from django.db.models import Q
from reports.logic import newReport
from settings import PER_PAGE

@login_required
def tradeQueryView(request):
    message = "Please type in a query."            
    return render(request,"trade_query_view.html", locals())

@login_required
def tradeView(request, strpage):
    today = date.today()
    
    mypage = int(strpage)
    if strpage == None:
        mypage = 1
        
    start = (mypage - 1) * PER_PAGE
    end = mypage * PER_PAGE
    
    trade_list = Trade.objects.filter(Q(tradeDate__year=today.year) & Q(tradeDate__month=today.month) & Q(tradeDate__day=today.day))[start:end]
    count = trade_list.count()
    if count == 0:
        if  mypage == 1:
            error = True
            error_message = "No trades yet today."
        else:
            url="/trade/%s/"%(str(mypage-1))
            return HttpResponseRedirect(url)
    else:
        if count == PER_PAGE:
            nextPage = True
            np = mypage + 1
        else:
            nextPage = False
        if  mypage == 1:
            previousPage = False
        else:
            previousPage = True
            pp = mypage - 1
            
    return render(request,"trades_view.html", locals())

@login_required
def symbolView(request, account, symbol, year, month, day, strpage):
    
    if symbol == None:
        return HttpResponseRedirect("/report/")
    
    # get latest reports
    if year == None or month == None or day == None:
        today = date.today()
        year = today.year
        month = today.month
        day = today.day
    
    mypage = int(strpage)
    if strpage == None:
        mypage = 1
    
    start = (mypage - 1) * PER_PAGE
    end = mypage * PER_PAGE - 1
    
    reportDate = date(int(year), int(month), int(day))
    today = date.today()
    trade_list = Trade.objects.filter(Q(account=account) & Q(symbol=symbol) & Q(tradeDate__year=year) & 
                                      Q(tradeDate__month=month) & Q(tradeDate__day=day))[start:end]
    count = trade_list.count()
                                    
    if count == 0:
        if mypage == 1:
            error = True
            error_message = "No trades of symbol %s." % symbol
        else:
            url="/symbol/%s/%s/%s/%s/%s/"%(account, year, month, day, str(mypage-1))
            return HttpResponseRedirect(url)
    else:
        if count == PER_PAGE:
            nextPage = True
            np = mypage + 1
        else:
            nextPage = False
        if  mypage == 1:
            previousPage = False
        else:
            previousPage = True
            pp = mypage - 1
            
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