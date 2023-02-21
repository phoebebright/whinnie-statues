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
    path('score/', ScoreStatues.as_view(), name='score_statue'),
    path('admin/', admin.site.urls),

]
urlpatterns += [path(r"images-handler/", include("galleryfield.urls"))]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)