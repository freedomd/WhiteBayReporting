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
    
#    try:
#        report_list = Report.objects.filter(Q(reportDate__year=today.year) & Q(reportDate__month=today.month) & Q(reportDate__day=today.day))
#        if report_list == None:
#            report_list = Report.objects.filter(Q(reportDate__year=yesterday.year) & Q(reportDate__month=yesterday.month) & Q(reportDate__day=yesterday.day))
#            report_date = yesterday
#        else:
#            report_date = today
#        total = report_list.get(symbol="Total")
#        report_list = report_list.exclude(symbol="Total")
#    except:
#        return HttpResponseRedirect("/")
    
    # get latest reports
    try:
        report_list = Report.objects.all().order_by('-reportDate')
        if report_list != None:
            report_date = report_list[0].reportDate
            report_list = Report.objects.filter(Q(reportDate__year=report_date.year) & Q(reportDate__month=report_date.month) & Q(reportDate__day=report_date.day))
        else:
            error = True
            error_message = "No reports yet."
            return render(request,"reports_view.html", locals())
        total = report_list.get(symbol="Total")
        report_list = report_list.exclude(symbol="Total")
    except Exception, e:
        error = True
        error_message = str(e.message)
        return render(request,"reports_view.html", locals())
    
    return render(request,"reports_view.html", locals())
