from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from reports.models import Report
from datetime import date
from django.db.models import Q
import datetime
from reports.logic import *

def reportView(request):
    today = date.today()
    
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
        try:
            total = report_list.get(symbol="Total")
            report_list = report_list.exclude(symbol="Total")
        except: # no today's new report
            error = True
            error_message = "No reports yet."
            return render(request,"reports_view.html", locals())
    except Exception, e:
        error = True
        error_message = str(e.message)
        return render(request,"reports_view.html", locals())
    
    return render(request,"reports_view.html", locals())
