from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import logout,authenticate,login
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.utils.encoding import force_text,force_bytes
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode

from .models import User
from .forms import (UserRegisterForm, LoginForm, ChangePasswordForm,
    ResetPasswordValidateEmailForm, ForgetPasswordForm)
from .tokens import acount_confirm_token



def verification_message(request, user, template):
	site=get_current_site(request)
	uid=urlsafe_base64_encode(force_bytes(user.pk))
	token=acount_confirm_token.make_token(user)
	message=render_to_string(template,{
		"user": user.profile.discord_username,
		"uid": uid,
		"token": token,
		"domain": site.domain,
		'from': settings.DEFAULT_FROM_EMAIL
	})
	return message


class RegistrationView(FormView):
    template_name = 'account/register.html'
    extra_context = {
        'title': 'Get started today',
    }
    form_class = UserRegisterForm

    def get(self, request, *args, **kwargs):
        # Check if user is already logged in
        if request.user.is_authenticated:
            return redirect('dashboard:home')

        context = self.get_context_data()
        context['form'] = self.form_class()
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        request = self.request
        context = self.get_context_data()

        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            subject=f"Lunar Promos Verification"
            message = verification_message(request, user, "account/activation_email.html")
            sent=user.email_user(subject,message)
            messages.success(request, f'You account is successfully created. A link was sent to your email {user.email}, use the link to verify you account.')
            return redirect('account:login')

        context['form'] = form
        messages.warning(request, 'Please correct your data.')
        
        return render(request, self.template_name, context)


class LoginView(FormView):
    template_name = 'account/login.html'
    extra_context = {
        'title': 'We have missed you'
    }
    form_class = LoginForm

    def get(self, request, *args, **kwargs):
        # Check if user is already logged in
        if request.user.is_authenticated:
            return redirect('dashboard:home')

        context = self.get_context_data()
        context['form'] = self.form_class()
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        request = self.request
        context = self.get_context_data()

        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            user = authenticate(request, username=email, password=password)
            if user:
                login(request, user)
                messages.success(request, f'Welcome, {user.profile.discord_username}')
                return redirect('dashboard:home')
            else:
                messages.warning(request, 'Your email is not yet verified.')
                return redirect('account:login')
        
        context['form'] = form
        messages.warning(request, 'Please correct your data.')
        
        return render(request, self.template_name, context)


def activate_email(request, uidb64, token):
	try:
		uid=force_text(urlsafe_base64_decode(uidb64))
		user=User.objects.get(pk=uid)
	except (TypeError, ValueError, OverflowError, User.DoesNotExist):
		user=None
	if user!=None and acount_confirm_token.check_token(user,token):
		user.active=True
		user.save()

		messages.success(request,f'{user.email}, your email is now verified successfully, you can now login')
		return redirect('account:login')
	else:
		messages.warning(request, 'This link is invalid')
		return redirect('account:login')


class ChangePassword(LoginRequiredMixin, UpdateView):
    template_name = 'account/change_password.html'
    extra_context = {
        'title': 'Change Password'
    }
    form_class = ChangePasswordForm

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['form'] = self.form_class()

        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        request = self.request
        context = self.get_context_data()

        cloned = request.POST.copy()
        cloned['user_pk'] = request.user.pk

        form = self.form_class(cloned)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Your password is successfully changed, please login with your new password')
            return redirect('account:logout')
        else:
            messages.warning(request, 'You did not properly fill the change password form.')
        
        context['form'] = form
        
        return render(request, self.template_name, context)


class ResetPasswordFormPage(FormView):
    template_name = 'account/reset_password_form.html'
    extra_context = {
        'title': 'Reset Password',
    }
    form_class = ResetPasswordValidateEmailForm

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['form'] = self.form_class()

        return render(request, self.template_name, context)
    
    def post(self, *args, **kwargs):
        request = self.request

        form = self.form_class(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            user = get_object_or_404(User, email=email)

            # Send the reset link to user
            subject = "Lunar Promos Password Reset"
            message = verification_message(request, user, "account/password_reset.html")
            sent = user.email_user(subject,message)

            messages.success(request, 'We sent your password reset link to your email, click on the link to reset your password')

            return redirect('dashboard:home')
        
        context = self.get_context_data()
        context['form'] = form

        return render(request, self.template_name, context)


class ResetPasswordVerify(FormView):
    template_name = 'account/reset_password_page.html'
    extra_context = {
        'title': 'Reset your password',
    }
    form_class = ForgetPasswordForm

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        context['form'] = self.form_class()

        # Get uidb4 and token from kwargs
        uidb64 = self.kwargs.get('uidb64')
        token = self.kwargs.get('token')

        uid=force_text(urlsafe_base64_decode(uidb64))
        user=get_object_or_404(User, pk=uid)

        if acount_confirm_token.check_token(user,token):
            messages.success(request,'Reset password link is valid, change your password with the form below')
        else:
            messages.warning(request, 'This password reset link is already invalid.')
            return redirect('dashboard:home')

        return render(request, self.template_name, context)
    
    def post(self, *args, **kwargs):
        request = self.request

        # Get uidb4 from kwargs and get the user instance
        uidb64 = self.kwargs.get('uidb64')
        uid=force_text(urlsafe_base64_decode(uidb64))
        user=get_object_or_404(User, pk=uid)

        # Get request.POST and copy
        default_post = request.POST.copy()
        default_post['user_pk'] = user.pk

        form = self.get_form_class()
        form = form(default_post)

        if form.is_valid():
            form.save()
            messages.success(request, 'You password has been successfully changed, now login with your new password')
            return redirect('account:login')
        
        context = self.get_context_data()
        context['form'] = form

        return render(request, self.template_name, context)

def Logout(request):
    logout(request)
    messages.success(request, 'You have logged out')
    return redirect('account:login')