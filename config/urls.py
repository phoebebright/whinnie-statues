"""equistatue URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.auth.decorators import login_required
from django.urls import path, include
from rest_framework import routers
from django.conf.urls.static import static
from django.conf import settings

from web.views import *

router = routers.DefaultRouter()
router.register(r'statues', StatueViewSet)




urlpatterns = [
    path('api/', include(router.urls)),
    path('get_statues/eqstatuesorg/', get_eqs_website, name='get_eqstatueorg'),
    path('like_dislike/', LikeDislike.as_view(), name='like_dislike'),
    path('stats/', StatueStats.as_view(), name='statue_stats'),
    path('score/', login_required()(ScoreStatues.as_view()), name='score_statues'),
    path('statue/', login_required()(ScoreStatue.as_view()), name='score_statue'),
    path('admin/', admin.site.urls),

    path('privacy/', TemplateView.as_view(template_name='privacy_policy.html'), name="privacy"),
    path('cookies/', TemplateView.as_view(template_name='cookies.html'), name="cookies"),
    path('about/', TemplateView.as_view(template_name='about/help_overview.html'), name="about"),

    path('js_error_hook/', include('django_js_error_hook.urls')),
]
urlpatterns += [path(r"images-handler/", include("galleryfield.urls"))]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)