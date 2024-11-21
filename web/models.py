import uuid
from urllib.request import urlopen
import os
import requests
import nanoid
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import mail_admins
from django.db import models
from django.db.models import Avg
from django_random_queryset import RandomManager
from galleryfield.fields import GalleryField
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.conf import settings
from django.db.models import Count, Max, Min


from django_random_queryset import strategies

User = get_user_model()

class WebPage(models.Model):
    '''Store pages being scraped so only need to get them once'''
    url = models.CharField(max_length=250)
    content = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_or_create(cls, url):

        if not 'http' in url:
            url = 'http://' + url

        try:
            page = cls.objects.get(url=url)
            return page.content
        except cls.DoesNotExist:
            page_html = urlopen(url).read()
            x = type(page_html)
            print("Type %s" % x)
            print("Loading page from internet")

            #content = page_html.decode('iso-8859-1').encode('utf-8')
            content = page_html.decode('utf-8')
            cls.objects.create(url=url, content=content)
            return page_html

class StatueQuerySet(models.QuerySet):

    def live(self):
        return self.filter(public_start__lte=timezone.now())

    def scorable(self):
        return self.filter(main_image_url__isnull=False, skip=False, ref__isnull=False)

    def random(self, amount=1):
            # from django-random-queryset - https://pypi.org/project/django-random-queryset/
            aggregates = self.aggregate(
                min_id=Min("id"), max_id=Max("id"), count=Count("id")
            )

            if not aggregates["count"]:
                return self.none()

            if aggregates["count"] <= amount:
                return self.all()

            if (aggregates["max_id"] - aggregates["min_id"]) + 1 == aggregates["count"]:
                return self.filter(
                    id__in=strategies.min_max(
                        amount,
                        aggregates["min_id"],
                        aggregates["max_id"],
                        aggregates["count"],
                    )
                )

            try:
                selected_ids = strategies.min_max_count(
                    amount, aggregates["min_id"], aggregates["max_id"], aggregates["count"]
                )
            except strategies.SmallPopulationSize:
                selected_ids = self.values_list("id", flat=True)

            assert len(selected_ids) > amount
            return self.filter(id__in=selected_ids).order_by("?")[:amount]


class Statue(models.Model):
    ref = models.CharField(max_length=6, blank=True, null=True)
    name = models.CharField(max_length=100)
    # main_image = models.ImageField(blank=True, null=True)
    main_image_url = models.URLField(blank=True, null=True)
    details_url = models.URLField(blank=True, null=True)
    other_img_url = models.URLField(blank=True, null=True)
    sculptor = models.CharField(max_length=100)
    year = models.CharField(max_length=10, blank=True, null=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    original = models.CharField(max_length=50, blank=True, null=True)
    skip = models.BooleanField(default=False)
    missing_image =  models.BooleanField(default=False)
    servant_partner_avg = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    scored_count = models.PositiveSmallIntegerField(default=0)
    like_yes = models.PositiveSmallIntegerField(default=0)
    like_no = models.PositiveSmallIntegerField(default=0)
    like_dontknow = models.PositiveSmallIntegerField(default=0)
    # gallery = GalleryField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    updated = models.DateTimeField(blank=True, null=True)
    public_start = models.DateTimeField(blank=True, null=True)


    objects = StatueQuerySet().as_manager()


    def __str__(self):
        return f"{self.name} - {self.location},{self.country}"

    def save(self, *args, **kwargs):

        if not self.ref:
            self.ref = nanoid.generate(alphabet="23456789abcdefghjkmnpqrstvwxyz", size=6)
        self.updated = timezone.now()
        self.scored_count = self.like_no + self.like_yes + self.like_dontknow
        super().save(*args, **kwargs)

    @property
    def main_image(self):

        local_image_path = f"images/image_{self.ref}.jpg"  # Relative path within the MEDIA directory

        try:
            image_url = get_or_download_image(self.main_image_url, local_image_path)
        except ValueError as e:
            # Handle error gracefully, e.g., use a placeholder image
            image_url = "/static/images/placeholder.jpg"


        return image_url

    def add_score(self, data, user):
        Score.objects.update_or_create(statue=self, creator=user, defaults={'servant_partner':data['servant_partner']} )

        # recalc avg and count

        self.update_avg()

    def update_avg(self):
        self.scored_count = Score.objects.filter(statue=self).count()
        if self.scored_count > 0:
            result = Score.objects.filter(statue=self).aggregate(Avg('servant_partner'))
            if result['servant_partner__avg'] > 0:
                self.servant_partner_avg = result['servant_partner__avg']
                self.save()

    def update_likes(self, value):

        if value == 0:
            self.like_dontknow += 1
        elif value < 0:
            self.like_no += 1
        else:
            self.like_yes += 1
        self.save()

class Score(models.Model):
    statue = models.ForeignKey(Statue, on_delete=models.CASCADE)
    servant_partner = models.IntegerField(default=99)
    created = models.DateTimeField(auto_created=True)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,auto_created=True, null=True, on_delete=models.SET_NULL)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.statue} - {self.creator}"

    def save(self, *args, **kwargs):
        self.created = timezone.now()
        super().save(*args, **kwargs)

class LikeDislike(models.Model):
    session_id = models.CharField(max_length=255, null=True, blank=True)  # Track by session
    source = models.CharField(max_length=12, default="Equistatue")   # where was response left
    statue = models.ForeignKey(Statue, on_delete=models.CASCADE)
    score = models.SmallIntegerField(default=0, help_text=_("-1 for dislike, 1 for like, 0 for don't know"))
    created = models.DateTimeField(auto_created=True)

    def __str__(self):
        return f"{self.pk} - {self.statue} - {self.score}"

class Subscribe(models.Model):
    email = models.EmailField(unique=True)
    created = models.DateTimeField(auto_created=True)


    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        self.created = timezone.now()
        super().save(
            *args, **kwargs)


class HorseColor(models.Model):

    UNKNOWN = '-'

    code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=12)
    coat_color_css = models.CharField(max_length=7, default="black")
    mane_color_css = models.CharField(max_length=7,default="black")


    def __str__(self):
        return str(self.name)
    class Meta:
        ordering = ['name',]
    @classmethod
    def init(cls):
        '''lazy approach to fixtures'''
        cls.objects.get_or_create(code="app", name="Appaloosa", coat_color_css="#c8702b", mane_color_css="white")
        cls.objects.get_or_create(code="bay", name="Bay", coat_color_css="#7a4924", mane_color_css="black")
        cls.objects.get_or_create(code="bl", name="Black", coat_color_css="black", mane_color_css="black")
        cls.objects.get_or_create(code="br", name="Brown", coat_color_css="#c8702b", mane_color_css="#c8702b")
        cls.objects.get_or_create(code="bu", name="Buckskin", coat_color_css="#b87f53")
        cls.objects.get_or_create(code="ch", name="Chestnut", coat_color_css="#c8702b", mane_color_css="#bc6c2e")
        cls.objects.get_or_create(code="cr", name="Cremelo", coat_color_css="#c7baaa", mane_color_css="#c7baaa")
        cls.objects.get_or_create(code="dun", name="Dun", coat_color_css="#b87f53")
        cls.objects.get_or_create(code="gr", name="Grey",  coat_color_css="#b0adad", mane_color_css="#cac8c8")
        cls.objects.get_or_create(code="pal", name="Palamino")
        cls.objects.get_or_create(code="pie", name="Piebald")
        cls.objects.get_or_create(code="ro", name="Roan")
        cls.objects.get_or_create(code="sk", name="Skewbald")
        cls.objects.get_or_create(code=cls.UNKNOWN, name="Not Known")

        for item in cls.objects.all():
            setattr(cls, item.name.upper(), item.code)

class UserContact(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    contact_date = models.DateTimeField(auto_now_add=True)
    method = models.CharField(max_length=40)
    notes = models.TextField(blank=True, null=True)
    data = models.TextField(blank=True, null=True)  # use for json data, convert to field when avaialble

    def __str__(self):
        return "%s" % self.user

    def __str__(self):
        return "%s" % self.user

    @classmethod
    def add(cls, user, method, notes=None, data=None):

        obj = cls.objects.create(user=user, method=method, notes=notes, data=data)

        mail_admins("User Contact %s - %s " % (obj.user, obj.method), obj.notes, fail_silently=True)


def get_or_download_image(image_url, local_path):
    """
    Check if the image exists locally. If not, download and save it locally.

    :param image_url: The URL of the remote image
    :param local_path: The relative path to store the image locally
    :return: The local file path (URL-safe for templates)
    """
    # Build the full local path
    full_local_path = os.path.join(settings.MEDIA_ROOT, local_path)
    local_url_path = os.path.join(settings.MEDIA_URL, local_path)

    # Check if the file already exists locally
    if default_storage.exists(local_path):
        return local_url_path

    # Download the image if it doesn't exist
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        # Save the file locally
        default_storage.save(local_path, ContentFile(response.content))
        return local_url_path

    # Handle the case where the image couldn't be retrieved
    raise ValueError(f"Could not retrieve image from {image_url}. HTTP Status: {response.status_code}")
