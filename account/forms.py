from django import forms
from django.core.validators import validate_email
from django.contrib.auth import password_validation
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.hashers import check_password
from django.shortcuts import get_object_or_404

from .models import User, Profile


class ResetPasswordValidateEmailForm(forms.Form):
    email=forms.CharField(help_text="Enter your account email")

    def clean_email(self):
        email = self.data.get('email')
        validate_email(email)
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist as e:
            raise forms.ValidationError("Email user matched no account")
        
        return email


class ForgetPasswordForm(forms.Form):
    user_pk = forms.CharField(max_length=255)
    new_password=forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form__input'}),
        help_text=password_validation.password_validators_help_text_html()
    )
    confirm_password=forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form__input'}),
        help_text='Must be similar to first password to pass verification'
    )

    # Cleaning password one to check if all validations are met
    def clean_new_password(self):
        ps1=self.cleaned_data.get("new_password")
        password_validation.validate_password(ps1,None)
        return ps1

    """Override clean on password2 level to compare similarities of password"""
    def clean_confirm_password(self):
        ps1=self.cleaned_data.get("new_password")
        ps2=self.cleaned_data.get("confirm_password")
        if (ps1 and ps2) and (ps1 != ps2):
            raise forms.ValidationError("The passwords does not match")
        return ps2

    def save(self, commit=True):
        user = get_object_or_404(User, pk=self.cleaned_data.get('user_pk'))
        user.set_password(self.cleaned_data.get("new_password"))
        if commit:
            user.save()
        return user


class ChangePasswordForm(forms.Form):
    user_pk = forms.IntegerField()
    current_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form__input'}),
        help_text='Enter your current password here'
    )
    new_password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form__input'}),
        help_text=password_validation.password_validators_help_text_html()
    )

    # Cleaning old password to check if provided password matches user password
    def clean_current_password(self):
        user = get_object_or_404(User, pk=self.cleaned_data.get('user_pk'))
        password = self.cleaned_data.get('current_password')
        if not user.check_password(password):
            raise forms.ValidationError('Your password is not correct')
        return password

    # Cleaning password one to check if all validations are met
    def clean_new_password(self):
        ps1=self.cleaned_data.get("new_password")
        password_validation.validate_password(ps1,None)
        return ps1

    def save(self, commit=True):
        user = get_object_or_404(User, pk=self.cleaned_data.get('user_pk'))
        user.set_password(self.cleaned_data.get("new_password"))
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email      = forms.EmailField()
    password   = forms.CharField(widget=forms.PasswordInput())
    def clean(self):
        data=super(LoginForm, self).clean()
        email = data.get('email')
        password = data.get('password')
        validate_email(email)
        try:
            user = User.objects.get(email=email)
            if not user.check_password(password):
                self.add_error('password', forms.ValidationError('Your password is incorrect'))
        except User.DoesNotExist as e:
            self.add_error('email', forms.ValidationError("This account does not exist"))
        return data


class UserRegisterForm(forms.ModelForm):
    password=forms.CharField(label="Password",
        widget=forms.PasswordInput,
        min_length=8,
        help_text=password_validation.password_validators_help_text_html())
    confirm_password=forms.CharField(label="Confirm password",
                            widget=forms.PasswordInput,
                            help_text='Must be similar to first password to pass verification')
    username = forms.CharField(max_length=200)

    class Meta:
        model=User
        fields=("email", "password",)

    # Cleaning password one to check if all validations are met
    def clean_password(self):
        ps1=self.cleaned_data.get("password")
        here = password_validation.validate_password(ps1,None)
        return ps1
    
    # """Override clean on password2 level to compare similarities of password"""
    def clean_confirm_password(self):
        ps1=self.cleaned_data.get("password")
        ps2=self.cleaned_data.get("confirm_password")
        if (ps1 and ps2) and (ps1 != ps2):
            raise forms.ValidationError("Confirm password does not match with above password")
        return ps2
    
    def clean_username(self):
        username = self.cleaned_data.get('username')

        if Profile.objects.filter(discord_username__exact=username).exists():
            raise forms.ValidationError('Username has already been used')
        
        return username

    """ Override the default save method to use set_password method to convert text to hashed """
    def save(self, commit=True):
        user=super(UserRegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data.get("password"))

        if commit:
            user.save()
            # User profile is already created with user creation signal ( code is in the models.py )
            # Now we can access this newly created profile to update the username information
            user.profile.discord_username = self.cleaned_data.get("username")
            user.profile.save()

        return user

class ProfileForm(forms.Form):
    pk = forms.IntegerField()
    discord_username = forms.CharField(max_length=225)
    
    def save(self, commit=True):
        # Get the user object
        pk = self.cleaned_data.get('pk')
        user = get_object_or_404(User, id=pk)
        profile = user.profile

        discord_username = self.cleaned_data.get('discord_username')

        # Setting the profile data
        if discord_username:
            profile.discord_username = discord_username
        
        if commit:
            profile.save()
        
        return user


class UserUpdateForm(forms.ModelForm):
    password=ReadOnlyPasswordHashField()
    class Meta:
        model=User
        fields=("email","password","active","staff","admin",)
        def clean_password(self):
            # Regardless of what the user provides, return the initial value.
            # This is done here, rather than on the field, because the
            # field does not have access to the initial value
            return self.initial["password"]