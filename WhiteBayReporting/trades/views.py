from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import csv
from trades.models import Trade
from datetime import date
from django.db.models import Q

def home(request):
    trade_list = Trade.objects.order_by('tradeDate').all()
    #today = date.today()
    #print today.day
    #trade_list = Trade.objects.filter(Q(date_published__year=today.year) & Q(date_published__month=today.month) & Q(date_published__day=today.day))
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
            print str(e.message)
            return HttpResponseRedirect("/")

    return HttpResponseRedirect("/")