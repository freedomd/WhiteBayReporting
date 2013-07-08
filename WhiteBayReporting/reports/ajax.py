import csv
import os
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from reports.models import Report
from django.db.models import Q
from django.core import serializers
from datetime import date
from settings import PER_PAGE
from reports.logic import getSummary
from email_sender import EmailSender
from admins.models import Account

@dajaxice_register
def sayhello(request):
    print "!"
    return simplejson.dumps({'message':'Hello World'})


@dajaxice_register
def getReportList(request, tab, strorder, account, year, month, day, strpage):
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
        
    report_list = Report.objects.filter(Q(account=account) & Q(reportDate__year=year) & Q(reportDate__month=month) & Q(reportDate__day=day)).order_by(method)[start:end]
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
            report_list = Report.objects.filter(Q(account=account) & Q(reportDate__year=year) & Q(reportDate__month=month) & Q(reportDate__day=day)).order_by(method)[start:end]

        
    report_list_serialized = serializers.serialize('json', report_list)
    data = { 'report_list': simplejson.loads(report_list_serialized), 
             'pp': pp,
             'np': np }
    
    return simplejson.dumps(data)

@dajaxice_register
def queryReportList(request, tab, strorder, account, symbol, datefrom, dateto, strpage):

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
    if account is not u"" or None:
        if report_list is None:
            report_list = Report.objects.filter(Q(account__icontains=account))
        else:
            report_list = report_list.filter(Q(account__icontains=account))
    
    if symbol is not u"" or None:
        if report_list is None:
            report_list = Report.objects.filter(Q(symbol__icontains=symbol))
        else:
            report_list = report_list.filter(Q(symbol__icontains=symbol))

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


@dajaxice_register
def getSummaryReport(request, account, symbol, datefrom, dateto, user_email):
    
    # start filter
    report_list = None
    filename = ""
    content = "" #email content
    
    if account is not u"" or None:
        filename += account + "_"
        content += "Account: " + account + "\n"
        if report_list is None:
            report_list = Report.objects.filter(Q(account__icontains=account))
        else:
            report_list = report_list.filter(Q(account__icontains=account))
    
    if symbol is not u"" or None:
        filename += symbol + "_"
        content += symbol + " "
        if report_list is None:
            report_list = Report.objects.filter(Q(symbol=symbol))
        else:
            report_list = report_list.filter(Q(symbol=symbol))
    
    content += "Summary Report:\n"

    if datefrom is not u"" or None:
        filename += "%s_" % datefrom.replace("-", "")
        content += "from %s\n" % datefrom
        if report_list is None:
            report_list = Report.objects.filter(Q(reportDate__gte=datefrom))
        else:
            report_list = report_list.filter(Q(reportDate__gte=datefrom))
    
    if dateto is not u"" or None:
        filename += "%s_" % dateto.replace("-", "")
        content += "to %s\n" % dateto
        if report_list is None:
            report_list = Report.objects.filter(Q(reportDate__lte=dateto))
        else:
            report_list = report_list.filter(Q(reportDate__lte=dateto))
    
    if report_list != None:
        filename += "SUMM.csv"
        filepath = "./temp/" + filename 
        with open(filepath, 'wb') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(['Symbol', 'SOD', 'Buys', 'BuyAve', 'Sells', 'SellAve', 'EOD',
                             'GrossPNL', 'UnrealizedPNL', 'Commission', 'SEC Fees', 'ECN Fees', 'Net PNL'])
            
            summary_list = getSummary(report_list.order_by("reportDate"))
            
            for summary in summary_list:
                report = summary_list[summary]
                writer.writerow([report.symbol, report.SOD,
                                 report.buys, round(report.buyAve, 2), 
                                 report.sells, round(report.sellAve, 2), report.EOD,
                                 round(report.grossPNL, 2), round(report.unrealizedPNL, 2), 
                                 round(report.commission, 2), round(report.secFees, 2), round(report.ecnFees, 2), 
                                 round(report.netPNL, 2)])
        
        es = EmailSender()
        success, message = es.send_email(filename, content, user_email, filepath)
        if success:
            message = "Summary report will be sent to <i><strong>%s</strong></i>." % user_email 
        os.remove(filepath)
    else:
        message = "No match reports."
        
    data = { 'message': message }
    
    return simplejson.dumps(data)


@dajaxice_register
def getAccountList(request, group, tab, strorder):

    # order 0 = ascending, 1 = descending
    order = int(strorder)
    if tab == None or strorder == None:
        tab = "account"
        order = 0
    if order != 0 and order != 1:
        order = 0
    
    # check tab
    if order == 0:
        method = tab
    else:
        method = "-" + tab
    
        
    if  group == "":
        account_list = Account.objects.all().order_by(method)
    else:
        account_list = Account.objects.filter(group=group).order_by(method)
    
    total = Account()
    for account in account_list:
        total.grossPNL += account.grossPNL
        total.unrealizedPNL += account.unrealizedPNL
        total.netPNL += account.netPNL
    
        total.commission += account.commission
        total.secFees += account.secFees
        total.ecnFees += account.ecnFees
        total.accruedSecFees += account.accruedSecFees
        
    account_list_serialized = serializers.serialize('json', account_list)
    data = { 'account_list': simplejson.loads(account_list_serialized),
             'total_grossPNL': total.grossPNL,
             'total_unrealizedPNL': total.unrealizedPNL,
             'total_commission': total.commission,
             'total_secFees': total.secFees,
             'total_accruedSecFees': total.accruedSecFees,
             'total_ecnFees': total.ecnFees,
             'total_netPNL': total.netPNL }

    return simplejson.dumps(data)