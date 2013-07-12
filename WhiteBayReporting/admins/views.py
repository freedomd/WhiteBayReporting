from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from datetime import date
from admins.models import Broker, Trader, System, Firm, Employer, FutureFeeRate, FutureFeeGroup, Route, Account, Group
from settings import ERROR_LOG
from django.views.decorators.csrf import csrf_exempt

def navbar_settings(request):
    account_list = Account.objects.all().order_by("account")
    additions = {
        'account_list': account_list,
    }
    return additions

@login_required
def adminView(request):
    if request.GET:
        message = request.GET.get('message')

@login_required
def firmView(request):
    if request.GET:
        message = request.GET.get('message')
    firm = Firm.objects.all()[0]
    broker_list = Broker.objects.all().order_by("brokerNumber")          
    return render(request,"firm_view.html", locals())

@login_required
def traderView(request):
    pk = request.GET.get('pk')
    trader_list = Trader.objects.all().order_by("name")  
    system_list = System.objects.all().order_by("name")
    return render(request,"trader_view.html", locals())

@login_required
def employerView(request):
    pk = request.GET.get('pk')
    employer_list = Employer.objects.all().order_by("name")  
    return render(request,"employer_view.html", locals())

@login_required
def futureFeeRateView(request):
    pk = request.GET.get('pk')
    futureFeeRate_list = FutureFeeRate.objects.all().order_by("symbol")
    group_list = Group.objects.all().order_by("name")
    return render(request, "futureFeeRate_view.html", locals())

@login_required
def futureFeeGroupView(request):
    pk = request.GET.get('pk')
    account_list = Account.objects.all().order_by("account")  
    group_list = Group.objects.all().order_by("name")
    symbol_list = FutureFeeRate.objects.values("symbol").order_by("symbol").distinct()
    feeGroup_list = FutureFeeGroup.objects.all().order_by("symbol")
    return render(request, "futureFeeGroup_view.html", locals())

@login_required
def accountView(request):
    pk = request.GET.get('pk')
    account_list = Account.objects.all().order_by("account")  
    return render(request,"account_view.html", locals())

@login_required
def groupView(request):
    pk = request.GET.get('pk')
    group_list = Group.objects.all().order_by("name")  
    return render(request,"group_view.html", locals())

@login_required
def systemView(request):  
    system_list = System.objects.all().order_by("name")
    return render(request,"system_view.html", locals())

@login_required
def routeView(request):  
    route_list = Route.objects.all().order_by("seqNo")
    return render(request,"route_view.html", locals())

@login_required
def logView(request):  
    log = open(ERROR_LOG, "r")
    lines = []
    line = log.readline()
    while line:
        lines.append(line)
        line = log.readline()
   
    lines.reverse()
    lines = lines[1:20]

    log.close()
    return render(request,"log_view.html", locals())

@login_required
def addBroker(request):
    if request.POST:
        brokerNumber = request.POST.get('add_name')
        securityType = request.POST.get('add_type')
        commissionRate = request.POST.get('add_commission')

        try:
            broker = Broker.objects.create(brokerNumber = brokerNumber, securityType = securityType, 
                                           commissionRate = commissionRate)
            firm = Firm.objects.all()[0]
            firm.brokers.add(broker)
            firm.save()
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
                brokerNumber = request.POST.get('mod_name')
                securityType = request.POST.get('mod_type')
                commissionRate = request.POST.get('mod_commission')
                broker.brokerNumber = brokerNumber
                broker.securityType = securityType
                broker.commissionRate = commissionRate
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
                url = "/traderProfile/"
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
                url = "/traderProfile/?pk=" + str(pk)
        except Exception, e:
            print str(e.message)
            url = "/traderProfile/"

    return HttpResponseRedirect(url)

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

@login_required
def modFirm(request):
    if request.POST:
        try:
            firm = Firm.objects.get(pk=request.POST.get('pk'))
                        
            firm.equity = request.POST.get('equity')
            firm.DVP = request.POST.get('DVP')
            firm.options = request.POST.get('options')
            firm.H2B = request.POST.get('H2B')
            firm.secFee = request.POST.get('secFee')
            firm.rent = request.POST.get('rent')
            firm.technology = request.POST.get('technology')
            firm.save()
        except Exception, e:
            print str(e.message)

    return HttpResponseRedirect("/firmProfile/")

@login_required
def addEmployer(request):
    if request.POST:
        name = request.POST.get('add_name')
        
        try:
            Employer.objects.create(name = name)

        except Exception, e:
            print str(e.message)
    
    return HttpResponseRedirect("/employerProfile/")

@login_required
def modEmployer(request):
    if request.POST:
        save = request.POST.get('save')
        delete = request.POST.get('delete')
        pk = request.POST.get('mod_pk')
        
        try:
            employer = Employer.objects.get(pk = pk)
            if delete:
                employer.delete()
                url = "/employerProfile/"
            elif save:
                name = request.POST.get('mod_name')
                
                employer.name = name
                employer.save()
                url = "/employerProfile/?pk=" + str(pk)
        except Exception, e:
            print str(e.message)
            url = "/employerProfile/"

    return HttpResponseRedirect(url)

@login_required
def addFuture(request):
    if request.POST:
        symbol = request.POST.get('add_symbol')
        clearingFeeRate = request.POST.get('add_clearing')
        exchangeFeeRate = request.POST.get('add_exchange')
        nfaFeeRate = request.POST.get('add_nfa')
        group = request.POST.get('add_group')
        
        # avoid duplicate
        try:
            FutureFeeRate.objects.get(Q(symbol=symbol) & Q(clearingFeeRate=clearingFeeRate) & 
                                      Q(exchangeFeeRate = exchangeFeeRate) & Q(nfaFeeRate = nfaFeeRate) &
                                      Q(group = group))

        except FutureFeeRate.DoesNotExist:
            FutureFeeRate.objects.create(symbol = symbol, clearingFeeRate = clearingFeeRate, 
                                         exchangeFeeRate = exchangeFeeRate, nfaFeeRate = nfaFeeRate,
                                         group = group)
    
    return HttpResponseRedirect("/futureFeeRateProfile/")

@login_required
def modFuture(request):
    if request.POST:
        save = request.POST.get('save')
        delete = request.POST.get('delete')
        pk = request.POST.get('mod_pk')
        
        try:
            future = FutureFeeRate.objects.get(pk = pk)
            if delete:
                future.delete()
                url = "/futureFeeRateProfile/"
            elif save:
                symbol = request.POST.get('mod_symbol')
                clearingFeeRate = request.POST.get('mod_clearing')
                exchangeFeeRate = request.POST.get('mod_exchange')
                nfaFeeRate = request.POST.get('mod_nfa')
                group = request.POST.get('mod_group')
                
                future.symbol = symbol
                future.clearingFeeRate = clearingFeeRate
                future.exchangeFeeRate = exchangeFeeRate
                future.nfaFeeRate = nfaFeeRate
                future.group = group
                future.save()
                url = "/futureFeeRateProfile/?pk=" + str(pk)
        except Exception, e:
            print str(e.message)
            url = "/futureFeeRateProfile/"

    return HttpResponseRedirect(url)


@login_required
def addAccount(request):
    if request.POST:
        account = request.POST.get('add_name')
        
        try:
            Account.objects.get(account = account)
        except Account.DoesNotExist:
            Account.objects.create(account = account)
            
    return HttpResponseRedirect("/accountProfile/")

@login_required
def modAccount(request):
    if request.POST:
        save = request.POST.get('save')
        delete = request.POST.get('delete')
        pk = request.POST.get('mod_pk')
        
        try:
            account = Account.objects.get(pk = pk)
            if delete:
                account.delete()
                url = "/accountProfile/"
            elif save:
                account_name = str(request.POST.get('mod_name'))

                if account.account != account_name:
                    try:
                        Account.objects.get(account = account_name)
                        # if exists, forbidden
                    except Account.DoesNotExist:
                        account.account = account_name

                account.save()
                url = "/accountProfile/?pk=" + str(pk)
        except Exception, e:
            print str(e.message)
            url = "/accountProfile/"

    return HttpResponseRedirect(url)

@login_required
@csrf_exempt
def modFeeGroup(request):
    if request.POST:
        add = request.POST.get('add')
        save = request.POST.get('save')
        delete = request.POST.get('delete')
        
        if add:
            symbol = request.POST.getlist('symbols')[0]
            account = request.POST.getlist('accounts')[0]
            group = request.POST.getlist('groups')[0]
        else:
            symbol = request.POST.get('symbols')
            account = request.POST.get('accounts')
            group = request.POST.get('groups')
        
        try:
            feeGroup = FutureFeeGroup.objects.get(Q(symbol = symbol) & Q(account = account))
            if delete:
                if feeGroup.group == group:
                    feeGroup.delete()
            elif save:
                feeGroup.group = group
                feeGroup.save()
        except FutureFeeGroup.DoesNotExist:
            FutureFeeGroup.objects.create(symbol = symbol, account = account, group = group)

    return HttpResponseRedirect("/futureFeeGroupProfile/")

@login_required
def addGroup(request):
    if request.POST:
        name = request.POST.get('add_name')
        
        try:
            Group.objects.get(name = name)
        except Group.DoesNotExist:
            Group.objects.create(name = name)
            
    return HttpResponseRedirect("/groupProfile/")

@login_required
def modGroup(request):
    if request.POST:
        save = request.POST.get('save')
        delete = request.POST.get('delete')
        pk = request.POST.get('mod_pk')
        
        try:
            group = Group.objects.get(pk = pk)
            if delete:
                group.delete()
                url = "/groupProfile/"
            elif save:
                name = str(request.POST.get('mod_name'))
                if group.name != name:
                    try:
                        Group.objects.get(name = name)
                        # if exists, forbidden
                    except Group.DoesNotExist:
                        group.name = name
                        group.save()
                url = "/groupProfile/?pk=" + str(pk)
        except Exception, e:
            print str(e.message)
            url = "/groupProfile/"

    return HttpResponseRedirect(url)
