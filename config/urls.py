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
import os

from web.api import StatueViewSet, ScoreViewSet
from web.views import *

router = routers.DefaultRouter()
router.register(r'statues', StatueViewSet)
router.register(r'score', ScoreViewSet)

challenge_dir = os.path.join(settings.BASE_DIR,".well-known/acme-challenge")



urlpatterns = [
    path('api/', include(router.urls)),
    path('keycloak/', include('django_keycloak.urls')),
    path('get_statues/eqstatuesorg/', get_eqs_website, name='get_eqstatueorg'),
    path('like_dislike/landing/', LikeDislikeLanding.as_view(), name='like_dislike'),
    path('like_dislike/', LikeDislike.as_view(), name='like_dislike'),
    path('like_dislike/done/', LikeDislikeDone.as_view(), name='like_dislike_done'),
    path('stats/', StatueStats.as_view(), name='statue_stats'),
    path('examples/score/<int:score>/', Show4Score.as_view(), name='show4score'),
    path('examples/<str:like>/', Show4Score.as_view(), name='show4score'),

    path('statue/', login_required()(ScoreStatue.as_view()), name='score_statue'),
    path('statue/<int:pk>/', login_required()(ScoreStatue.as_view()), name='score_statue'),
    path('update_avg/',update_avg, name='update_avg'),
    path('admin/', admin.site.urls),

    path('hi/', ContactView.as_view(), name='contact'),
    path('privacy/', TemplateView.as_view(template_name='privacy_policy.html'), name="privacy"),
    path('cookies/', TemplateView.as_view(template_name='cookies.html'), name="cookies"),
    path('about/', About.as_view(), name="about"),

    path('js_error_hook/', include('django_js_error_hook.urls')),

    path('', landing, name='landing'),
]
urlpatterns += static('.well-known/acme-challenge', document_root=challenge_dir)


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [path(r"images-handler/", include("galleryfield.urls"))]
