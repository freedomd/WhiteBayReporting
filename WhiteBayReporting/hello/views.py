from django.http import HttpResponse

def hello_world(request):
    info = 'Hello, world!\nThis would be a reporting system in the near future.'
    return HttpResponse(info)