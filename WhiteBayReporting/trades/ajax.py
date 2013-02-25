from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from trades.models import Trade
from django.core import serializers
from django.db.models import Q
from datetime import datetime, date, timedelta
from settings import PER_PAGE

@dajaxice_register
def tradeQuery(request, account, symbol, datefrom, dateto, strpage):
    
    mypage = int(strpage)
    
    if strpage == None:
        mypage = 1
        
    start = (mypage - 1) * PER_PAGE
    end = mypage * PER_PAGE
    
    trade_list = None    
    # start filter
    if account is not u"" or None:
        trade_list = Trade.objects.filter(Q(account=account))
    
    if symbol is not u"" or None:
        if trade_list is None:
            trade_list = Trade.objects.filter(Q(symbol=symbol))
        else:
            trade_list = trade_list.filter(Q(symbol=symbol))

    if datefrom is not u"" or None:
        if trade_list is None:
            trade_list = Trade.objects.filter(Q(tradeDate__gte=datefrom))
        else:
            trade_list = trade_list.filter(Q(tradeDate__gte=datefrom))
    
    if dateto is not u"" or None:
        if trade_list is None:
            trade_list = Trade.objects.filter(Q(tradeDate__lte=dateto))
        else:
            trade_list = trade_list.filter(Q(tradeDate__lte=dateto))
    
    trade_list = trade_list[start:end]
    count = trade_list.count()

    if count == PER_PAGE:
        np = mypage + 1
    else:
        np = 0
    if  mypage == 1:
        pp = 0
    else:
        pp = mypage - 1
    
    trade_list_serialized = serializers.serialize('json', trade_list)
    data = { 'trade_list': simplejson.loads(trade_list_serialized), 
             'pp': pp,
             'np': np }
    
    #print data
    
    return simplejson.dumps(data)