from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from reports.models import Report, getCacheReportApi
from datetime import date
from django.db.models import Q
import datetime
from reports.logic import *
from admins.models import Group


@login_required
def reportView(request, account):
    today=date.today()
    url="/monthlyReport/%s/%s/%s/"%(account, str(today.year), str(today.month))
    return HttpResponseRedirect(url)

@login_required
def reportQueryView(request):
    default = "symbol" # default order
    default_order = 0 # ascending, 1 for descending
    user_email = request.user.email    
    return render(request,"report_query_view.html", locals())

@login_required
def firmReportView(request):
    default = "account" # default order
    default_order = 0 # ascending, 1 for descending
    group_list = Group.objects.all().order_by("name")   
    return render(request,"firm_report_view.html", locals())

@login_required
def monthlyReportView(request, account, year, month):
    
    # get latest reports
    today = date.today()
    if year == None or month == None:
        year = today.year
        month = today.month
    
    year = int(year)
    month = int(month)
    
    reportDate = date(int(year), int(month), 1)
    
    if year < today.year: # reports for next year
        nextYear = year + 1
        nextURL = "/monthlyReport/%s/%s/1/"%(account, str(nextYear))
        
    tmp = MonthlyReport.objects.filter(Q(reportDate__year=year-1))
    if tmp.count() > 0: # reports for previous year
        prevYear = year - 1
        prevURL = "/monthlyReport/%s/%s/12/"%(account, str(prevYear))
    
    try:
        monthly_report_list = MonthlyReport.objects.filter(Q(account=account) & Q(reportDate__year=year)).order_by('reportDate')
        if monthly_report_list.count() == 0:
            year_error = True
            error_message = "No reports for year %s." % str(year)
            return render(request,"monthly_reports_view.html", locals())
        
        report_list = DailyReport.objects.filter(Q(account=account) & Q(reportDate__year=year) & Q(reportDate__month=month)).order_by('reportDate')
        if report_list.count() != 0:
            report_date = report_list[0].reportDate
        else:
            month_error = True
            error_message = "No reports for %s-%s." % (str(year), str(month))
            return render(request,"monthly_reports_view.html", locals())
        try:
            total = MonthlyReport.objects.get(Q(account=account) & Q(reportDate__year=year) & Q(reportDate__month=month))
        except: # no this month's new report
            month_error = True
            error_message = "No reports for %s-%s." % (str(year), str(month))
            return render(request,"monthly_reports_view.html", locals())
            
    except Exception, e:
        year_error = True
        print
        error_message = str(e.message)
        return render(request,"monthly_reports_view.html", locals())
    
    return render(request,"monthly_reports_view.html", locals())

@login_required
def dailyReportViewAjax(request, account, year, month, day):
    default = "symbol" # default order
    default_order = 0 # ascending, 1 for descending
    reportDate = date(int(year), int(month), int(day))
    return render(request,"daily_reports_view_ajax.html", locals())
