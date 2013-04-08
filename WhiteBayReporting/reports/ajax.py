from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from reports.models import Report
from django.db.models import Q
from django.core import serializers
from datetime import date
from settings import PER_PAGE

@dajaxice_register
def sayhello(request):
    print "!"
    return simplejson.dumps({'message':'Hello World'})


@dajaxice_register
def getReportList(request, tab, strorder, year, month, day, strpage):
    # order 0 = ascending, 1 = descending
    order = int(strorder)
    if tab == None or strorder == None:
        tab = "symbol"
        order = 0
    if order != 0 and order != 1:
        order = 0
    
    if year == None or month == None or day == None:
        today = date.today()
        year = today.year
        month = today.month
        day = today.day
    
    mypage = int(strpage)
    if strpage == None:
        mypage = 1
    
    start = (mypage - 1) * PER_PAGE
    end = mypage * PER_PAGE
    
    # check tab
    if order == 0:
        method = tab
    else:
        method = "-" + tab
        
    report_list = Report.objects.filter(Q(reportDate__year=year) & Q(reportDate__month=month) & Q(reportDate__day=day)).order_by(method)[start:end]
    count = report_list.count()
    
    if count != 0:
        if count == PER_PAGE:
            np = mypage + 1
        else:
            np = 0
        if mypage == 1:
            pp = 0
        else:
            pp = mypage - 1
    else:
        if mypage != 1:
            start = (mypage - 2) * PER_PAGE
            end = (mypage - 1) * PER_PAGE
            report_list = Report.objects.filter(Q(reportDate__year=year) & Q(reportDate__month=month) & Q(reportDate__day=day)).order_by(method)[start:end]

        
    report_list_serialized = serializers.serialize('json', report_list)
    data = { 'report_list': simplejson.loads(report_list_serialized), 
             'pp': pp,
             'np': np }
    
    return simplejson.dumps(data)

@dajaxice_register
def queryReportList(request, tab, strorder, symbol, datefrom, dateto, strpage):

    # order 0 = ascending, 1 = descending
    order = int(strorder)
    if tab == None or strorder == None:
        tab = "symbol"
        order = 0
    if order != 0 and order != 1:
        order = 0
    
    mypage = int(strpage)
    if strpage == None:
        mypage = 1
    
    start = (mypage - 1) * PER_PAGE
    end = mypage * PER_PAGE
    
    # check tab
    if order == 0:
        method = tab
    else:
        method = "-" + tab
    
    # start filter
    report_list = None
    if symbol is not u"" or None:
        if report_list is None:
            report_list = Report.objects.filter(Q(symbol=symbol))
        else:
            report_list = report_list.filter(Q(symbol=symbol))

    if datefrom is not u"" or None:
        if report_list is None:
            report_list = Report.objects.filter(Q(reportDate__gte=datefrom))
        else:
            report_list = report_list.filter(Q(reportDate__gte=datefrom))
    
    if dateto is not u"" or None:
        if report_list is None:
            report_list = Report.objects.filter(Q(reportDate__lte=dateto))
        else:
            report_list = report_list.filter(Q(reportDate__lte=dateto))
    
    if method != "reportDate" and method != "-reportDate":
        report_list = report_list.order_by(method, "reportDate")[start:end]
    else:
        report_list = report_list.order_by(method, "symbol")[start:end]
    count = report_list.count()
    
    if count == PER_PAGE:
        np = mypage + 1
    else:
        np = 0
    if mypage == 1:
        pp = 0
    else:
        pp = mypage - 1
        
    report_list_serialized = serializers.serialize('json', report_list)
    data = { 'report_list': simplejson.loads(report_list_serialized), 
             'pp': pp,
             'np': np }
    
    return simplejson.dumps(data)
