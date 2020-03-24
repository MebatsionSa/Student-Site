from django.http import HttpResponse
from django.shortcuts import render, redirect
# from django.db import ...
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.core.mail import EmailMessage
from django.template.loader import get_template, render_to_string
from django.template import Context
from .forms import UserRegisterForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from .tokens import account_activation_token
from .forms import User
# Create your views here.
def index(request):
    return render(request,
                 'siteapp/index.html')

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active=False
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activate your account'
            message = render_to_string('siteapp/acc_activation_email.html',{
                'user':user,
                'domain':current_site.domain,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token':account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            return render(request,
                         'siteapp/email_confirmation.html')

    else:
        form = UserRegisterForm()
    return render(request,
                  "siteapp/register.html",
                  context={"form":form}) # must be tha same name as the one in register.html
        
# user will get activate link to their email address
def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect("/")
    else:
        return render(request,
                      "siteapp/activation_expired.html")

def logout_(request):
    logout(request)
    messages.info(request, "logged out successfully!")
    return redirect("siteapp:index")

def login_(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
           
            if user is not None:
               form = login(request,user)
               messages.success(request, f"you are now logged in as {username}")
               return redirect("siteapp:home")
            else:
                messages.error(request, "Invalid username or password")    
        else:
            messages.error(request, "Invalid username or password")

    form = AuthenticationForm()
    return render(request,
                  "siteapp/login.html",
                  {"form":form}) # must be tha same name as the one in register.html
  
