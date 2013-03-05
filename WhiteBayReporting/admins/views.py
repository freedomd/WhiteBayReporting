from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from datetime import date
from admins.models import Broker, Trader, System

@login_required
def adminView(request):
    if request.GET:
        message = request.GET.get('message')

@login_required
def firmView(request):
    if request.GET:
        message = request.GET.get('message')
    broker_list = Broker.objects.all().order_by("name")          
    return render(request,"firm_view.html", locals())

@login_required
def traderView(request):
    trader_list = Trader.objects.all().order_by("name")  
    system_list = System.objects.all().order_by("name")
    return render(request,"trader_view.html", locals())

@login_required
def systemView(request):  
    system_list = System.objects.all().order_by("name")
    return render(request,"system_view.html", locals())

@login_required
def addBroker(request):
    if request.POST:
        name = request.POST.get('add_name')
        commission = request.POST.get('add_commission')

        try:
            Broker.objects.create(name = name, commission = commission)
        except Exception, e:
            print str(e.message)
    
    return HttpResponseRedirect("/firmProfile/")

@login_required
def modBroker(request):
    if request.POST:
        save = request.POST.get('save')
        delete = request.POST.get('delete')
        pk = request.POST.get('mod_pk')
        
        try:
            broker = Broker.objects.get(pk = pk)
            if delete:
                broker.delete()
            elif save:
                name = request.POST.get('mod_name')
                commission = request.POST.get('mod_commission')
                broker.name = name
                broker.commission = commission
                broker.save()
        except Exception, e:
            print str(e.message)

    return HttpResponseRedirect("/firmProfile/")


@login_required
def addTrader(request):
    if request.POST:
        name = request.POST.get('add_name')
        ssn = request.POST.get('add_ssn')
        addr = request.POST.get('add_addr')
        phone = request.POST.get('add_phone')
        email = request.POST.get('add_email')
        username = request.POST.get('add_username')
        password = request.POST.get('add_password')
        cfee = request.POST.get('add_cfee')
        bfee = request.POST.get('add_bfee')
        systems = request.POST.getlist('systems')
        
        if cfee == "" or cfee == None:
            cfee = 0.0
        if bfee == "" or bfee == None:
            bfee = 0.0

        try:
            trader = Trader.objects.create(name = name, SSN = ssn, addr = addr, phone = phone,
                                           email = email, username = username, password = password, 
                                           clearanceFee = cfee, brokerFee = bfee)
            
            for system in systems:
                try:
                    trader.systems.add(System.objects.get(pk=system))
                except Exception, e:
                    print str(e.message)
                    continue
            
            trader.save()
            
        except Exception, e:
            print str(e.message)
    
    return HttpResponseRedirect("/traderProfile/")

@login_required
def modTrader(request):
    if request.POST:
        save = request.POST.get('save')
        delete = request.POST.get('delete')
        pk = request.POST.get('mod_pk')
        
        try:
            trader = Trader.objects.get(pk = pk)
            if delete:
                trader.delete()
            elif save:
                name = request.POST.get('mod_name')
                ssn = request.POST.get('mod_ssn')
                addr = request.POST.get('mod_addr')
                phone = request.POST.get('mod_phone')
                email = request.POST.get('mod_email')
                username = request.POST.get('mod_username')
                password = request.POST.get('mod_password')
                cfee = request.POST.get('mod_cfee')
                bfee = request.POST.get('mod_bfee')
                systems = request.POST.getlist('systems')
                
                if cfee == "" or cfee == None:
                    cfee = 0.0
                if bfee == "" or bfee == None:
                    bfee = 0.0
                
                trader.name = name
                trader.SSN = ssn
                trader.addr = addr
                trader.phone = phone
                trader.email = email
                trader.username = username
                trader.password = password
                trader.clearanceFee = cfee
                trader.brokerFee = bfee
                trader.systems.clear()
                for system in systems:
                    try:
                        trader.systems.add(System.objects.get(pk=system))
                    except:
                        continue
                    
                trader.save()
        except Exception, e:
            print str(e.message)

    return HttpResponseRedirect("/traderProfile/")

@login_required
def addSystem(request):
    if request.POST:
        name = request.POST.get('name')
        cost = request.POST.get('cost')

        try:
            System.objects.create(name = name, cost = cost)
        except Exception, e:
            print str(e.message)
    
    return HttpResponseRedirect("/systemProfile/")

@login_required
def modSystem(request):
    if request.POST:
        save = request.POST.get('save')
        delete = request.POST.get('delete')
        pk = request.POST.get('pk')
        
        try:
            system = System.objects.get(pk = pk)
            if delete:
                system.delete()
            elif save:
                name = request.POST.get('name')
                cost = request.POST.get('cost')
                system.name = name
                system.cost = cost
                system.save()
        except Exception, e:
            print str(e.message)

    return HttpResponseRedirect("/systemProfile/")

