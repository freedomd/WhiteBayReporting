'''
Created on Apr 28, 2013

@author: ZhiZeng
'''
from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from accounts.models import UserProfile


@dajaxice_register
def getUserProfile(request, pk):
    try:
        userprofile = UserProfile.objects.get(pk=pk)
        success = "true"
        message = ""
        message += "result"
    except:
        success = "false"
        message = "Cannot find your profile."
    
    data = {'pk': userprofile.pk, 'first_name': userprofile.user.first_name, 'last_name': userprofile.user.last_name,
            'addr': userprofile.addr, 'phone': userprofile.phone, 'description': userprofile.description,
            'success': success, 'message': message}
    
    return simplejson.dumps(data)

