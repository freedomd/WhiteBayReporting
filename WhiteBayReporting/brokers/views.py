from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import date
from brokers.models import Broker

@login_required
def adminView(request):
    if request.GET:
        message = request.GET.get('message')
    broker_list = Broker.objects.all().order_by("name")          
    return render(request,"admin_view.html", locals())

@login_required
def addBroker(request):
    if request.POST:
        name = request.POST.get('add_name')
        commission = request.POST.get('add_commission')

        try:
            Broker.objects.create(name = name, commission = commission)
        except Exception, e:
            print str(e.message)
    
    return HttpResponseRedirect("/management/")

@login_required
def delBroker(request):
    if request.POST:
        pk = request.POST.get('mod_pk')

        try:
            Broker.objects.get(pk = pk).delete()
        except Exception, e:
            print str(e.message)
    
    return HttpResponseRedirect("/management/")


