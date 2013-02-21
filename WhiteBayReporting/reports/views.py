from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from reports.models import Report
from datetime import date
from django.db.models import Q
import datetime
from reports.logic import *
from settings import PER_PAGE

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
def dailyReportView(request, year, month, day, strpage):
    
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
    
    # get latest reports
    try:
        report_list = Report.objects.filter(Q(reportDate__year=year) & Q(reportDate__month=month) & Q(reportDate__day=day)).order_by("symbol")[start:end]
        count = report_list.count()
        if count != 0:
            report_date = report_list[0].reportDate
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
                url="/dailyReport/%s/%s/%s/%s/"%(str(today.year), str(today.month), str(today.day), str(mypage-1))
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