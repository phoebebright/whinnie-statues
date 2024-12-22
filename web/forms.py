from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser

class ContactForm(forms.Form):


    email = forms.EmailField()
    message = forms.CharField( widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}) )
    passed = forms.CharField(widget=forms.HiddenInput())

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'horsey', 'subscribed', 'unsubscribed', 'country']

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'horsey', 'subscribed', 'unsubscribed', 'country']
