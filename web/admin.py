from django.contrib import admin
from .models import *
from galleryfield.mixins import GalleryFormMediaMixin
from django import forms

class MyGalleryAdminForm(GalleryFormMediaMixin, forms.ModelForm):
    class Meta:
        model = Statue
        exclude = ()

@admin.register(Statue)
class StatueAdmin(admin.ModelAdmin):
    list_display = ('name','country','year','original')