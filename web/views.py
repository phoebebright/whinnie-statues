import logging

from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from bs4 import BeautifulSoup
from django.views.generic import TemplateView
from django_pandas.io import read_frame

from django.urls import reverse_lazy

from web.models import WebPage, Statue, Score
import logging



from selenium import webdriver
#from PIL import Image
from web.serializers import StatueSerializer

logger = logging.getLogger('django')

def is_superuser(user):
    return user.is_superuser

def landing(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse_lazy("score_statue"))
    else:
        return HttpResponseRedirect(reverse_lazy("like_dislike"))

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


class LikeDislike(TemplateView):

    '''gut like or dislike - https://pypi.org/project/django-random-queryset/'''

    template_name = "like_dislike.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        queryset = Statue.objects.filter(skip=False, main_image_url__isnull=False)
        context['statues'] = queryset.random(10)
        context['session_id'] = self.request.session._get_or_create_session_key()
        return context



class ScoreStatues(TemplateView):

    '''competition dashboard'''

    template_name = "statues.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['statues'] = Statue.objects.filter(scored_count=0, skip=False).order_by('-servant_partner')
        return context


class ScoreStatue(TemplateView):

    '''competition dashboard'''

    template_name = "score_statue.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if 'pk' in kwargs:
            context['statue'] = Statue.objects.get(pk=kwargs['pk'])
        else:
            queryset = Statue.objects.filter(scored_count=0, skip=False)
            context['statue'] = queryset.random().first()
        return context



class StatueStats(TemplateView):

    template_name = "statues_stats.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = Statue.objects.filter(scored_count__gt=0, skip=False).order_by('-servant_partner')
        df = read_frame(qs)
        df.to_csv('statue.csv', index=False)
        return context





#
# def move_score(request):
#
#     for item in Statue.objects.filter(servant_partner__lte=10, skip=False):
#         Score.objects.create(statue=item, creator=request.user, servant_partner=item.servant_partner)
#         item.scored_count = 1
#         item.save()
#     return HttpResponse("Done")