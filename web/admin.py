from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from .models import *
from galleryfield.mixins import GalleryFormMediaMixin
from django import forms
from .forms import CustomUserCreationForm, CustomUserChangeForm

class MyGalleryAdminForm(GalleryFormMediaMixin, forms.ModelForm):
    class Meta:
        model = Statue
        exclude = ()

@admin.register(Statue)
class StatueAdmin(admin.ModelAdmin):
    list_display = ('name','country','year','original','main_image_url')



class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (_("Additional Info"), {
            "fields": (
                "horsey",
                "subscribed",
                "unsubscribed",
                "country",
                "sex",
                "age_range",
                "status",
            ),
        }),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (_("Additional Info"), {
            "fields": (
                "horsey",
                "subscribed",
                "unsubscribed",
                "country",
                "sex",
                "age_range",
                "status",
            ),
        }),
    )

admin.site.register(CustomUser, CustomUserAdmin)
