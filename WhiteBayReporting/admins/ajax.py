from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from admins.models import Broker, Trader, System, Employer, Account, Group, FutureFeeRate
from django.core import serializers

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
def modifyBroker(request, pk, brokerNumber, securityType, commissionRate):
    try:
        broker = Broker.objects.get(pk = pk)
        broker.brokerNumber = brokerNumber
        broker.securityType = securityType
        broker.commissionRate = commissionRate
        broker.save()
        success = "true"
        message = ""
    except:
        success = "false"
        message = "No such broker found."
    
    data = {'pk': broker.pk, 'brokerNumber': broker.brokerNumber, 'securityType': broker.securityType, 
            'commissionRate': broker.commissionRate, 
            'success': success, 'message': message }

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
def getFuture(request, pk):
    try:
        future = FutureFeeRate.objects.get(pk = pk)
        success = "true"
        message = ""
    except:
        success = "false"
        message = "No such trader found."
    
    data = {'pk': future.pk, 'symbol': future.symbol, 
            'clearing': future.clearingFeeRate,
            'exchange': future.exchangeFeeRate,
            'nfa': future.nfaFeeRate,
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
    
    data = {'pk': account.pk, 'group': account.group, 'account': account.account,
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