from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from reports.models import Report, getCacheReportApi
from datetime import date
from django.db.models import Q
import datetime
from reports.logic import *
from settings import PER_PAGE
from operator import attrgetter

@login_required
def reportView(request):
    today=date.today()
    url="/monthlyReport/%s/%s/"%(str(today.year), str(today.month))
    return HttpResponseRedirect(url)

@login_required
def monthlyReportView(request, year, month):
    
    # get latest reports
    if year == None or month == None:
        today = date.today()
        year = today.year
        month = today.month
    
    try:
        monthly_report_list = MonthlyReport.objects.filter(Q(reportDate__year=year))
        report_list = DailyReport.objects.filter(Q(reportDate__year=year) & Q(reportDate__month=month)).order_by('reportDate')
        if report_list.count() != 0:
            report_date = report_list[0].reportDate
        else:
            error = True
            error_message = "No reports for this month yet."
            return render(request,"monthly_reports_view.html", locals())
        try:
            total = MonthlyReport.objects.get(Q(reportDate__year=year) & Q(reportDate__month=month))
        except: # no this month's new report
            error = True
            error_message = "No reports for this month yet."
            return render(request,"monthly_reports_view.html", locals())
    except Exception, e:
        error = True
        error_message = str(e.message)
        return render(request,"monthly_reports_view.html", locals())
    
    return render(request,"monthly_reports_view.html", locals())

@login_required
def dailyReportView(request, tab, strorder, year, month, day, strpage):
    
    # method 0 = ascending, 1 = descending
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
    
    # order for each tab
    SY, SO, MA, BS, BA, SS, SA, GP, UP, FS, NP, LM, SM, EO, CL = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    new_order = (order + 1) % 2
    if tab == "symbol":
        SY = new_order
    elif tab == "SOD":
        SO = new_order
    elif tab == "mark":
        MA = new_order
    elif tab == "buys":
        BS = new_order
    elif tab == "buyAve":
        BA = new_order
    elif tab == "sells":
        SS = new_order
    elif tab == "sellAve":
        SA = new_order
    elif tab == "grossPNL":
        GP = new_order
    elif tab == "unrealizedPNL":
        UP = new_order
    elif tab == "fees":
        FS = new_order
    elif tab == "netPNL":
        NP = new_order
    elif tab == "LMV":
        LM = new_order
    elif tab == "SMV":
        SM = new_order
    elif tab == "EOD":
        EO = new_order
    elif tab == "closing":
        CL = new_order
    else: # error tab
        tab = "symbol"
        SY = new_order
    
    
    # get latest reports
    try:
        
        # check tab
        if order == 0:
            method = tab
        else:
            method = "-" + tab
        
        # get reports from cache
#        api = getCacheReportApi()
#        report_list = api.getReportsByDate(date(year=int(year), month=int(month), day=int(day)))[start:end]
#        count = len(report_list)
#        print count
        
        report_list = Report.objects.filter(Q(reportDate__year=year) & Q(reportDate__month=month) & Q(reportDate__day=day)).order_by(method)[start:end]
        count = report_list.count()
        if count != 0:
            #report_date = report_list[0].reportDate
            if count == PER_PAGE:
                nextPage = True
                np = mypage + 1
            else:
                nextPage = False
            if mypage == 1:
                previousPage = False
            else:
                previousPage = True
                pp = mypage - 1
        else:
            if mypage == 1:
                error = True
                error_message = "No reports for %s-%s-%s." % (str(year), str(month), str(day)) 
                return render(request,"daily_reports_view.html", locals())
            else:
                url="/dailyReport/symbol/0/%s/%s/%s/%s/"%(str(today.year), str(today.month), str(today.day), str(mypage-1))
                return HttpResponseRedirect(url)
#        try:
#            total = DailyReport.objects.get(Q(reportDate__year=year) & Q(reportDate__month=month) & Q(reportDate__day=day))
#        except: # no this day's summary report
#            error = True
#            error_message = "No reports for %s-%s-%s." % (str(year), str(month), str(day)) 
#            return render(request,"daily_reports_view.html", locals())
    except Exception, e:
        error = True
        error_message = str(e.message)
        return render(request,"daily_reports_view.html", locals())

    return render(request,"daily_reports_view.html", locals())