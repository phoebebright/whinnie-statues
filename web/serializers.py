from django.contrib.auth.models import User, Group
from rest_framework import serializers

from web.models import Statue, Score


class StatueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statue
        fields = '__all__'


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = '__all__'