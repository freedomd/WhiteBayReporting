from django.utils import simplejson
from dajaxice.decorators import dajaxice_register

@dajaxice_register
def sayhello(request):
    print "!"
    return simplejson.dumps({'message':'Hello World'})