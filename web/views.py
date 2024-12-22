import logging
import os
import string


from PIL import Image
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import user_passes_test
from django.contrib.messages.storage import default_storage
from django.contrib.sites import requests
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from bs4 import BeautifulSoup
from django.views.generic import TemplateView, FormView
from django.db.models import Q
from django_pandas.io import read_frame
import random
from django.urls import reverse_lazy
import json

from config import settings
from web.forms import ContactForm
from web.models import WebPage, Statue, Score, Subscribe, HorseColor, UserContact, LikeDislike, fetch_and_resize_image
import logging

User = get_user_model()

from selenium import webdriver
#from PIL import Image
from web.serializers import StatueSerializer

logger = logging.getLogger('django')

def is_superuser(user):
    return user.is_superuser

def landing(request):
    return HttpResponseRedirect(reverse_lazy("about"))

@user_passes_test(is_superuser)
def get_eqs_website(request):
    '''load initial database - NOTE images are loaded after main page content so beautiful soup can't see them'''

    url = "https://equestrianstatue.org/category/statues/"

    created = 0
    updated = 0
    processed = 0

    page_html = WebPage.get_or_create(url)

    data = []
    soup = BeautifulSoup(page_html, 'html.parser')
    # Find all article tags
    articles = soup.find_all('article')

    '''
    <article id="post-7931" class="post-7931 post type-post status-publish format-standard hentry category-india category-statues category-ullal-karnataka category-unknown">
	<header class="entry-header">
		
		<h2 class="entry-title"><a href="https://equestrianstatue.org/abbakka-chowta/" rel="bookmark">Abbakka, Chowta</a></h2>	</header><!-- .entry-header -->

	
	
	<div class="entry-content">
            <div class="lijst">
            <ul class="post-meta">
                                                                
                <a href="https://equestrianstatue.org/abbakka-chowta/" rel="bookmark"><li class="ab">Abbakka, Chowta</li></a>
                                <a href="https://equestrianstatue.org/category/sculptors/unknown/"><li class="ac">Unknown</li></a>
                                <li class="ad"></li>
                <a href="https://equestrianstatue.org/category/countries/india/"><li class="aa">India</li></a>
                <a href="https://equestrianstatue.org/category/town/ullal-karnataka/"><li class="aa">Ullal, Karnataka</li></a>
                <li class="ae"></li>
            </ul>
            </div>
	</div><!-- .entry-content -->

	
</article>
'''
    for article in articles:

        statue = {}

        header = article.find("h2").find("a")
        statue['name'] = header.string.get_text()
        statue['details_url'] = header.attrs['href']

        data = article.find("ul").find_all("li")
        statue['sculptor'] = data[1].string.get_text()
        statue['year'] = data[2].string
        statue['country'] = data[3].string.get_text()
        statue['location'] = data[4].string.get_text()
        statue['original'] = data[5].string

        obj, created = Statue.objects.get_or_create(**statue)
        print(obj)


class LikeDislikeLanding(TemplateView):
    #NOT USED
    '''gut like or dislike - https://pypi.org/project/django-random-queryset/'''

    template_name = "like_dislike_landing.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not self.request.user.is_authenticated:
            # Generate a random username and email
            random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

            email = f'{random_string}@equistatue.com'
            username = email
            password = User.objects.make_random_password()

            # Create and save the temporary user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # Log the user in
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(self.request, user)

        return context

class LikeDislikeView(TemplateView):

    '''gut like or dislike - https://pypi.org/project/django-random-queryset/'''

    template_name = "like_dislike.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if not self.request.user.is_authenticated:
            make_user(self.request)

        queryset = Statue.objects.scorable().filter(Q(like_yes__gt=0) | Q(like_no__gt=0) | Q(like_dontknow__gt=0)).order_by('updated')
        context['statues'] = queryset[0:10]

        return context


class LikeDislikeDone(TemplateView):

    '''gut like or dislike - https://pypi.org/project/django-random-queryset/'''

    template_name = "like_dislike_done.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['statues'] = LikeDislike.objects.filter(user=self.request.user).order_by('-created')[0:10]

        return context

    def post(self, request, *args, **kwargs):

        email = request.POST.get('email', None)


        # Update the user's email if provided
        user = None
        if email and request.user.is_authenticated:
            user = request.user
            user.email = email
            user.save()

        horsey = request.POST.get('horsey', False)
        if horsey== "Y":
            user.horsey = 1
            user.save()


        if email:
            # this is not working correctly - someone could enter someone else's email
            try:
                Subscribe.objects.get(email=email)
            except:
                Subscribe.objects.create(email=email, user=user)


        if 'feedback' in request.POST:
            contact = UserContact.add(user=user,  method="Feedback", notes=request.POST['feedback'])

        return HttpResponseRedirect("/")

class About(TemplateView):

    '''gut like or dislike - https://pypi.org/project/django-random-queryset/'''

    template_name='about.html'

    def post(self, request, *args, **kwargs):
        if 'email' in request.POST:
            Subscribe.objects.get_or_create(email=request.POST['email'])
        return HttpResponseRedirect("/")




class ScoreStatue(TemplateView):

    '''competition dashboard'''

    template_name = "score_statue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'pk' in kwargs:
            context['statue'] = Statue.objects.scorable().get(pk=kwargs['pk'])
        elif 'ref' in kwargs:
            context['statue'] = Statue.objects.scorable().get(ref=kwargs['ref'])
        else:
            queryset = Statue.objects.scorable()
            context['statue'] = queryset.random().first()
        return context

class ViewStatue(TemplateView):

    '''competition dashboard'''

    template_name = "statue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_staff:
            queryset = Statue.objects.all()
        else:
            queryset = Statue.objects.live()

        if 'pk' in kwargs:
            context['object'] = queryset.get(pk=kwargs['pk'])
        elif 'ref' in kwargs:
            context['object'] = queryset.get(ref=kwargs['ref'])
        else:
            context['object'] = None
        return context


class StatueStats(TemplateView):

    template_name = "statues_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Statue.objects.filter(scored_count__gt=0, skip=False).exclude('gallery',).order_by('-servant_partner_avg')
        df = read_frame(qs)
        df.to_csv('statue.csv', index=False)
        return context



class Show4Score(TemplateView):

    template_name = "show_statues.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'like' in kwargs:
            if kwargs['like'] == 'like':
                context['selection'] = f"Statues where people liked the representation of the horse"
                context['objects'] = Statue.objects.filter(like_yes__gt=1).order_by('-servant_partner_avg')
            else:
                context['selection'] = f"Statues where people did NOT like the representation of the horse"
                context['objects'] = Statue.objects.filter(like_no__gt=1).order_by('-servant_partner_avg')
        else:
            score = int(kwargs['score'])
            context['selection'] = f"Scores for Servant/Partner between {score-0.5} and {score+0.5}"
            context['objects'] = Statue.objects.filter(servant_partner_avg__gt=score-0.5, servant_partner_avg__lt=score+0.5).order_by('-servant_partner_avg')
        return context




class ContactView(FormView):

    form_class = ContactForm
    success_url = reverse_lazy('contact-thanks')
    template_name = "contact.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['horse_colors']= []
        for item in HorseColor.objects.exclude(code="_").exclude(code__in=['app','bay', 'bu','cr','pie','ro','sk']).order_by('?')[:3]:
            context['horse_colors'].append({'coat': item.coat_color_css,'mane': item.mane_color_css, 'id': item.code})

        # add bay because we are going to pick it
        item = HorseColor.objects.get(code="bay")
        context['chosen_color'] = item
        context['horse_colors'].append({'coat': item.coat_color_css, 'mane': item.mane_color_css, 'id': item.code})

        random.shuffle(context['horse_colors'])



        return context

    def form_valid(self, form):

        # contact form where there is not a logged in user includes a question.  If answered correctly "passed" field is set to "yes"
        method = "Contact"
        email = form.cleaned_data['email']
        user = None
        if self.request.user and self.request.user.is_authenticated:
            user = self.request.user
            method = "Support"

        # if user is logged in, we let them use a different email
        # if they are not logged in, we try to link them to a user to give them higher priority
        if not user:
            try:
                user = User.objects.get(email=email)
                method = "Support2"
            except:
                pass


        #user, _ = CustomUser.objects.update_or_create(email=email)

        # allow known users to pass through, otherwise do quick filter for bots
        if not user:
            msg = form.cleaned_data['message'].lower().strip()
            if 'robot' in msg or 'income' in msg or form.cleaned_data['passed'] != "yes":
                logger.warning(f"Dumped contact message from {email} message {json.dumps(form.cleaned_data)} ")
                # no feedback if junk
                return True

            user = User.system_user()

        # add contact note
        UserContact.add(user=user, method=method, notes = json.dumps(form.cleaned_data), data=json.dumps(form.cleaned_data))

        return super().form_valid(form)



@user_passes_test(is_superuser)
def update_avg(request):
    HorseColor.init()
    #
    # for item in Statue.objects.filter(main_image_url__isnull=False):
    #     item.update_avg()
    # return HttpResponse("Done")

@user_passes_test(is_superuser)
def fix(request):
    for item in Statue.objects.filter(ref__isnull=True):
        item.save()


def make_user(request):

        # Generate a random username and email
        random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=16))

        email = f'{random_string}@equistatue.com'
        username = email
        password = User.objects.make_random_password()

        # Create and save the temporary user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Log the user in
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)

def process_statue_image(request, statue_ref):
    """
    Fetch, resize, and save an image for a Statue object.

    Args:
        request: Django HTTP request.
        statue_id (int): ID of the Statue to process.

    Returns:
        JsonResponse with the result of the operation.
    """
    try:
        # Fetch the Statue object
        statue = Statue.objects.get(ref=statue_ref)

        if not statue.main_image_url:
            raise ValidationError('Main image URL is not set for this statue')

        # Resize and save the image to MEDIA_ROOT/statue_display_images/
        resized_image_path = fetch_and_resize_image(statue.main_image_url, filename=f'statue_{statue_ref}.jpg', media_subdir='statue_display_images',)

        if resized_image_path:
            # Save the resized image path in the display_image field
            statue.display_image.name = resized_image_path
            statue.save()

            # Construct the full URL for the image
            display_image_url = f"{settings.MEDIA_URL}{resized_image_path}"

            return JsonResponse({
                'message': 'Image processed successfully',
                'statue_id': statue.id,
                'display_image_url': display_image_url
            })
        else:
            return JsonResponse({'error': 'Failed to process image'}, status=500)

    except Statue.DoesNotExist:
        return JsonResponse({'error': 'Statue not found'}, status=404)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {e}'}, status=500)


def update_statue_images(request):

    for statue in Statue.objects.filter(main_image_url__isnull=False):
        process_statue_image(request, statue.ref)

    return HttpResponse("Done")
