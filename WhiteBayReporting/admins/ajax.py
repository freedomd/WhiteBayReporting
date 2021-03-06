from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from admins.models import Broker, Trader, System, Employer, Account, Group, FutureMultiplier, FutureFeeRate, FutureFeeGroup
from django.core import serializers
from django.db.models import Q

@dajaxice_register
def getBroker(request, pk):
    try:
        broker = Broker.objects.get(pk = pk)
        success = "true"
        message = ""
    except:
        success = "false"
        message = "No such broker found."
    
    data = {'pk': broker.pk, 'brokerNumber': broker.brokerNumber, 'securityType': broker.securityType, 
            'commissionRate': broker.commissionRate, 
            'success': success, 'message': message }
    #print data
    
    return simplejson.dumps(data)

@dajaxice_register
def getTrader(request, pk):
    try:
        trader = Trader.objects.get(pk = pk)
        system_list = trader.systems.all()
        system_list_serialized = serializers.serialize('json', system_list)
        success = "true"
        message = ""
    except:
        success = "false"
        message = "No such trader found."
    
    data = {'pk': trader.pk, 'name': trader.name, 'ssn': trader.SSN, 
            'addr': trader.addr, 'phone': trader.phone, 
            'email': trader.email, 'username': trader.username, 
            'password': trader.password, 'cfee': trader.clearanceFee, 'bfee': trader.brokerFee, 
            'system_list': simplejson.loads(system_list_serialized),
            'success': success, 'message': message }
    
    return simplejson.dumps(data)

@dajaxice_register
def queryFutureList(request, symbol):
    
    # start filter
    future_list = None
    
    if symbol is not u"" or None:
        if future_list is None:
            future_list = FutureFeeRate.objects.filter(Q(symbol__icontains=symbol))
        else:
            future_list = future_list.filter(Q(symbol__icontains=symbol))
    
    future_list = future_list.order_by("symbol", "group")
        
    future_list_serialized = serializers.serialize('json', future_list)

    data = { 'future_list': simplejson.loads(future_list_serialized) }
    
    return simplejson.dumps(data)

@dajaxice_register
def showFutureList(request):
    
    # get all the objects
    future_list = FutureFeeRate.objects.all().order_by("symbol", "group")        
    future_list_serialized = serializers.serialize('json', future_list)

    data = { 'future_list': simplejson.loads(future_list_serialized) }
    
    return simplejson.dumps(data)

@dajaxice_register
def getFuture(request, pk):
    try:
        future = FutureFeeRate.objects.get(pk = pk)
        success = "true"
        message = ""
    except:
        success = "false"
        message = "No such Future found."
    
    data = {'pk': future.pk, 'symbol': future.symbol, 
            'clearing': future.clearingFeeRate,
            'exchange': future.exchangeFeeRate,
            'nfa': future.nfaFeeRate,
            'group': future.group,
            'success': success, 'message': message }
    
    return simplejson.dumps(data)

@dajaxice_register
def queryFutureMultiList(request, symbol):
    
    # start filter
    future_list = None
    
    if symbol is not u"" or None:
        if future_list is None:
            future_list = FutureMultiplier.objects.filter(Q(symbol__icontains=symbol))
        else:
            future_list = future_list.filter(Q(symbol__icontains=symbol))
    
    future_list = future_list.order_by("symbol")
        
    future_list_serialized = serializers.serialize('json', future_list)

    data = { 'future_list': simplejson.loads(future_list_serialized) }
    
    return simplejson.dumps(data)

@dajaxice_register
def showFutureMultiList(request):
    
    # get all the objects
    future_list = FutureMultiplier.objects.all().order_by("symbol")        
    future_list_serialized = serializers.serialize('json', future_list)

    data = { 'future_list': simplejson.loads(future_list_serialized) }
    
    return simplejson.dumps(data)

@dajaxice_register
def getFutureMulti(request, pk):
    try:
        future = FutureMultiplier.objects.get(pk = pk)
        success = "true"
        message = ""
    except:
        success = "false"
        message = "No such Future found."
    
    data = {'pk': future.pk, 'symbol': future.symbol, 
            'multiplier': future.multiplier,
            'success': success, 'message': message }
    
    return simplejson.dumps(data)


@dajaxice_register
def getSystem(request, systemIdList):
    print systemIdList

    try:
        system_list = []
        for system in systemIdList:
            system_list.append(System.objects.get(pk=system))
        
        system_list_serialized = serializers.serialize('json', system_list)
        success = "true"
        message = ""
    except Exception, e:
        success = "false"
        message = str(e.message)
    
    data = {'system_list': simplejson.loads(system_list_serialized),
            'success': success, 'message': message }
    
    print data
    
    return simplejson.dumps(data)

@dajaxice_register
def getEmployer(request, pk):
    try:
        employer = Employer.objects.get(pk = pk)
        success = "true"
        message = ""
    except:
        success = "false"
        message = "No such employer found."
    
    data = {'pk': employer.pk, 'name': employer.name,
            'success': success, 'message': message }
    
    return simplejson.dumps(data)

@dajaxice_register
def getAccount(request, pk):
    try:
        account = Account.objects.get(pk = pk)
        success = "true"
        message = ""
    except:
        success = "false"
        message = "No such account found."
    
    data = {'pk': account.pk, 'account': account.account,
            'success': success, 'message': message }
    
    return simplejson.dumps(data)

@dajaxice_register
def getGroup(request, pk):
    try:
        group = Group.objects.get(pk = pk)
        success = "true"
        message = ""
    except:
        success = "false"
        message = "No such group found."
    
    data = {'pk': group.pk, 'name': group.name,
            'success': success, 'message': message }
    
    return simplejson.dumps(data)

@dajaxice_register
def getFeeGroup(request, symbol, account, group):
    #print symbol, account, group
    try:
        feeGroupList = None
        if symbol != "default":
            feeGroupList = FutureFeeGroup.objects.filter(Q(symbol=symbol))
        if account != "default":
            if feeGroupList == None:
                feeGroupList = FutureFeeGroup.objects.filter(Q(account=account))
            else:
                feeGroupList = feeGroupList.filter(Q(account=account))
            num = len(feeGroupList) # one account should be only in one group for one symbol
        if group != "default":
            if feeGroupList == None:
                feeGroupList = FutureFeeGroup.objects.filter(Q(group=group))
            else:
                feeGroupList = feeGroupList.filter(Q(group=group))
        
        groupList = Group.objects.all()
        groupList_serialized = serializers.serialize('json', groupList)
        
        feeGroupList = feeGroupList.order_by("symbol", "account")
        feeGroupList_serialized = serializers.serialize('json', feeGroupList)
        
        if symbol != "default" and account != "default" and num != 0:
            existed = "true"
        else:
            existed = "false"
        success = "true"
        message = ""
        data = {'feeGroupList': simplejson.loads(feeGroupList_serialized),
                'groupList': simplejson.loads(groupList_serialized),
                'existed': existed, 'success': success, 'message': message }
    except:
        success = "false"
        message = ""
        data = { 'success': success, 'message': message }

    
    return simplejson.dumps(data)