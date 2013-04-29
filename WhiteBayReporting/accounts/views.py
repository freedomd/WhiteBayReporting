from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from accounts.models import UserProfile
from datetime import date
from admins.models import Account

@login_required
def home(request):
    today=date.today()
    url="/firmReport/"
    return HttpResponseRedirect(url)

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

@login_required
def settingView(request):
    user = request.user
    userProfile = UserProfile.objects.get(user=request.user)
    
    if request.POST:
        user.first_name = request.POST.get('firstname')
        user.last_name = request.POST.get('lastname')
        user.save()
        
        userProfile.user = user
        userProfile.addr = request.POST.get('addr')
        userProfile.phone = request.POST.get('phone')
        userProfile.description = request.POST.get('description')
        userProfile.save()

    return render(request, 'settings.html', locals()) 

@login_required
def changePasswordView(request):
    if request.POST:
        oldpassword = request.POST.get('oldpassword')
        newpassword = request.POST.get('newpassword')
        renewpassword = request.POST.get('renewpassword')
        username = request.user.username
        
        if newpassword != renewpassword:
            message = "Your password doesn't match."
        else:
            loginUser = auth.authenticate(username = username, password = oldpassword)
            if loginUser:
                loginUser.set_password(newpassword)
                loginUser.save()
                message = "Saved."
            else:
                message = "Invalid old password."

    return render(request, 'changePassword.html', locals()) 
        

def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")
    