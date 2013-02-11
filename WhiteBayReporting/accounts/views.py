from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from accounts.models import UserProfile

@login_required
def home(request):
    return HttpResponseRedirect("/tradeView/")

def register(request):
    try:
        user = request.user
        userProfile = user.get_profile()
    except:     
        email = password = firstname = lastname = error_message = '' 
        if request.POST:
            email = request.POST.get('email')
            password = request.POST.get('password')
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
         
            try:
                user = User.objects.get(username = email);  
                if user is not None:  
                    error_message = 'This email address has already been registered!'
                    password = ''
                    return render(request, 'register.html', locals())  
            except:
                user = User.objects.create_user(username = email, password = password, email = email)
                user.first_name = firstname
                user.last_name = lastname
                user.save()
                
                userProfile= UserProfile.objects.create( user = user )           
                userProfile.save()
                
                loginUser = auth.authenticate(username = email, password = password)
                auth.login(request,loginUser)
             
                return HttpResponseRedirect("/")
        else:
            return render(request, 'register.html', locals()) 
         
    return HttpResponseRedirect("/")

def login(request):
    try:
        user = request.user
        userProfile = user.get_profile()
    except:
        error = False
        email = password = ''
        if request.POST:
            email = request.POST.get('email')
            password = request.POST.get('password')
            loginUser = authenticate(username = email, password = password)
            if loginUser is not None and loginUser.is_active:
                auth.login(request, loginUser)
                return HttpResponseRedirect("/")
            else:
                error = True
                error_message = 'Invalid username or password.'
                password = ''
                return render(request, 'login.html', locals())
        else:
            return render(request, 'login.html', locals())
        
    return HttpResponseRedirect("/")

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")
    