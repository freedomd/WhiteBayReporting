from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from reports.models import Report
from datetime import date
from django.db.models import Q
import datetime
from reports.logic import *

def reportView(request):
    today = date.today()
    delta = datetime.timedelta(days=1)
    yesterday = today - delta
    
    print today
    print yesterday
    
    report_list = Report.objects.filter(Q(reportDate__year=today.year) & Q(reportDate__month=today.month) & Q(reportDate__day=today.day))
    if report_list == None:
        report_list = Report.objects.filter(Q(reportDate__year=yesterday.year) & Q(reportDate__month=yesterday.month) & Q(reportDate__day=yesterday.day))
        report_date = yesterday
    else:
        report_date = today
    total = report_list.get(symbol="Total")
    report_list = report_list.exclude(symbol="Total")
    
    return render(request,"reports_view.html", locals())
