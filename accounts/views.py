from django.shortcuts import render, redirect, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.core.mail import  send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_text, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from .utils import token_gen
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.validators import validate_email
from .forms import ResetEmailForm
import random
from django.contrib.auth.decorators import login_required
from .models import Profile, PhoneNumber
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.conf import settings

User = get_user_model()

"""for threading function where a user 
is told a function is complete while still loading
"""
import threading


#africanstalking api
from decouple import config
import africastalking
username= config("username")
api_key = config("api_key")
africastalking.initialize(username, api_key)
sms_provider = africastalking.SMS

# Create your views here.
# class EmailThread(threading.Thread):
#     def __init__(self, mail):
#         self.mail = mail
#         threading.Thread.__init__(self)
        
#     def run(self):
#         self.mail.send_mail()
        
def LogInView(request, *args, **kwargs):
    next_page = request.GET.get('next')
    if request.method == 'POST':
        username = request.POST.get('log')
        password = request.POST.get('pwd')
    
        if username == "":
            messages.error(request, "Username required")
        if password == "":
            messages.error(request, "Password is required")
        
        user = authenticate(request, username=username, password=password)
            
        if user is not None:
            login(request, user)
            messages.info(request, "You have successfully logged in")
            if next_page is not None:
                return HttpResponseRedirect(next_page)
            return redirect('core:index')
        else:
            messages.error(request,"invalid Login! Try again")
            return render(request,'auth/login.html')
    return render(request, 'auth/login.html', {})

def LogOutView(request, *args, **kwargs):
    logout(request)
    messages.success(request,"You successfully logged out")
    return redirect('core:index')

def RegisterView(request):
    if request.method == 'POST':
        username = request.POST.get('user_login')
        email = request.POST.get('user_email')
        # phone = request.POST.get('phone') or None
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password1 = request.POST.get('pass1')
        password2 = request.POST.get('pass2')
        
        if username == "":
            messages.error(request, "Username is required")
        if email == "":
            messages.error(request, "Email is required")
        if password1 == "":
            messages.error(request, "Password is required")
        if password2 == "":
            messages.error(request, "Repeat Password is required")
            return redirect('user:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "A user with the username exists")
        if User.objects.filter(email=email).exists():
            messages.error(request, "The Email has already been taken")
            return redirect('user:register')

        
        if password1 != password2:
            messages.error(request, "Passwords do not match")
        if len(password1)<6:
            messages.error(request,"Password is too short")
            return redirect('user:register') 
            
                
        else:
            user = User.objects.create_user(username=username, 
                                            email=email)
            user.set_password(password1)
            user.is_active=False
            user.save()
            
            # profile = Profile.objects.get(user=user)
            # profile.phone = phone
            # phone_database = PhoneNumber(user=user,
            #                          phone=phone,
            #                          otp = random.randint(100000,999999),
            #                          is_verified=False)
            # phone_database.save()
            # profile.save()

            
            
            
            
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            domain = get_current_site(request).domain #gives us the domain
            link = reverse('user:activate', 
                            kwargs={
                                'uidb64':uidb64, 
                                'token':token_gen.make_token(user)
                                    })
            activate_url = f"http://{domain+link}"
            
            mail_subject = "Activate your account"
            
            """
            message = render_to_string('auth/activate.html', {
                'user':user,
                'domain':domain,
                'uidb64':uidb64,
                'token':token_gen.make_token(user)
            })
            """
            
            mail_body = f"hi {user.username} click the link below to verify your account\n {activate_url}"
            mail = send_mail (mail_subject, mail_body,'noreply@greengarnetsfilms.com',[email], fail_silently=False)
            messages.success(request, "Account created, Check your email to activate your account")
            return redirect('user:login')
            
    return render(request, 'auth/register.html', {})

def VerificationView(request,uidb64, token):

    uidb = force_text(urlsafe_base64_decode(uidb64)) or None
    user = User.objects.get(pk=uidb) or None

        
    if user is not  None and token_gen.check_token(user, token):
        user.is_active=True
        user.save()
        messages.info(request, "account activated successfully")  
        return redirect("user:login")
    return render(request,'auth/activation_failed.html')


def RequestResetEmail(request):
    if request.method == 'POST':
        email = request.POST.get('pms_username_email')
    
        user = User.objects.filter(email=email)
    
        if user.exists():
            uidb64 = urlsafe_base64_encode(force_bytes(user[0].pk))
            domain = get_current_site(request).domain #gives us the domain
            link = reverse('user:reset-password', 
                            kwargs={
                                'uidb64':uidb64, 
                                'token':PasswordResetTokenGenerator().make_token(user[0])
                                    })
            reset_password_url = f"http://{domain+link}"
            
            mail_subject = "Reset Password"
            
            """
            message = render_to_string('auth/activate.html', {
                'user':user.username,
                'url':activate_url,
            })
            """
            
            mail_body = f"hi {user[0].username} click the link below to reset your password\n {reset_password_url}"
            mail = send_mail (mail_subject, mail_body,'noreply@greengarnetsfilms.com',[email], fail_silently=False)
            messages.success(request, "Check your Email for the reset link")
            return redirect('user:login')
        else:
            messages.error(request, "Sorry, there is no user with that email")
            return redirect('user:request-reset-email')

    return render(request, 'auth/reset_email_form.html', {})
  
def ResetPasswordView(request, uidb64, token):
    
    
    
    if request.method == 'POST':
        context = {
            'uidb64':uidb64,
            'token':token,
        }
        
        password1 = request.POST.get('pass1')
        password2 = request.POST.get('pass2')
        
        if password1 == "":
            messages.error(request, "Password is required")
        if password2 == "":
            messages.error(request, "Repeat Password is required")
            return render(request, 'auth/reset_password.html', context)
        if password1 != password2:
            messages.error(request, "Passwords do not match")
        if len(password1)<6:
            messages.error(request,"Password is too short")
            return render(request, 'auth/reset_password.html', context)
        if password1 != password2:
            messages.error(request, "Passwords do not match")
        if len(password1)<6:
            messages.error(request,"Password is too short")
            return render(request, 'auth/reset_password.html', context)  
        
        try:
            user_id = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
            user.set_password(password1)
            user.save()
            messages.success(request, "password changed successfully")
            return redirect('user:login')
        except DjangoUnicodeDecodeError as identifier:
            messages.error(request, "oops! something went wrong")
            return render(request, 'auth/reset_password.html', context)
        
    context = {
        'uidb64':uidb64, 
        'token':token
        }
    try:
        user_id = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
        
        if not PasswordResetTokenGenerator().check_token(user, token):
            messages.error(request, "Opps, The link has expired")
            return render(request, 'auth/reset_email_form.html')
        
        messages.success(request, "verified")
        return render(request, 'auth/reset_password.html', context)
    except DjangoUnicodeDecodeError as identifier:
        messages.error(request, "oops! something went wrong")
        return render(request, 'auth/reset_email_form.html', context)
    return render(request, 'auth/reset_password.html', context)

@login_required
def MyAccountView(request, *args, **kwargs):
    profile = get_object_or_404(Profile, user=request.user)
    print(profile)
    context = {
        "profile":profile,
    }
    return render(request,'my-account.html',context)