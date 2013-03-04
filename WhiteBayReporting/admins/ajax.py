from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from admins.models import Broker
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
    
    data = {'pk': broker.pk, 'name': broker.name, 'commission': broker.commission, 
            'success': success, 'message': message }
    
    return simplejson.dumps(data)


@dajaxice_register
def modifyBroker(request, pk, name, commission):
    try:
        broker = Broker.objects.get(pk = pk)
        broker.name = name
        broker.commission = commission
        broker.save()
        success = "true"
        message = ""
    except:
        success = "false"
        message = "No such broker found."
    
    data = {'pk': broker.pk, 'name': broker.name, 'commission': broker.commission, 
            'success': success, 'message': message }

    return simplejson.dumps(data)