from django.conf import settings
from django.utils import timezone
from django.urls import reverse

import logging
logger = logging.getLogger('django')

def include_settings(request=None):
    """
    add settings related to environment
    """



    mode = request.session.get('user_mode', None)


    context = {'request': request,
               'user': request.user,
               'DEBUG': settings.DEBUG,
               'USE_ASSETS': settings.USE_ASSETS,
               'LANGUAGE_CODE': settings.LANGUAGE_CODE,
               'VERSION' : settings.VERSION,
               'API_VERSION' : settings.API_VER,
               'SITE_URL' : settings.SITE_URL,
               'SITE_NAME' : settings.SITE_NAME,
               'LOGIN_URL' : settings.LOGIN_URL,

               'cookielaw_accepted': request.COOKIES.get('cookielaw_accepted', False),

               }

    return context
