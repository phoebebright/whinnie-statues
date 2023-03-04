from django import forms


class ContactForm(forms.Form):


    email = forms.EmailField()
    message = forms.CharField( widget=forms.Textarea(attrs={'cols': 80, 'rows': 20}) )
    passed = forms.CharField(widget=forms.HiddenInput())

